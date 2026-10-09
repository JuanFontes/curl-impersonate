# Changelog

## 0.1.1 — 2026-10-09

### Fixed

- Automatically decode compressed HTTP responses whenever an impersonation profile is active, including the default profile and environment-selected profiles.
- Preserve explicit `--compressed` and `--no-compressed` choices; the last compression flag wins. Without impersonation, decompression remains opt-in.
- Simplify the documented `curli` alias and request examples: no compression flag is needed for normal browser-profile requests.

### Compatibility

Use `--no-compressed` if a script needs the encoded response bytes returned by earlier versions. Existing `--compressed` commands continue to work. Suppressing profile headers with `:no` or `CURL_IMPERSONATE_HEADERS=no` does not disable decoding. Response headers retain their received values, and binary response bodies are not converted to text.

The native engine, profile definitions, supported platforms, and documented curl option subset are unchanged. Regression checks cover decoding, opt-out, profile selection, header preservation, and file output.

## 0.1.0 — 2026-10-09

First public release of the Rust CLI backed by the bundled libcurl-impersonate engine.

### Included

- Browser impersonation enabled by default with the fixed `chrome150` profile.
- 39 browser and HTTP client presets, selected with `--impersonate` and listed with `--list-profiles`.
- `--no-impersonate` to disable profiles; explicit CLI selection takes precedence over environment defaults.
- A documented subset of curl options for HTTP requests, redirects, authentication, headers, cookies, proxies, TLS configuration, and response output.
- Docker images for Linux amd64 and arm64, plus native Linux bundles and an experimental macOS Apple Silicon download.
- Checksums, dependency notices, and source provenance packaged with downloads.
- A shared release version from `Cargo.toml` for the CLI, CI, and default package names.

### Upgrading from release candidates

RC3 already enables Chrome 150 by default. Scripts written for the unprofiled default in RC1/RC2 should add `--no-impersonate`. Keep `--compressed` when you want decoded response bodies. The native engine and profile definitions are unchanged from RC3.

### Scope

One URL per invocation. Multiple URLs, `--next`, `.curlrc`/`--config`, multipart forms, streaming uploads, retries, and parallel transfers are not implemented. The CLI does not render pages or execute JavaScript. HTTP/3 and real-browser fingerprint equivalence remain unverified.

The macOS package is experimental, signed ad hoc, and not notarized. Windows and Intel Mac native packages are not available. See the [compatibility guide](README.md#current-compatibility) and [platform table](README.md#platform-support).
