# syntax=docker/dockerfile:1
# Pin the published multiarch runtime; override RUNTIME_IMAGE for local builds.
ARG RUNTIME_IMAGE=juanfontes/curl-impersonate:0.1.1@sha256:181c7b7794899b1c6f37bb220453b5d6ed749b561cc5cecfff590f416e4b1005
FROM ${RUNTIME_IMAGE}
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/curl-impersonate"]
CMD ["--help"]
