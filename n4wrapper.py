#!/usr/bin/env python
import os
import shlex
import sys
from pathlib import Path
from collections.abc import Iterator
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
import subprocess as sp
from tqdm.contrib.concurrent import thread_map
from tqdm.contrib.logging import logging_redirect_tqdm

from chris_plugin import chris_plugin, PathMapper
from loguru import logger

__version__ = '2.6.5.0'

DISPLAY_TITLE = r"""
 _   _   ___ ______ _           ______ _      _     _ _____                          _   _             
| \ | | /   || ___ (_)          |  ___(_)    | |   | /  __ \                        | | (_)            
|  \| |/ /| || |_/ /_  __ _ ___ | |_   _  ___| | __| | /  \/ ___  _ __ _ __ ___  ___| |_ _  ___  _ __  
| . ` / /_| || ___ \ |/ _` / __||  _| | |/ _ \ |/ _` | |    / _ \| '__| '__/ _ \/ __| __| |/ _ \| '_ \ 
| |\  \___  || |_/ / | (_| \__ \| |   | |  __/ | (_| | \__/\ (_) | |  | | |  __/ (__| |_| | (_) | | | |
\_| \_/   |_/\____/|_|\__,_|___/\_|   |_|\___|_|\__,_|\____/\___/|_|  |_|  \___|\___|\__|_|\___/|_| |_|
"""

parser = ArgumentParser(description='ChRIS plugin wrapper for N4BiasFieldCorrection',
                        formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument('-s', '--shrink-factor', type=int, default=3,
                    help='Shrink factor')
parser.add_argument('-c', '--convergence', type=str, default='[400x400x400,0.00]',
                    help='')

parser.add_argument('-p', '--pattern', type=str, default='**/*.nii,**/*.nii.gz',
                    help='Input file patterns')
parser.add_argument('-q', '--required-success', type=int, default=None,
                    help='Number of successful jobs required for exit code 0. '
                    'Setting this parameter implies [0, N) jobs may fail. If '
                    'unspecified, all jobs must be successful.')
parser.add_argument('-J', '--threads', type=int,
                    help='Number of threads to use')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


# The main function of this *ChRIS* plugin is denoted by this ``@chris_plugin`` "decorator."
# Some metadata about the plugin is specified here. There is more metadata specified in setup.py.
#
# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='MRI Bias Field Correction (ANTs N4 Algorithm)',
    category='MRI',
    min_memory_limit='8Gi',
    min_cpu_limit='8000m',
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    print(DISPLAY_TITLE, flush=True)
    mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern.split(','))
    nproc = options.threads if options.threads else len(os.sched_getaffinity(0))
    with logging_redirect_tqdm():
        results = thread_map(
            lambda t: n4bfc(t[0], t[1], convergence=options.convergence, shrink_factor=options.shrink_factor),
            mapper, max_workers=nproc, total=mapper.count(), maxinterval=0.1
        )

    successes, failures = _count_bool(results)
    if options.required_success is None:
        sys.exit(0 if failures == 0 else 1)
    else:
        sys.exit(0 if successes >= options.required_success else 1)


def n4bfc(input: Path, output: Path, convergence: str, shrink_factor: str) -> bool:
    cmd = [
        'N4BiasFieldCorrection',
        '--input-image', input, '--output', output,
        '--convergence', convergence, '--shrink-factor', str(shrink_factor)
    ]
    log_file = output.with_name(output.name + '.log')
    str_cmd = shlex.join(map(str, cmd))
    logger.info(f'Running: {str_cmd} > {log_file}')
    with log_file.open('wb') as f:
        proc = sp.run(cmd, stdout=f, stderr=f)

    if proc.returncode != 0:
        logger.error(f'Failed to process {input}, please check log file: {log_file}')
        return False
    return True


def _count_bool(values: Iterator[bool]) -> tuple[int, int]:
    n_true = 0
    n_false = 0
    for value in values:
        if value:
            n_true += 1
        else:
            n_false += 1
    return n_true, n_false


if __name__ == '__main__':
    main()
