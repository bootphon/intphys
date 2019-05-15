#!/bin/bash
#
# Run multiple instances of intphys.py in parallel. Assumes GNU
# parallel is installed and intphys is built in packaged mode (with
# Tools/build_package.sh)


# absolute path to intphys.py
intphys=$(readlink -f $(dirname $(readlink -f $0))/../intphys.py)


# a usage message displayed on bad params or --help
usage()
{
    echo "Usage: $0 <json-file> <output-dir> [<njobs>] [<height>x<width>]"
    echo
    echo "The default <njobs> is $(nproc), the default resolution is 288x288."
    echo "This script does the following:"
    echo "1 - split the json file into n balanced subparts"
    echo "2 - call n instances of intphys.py in parallel on each of the sub-json"
    echo "3 - merge the n resulted dirs into a single output-dir"

    exit 1
}

# display usage if needed
[ $# -le 1 -o $# -gt 4 ] && usage
[[ $1 == "-h" || $1 == "-help" || $1 == "--help" ]] && usage


# parse resolution
resolution=$4
[ -z $resolution ] && resolution="288x288"


# parse njobs
njobs=$3
[ -z $njobs ] && njobs=$(nproc)
njobs=$(( $(nproc) > $njobs ? $njobs : $(nproc) ))  # max(ncores, njobs)


# parse output directory
output_dir=$(readlink -f $2)
[ -d $output_dir ] && echo "Error: $output_dir already exists" && exit 1
mkdir -p $output_dir


# parse json file
json=$(readlink -f $1)
if ! [ -f $json ]; then echo "Error: file $1 not found"; exit 1; fi


# split the json file in 'njobs' subparts
tmpdir=$(mktemp -d)
trap "rm -rf $tmpdir" EXIT
$(dirname $0)/split_json.py $json $njobs $tmpdir || exit 1
njsons=$(( $(ls -l $tmpdir | wc -l) - 1 ))


# a function to run a single intphys instance
export intphys output_dir resolution tmpdir
run_intphys()
{
    $intphys -o $output_dir/parallel/$1 -r $resolution $tmpdir/$1.json
}
export -f run_intphys


# run the instances in parallel
parallel -j $njobs run_intphys ::: $(seq 1 $njsons) || exit 1


# merge the output directories
$(dirname $0)/merge_directories.py $output_dir/parallel  $output_dir || exit 1


exit 0
