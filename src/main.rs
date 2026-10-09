use curl_impersonate_rs::{
    cli::{self, Action, CliError},
    engine,
};
use std::io::{self, Write};

fn output(bytes: &[u8]) -> Result<(), CliError> {
    let mut stdout = io::stdout().lock();
    stdout
        .write_all(bytes)
        .and_then(|_| stdout.flush())
        .map_err(|e| CliError::new(23, e.to_string()))
}

fn main() {
    let args: Result<Vec<_>, _> = std::env::args_os()
        .skip(1)
        .map(|s| s.into_string())
        .collect();
    let parsed = args
        .map_err(|_| CliError::new(2, "v0 requires UTF-8 arguments"))
        .and_then(cli::parse);
    let mut show_error = true;
    let result = match parsed {
        Ok(Action::Help) => output(include_bytes!("help.txt")),
        Ok(Action::Version) => engine::version().and_then(|v| {
            output(
                format!(
                    "curl-impersonate-rs {}\nEngine: {v}\n",
                    env!("CARGO_PKG_VERSION")
                )
                .as_bytes(),
            )
        }),
        Ok(Action::Profiles) => engine::list_profiles().and_then(|p| output(p.as_bytes())),
        Ok(Action::Transfer(config)) => {
            show_error = !config.silent || config.show_error;
            engine::run(&config)
        }
        Err(error) => Err(error),
    };
    if let Err(error) = result {
        if show_error {
            let _ = writeln!(
                io::stderr().lock(),
                "curl-impersonate: ({}) {}",
                error.code,
                error.message
            );
        }
        std::process::exit(error.code.clamp(1, 255));
    }
}
