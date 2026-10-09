<div align="center">

<h1>🦎 curl-impersonate-rs</h1>

<p><strong>Browser profiles. curl-style commands. Ready-to-run Docker.</strong></p>

<p>Explore HTTP responses with browser-specific TLS and HTTP settings,<br>right from your terminal and scripts.</p>

<p>
  <a href="Cargo.toml"><img src="https://img.shields.io/badge/Rust-CLI-E57324?style=for-the-badge&amp;logo=rust&amp;logoColor=white" alt="Rust CLI"></a>
  <a href="native/bridge.c"><img src="https://img.shields.io/badge/C-Native_bridge-526D82?style=for-the-badge&amp;logo=c&amp;logoColor=white" alt="C native bridge"></a>
  <a href="vendor/curl-impersonate/"><img src="https://img.shields.io/badge/libcurl-Native_engine-073551?style=for-the-badge&amp;logo=curl&amp;logoColor=white" alt="libcurl native engine"></a>
  <a href="https://hub.docker.com/r/juanfontes/curl-impersonate"><img src="https://img.shields.io/badge/Docker-Ready_to_run-2496ED?style=for-the-badge&amp;logo=docker&amp;logoColor=white" alt="Ready-to-run Docker image"></a>
</p>

<p>
  <a href="https://hub.docker.com/r/juanfontes/curl-impersonate/tags?name=0.0.1-rc.1"><img src="https://img.shields.io/badge/Release-0.0.1--rc.1-D97706?style=flat-square" alt="Release 0.0.1-rc.1"></a>
  <img src="https://img.shields.io/badge/Profiles-39-0F766E?style=flat-square" alt="39 browser and client profiles">
  <img src="https://img.shields.io/badge/Linux-amd64_%7C_arm64-334155?style=flat-square&amp;logo=linux&amp;logoColor=white" alt="Linux amd64 and arm64">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-0F766E?style=flat-square" alt="MIT license"></a>
</p>

<p>
  <a href="#use-the-published-docker-image">🚀 Quick start</a> ·
  <a href="#browser-profiles">🌐 Profiles</a> ·
  <a href="#http-examples">🧰 Examples</a> ·
  <a href="#current-compatibility">🧭 Compatibility</a> ·
  <a href="CONTRIBUTING.md">🛠️ Contributing</a>
</p>

</div>

---

<a id="use-the-published-docker-image"></a>

## 🚀 Quick start — use the published image

