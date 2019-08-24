use rocket_contrib::json::Json;
use serde::{Deserialize, Serialize};

use grover::GroverConfig;

#[derive(Debug, Serialize, Deserialize)]
pub struct GenerateRequest {
    pub meta: ArticleMetadata,
    pub target: GenerateTarget
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ArticleMetadata {
    title: String,
    text: String,
    domain: String,
    summary: String,
    authors: String,
    url: String,
    publish_date: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum GenerateTarget {
    Article,
    Title
}

impl GenerateTarget {
    pub fn to_str(&self) -> &str {
        match self {
            GenerateTarget::Article => "article",
            GenerateTarget::Title => "title"
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct Generated {
    #[serde(alias = "gens_title")]
    gens_article: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ArticleResponse {
    gen: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Model {
    Base,
    Large,
    Mega
}

#[post("/", format = "application/json", data = "<req>")]
pub fn gen(req: Json<GenerateRequest>) -> String {
    println!("received gen request {:?}", req);
    let req = req.0;

    let mut cfg = GroverConfig::from_fs("GroverConfig.json")
        .unwrap_or(GroverConfig::default());
    println!("using grover config {:?}", cfg);

    let gen = cfg.generate_article(req)
        .expect("failed to generate article");
    let resp = ArticleResponse {
        gen: gen.gens_article.get(0)
            .expect("failed to create article response from generated article").clone()
    };

    println!("generated article {}", resp.gen.clone());
    serde_json::to_string(&resp)
        .expect("failed to serialize generated article response")
}

#[cfg(test)]
mod tests {
    use grover::GroverConfig;

    #[test]
    fn foo() {
        let cfg = GroverConfig::from_fs("GroverConfig.json")
            .unwrap_or(GroverConfig::default());
        println!("using grover config {:?}", cfg);
    }
}

