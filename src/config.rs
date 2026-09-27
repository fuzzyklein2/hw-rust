use std::fs;
use std::io::Error;
use std::path::PathBuf;

use clap::Parser;
use json::JsonValue;

use crate::CONFIGURATION;
use crate::constants::ERROR_PICT;
use crate::FILE_SYSTEM;
use crate::INPUT;
use crate::ARGUMENTS;

use crate::files::FileSystem;
use crate::getargs::{ Args, get_piped_input };

#[derive(Debug)]
pub struct JSON {
    pub value: JsonValue,
}

impl JSON {
    pub fn new(p: &PathBuf) -> Self {
        let contents = fs::read_to_string(p).unwrap();

        Self {
            value: json::parse(&contents).unwrap(),
        }
    }
}

pub fn configure() -> Result<(), Error> {
    let args = Args::parse();
    FILE_SYSTEM.set(FileSystem::new())
        .expect("`FILE_SYSTEM` initialized");
    CONFIGURATION.set(JSON::new(&FILE_SYSTEM.get()
        .expect(&format!("{}  Configuration file failed to load!", ERROR_PICT))
        .config_file))
        .expect(&format!("{}  `CONFIGURATION` could not be loaded!", ERROR_PICT));
    ARGUMENTS.set(args).unwrap();
    
    if let Some(input) = get_piped_input() {
        INPUT.set(input).unwrap();
    }
    Ok(())
}