The ready-to-use image is public on [Docker Hub](https://hub.docker.com/r/juanfontes/curl-impersonate): **`juanfontes/curl-impersonate:0.0.1-rc.1`**. You only need Docker with Linux container support. No repository checkout, Rust/C toolchain, or `docker build` is required.

### Your first request

```sh
# Send a request with the Chrome 150 profile and print the response body.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome150 --compressed -sS https://httpbin.org/get
```

`docker run` automatically downloads the image if it is not already available locally. Pass CLI options directly after the image name. The image starts `curl-impersonate` automatically.

The same tag includes **Linux amd64 and arm64**; Docker selects the matching architecture automatically. This is a release candidate of CLI 0.0.1; the [compatibility limits](#current-compatibility) below still apply.

### Explore the CLI

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 --version
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 --help
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 --list-profiles
```

The image includes the CLI, native engine, shared libraries, and CA certificates. The [HTTP examples](#http-examples) below all use this published image, including headers, body output, authentication, redirects, and saving files.

<a id="browser-profiles"></a>

## 🌐 Browser profiles

Pick a browser family, copy a profile ID, and pass it to `--impersonate`. Release `0.0.1-rc.1` includes **39 profiles** across desktop browsers, mobile browsers, and HTTP clients.

| Browser or client | Target | Profile IDs |
| --- | --- | --- |
| Chrome | 🖥️ Desktop | `chrome99`, `chrome100`, `chrome101`, `chrome104`, `chrome107`, `chrome110`, `chrome116`, `chrome119`, `chrome120`, `chrome123`, `chrome124`, `chrome131`, `chrome133a`, `chrome136`, `chrome142`, `chrome145`, `chrome146`, `chrome150` |
| Chrome | 🤖 Android | `chrome99_android`, `chrome131_android` |
| Edge | 🖥️ Desktop | `edge99`, `edge101` |
| Firefox | 🖥️ Desktop | `firefox133`, `firefox135`, `firefox144`, `firefox147` |
| Safari | 🖥️ Desktop | `safari153`, `safari155`, `safari170`, `safari180`, `safari184`, `safari260`, `safari2601` |
| Safari | 📱 iOS | `safari172_ios`, `safari180_ios`, `safari184_ios`, `safari260_ios` |
| Tor Browser | 🖥️ Desktop | `tor145` |
| OkHttp | 🤖 Android client | `okhttp4_android` |

These are versioned presets, not an automatically updated list of current browser releases. For example, `safari2601` targets Safari 26.0.1 and `tor145` targets Tor Browser 14.5. Selecting a Tor Browser profile does not route traffic through Tor. The target describes the impersonated client; any listed profile can be selected in either the Linux amd64 or arm64 image.

> **Preset note:** `okhttp4_android` is an HTTP client profile, and its bundled default headers include a desktop Safari User-Agent. Inspect or override those headers before using it; its presence in the catalog does not establish OkHttp fingerprint fidelity.

Run `--list-profiles` to check the IDs accepted by your installed engine. The [CLI catalog](src/profiles.txt) supplies that command; the [native profile definitions](vendor/curl-impersonate/patches/curl.patch) contain the TLS, HTTP/2, and header settings compiled into the engine. The catalog is embedded in the CLI at build time.

### Try desktop and mobile profiles

```sh
# Firefox desktop.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate firefox147 --compressed -sS https://httpbin.org/user-agent

# Safari desktop.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate safari2601 --compressed -sS https://httpbin.org/user-agent

# Chrome on Android.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome131_android --compressed -sS https://httpbin.org/headers

# Safari on iOS.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate safari260_ios --compressed -sS https://httpbin.org/headers
```

These endpoints echo HTTP headers received by httpbin. They are useful for inspecting requests, but do not validate TLS or HTTP/2 fingerprints against real browsers.

### Set a default profile or supply your own headers

Pass `CURL_IMPERSONATE` into the container to select a profile through the environment:

```sh
docker run --rm -e CURL_IMPERSONATE=firefox147 \
  juanfontes/curl-impersonate:0.0.1-rc.1 \
  --compressed -sS https://httpbin.org/headers
```

Profiles include browser headers by default. Use `:no` to keep the profile's TLS/HTTP settings while disabling its default headers; `:yes` explicitly enables them:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome150:no --compressed -sS \
  -H 'Accept: application/json' -H 'X-Test: custom-headers' \
  https://httpbin.org/headers
```

For environment-based selection, `-e CURL_IMPERSONATE_HEADERS=no` disables profile headers. Explicit CLI options are applied after the profile: `-H`, `-A`, and protocol flags can change its network characteristics. `--compressed` enables response decompression; a profile's `Accept-Encoding` header alone does not enable decoding in this CLI.

<a id="http-examples"></a>

## 🧰 HTTP cookbook

The commands below use [httpbin](https://httpbin.org/), a public HTTP request/response testing service. Impersonation is opt-in through `--impersonate` or `CURL_IMPERSONATE`. Add `--impersonate <profile>` to any of the general HTTP examples to select a browser preset.

Find the recipe you need:

| You want to… | Jump to |
| --- | --- |
| Read the HTTP status | [Status codes](#print-only-the-http-status) |
| Inspect response headers | [HEAD and GET headers](#print-only-response-headers) |
| Print or save the response body | [Body and output files](#print-the-body-or-headers-and-body-together) |
| Follow a redirect or fail on an HTTP error | [Redirects and errors](#follow-redirects-and-handle-http-errors) |
| Send custom headers, Basic auth, or JSON | [Request data](#send-headers-credentials-and-json) |
| Inspect the request or set a timeout | [Diagnostics](#diagnose-a-request-and-limit-waiting-time) |

### Print only the HTTP status

Discard the body with `-o /dev/null`, use `-sS` for silent mode with errors still shown, and print the status with `-w`:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome150 --compressed -sS -o /dev/null \
  -w '%{http_code}\n' https://httpbin.org/status/200

docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -o /dev/null -w '%{http_code}\n' https://httpbin.org/status/301

docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -o /dev/null -w '%{http_code}\n' https://httpbin.org/status/502
```

Without `-L`, the redirect response is returned directly. HTTP 4xx/5xx responses do not make the process fail unless a failure option is enabled; the HTTP status and process exit code are different values.

### Print only response headers

`-I` sends a **HEAD request**, which asks for headers without a response body:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -I https://httpbin.org/status/200
```

To inspect the headers of a **GET request**, keep the default method, send headers to stdout with `-D -`, and discard the body:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -D - -o /dev/null https://httpbin.org/get
```

### Print the body, or headers and body together

The response body is the default output. `/get` returns JSON; `/status/200` can return an empty body:

```sh
# Body only.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome150 --compressed -sS https://httpbin.org/get

# Response headers followed by the body.
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -i https://httpbin.org/get
```

Save headers and body separately to your current host directory:

```sh
docker run --rm -v "$PWD:/work" juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -D response.headers -o response.json \
  -w 'HTTP %{http_code}\n' https://httpbin.org/get
```

Container file paths are relative to `/work`. Mount a writable directory when saving responses, especially when running with a custom `--user`.

### Follow redirects and handle HTTP errors

Follow a redirect and print the final URL and status after the body:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -L --max-redirs 5 \
  -w '\nFinal: %{url_effective} — HTTP %{http_code}\n' \
  https://httpbin.org/status/301
```

Use `--fail-with-body` to return process exit code 22 on HTTP errors while retaining any body supplied by the server. `-f` also returns 22 but suppresses the error body:

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS --fail-with-body -w '\nHTTP %{http_code}; exit %{exitcode}\n' \
  https://httpbin.org/status/502

docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -f https://httpbin.org/status/502
```

These two examples intentionally fail when the server returns 502. That exit code propagates through `docker run` and may stop a shell script using `set -e`.

### Send headers, credentials, and JSON

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -H 'X-Test: hello' https://httpbin.org/headers

docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS -u demo:demo https://httpbin.org/basic-auth/demo/demo

printf '{"hello":"world"}' | docker run --rm -i juanfontes/curl-impersonate:0.0.1-rc.1 \
  -sS --json @- https://httpbin.org/post
```

### Diagnose a request and limit waiting time

```sh
docker run --rm juanfontes/curl-impersonate:0.0.1-rc.1 \
  --impersonate chrome150 --compressed -v \
  --connect-timeout 5 --max-time 20 https://httpbin.org/get
```

Verbose diagnostics go to stderr; the body goes to stdout or `-o`. Public service responses can vary or time out; automated compatibility tests use local fixtures. Pass container environment variables explicitly with `docker run -e NAME=value`. `--help` lists supported options.

<a id="current-compatibility"></a>

## 🧭 Compatibility & scope

The Rust CLI calls **libcurl-impersonate directly** through a small C bridge. The native profiles configure TLS ClientHello characteristics, protocol negotiation, HTTP/2 settings and pseudo-header ordering, and default HTTP headers. The CLI accepts a documented subset of curl options and preserves response bytes.

This is an HTTP client: it does not render pages or execute JavaScript. The bundled profiles are presets; successful requests do not establish equivalence with a real browser's fingerprint.

- One HTTP(S) URL per process; GET, HEAD, `-X`, `-G`, and redirects with `-L`.
- Repeated headers and header files, user-agent, referer, and Basic credentials with `user:password`.
- `-d`, `--data-raw`, `--data-binary`, `--json`, files, and stdin. `--data @file` strips CR/LF/NUL as documented by current curl; `--data-binary` preserves bytes.
- `-o`, `-D`, `-i`, binary response bodies, `--compressed`, cookies, HTTP/SOCKS proxy options, and fractional timeouts.
- TLS verification enabled by default; explicit `--cacert` and `-k`. `CURL_CA_BUNDLE`, `SSL_CERT_FILE`, and `SSL_CERT_DIR` are supported.
- `--http1.0`, `--http1.1`, `--http2`, `--http3`, and `--http3-only` map to the engine. HTTP/3 has not been validated end to end by this project.
- Browser profiles via `--impersonate` and upstream `CURL_IMPERSONATE`/`CURL_IMPERSONATE_HEADERS`; `--list-profiles` validates every catalog name against the loaded library.
- Native transfer exit codes, `-f`, `--fail-with-body`, `-sS`, `-v`, `-N`, and limited write-out.

Write-out supports `%{http_code}`, `%{response_code}`, `%{url_effective}`, `%{content_type}`, `%{num_redirects}`, `%{http_version}`, `%{time_total}`, `%{exitcode}`, `%%`, `\n`, `\r`, `\t`, and formats from `@file`. Unknown variables are errors.

Deliberate v0 limits: no `.curlrc`, `--config`, `--next`, multiple URLs, URL globbing, multipart forms, streaming uploads, retries, parallel transfers, progress meter, or exact stderr parity. `-q` is accepted; `.curlrc` is never loaded. Unknown flags fail with code 2. There is no interactive password prompt; use `-u user:password`. Arguments, header files, and write-out formats require UTF-8. Mixing `--json` with other body options is rejected. Request bodies are buffered; response bodies stream without text conversion.

Compatibility comparisons cover the tested subset, not every flag combination. Successful HTTPS/HTTP/2 requests do not prove browser fingerprint equivalence. There are no claims of undetectability or performance gains.

<a id="development-and-validation"></a>

## 🛠️ Build & contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for source builds, focused checks, runtime exports, engine updates, and pull request guidance. The root `Dockerfile` derives from the published runtime; `docker/Dockerfile.build` compiles the project for maintainers.

<a id="repository-layout"></a>

## 🗂️ Project layout

| Path | Purpose |
| --- | --- |
| `src/` | Rust CLI, embedded help text, and profile catalog |
| `native/` | C bridge to the native engine |
| `vendor/curl-impersonate/` | Verified engine build inputs, patches, provenance, and license |
| `scripts/` | Source verification, compilation, and runtime packaging |
| `tests/` | Parser, source-integrity, and HTTP/TLS compatibility checks |
| `docker/` | Maintainer Dockerfile and its build-context exclusions |
| `.github/workflows/` | CI for amd64 and arm64 |
| `Dockerfile` | Distribution image derived from a ready runtime |
| `engine.lock` | Engine input pins |
| `CONTRIBUTING.md` | Build, validation, maintenance, and contribution guide |
| `Cargo.toml`, `Cargo.lock`, `build.rs` | Rust package, dependency lock, and native build integration |
| `LICENSE`, `NOTICE` | Project license and third-party attribution |

<a id="next-steps"></a>

## 🗺️ What’s next

The next milestones focus on measurable fidelity and easier maintenance:

- [ ] Compare network captures with real browsers.
- [ ] Automate tested releases for amd64 and arm64.
- [ ] Publish standalone CLI artifacts.
- [ ] Update browser catalogs and dependencies together.
- [ ] Expand curl compatibility using representative scripts.
- [ ] Validate HTTP/3 end to end.

<a id="licenses"></a>

## 📄 License

Original code is MIT licensed under [LICENSE](LICENSE). [NOTICE](NOTICE) describes the incorporated components; the engine's original license remains in [vendor/curl-impersonate/LICENSE](vendor/curl-impersonate/LICENSE). Docker includes the collected native dependency notices at `/usr/share/licenses/curl-impersonate-rs/native/`. This is an independent project, not an official curl or upstream curl-impersonate release.

<p align="center"><a href="#use-the-published-docker-image">↑ Back to quick start</a></p>
