#!/usr/bin/env python3
"""This script prepares data to be released on www.intphys.com.

The input data directory must contain {dev, test and train}
subdirectories with data generated by intphys. It creates the
following tar.gz archives:
  - dev.tar.gz contains all the dev/ folder,
  - test.{block}.tar.gz contain the test/{block} folder, metadata excluded,
  - test_metadata.{block}.tar.gz contains metadata of the test/{block} folder,
  - train.{1, ..., n}.tar.gz contain the train/ folder split in n
    archives of approx. equal size

Installation note
-----------------

If the program fails complaining the "progressbar" module is not found, you
need to install it: "conda install progressbar2" or "pip install progressbar2"

"""

import argparse
import logging
import numpy
import os
import pathlib
import progressbar
import random
import tarfile
import tempfile


logging.basicConfig(level=logging.DEBUG, format='%(message)s')
log = logging.getLogger()


def permute_subblocks(data_dir, output_dir):
    """Permute possible and impossible runs in a test scenario

    A test block is made of subdirectories 1, 2, 3 and 4, where 1 and
    2 are possible cases and 3 and 4 impossible cases. This method
    create symlinks from `data_dir` to `output_dir`, simply shuffling
    1, 2, 3, 4 subdirectories in a random way.

    """
    assert os.path.isdir(output_dir)

    for block_dir in os.listdir(data_dir):
        # a block_dir contains 1, 2, 3, 4 subdirectories
        assert sorted(os.listdir(os.path.join(data_dir, block_dir))) \
            == ['1', '2', '3', '4']

        # compute a random permutation
        order = [1, 2, 3, 4]
        random.shuffle(order)

        # prepare the destination directory
        os.makedirs(os.path.join(output_dir, block_dir))

        # move from original to permuted
        for i in range(4):
            src = os.path.join(data_dir, block_dir, str(i+1))
            dst = os.path.join(output_dir, block_dir, str(order[i]))
            os.symlink(src, dst)

    return output_dir


def create_archive(archive, files, arcfiles):
    """Create a tar.gz archive from a given list of files

    This operation can be long and display a progress bar.

    Parameters
    ----------
    archive : filename
        The name of the created tar gz archive, should end with
        the '.tar.gz' extension
    files : list
        The list of files (as absolute paths) to put in the archive
    arcfiles : list
        The list of files as named in the archive, we must have
        len(files) == len(arcfiles)

    """
    log.info('creating %s', archive)
    pbar = progressbar.ProgressBar(maxval=len(files)).start()
    tar = tarfile.open(archive, 'w:gz', dereference=True)
    for n, f in enumerate(files):
        tar.add(f, arcname=arcfiles[n])
        pbar.update(n+1)
    tar.close()
    pbar.finish()


def prepare_dev(data_dir, output_dir):
    """Create `output_dir`/dev.tar.gz from `data_dir`/dev"""
    data_dir = os.path.join(data_dir, 'dev')
    assert os.path.isdir(data_dir)

    # write the tar.gz from the tmp_dir
    create_archive(
        os.path.join(output_dir, 'dev.tar.gz'),
        [os.path.join(data_dir, c) for c in os.listdir(data_dir)],
        [os.path.join('dev', c) for c in os.listdir(data_dir)])


def prepare_train(data_dir, output_dir, N=4):
    """Create `output_dir`/train.n.tar.gz from `data_dir`/train"""
    data_dir = os.path.join(data_dir, 'train')
    assert os.path.isdir(data_dir)

    # write the tar.gz from the data_dir. Split in 4 subarchives of
    # equal lenght.
    N = max(1, N)
    dirs = os.listdir(data_dir)
    chunks = [list(a) for a in numpy.array_split(dirs, N)]

    for n in range(N):
        create_archive(
            os.path.join(output_dir, 'train.' + str(n+1) + '.tar.gz'),
            [os.path.join(data_dir, c) for c in chunks[n]],
            [os.path.join('train', c) for c in chunks[n]])


def prepare_test(data_dir, output_dir, block):
    """Create `output_dir`/test.`block`.tar.gz from `data_dir`/test/`block`"""
    data_dir = os.path.join(data_dir, 'test', block)
    assert os.path.isdir(data_dir)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # replace [1, 2, 3, 4] (where 1, 2 are possible and 3, 4 are
        # impossible) by a random permutation
        log.info('shuffling possible/impossible subblocks')
        permute_subblocks(data_dir, tmp_dir)

        log.info('retrieving metadata')

        meta_files = [
            str(p) for p in pathlib.Path(tmp_dir).glob('**/*/*.json')]
        meta_arcfiles = [
            p.replace(tmp_dir, os.path.join('test', block))
            for p in meta_files]

        create_archive(
            os.path.join(output_dir, 'test_metadata.{}.tar.gz'.format(block)),
            meta_files, meta_arcfiles)

        log.info('retrieving data')

        def _create_test_archive(directories, archive):
            data_files = [
                str(p) for d in sorted(directories)
                for p in pathlib.Path(d).glob('**/*/*/*.png')]
            data_arcfiles = [
                p.replace(tmp_dir, os.path.join('test', block))
                for p in data_files]

            create_archive(
                os.path.join(output_dir, archive),
                data_files, data_arcfiles)

        dirs = [os.path.join(tmp_dir, d) for d in os.listdir(tmp_dir)]
        _create_test_archive(dirs, 'test.{}.tar.gz'.format(block))


def parse_args():
    """Define and parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'data_dir', help='the input data directory')
    parser.add_argument(
        '-o', '--output-dir',
        help=('the output directory where to write the tar.gz files, '
              'use data_dir by default'))
    args = parser.parse_args()
    return args.data_dir, args.output_dir if args.output_dir else args.data_dir


def main():
    data_dir, output_dir = parse_args()

    if not os.path.isdir(data_dir):
        raise IOError('"{}" is not a directory'.format(data_dir))
    data_dir = os.path.abspath(data_dir)

    if not os.path.isdir(output_dir):
        raise IOError('"{}" is not a directory'.format(output_dir))
    output_dir = os.path.abspath(output_dir)

    # prepare_dev(data_dir, output_dir)
    # prepare_train(data_dir, output_dir, N=4)
    # prepare_test(data_dir, output_dir, block='O1')
    # prepare_test(data_dir, output_dir, block='O2')
    prepare_test(data_dir, output_dir, block='O3')


if __name__ == '__main__':
    main()
