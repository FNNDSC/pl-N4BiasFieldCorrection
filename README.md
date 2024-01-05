# `pl-N4BiasFieldCorrection`

[![Version](https://img.shields.io/docker/v/fnndsc/pl-N4BiasFieldCorrection?sort=semver)](https://hub.docker.com/r/fnndsc/pl-N4BiasFieldCorrection)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-N4BiasFieldCorrection)](https://github.com/FNNDSC/pl-N4BiasFieldCorrection/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-N4BiasFieldCorrection/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-N4BiasFieldCorrection/actions/workflows/ci.yml)

`pl-N4BiasFieldCorrection` is a [_ChRIS_](https://chrisproject.org/)
_ds_ plugin wrapper for the [`N4BiasFieldCorrection`](https://github.com/ANTsX/ANTs/wiki/N4BiasFieldCorrection)
program from [ANTs](https://github.com/ANTsX/ANTs).
`pl-N4BiasFieldCorrection` runs `N4BiasFieldCorrection` on every `.nii` and `.nii.gz` file found in a specified input directory.

## Installation

`pl-N4BiasFieldCorrection` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-N4BiasFieldCorrection` as a container:

```shell
apptainer exec docker://fnndsc/pl-N4BiasFieldCorrection n4wrapper input/ output/
```

To print its available options, run:

```shell
apptainer exec docker://fnndsc/pl-N4BiasFieldCorrection n4wrapper --help
```
