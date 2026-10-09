use curl_impersonate_rs::cli::{parse, Action, Config};

fn transfer(args: &[&str]) -> Config {
    match parse(args.iter().map(|s| s.to_string()).collect()).unwrap() {
        Action::Transfer(c) => *c,
        other => panic!("expected a transfer, got {other:?}"),
    }
}

#[test]
fn clustered_flags_and_attached_values_preserve_curl_meaning() {
    let c = transfer(&[
        "-sSL",
        "-XPOST",
        "-H",
        "Accept: application/json",
        "-oout.bin",
        "https://httpbin.org/get",
    ]);
    assert!(c.silent && c.show_error && c.follow);
    assert_eq!(c.method.as_deref(), Some("POST"));
    assert_eq!(c.headers, ["Accept: application/json"]);
    assert_eq!(c.output.as_deref(), Some("out.bin"));
    assert_eq!(c.url, "https://httpbin.org/get");
}

#[test]
fn equals_values_and_fractional_timeouts_are_supported() {
    let c = transfer(&[
        "--url=https://httpbin.org/get",
        "--max-time=0.125",
        "--header=X-Test: a=b",
    ]);
    assert_eq!(c.timeout_ms, Some(125));
    assert_eq!(c.headers, ["X-Test: a=b"]);
}

#[test]
fn repeated_headers_and_data_are_not_discarded() {
    let c = transfer(&[
        "-H",
        "X-A: 1",
        "-H",
        "X-A: 2",
        "-d",
        "a=1",
        "-d",
        "b=2",
        "https://httpbin.org/get",
    ]);
    assert_eq!(c.headers, ["X-A: 1", "X-A: 2"]);
    assert_eq!(c.data.len(), 2);
}

#[test]
fn unsupported_or_incomplete_invocations_fail_before_transfer() {
    for args in [
        vec!["--retry", "2", "https://httpbin.org/get"],
        vec!["-H"],
        vec!["https://a.test", "https://b.test"],
        vec!["--max-time", "NaN", "https://httpbin.org/get"],
        vec!["--max-time", "-1", "https://httpbin.org/get"],
        vec!["--silent=yes", "https://httpbin.org/get"],
        vec!["--no-impersonate=yes", "https://httpbin.org/get"],
    ] {
        assert_eq!(
            parse(args.into_iter().map(String::from).collect())
                .unwrap_err()
                .code,
            2
        );
    }
}

#[test]
fn informational_commands_do_not_require_a_url() {
    assert_eq!(parse(vec!["--help".into()]).unwrap(), Action::Help);
    assert_eq!(parse(vec!["--version".into()]).unwrap(), Action::Version);
    assert_eq!(
        parse(vec!["--list-profiles".into()]).unwrap(),
        Action::Profiles
    );
}
