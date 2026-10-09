# syntax=docker/dockerfile:1
# Pin the published multiarch runtime; override RUNTIME_IMAGE for local builds.
ARG RUNTIME_IMAGE=juanfontes/curl-impersonate:0.0.1-rc.3@sha256:fec8b06621fad3ae9a31310c1fbd7aa9c129f8ee2ec5e05f499c8000c3d8fddb
FROM ${RUNTIME_IMAGE}
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/curl-impersonate"]
CMD ["--help"]
