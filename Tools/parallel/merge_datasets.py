#!/usr/bin/env python3

import argparse
import os
import random
import shutil
import string


class Dataset:
    def __init__(self, directory):
        if not os.path.isdir(directory):
            raise ValueError(f'{directory} is not an existing dircetory')

        self.root_directory = os.path.abspath(directory)

    def _blocks(self):
        """Yields block directories relative to root_directory

        Blocks are root/train, root/test/O1, root/test/O2, etc...

        """
        # visit train
        train_dir = os.path.join(self.root_directory, 'train')
        if os.path.isdir(train_dir):
            yield('train')

        # visit dev and test
        for name in ('test', 'dev'):
            test_dir = os.path.join(self.root_directory, name)
            if os.path.isdir(test_dir):
                # level root/test/O1
                for sub_dir in os.listdir(test_dir):
                    yield os.path.join(name, sub_dir)

    def _scenes(self):
        """Yields scene directories relative to root_directory

        Scenes are root/train/001, root/test/O1/001, root/test/O1/002, etc...

        """
        for block in self._blocks():
            directory = os.path.join(self.root_directory, block)
            for scene in os.listdir(directory):
                yield os.path.join(block, scene)

    def _count(self, directory):
        """Returns the number of elements in `root_directory/directory`"""
        return len(os.listdir(os.path.join(self.root_directory, directory)))

    def nscenes(self):
        """Returns the number of scenes contained in the dataset"""
        return len(list(self._scenes()))

    def merge_into(self, directory, copy=False):
        for scene in self._scenes():
            src = os.path.join(self.root_directory, scene)

            # use a unique directory name
            suffix = '_' + ''.join(random.choices(string.digits, k=10))
            dest = os.path.join(directory, scene) + suffix
            while os.path.exists(dest):
                suffix = '_' + ''.join(random.choices(string.digits, k=10))
                dest = os.path.join(directory, scene) + suffix

            if copy is True:
                shutil.copytree(src, dest)
            else:
                shutil.move(src, dest)

    def normalize(self):
        """Rename all the scenes directory with increasing zfilled numbers"""
        for block in self._blocks():
            nscenes = self._count(block)
            zlen = int(len(str(nscenes)))
            directory = os.path.join(self.root_directory, block)
            for n, scene in enumerate(os.listdir(directory)):
                src = os.path.join(directory, scene)
                dest = os.path.join(directory, str(n+1).zfill(zlen))
                shutil.move(src, dest)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Creates a new intphys dataset from several existing ones')

    parser.add_argument(
        'output_dataset', metavar='<output-dataset>',
        help='output directory with the merged dataset (may exist but must '
        'not contain an existing dataset)')

    parser.add_argument(
        'input_datasets', nargs='+', metavar='<input-dataset>',
        help='directory with a dataset to move into <output-dataset>')

    parser.add_argument(
        '-c', '--copy', action='store_true',
        help='copy the input datasets to the output (default is to move them)')

    return parser.parse_args()


def main():
    args = parse_args()

    output = os.path.abspath(args.output_dataset)
    print('merging {} datasets into {} ...'.format(
        len(args.input_datasets), output))

    if os.path.exists(output):
        if not os.path.isdir(output):
            raise ValueError(f'{output} exists but is not a directory')
        if Dataset(output).nscenes() != 0:
            raise ValueError(f'{output} is not an empty dataset')
    else:
        os.makedirs(output)

    datasets = [Dataset(d) for d in args.input_datasets]
    for dataset in datasets:
        dataset.merge_into(output, copy=args.copy)
        if not args.copy:
            shutil.rmtree(dataset.root_directory)

    Dataset(output).normalize()


if __name__ == '__main__':
    main()
