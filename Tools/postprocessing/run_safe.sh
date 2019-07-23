#!/bin/bash

data_path=/mnt/data/databases/intphys

echo "copying dataset..."
sudo rm -rf $data_path/dataset
cp -a $data_path/dataset_ro $data_path/dataset

./build/postprocess $data_path/dataset -j4
