#!/usr/bin/env python3

"""High-level wrapper for intphys data generation

This program wraps the intphys binary (as packaged by Unreal Engine)
into a simple to use command-line interface. It defines few
environment variables (namely input JSon scenes file, output directory
and random seed), launch the binary and filter its log messages at
runtime, keeping only relevant messages.

To see command-line arguments, have a::

    ./intphys.py --help

"""

import argparse
import copy
import json
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading

# absolute path to the directory containing this script
INTPHYS_ROOT = os.path.dirname(os.path.abspath(__file__))

# path to the UnrealEngine directory
try:
    UE_ROOT = os.environ['UE_ROOT']
except KeyError:
    print(
        'The UE_ROOT environment variable is undefined. '
        'Please set it as the absolute path to your Unreal Engine directory')

# the default screen resolution (in pixels)
DEFAULT_RESOLUTION = '288x288'


def intphys_binaries():
    """Returns the list of packaged intphys programs as absolute paths"""
    path = os.path.join(
        INTPHYS_ROOT, 'Package/LinuxNoEditor/intphys/Binaries/Linux')

    if os.path.isdir(path):
        return [os.path.join(path, bin) for bin in os.listdir(path)]
    else:
        print('WARNING: intphys package not found')
        return []


class LogStripFormatter(logging.Formatter):
    """Strips trailing \n in log messages"""
    def format(self, record):
        record.msg = record.msg.strip()
        return super(LogStripFormatter, self).format(record)


class LogUnrealFormatter(LogStripFormatter):
    """Removes begining date, module name and trailing '\n'"""
    def format(self, record):
        # remove all content before and including the second ':' (this
        # strip off the date and id from Unreal log messages)
        try:
            record.msg = record.msg[
                [m.start() for m in re.finditer(':', record.msg)][1]+1:]
        except IndexError:
            pass

        return super(LogUnrealFormatter, self).format(record)


class LogNoEmptyMessageFilter(logging.Filter):
    """Inhibits empty log messages (spaces only or \n)"""
    def filter(self, record):
        return len(record.getMessage().strip())


class LogNoStartupMessagesFilter(logging.Filter):
    """Removes luatorch import messages and unreal startup messages"""
    def filter(self, record):
        msg = record.getMessage()
        return not (
            'Using binned.' in msg or
            'per-process limit of core file size to infinity.' in msg or
            'depot+UE4-Releases' in msg)


class LogInhibitUnrealFilter(logging.Filter):
    """Inhibits some unrelevant Unreal log messages

    Messages containing 'Error' or 'LogPython' are kept, other are
    removed from the Unreal Engine log (messages like
    "[data][id]message")

    """
    def filter(self, record):
        msg = record.getMessage()

        # filter out empty messages
        if not msg.strip():
            return False

        # keep only messages with Error, logPython and LogTemp
        return 'LogPython' in msg or 'Error' in msg or (
            'LogTemp' in msg and 'Display: Loaded TP' not in msg)


def GetLogger(verbose=False, name=None):
    """Returns a logger configured to filter Unreal log messages

    If `verbose` is True, do not filter any message, if `verbose` is
    False (default), keep only relevant messages).

    If `name` is not None, prefix all messages with it.

    """
    msg = '{}%(message)s'.format('{}: '.format(name) if name else '')

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addFilter(LogNoEmptyMessageFilter())

    if not verbose:
        log.addFilter(LogInhibitUnrealFilter())
        log.addFilter(LogNoStartupMessagesFilter())
        formatter = LogUnrealFormatter(msg)
    else:
        formatter = LogStripFormatter(msg)

    # log to standard output
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    std_handler.setLevel(logging.DEBUG)
    log.addHandler(std_handler)

    return log


