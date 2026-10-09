# 🦎 curl-impersonate

**Browser impersonation from your terminal. Ready to run with Docker.**

![Release 0.1.1](https://img.shields.io/badge/Release-0.1.1-0F766E?style=flat-square)
![Rust CLI](https://img.shields.io/badge/Rust-CLI-E57324?style=flat-square&logo=rust&logoColor=white)
![libcurl engine](https://img.shields.io/badge/libcurl-Engine-073551?style=flat-square&logo=curl&logoColor=white)
![Linux amd64 and arm64](https://img.shields.io/badge/Linux-amd64_%7C_arm64-334155?style=flat-square&logo=linux&logoColor=white)

Send HTTP requests with browser-specific TLS and HTTP settings using familiar curl-style options. **Chrome 150 impersonation and response decompression are enabled by default.** Select Firefox, Safari, Edge, mobile browser profiles, and more with `--impersonate`.

The Rust CLI calls the bundled libcurl-impersonate engine directly. The image includes its runtime libraries and CA certificates. You only need Docker with Linux container support.

[Source & full guide](https://github.com/JuanFontes/curl-impersonate) · [Native downloads](https://github.com/JuanFontes/curl-impersonate/releases/tag/v0.1.1) · [Changelog](https://github.com/JuanFontes/curl-impersonate/blob/main/CHANGELOG.md) · [Report an issue](https://github.com/JuanFontes/curl-impersonate/issues)

## 🚀 Your first request

```sh
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS https://httpbin.org/get
```

Docker downloads the image automatically if needed and selects the matching CPU architecture. The image starts `curl-impersonate`: put its flags directly after the image name.

- **`0.1.1`** is the versioned tag for this release.
- **`latest`** follows the newest final release. Use a versioned tag or digest for a fixed version.
- Both tags support **`linux/amd64` and `linux/arm64`**.

This is an HTTP client, so it does not open a browser, render pages, or execute JavaScript. Version 0.1.1 supports **one URL per invocation and a documented subset of curl flags**.

## ⌨️ A shorter command: `curli`

In Bash or Zsh, define an alias and pass options and a URL after it:

```sh
alias curli='docker run --rm -i juanfontes/curl-impersonate:0.1.1'

curli -sS https://httpbin.org/get
curli --impersonate firefox147 -sS -I https://httpbin.org/get
```

Add the alias line to `~/.zshrc` for Zsh or `~/.bashrc` for Bash to keep it across terminal sessions. Bash login shells must source `~/.bashrc` from `~/.bash_profile`. Use the full Docker command in scripts. Docker's `-i` forwards stdin; host files passed with CLI options require an explicit volume mount, while shell redirection and pipes work normally.

## 🎭 Choose your browser

```sh
# Chrome 150 is the default: no profile flag needed.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS https://httpbin.org/headers

# Firefox desktop.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --impersonate firefox147 -sS https://httpbin.org/headers

# Safari desktop.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --impersonate safari2601 -sS https://httpbin.org/headers

# Chrome on Android.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --impersonate chrome131_android -sS https://httpbin.org/headers

# Safari on iOS.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --impersonate safari260_ios -sS https://httpbin.org/headers
```

A profile configures TLS ClientHello characteristics, protocol negotiation, HTTP/2 settings and pseudo-header ordering, and default HTTP headers. Its target platform describes the client being impersonated, independently of your host OS.

**Available profiles — 39 presets**

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

Profiles are versioned presets, not an automatically refreshed browser list. Selecting a Tor Browser profile does not route requests through Tor. `okhttp4_android` is a client preset whose bundled default headers include a desktop Safari User-Agent; inspect or override those headers before use.

```sh
docker run --rm juanfontes/curl-impersonate:0.1.1 --list-profiles
```

The command validates the catalog against the installed engine. See the [catalog](https://github.com/JuanFontes/curl-impersonate/blob/v0.1.1/src/profiles.txt) and [native profile settings](https://github.com/JuanFontes/curl-impersonate/blob/v0.1.1/vendor/curl-impersonate/patches/curl.patch).

### Profile selection and environment variables

Priority: **last `--impersonate` / `--no-impersonate` flag → `CURL_IMPERSONATE` → `chrome150`**. The default is fixed per release and shown by `--version`.

```sh
# Supply an environment default to the container.
docker run --rm -e CURL_IMPERSONATE=firefox147 \
  juanfontes/curl-impersonate:0.1.1 -sS https://httpbin.org/get

# Disable browser profiles, including any environment default.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --no-impersonate -sS https://httpbin.org/headers
```

`CURL_IMPERSONATE_HEADERS=no` suppresses browser headers for environment/default selection. Explicit `--impersonate chrome150:no` keeps the profile's TLS/HTTP settings while disabling its browser headers; `chrome150:yes` enables them. An explicit profile without a suffix enables headers.

**Response decompression is automatic whenever a profile is active**, including the default and environment-selected profiles. `--no-compressed` returns the encoded response bytes; `--compressed` remains accepted for existing scripts. The last compression flag wins. With `--no-impersonate`, decoding is opt-in via `--compressed`. Disabling browser headers with `:no` or `CURL_IMPERSONATE_HEADERS=no` does not disable decoding.

```sh
# Decoded response, with no compression flag required.
docker run --rm juanfontes/curl-impersonate:0.1.1 -sS https://httpbin.org/gzip

# Save the encoded bytes on the host instead.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  --no-compressed -sS https://httpbin.org/gzip > response.gz
```

HTTP content encoding is decoded without converting the payload to text. Unencoded bodies pass through unchanged. Headers printed with `-i` or `-D` retain their original values, including `Content-Encoding` and `Content-Length`.

## 🧰 Everyday commands

### Print only the status code

```sh
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -o /dev/null -w '%{http_code}\n' https://httpbin.org/status/200
```

Replace the URL with `https://httpbin.org/status/301` or `https://httpbin.org/status/502` to inspect those responses. HTTP errors return a normal transfer status unless you request `--fail` or `--fail-with-body`.

### Headers only

```sh
# Make a HEAD request.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -I https://httpbin.org/get

# Keep GET semantics, print headers, and discard the body.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -D - -o /dev/null https://httpbin.org/get
```

### Body, or headers and body

```sh
# Body only.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS https://httpbin.org/json

# Include response headers before the body.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -i https://httpbin.org/get
```

### Redirects and HTTP errors

```sh
# Follow redirects and show the final status.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -L -o /dev/null -w '%{http_code}\n' \
  https://httpbin.org/redirect/2

# Return exit code 22 for this HTTP 502 while retaining its response body.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS --fail-with-body https://httpbin.org/status/502
```

### Authentication, headers, and JSON

```sh
# Public httpbin demo credentials.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -u demo:password https://httpbin.org/basic-auth/demo/password

# Add a header and send JSON; --json selects POST.
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -sS -H 'X-Request-Source: terminal' \
  --json '{"hello":"world"}' https://httpbin.org/post
```

### Save files and read stdin

```sh
# Mount the current directory so the response survives --rm.
docker run --rm -v "$PWD:/work" juanfontes/curl-impersonate:0.1.1 \
  -sS -o /work/response.json https://httpbin.org/json

# Keep stdin open with Docker's -i; send the bytes unchanged.
printf '{"hello":"world"}' | docker run --rm -i \
  juanfontes/curl-impersonate:0.1.1 -sS \
  -H 'Content-Type: application/json' --data-binary @- https://httpbin.org/post
```

### Diagnose a request

```sh
docker run --rm juanfontes/curl-impersonate:0.1.1 \
  -v --connect-timeout 10 --max-time 30 https://httpbin.org/get

docker run --rm juanfontes/curl-impersonate:0.1.1 --help
docker run --rm juanfontes/curl-impersonate:0.1.1 --version
```

Verbose output goes to stderr; response bodies go to stdout or `-o`. The runtime image is minimal and has no shell. Use CLI flags directly instead of overriding the entrypoint with `sh`.

## 💻 Prefer a native download?

| Platform | CPU | Native package |
| --- | --- | --- |
| Linux | amd64 | ✅ Available |
| Linux | arm64 | ✅ Available |
| macOS Apple Silicon | arm64 | ✅ Experimental |
| macOS Intel | amd64 | Not available |
| Windows | amd64 / arm64 | Not available |

[Download version 0.1.1 and SHA256SUMS](https://github.com/JuanFontes/curl-impersonate/releases/tag/v0.1.1). Keep the entire extracted folder together. Linux includes its loader and runtime libraries; macOS includes its engine in `lib/`. macOS downloads are signed ad hoc and are not notarized. Windows and Intel Mac users can run the Linux image with a suitable Docker installation.

## 🧭 Scope and validation

The published platforms have native CI coverage for packaged HTTP/TLS/HTTP2 transfers, profile selection, output handling, and certificate overrides. Linux also tests the assembled minimal filesystem. These are functional checks; **successful requests and echoed headers do not prove fingerprint equivalence to a real browser**.

Current limits include one HTTP(S) URL per process, a subset of curl flags, no `.curlrc`/`--config`, `--next`, multipart, retries, parallel transfers, or progress meter. HTTP/3 is exposed by the engine but has not been validated end to end. See the [full compatibility contract](https://github.com/JuanFontes/curl-impersonate#current-compatibility).

**Upgrading from RC1/RC2:** impersonation now defaults to Chrome 150. Add `--no-impersonate` to retain the earlier unprofiled behavior. RC3 already uses this default. Since 0.1.1, active profiles also decode compressed responses automatically; use `--no-compressed` if you need the earlier encoded output. Existing `--compressed` commands remain valid.

## 🛠️ Source, maintenance, and license

[Build and contribute](https://github.com/JuanFontes/curl-impersonate/blob/main/CONTRIBUTING.md) · [Release changes](https://github.com/JuanFontes/curl-impersonate/blob/main/CHANGELOG.md) · [Issues](https://github.com/JuanFontes/curl-impersonate/issues)

Original code is MIT licensed. Incorporated components retain their licenses and notices, included in the image under `/usr/share/licenses/curl-impersonate-rs/`. See [LICENSE](https://github.com/JuanFontes/curl-impersonate/blob/main/LICENSE) and [NOTICE](https://github.com/JuanFontes/curl-impersonate/blob/main/NOTICE). This is an independent project, not an official curl release.
