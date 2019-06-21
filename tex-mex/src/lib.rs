extern crate reqwest;
extern crate serde;
extern crate serde_json;
extern crate textwrap;

use reqwest::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct ArticleRequest {
    target: String,
    title: String,
    article: String,
    domain: String,
    date: String,
    authors: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ArticleResponse {
    gen: String,
}

pub fn gen_text(
    url: &str,
    target: &str,
    title: &str,
    article: &str,
    domain: &str,
    date: &str,
    authors: &str,
) -> Result<String> {
    let req = ArticleRequest {
        target: target.to_owned(),
        title: title.to_owned(),
        article: article.to_owned(),
        domain: domain.to_owned(),
        date: date.to_owned(),
        authors: authors.to_owned(),
    };

    let resp: ArticleResponse = reqwest::Client::new()
        .post(url)
        .header(
            "User-Agent",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0",
        )
        .json(&req)
        .send()?
        .json()?;

    Ok(resp.gen)
}

#[cfg(test)]
mod tests {
    use gen_text;

    #[test]
    fn req() {
        let headline = "Former President Bill Clinton disgraced again";
        if let Ok(gen) = gen_text(
            "https://api.grover.allenai.org/api/ask",
            "article",
            headline,
            "",
            "nytimes.com",
            "June 16, 2019",
            "",
        ) {
            let terminal_width = textwrap::termwidth();
            println!("\n\n{}\n", headline);
            println!("{}\n\n", textwrap::fill(&gen, terminal_width));
        }
    }
}
