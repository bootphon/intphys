#!/usr/bin/env python3

import os
import shutil
import sys


def usage():
    print('Usage: {} <input-dir> <output-dir>'.format(sys.argv[0]))
    sys.exit(1)


def main():
    for h in ('-h', '-help', '--help'):
        if h in sys.argv:
            usage()

    if len(sys.argv) != 3:
        usage()

    output_dir = os.path.abspath(sys.argv[2])
    input_dir = os.path.abspath(sys.argv[1])
    input_subdirs = [os.path.join(input_dir, v) for v in os.listdir(input_dir)]
    print('merging {} directories into {} ...'.format(
        len(input_subdirs), output_dir))

    scenes = sorted(
        os.path.join(d, sd) for d in input_subdirs for sd in os.listdir(d))

    count = 1
    for scene in scenes:
        root = '_'.join(scene.split('/')[-1].split('_')[1:])
        index = str(count).zfill(len(str(len(scenes))))
        count += 1

        dest = os.path.join(output_dir, index + '_' + root)
        print(scene, '->', dest)
        shutil.move(scene, dest)

    shutil.rmtree(sys.argv[1])


if __name__ == '__main__':
    main()
