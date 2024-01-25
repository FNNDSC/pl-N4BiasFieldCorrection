FROM docker.io/python:3.12.1-slim-bookworm

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="N4 Bias Field Correction" \
      org.opencontainers.image.description="A ChRIS plugin wrapper for N4BiasFieldCorrection"

# install N4BiasFieldCorrection
COPY --from=docker.io/fnndsc/n4biasfieldcorrection:2.5.0 /usr/local/bin/N4BiasFieldCorrection /usr/local/bin/N4BiasFieldCorrection

ARG SRCDIR=/usr/local/src/pl-N4BiasFieldCorrection
WORKDIR ${SRCDIR}

COPY requirements.txt .
RUN --mount=type=cache,sharing=private,target=/root/.cache/pip pip install -r requirements.txt

COPY . .
ARG extras_require=none
RUN pip install ".[${extras_require}]" \
    && cd / && rm -rf ${SRCDIR}
WORKDIR /

CMD ["n4wrapper"]
