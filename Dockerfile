# syntax=docker/dockerfile:1
# Pin the published multiarch runtime; override RUNTIME_IMAGE for local builds.
ARG RUNTIME_IMAGE=juanfontes/curl-impersonate:0.0.1-rc.2@sha256:e3ded3964a8e29d6651fa09260948eb5b6cb6c150835edbc5eed0c0041065d18
FROM ${RUNTIME_IMAGE}
WORKDIR /work
ENTRYPOINT ["/usr/local/bin/curl-impersonate"]
CMD ["--help"]
