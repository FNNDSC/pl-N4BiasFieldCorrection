#!/usr/bin/env python
import os
import shlex
import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
import subprocess as sp
from tqdm.contrib.concurrent import thread_map
from tqdm.contrib.logging import logging_redirect_tqdm

from chris_plugin import chris_plugin, PathMapper
from loguru import logger

__version__ = '2.5.3.0'

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
    min_memory_limit=f'8Gi',
    min_cpu_limit=f'8000m',
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
    if not all(results):
        sys.exit(1)


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


if __name__ == '__main__':
    main()
