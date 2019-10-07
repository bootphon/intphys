#!/usr/bin/env python

import argparse
import glob
import os
import random
import shutil


def shuffle_test_scenes(data_directory):
    """Shuffle possible/impossible runs in test scenes

    The test scenes are saved in 4 subdirectories 1, 2, 3 and 4, where 1
    and 2 are possible, 3 and 4 are impossible. This method simply shuffle
    in a random way the subdirectories.

    The method is called by the director, at the very end of the program.

    Dataset can be 'test' or 'dev' to shuffle the test dataset or the dev
    dataset respectively.

    """
    dataset = 'test'
    test_dir = os.path.join(data_directory, dataset)
    if not os.path.isdir(test_dir):
        # no test scene, nothing to do
        return

    # retrieve the list od directories to shuffle, those are 'test_dir/*/*'
    scenes = glob.glob('{}/*/*'.format(test_dir))
    print('Shuffling possible/impossible runs for {} {} scenes'
          .format(len(scenes), dataset))

    for scene in scenes:
        subdirs = sorted(os.listdir(scene))

        # make sure we have the expected subdirectories to shuffle
        if not subdirs == ['1', '2', '3', '4']:
            raise ValueError(
                'unexpected subdirectories in {}: {}'
                .format(scene, subdirs))

        # shuffle the subdirs (suffix with _tmp to avoid race conditions)
        shuffled = [s + '_tmp' for s in subdirs]
        random.shuffle(shuffled)

        # move original to shuffled
        for i in range(4):
            shutil.move(
                os.path.join(scene, subdirs[i]),
                os.path.join(scene, shuffled[i]))

        # remove the _tmp suffix
        for subdir in os.listdir(scene):
            shutil.move(
                os.path.join(scene, subdir),
                os.path.join(scene, subdir[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_directory')

    args = parser.parse_args()
    shuffle_test_scenes(args.data_directory)


if __name__ == '__main__':
    main()
