# Contributing

For the published image and request examples, start with the [README](README.md#use-the-published-docker-image). Run the commands below from the repository root.

## Propose a change

For a substantial feature, dependency update, or browser-profile change, describe the problem, intended behavior, and validation approach before implementing it. Bug reports should include the image tag or digest, CPU architecture, CLI version, a minimal command, and expected versus actual behavior. Remove credentials, cookies, and private request data from reports and logs.

Keep code, comments, documentation, and commit messages in English. Keep each pull request focused, preserve response bytes and the documented CLI behavior, and report unsupported options explicitly. Preserve third-party license notices and the engine's verified input manifest.

## Build and test locally

Use Docker with Linux container support and BuildKit. Docker supplies the compilers and native dependencies. The initial source build needs network access; this project currently packages Linux amd64 and arm64 runtimes.

The root `Dockerfile` derives an image from a **ready-to-run runtime**, selected with `RUNTIME_IMAGE`. It does not compile code or download source archives. `docker/Dockerfile.build` owns compilation, tests, complete runtime export, and the optional Debian diagnostic image.

Build source changes with the maintainer Dockerfile. These commands target Linux arm64; use `linux/amd64` in both commands for amd64:

```sh
docker build -f docker/Dockerfile.build --platform linux/arm64 \
  --target runtime -t curl-impersonate-rs:runtime .

docker build --platform linux/arm64 \
  --build-arg RUNTIME_IMAGE=curl-impersonate-rs:runtime \
  -t curl-impersonate-rs:local .
docker run --rm curl-impersonate-rs:local --version
```

The runtime is already executable. The second build derives the distribution image; its explicit override makes it use local changes instead of the published release. Use the same Docker daemon builder for both local builds. The initial source build downloads dependencies and compiler images; subsequent builds reuse cached native compilation when available.

```sh
# Compile and run parser, HTTP/TLS/HTTP2, and minimal filesystem tests.
docker build -f docker/Dockerfile.build --platform linux/arm64 \
  --target test-minimal -t curl-impersonate-rs:test-local .

# Optional Debian runtime with a shell for diagnostics.
docker build -f docker/Dockerfile.build --platform linux/arm64 \
  --target runtime-debian -t curl-impersonate-rs:debug .
```

`NATIVE_JOBS` defaults to 4; smaller builders can use `--build-arg NATIVE_JOBS=2`. CLI-only changes reuse native compilation layers when cached. Dockerfile-specific ignore rules include only source-build inputs and exclude generated or local files; distribution builds need no local files. Update `docker/Dockerfile.build.dockerignore` when adding a new build input outside the listed paths. The GitHub Actions workflow is configured to test each architecture, export runtime files into the runner filesystem, and build both runtime and distribution images using the same daemon builder. It also packages Linux downloads, runs the extracted launcher directly on each native runner, and uploads the tested archives as workflow artifacts. It does not publish releases or images automatically.

### Derive your own image from the published runtime

The root `Dockerfile` pins the published release by its **multiarch digest**. Build a derived image with:

```sh
docker build -t curl-impersonate-rs:local .
docker run --rm curl-impersonate-rs:local --version
```

Override `RUNTIME_IMAGE` to select another runtime image. An inaccessible image fails the build without falling back to source compilation. Docker may resolve or download the selected image and Dockerfile frontend.

### Export artifacts

```sh
# Shared engine library, matching headers, licenses, and source provenance.
docker build -f docker/Dockerfile.build --platform linux/arm64 \
  --target engine-artifacts --output type=local,dest=dist/engine-arm64 .

# Complete runtime filesystem, exported under rootfs/.
docker build -f docker/Dockerfile.build --platform linux/arm64 \
  --target runtime-artifacts --output type=local,dest=dist/runtime/arm64 .
```

Use `linux/amd64` and distinct output directories for amd64. Use an empty export directory when replacing artifacts: the exporter does not remove obsolete files. The root Dockerfile consumes a runtime image, not these directories. A local image must be available to the selected Docker daemon builder; an isolated buildx container builder requires a registry image instead.

Engine exports target Linux glibc on Debian bookworm and are not universal Linux binaries. They contain shared libraries, not a merged static library. The Linux CLI bundles below include the glibc loader and runtime libraries. They are not single static executables. macOS/Windows packages remain outside this deliverable.

### Package a Linux download

After exporting a complete runtime, use Python 3.10 or newer to create a bundle. Match `--arch` to the exported architecture and use the release channel version, which can differ from the CLI version in `Cargo.toml`:

```sh
python3 scripts/package-release.py \
  --rootfs dist/runtime/arm64/rootfs --arch arm64 \
  --version 0.0.1-rc.1 --revision "$(git rev-parse HEAD)" --output dist/release
python3 tests/release_package.py
```

The packager checks key ELF architectures, required runtime files and license notices, converts rootfs-absolute links to relative links, and rejects dangling or escaping links. It refuses to overwrite an archive. Archive timestamps and ownership are normalized; this does not make the underlying source build reproducible. `release.json` records the supplied source revision, so build from a clean checkout of that revision.

The launcher invokes the bundled dynamic loader with an explicit library path and preserves arguments, streams, working directory and exit status. It supplies the bundled CA file only when neither `CURL_CA_BUNDLE` nor `SSL_CERT_FILE` is nonempty (a directory-only `SSL_CERT_DIR` override still uses the bundled CA file); CLI `--cacert` still takes precedence. System DNS/NSS configuration remains host-controlled. Ubuntu 24.04 is the native CI validation target; do not infer support for all Linux distributions.

### Publish a release

1. Set `RELEASE_VERSION` in `.github/workflows/ci.yml` and update the download documentation for the intended version. Commit the source and run CI on that exact revision.
2. Require successful amd64 and arm64 jobs. Each job builds the engine, tests the minimal runtime, tests the packager, extracts the archive into a path with spaces, and runs HTTP/TLS/HTTP2 compatibility tests directly on the native runner. A bounded public HTTPS smoke check additionally exercises DNS and the bundled trust store; public-service failures can require a rerun.
3. Download the `linux-amd64` and `linux-arm64` artifacts from that run. Check each archive's `release.json` against the tested revision and release version. Preserve the tested `.tar.gz` bytes.
4. Generate `SHA256SUMS` over both archives, tag the exact tested commit, and upload both archives and the checksum file to a draft release. Download them again and verify the checksums before publishing. Mark release candidates as pre-releases.
5. Include installation instructions, validation scope, known limits and the Docker image tag/digest in the release notes. Do not replace an existing release's assets or Docker tag silently.

Packaging changes alone do not require republishing an unchanged Docker runtime. Native downloads are built by CI from the tagged source; the Docker distribution retains its separately published digest. Release publication does not change repository visibility.

### Engine inputs and updates

`engine.lock` pins the checksum manifest of the local engine snapshot and the separate libidn2 source archive. The vendored CMake superbuild pins the remaining dependency sources. `scripts/prepare-engine.sh` checks the manifest and imported files before use; `scripts/build-engine.sh` compiles them and runs native feature checks. The native API bridge uses matching headers and libraries. Native profile definitions are compiled into the engine; `src/profiles.txt` lists their names and is embedded in the CLI at compile time.

To update the engine, review and import the required source changes, preserve their notices, and update `vendor/curl-impersonate/ORIGIN.md`. Regenerate the existing `SHA256SUMS` file list and its hash in `engine.lock`, then update the profile catalog when needed. Build and test both architectures. Compare network captures with real browsers before claiming a fidelity improvement.

The runtime includes build provenance at `/opt/native/engine-build.txt`, plus `engine-origin.md`, `engine-inputs.sha256`, `runtime-libraries.txt`, and `runtime-packages.txt`. Inspect them in a filesystem export or with `docker cp`; the diagnostic image also supports `--entrypoint cat`.

Source builds download pinned dependency archives and use container registries and Debian package repositories. System package versions and the entire build environment are not locked, so byte-for-byte reproducibility is not guaranteed. Rebuild the runtime to refresh system libraries or certificates. Pin published images by digest when immutable selection is required. Signed releases and a complete SBOM remain future work.

### Validation scope

`test-minimal` runs source integrity checks, parser tests, and local HTTP/TLS/HTTP2 integration tests, then repeats the integration tests inside the assembled runtime filesystem with `chroot`. Test tools stay outside the final image. The suite checks all 39 profile names against the compiled engine. It does not compare browser fingerprints or establish HTTP/3 fidelity. Compatibility assertions use local fixtures; the download workflow also runs one bounded public HTTPS smoke check.

## Validate your change

Run checks for the code you changed and its directly affected dependencies. Documentation-only edits need a diff and link review. Do not rebuild the engine or run unrelated application tests for documentation changes.

For source verification helpers, use the focused checks below. They use temporary files and do not download engine sources:

```sh
python3 tests/vendor_engine.py
python3 tests/source_download.py
sh -n scripts/prepare-engine.sh scripts/build-engine.sh scripts/fetch-verified.sh scripts/package-minimal.sh
```

For CLI, native engine, or runtime-packaging changes, select the relevant integration checks. The `test-minimal` target above validates the assembled runtime; engine and packaging changes also need an actual-container DNS/HTTPS smoke check. Validate both architectures before a release. Distinguish functional compatibility checks from comparisons with real-browser network captures.

## Submit a pull request

Explain the problem, the resulting behavior, affected platforms or profiles, and the checks you ran. Include known limitations or checks you could not run. Keep generated binaries, runtime exports, local configuration, credentials, and session notes out of commits. Check the staged diff before submitting.

The root [LICENSE](LICENSE) covers original project code; [NOTICE](NOTICE) points to incorporated components and their notices. The profile catalog in `src/profiles.txt` is a CLI build input, while the native definitions contain the settings. Keep both and the README table synchronized when profiles change.
