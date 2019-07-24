#!/bin/bash
#
# This script illustrates the complete pipeline used to generate, postprocess
# and archive an intphys database.


# a usage message displayed on bad params or --help
usage()
{
    echo "Usage: $0 <json-file> <output-dir>"
    echo
    echo "This script does the following (using $(nproc) jobs):"
    echo "1 - generate a dataset in <output-dir> based on the scenes defined in <json-file>"
    echo "2 - postprocess the dataset"
    echo "3 - generate the .tar.gz archives"
}

# display usage if needed
[ $# -le 1 -o $# -gt 2 ] && usage
[[ $1 == "-h" || $1 == "-help" || $1 == "--help" ]] && usage


# parse output directory
output_dir=$(readlink -f $2)
[ -d $output_dir ] && echo "Error: $output_dir already exists" && exit 1


# parse json file
json=$(readlink -f $1)
[ ! -f $json ] && echo "Error: file $1 not found" && exit 1


# generate the dataset
$(dirname $0)/parallel/intphys_parallel.py $json $output_dir $(nproc) || exit 1

# postprocess it
$(dirname $0)/postprocessing/build/postprocess $output_dir || exit 1

# build the archives
$(dirname $0)/make_archives.py $output_dir || exit 1

exit 0