def ParseArgs():
    """Defines a commndline argument parser and returns the parsed arguments"""

    parser = argparse.ArgumentParser(
        description='Data generator for the intphys project')

    parser.add_argument(
        'scenes_file', metavar='<json-file>', help='''
        json configuration file defining the scenes to be rendered,
        for an exemple configuration file see {}'''
        .format(os.path.join(INTPHYS_ROOT, 'Exemples', 'exemple.json')))

    parser.add_argument(
        '-o', '--output-dir', metavar='<output-dir>', default=None, help='''
        directory where to write generated data, must be non-existing
        or used along with the --force option. If <output-dir> is not
        specified, the program run in "dry mode" and do not save any data.''')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='display all the UnrealEngine log messages')

    parser.add_argument(
        '-r', '--resolution', default=DEFAULT_RESOLUTION,
        metavar='<width>x<height>',
        help=('resolution of the rendered images (in pixels), '
              'default is %(default)s'))

    parser.add_argument(
        '-s', '--seed', default=None, metavar='<int>', type=int,
        help='optional random seed for data generator, '
        'by default use the current system time')

    parser.add_argument(
        '-p', '--pause-duration', default=50, metavar='<int>', type=int,
        help=('duration of the pause at the beginning of each run '
              '(in number of ticks), default is %(default)s'))

    parser.add_argument(
        '-f', '--force', action='store_true',
        help='overwrite <output-dir>, any existing content is erased')

    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='''optionnal flag which doesn't kill immediately the program after
        a crash to let time to the debug to print''')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-e', '--editor', action='store_true',
        help='launch the intphys project in the UnrealEngine editor')

    group.add_argument(
        '-g', '--standalone-game', action='store_true',
        help='launch the project as a standalone game (relies on UE4Editor)')

    group.add_argument(
        '--headless', action='store_true',
        help='disable screen rendering (only for packaged game)')

    args = parser.parse_args()
    if not re.match('[0-9]+x[0-9]+', args.resolution):
        raise ValueError(
            'resolution is not in <width>x<height> format'
            '(e.g. "800x600"): {}'.format(args.resolution))

    return args


def _Run(command, log, scenes_file, output_dir, cwd=None, seed=None,
         pause_duration=50, resolution=DEFAULT_RESOLUTION, headless=False,
         debug=False):
    """Run `command` as a subprocess

    The `command` stdout and stderr are forwarded to `log`. The
    `command` runs with the following environment variables, in top of
    the current environment:

    INTPHYS_SCENES is the absolute path to `SCENES_file`.

    INTPHYS_DATA is the absolute path to `output_dir` with a
       trailing slash added.

    INTPHYS_SEED is `seed`

    INTPHYS_RESOLUTION is `resolution`

    """
    # setup the environment variables used in python scripts
    environ = copy.deepcopy(os.environ)
    environ['INTPHYS_ROOT'] = INTPHYS_ROOT
    environ['INTPHYS_SCENES'] = os.path.abspath(scenes_file)
    environ['INTPHYS_RESOLUTION'] = resolution
    environ['INTPHYS_PAUSEDURATION'] = str(pause_duration)

    if headless is True:
        del environ['DISPLAY']

    if output_dir:
        # get the output directory as absolute path
        output_dir = os.path.abspath(output_dir)
        environ['INTPHYS_OUTPUTDIR'] = output_dir
        log.info('write data to ' + output_dir)
    else:
        log.info('running in dry mode, dont save anything')

    if seed is not None:
        environ['INTPHYS_SEED'] = str(seed)

    # run the command as a subprocess
    job = subprocess.Popen(
        shlex.split(command),
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=environ)

    # join the command output to log (from
    # https://stackoverflow.com/questions/35488927)
    def ConsumeLines(pipe, consume):
        with pipe:
            # NOTE: workaround read-ahead bug
            for line in iter(pipe.readline, b''):
                line = line.decode('utf8')
                consume(line)
                # exit the UE subprocess on the first encountered error
                if 'Error:' in line and debug is False:
                    job.kill()
            consume('\n')

    threading.Thread(
        target=ConsumeLines,
        args=[job.stdout, lambda line: log.info(line)]).start()

    # wait the job is finished, forwarding any error
    job.wait()
    if job.returncode:
        log.error('command "%s" returned with %s', command, job.returncode)
        sys.exit(job.returncode)


def RunBinary(output_dir, scenes_file, seed=None,
              resolution=DEFAULT_RESOLUTION, headless=False,
              pause_duration=50, verbose=False, debug=False):
    """Run the intphys packaged binary as a subprocess"""
    # overload binary if defined in the environment
    if 'INTPHYS_BINARY' in os.environ:
        intphys_binary = os.environ['INTPHYS_BINARY']
    else:
        intphys_binary = intphys_binaries()[0]

    if not os.path.isfile(intphys_binary):
        raise IOError('No such file: {}'.format(intphys_binary))

    if not os.path.isfile(scenes_file):
        raise IOError('Json file not found: {}'.format(scenes_file))

    print('running {}'.format(intphys_binary))

    # on packaged game, UnrealEnginePython expect the script to be in
    # ../../../intphys/Content/Scripts. Here we go to a directory
    # where that relative path works.
    cwd = os.path.join(INTPHYS_ROOT, 'Package/LinuxNoEditor')

    res = resolution.split('x')
    _Run(intphys_binary + ' -windowed ResX={} ResY={}'.format(res[0], res[1]),
         GetLogger(verbose=verbose),
         scenes_file, output_dir, seed=seed,
         pause_duration=pause_duration,
         resolution=resolution, cwd=cwd, headless=headless, debug=debug)


