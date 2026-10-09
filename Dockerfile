# syntax=docker/dockerfile:1
# Pin the published multiarch runtime; override RUNTIME_IMAGE for local builds.
ARG RUNTIME_IMAGE=juanfontes/curl-impersonate:0.1.0@sha256:82700537e87e72fb4d6cf9c5d67eea9e08b7a9ec326c9ebb9e9409ed8d539d53
FROM ${RUNTIME_IMAGE}
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/curl-impersonate"]
CMD ["--help"]
