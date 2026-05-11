FROM docker.io/library/python:3.14.4-slim-trixie

# install N4BiasFieldCorrection
COPY --from=docker.io/fnndsc/n4biasfieldcorrection:2.6.5 /usr/local/bin/N4BiasFieldCorrection /usr/local/bin/N4BiasFieldCorrection

ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=./requirements.txt,dst=/mnt/requirements.txt \
    pip install -r /mnt/requirements.txt

ARG extras_require=none
RUN --mount=type=bind,source=.,dst=/mnt/src \
    --mount=type=tmpfs,destination=/mnt/src/n4wrapper.egg-info \
    --mount=type=tmpfs,destination=/mnt/src/build \
    pip install "/mnt/src[${extras_require}]"

CMD ["n4wrapper"]
