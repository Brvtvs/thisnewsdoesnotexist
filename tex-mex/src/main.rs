#![feature(plugin)]
#![feature(proc_macro_hygiene, decl_macro)]

#[macro_use]
extern crate rocket;
extern crate rocket_codegen;
extern crate rocket_contrib;
extern crate serde;
extern crate serde_json;
extern crate uuid;

use rocket_codegen::routes;

mod api;
mod grover;

fn main() {
    rocket::ignite()
        .mount("/", routes![api::gen])
        .launch();
}