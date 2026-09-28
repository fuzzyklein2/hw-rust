/******************************************************************************
*
*   CONFIGURATION
*
******************************************************************************/
//! Read the configuration file. It helps if the file exists but, if it doesn't,
//! a default file should be created at the XDG_CONFIG_FILE location. This is
//! usually `~/.config/<PROGRAM>/config.json`.
use std::fs;
use std::io::Error;
use std::path::PathBuf;
use std::process::exit;

use clap::Parser;
use json::JsonValue;

use crate::CONFIGURATION;
use crate::FILE_SYSTEM;
use crate::INPUT;
use crate::ARGUMENTS;

use crate::constants::ERROR_PICT;
use crate::files::FileSystem;
use crate::getargs::{ Args, get_piped_input };
use crate::logging::error;

/******************************************************************************
*
*   JSON
*
******************************************************************************/
/// Contains a JSON value.
#[derive(Debug)]
pub struct JSON {
    /// `json` object
    pub value: JsonValue,
}

/******************************************************************************
*
*   JSON::new()
*
******************************************************************************/
/// Load a JSON object from a file.
/// 
/// # Parameters
/// 
/// *`p`: Path to the JSON file.
/// 
/// # Return
/// 
/// A new JSON object.
///
/// 🚧 TODO: This would be better implemented as the FromFile trait.
impl JSON {
    pub fn new(p: &PathBuf) -> Self {
        if !p.exists() {
            error(&format!("File {:?} does not exist!", p));
            exit(1);
        } // if !p.exists()
        let contents = fs::read_to_string(p)
            .expect(&format!("JSON::new : file {:?} cannot be read!", p));

        Self {
            value: json::parse(&contents).unwrap(),
        } // Self
    } // new
} // impl

/******************************************************************************
*
*   configure()
*
******************************************************************************/
/// Initialize `FILE_SYSTEM`, read `config.json` into `CONFIGURATION`, parse the
/// CLI arguments and piped input, if there is any.
/// 
/// # Return
/// 
/// `Error` if something goes wrong.
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
} // configure