def RunEditor(output_dir, scenes_file, seed=None,
              resolution=DEFAULT_RESOLUTION, verbose=False,
              pause_duration=50, standalone_game=False):
    """Run the intphys project within the UnrealEngine editor"""
    log = GetLogger(verbose=verbose)

    editor_dir = os.path.join(UE_ROOT, 'Engine', 'Binaries', 'Linux')
    if not os.path.isdir(editor_dir):
        raise IOError('No such directory {}'.format(editor_dir))

    project = os.path.join(INTPHYS_ROOT, 'intphys.uproject')
    if not os.path.isfile(project):
        raise IOError('No such file {}'.format(project))

    log.debug('running intphys in the Unreal Engine editor')

    command = './UE4Editor ' + project
    if standalone_game:
        res = resolution.split('x')
        command += ' -game -windowed ResX={} ResY={}'.format(res[0], res[1])

    _Run(command, log, scenes_file, output_dir, seed=seed,
         pause_duration=pause_duration, resolution=resolution, cwd=editor_dir)


def FindDuplicates(directory):
    """Find any duplicated scenes in `directory`

    Having two identical scenes is very unlikely but... who knows.
    Load and compare all 'params.json' files found in
    `directory`. Print duplicate on stdout.

    """
    # load all 'params.json' files in a dict: file -> content
    params = []
    for root, dirs, files in os.walk("./data"):
        for file in files:
            if file.endswith("params.json"):
                params.append(os.path.join(root, file))
    params = {p: json.load(open(p, 'r')) for p in params}

    # ensure each file have a different content (can't use
    # collections.Counter because dicts are unhashable)
    duplicate = []
    for i, (n1, p1) in enumerate(params.items()):
        for n2, p2 in params.items()[i+1:]:
            if p1 == p2:
                duplicate.append((n1, n2))

    if len(duplicate):
        print('WARNING: Found {} duplicated scenes.'.format(len(duplicate)))
        print('The following scenes are the same:')
        for (n1, n2) in sorted(duplicate):
            print('{}  ==  {}'.format(
                os.path.dirname(n1), os.path.dirname(n2)))


def Main():
    # parse command-line arguments
    args = ParseArgs()

    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
        if os.path.exists(output_dir):
            if args.force:
                print('Are you sure you want to ' +
                      'delete {} directory ? y/n'.format(output_dir))
                if input() != 'y':
                    raise IOError(
                        'Existing output directory {}\n'
                        .format(output_dir))
                shutil.rmtree(output_dir)
            else:
                raise IOError(
                    'Existing output directory {}\n'
                    'Use the --force option to overwrite it'
                    .format(output_dir))
        os.makedirs(output_dir)
    else:
        # saving disabled, run in dry mode
        output_dir = None

    # check the scenes_file is a correct JSON file
    try:
        json.load(open(args.scenes_file, 'r'))
    except ValueError:
        raise IOError(
              'The scene configuration is not a valid JSON file: {}'
              .format(args.scenes_file))

    # run the simulation either in the editor or as a standalone
    # program
    if args.editor:
        RunEditor(
            output_dir, args.scenes_file,
            seed=args.seed, resolution=args.resolution,
            pause_duration=args.pause_duration, verbose=args.verbose)
    elif args.standalone_game:
        RunEditor(
            output_dir, args.scenes_file,
            seed=args.seed, resolution=args.resolution,
            pause_duration=args.pause_duration, verbose=args.verbose,
            standalone_game=True)
    else:
        RunBinary(
            output_dir, args.scenes_file, seed=args.seed,
            resolution=args.resolution, headless=args.headless,
            pause_duration=args.pause_duration, verbose=args.verbose,
            debug=args.debug)

    if output_dir:
        # check for duplicated scenes and warn if founded
        FindDuplicates(output_dir)


if __name__ == '__main__':
    try:
        Main()
    except IOError as err:
        print('Fatal error, exiting: {}'.format(err))
        sys.exit(-1)
    except KeyboardInterrupt:
        print('Keyboard interruption, exiting')
        sys.exit(-1)
