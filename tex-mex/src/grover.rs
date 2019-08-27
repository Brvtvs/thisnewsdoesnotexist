use std::path::{Path, PathBuf};
use std::process::Command;
use serde::{Serialize, Deserialize};

use api::{ArticleMetadata, Generated, Model, GenerateRequest};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct GroverConfig {
    absolute_path: String,
    generate_script_path: String,
    config_path: String,
    model_path: String,
    metadata_path: String,
    model: Model
}

impl GroverConfig {
    pub fn new(absolute_path: &str,
               generate_script_path: &str,
               config_path: &str,
               model_path: &str,
               metadata_path: &str,
               model: Model) -> Self {
        GroverConfig {
            absolute_path: absolute_path.to_owned(),
            generate_script_path: generate_script_path.to_owned(),
            config_path: config_path.to_owned(),
            model_path: model_path.to_owned(),
            metadata_path: metadata_path.to_owned(),
            model,
        }
    }

    pub fn default() -> Self {
        GroverConfig::new("/tex-mex/grover/",
                          "sample/contextual_generate.py",
                          "lm/configs/meta.json",
                          "models/meta/model.ckpt",
                          "sample/meta.json",
                          Model::Mega)
    }

    pub fn from_fs(path: &str) -> Option<GroverConfig> {
        if let Ok(json) = std::fs::read_to_string(path) {
            if let Ok(res) = serde_json::from_str(json.as_str()) {
                return Some(res);
            }
        }

        None
    }

    pub fn get_path(&self, element: &str) -> PathBuf {
        let element = element.clone();
        Path::new(&self.absolute_path).join(element)
    }

    pub fn generate_article(&mut self, req: GenerateRequest) -> Option<Generated> {
        // use grover's embedded python
        std::env::set_var("PYTHON_PATH", self.absolute_path.clone());

        let meta = &req.meta;

        // write metadata to file
        let meta_path = self.get_path(&self.metadata_path);
        println!("wrote article metadata to {}", meta_path.clone().to_string_lossy());
        write_to_file(&meta_path, meta);

        // generate random file to store meta & output
        let output = self.rng_output_name();

        // init grover command
        if let Ok(mut child) = Command::new("python")
            .current_dir(&self.absolute_path)
            .arg(&self.generate_script_path)
            .arg("-model_config_fn")
            .arg(&self.config_path)
            .arg("-model_ckpt")
            .arg(&self.model_path)
            .arg("-target")
            .arg(req.target.to_str())
            .arg("-metadata_fn")
            .arg(&meta_path)
            .arg("-out_fn")
            .arg(&output)
            .spawn() {
            let code = child.wait()
                .expect("something went wrong waiting for the grover process to exit")
                .code()
                .expect("failed to get status code for grover process");
            println!("got status code {}", code);

            if code != 0 {
                None
            } else {
                Some(self.get_generated_article(output.as_str()))
            }
        } else {
            panic!("failed to start grover process");
        }
    }

    fn get_generated_article(&self, generated_file: &str) -> Generated {
        let path = Path::new(&self.absolute_path).join(generated_file);
        println!("reading generated article from {}", path.to_string_lossy());
        read_from_file(path)
    }

    fn rng_output_name(&self) -> String {
        let out_name = Uuid::new_v4().to_string();
        let out_file = Path::new(&self.absolute_path)
            .join(out_name.clone());
        out_file.to_string_lossy().into_owned()
    }
}

fn write_to_file(path: &PathBuf, meta: &ArticleMetadata) {
    let json = serde_json::to_string(meta)
        .expect("failed to serialize article metadata");
    std::fs::write(path, json)
        .expect("failed to write article metadata to file");
}

fn read_from_file(path: PathBuf) -> Generated {
    let json = std::fs::read_to_string(path)
        .expect("failed to read generated article from file");
    serde_json::from_str(json.as_str())
        .expect("failed to deserialize generated article")
}