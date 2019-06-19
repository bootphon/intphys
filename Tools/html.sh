#!/bin/bash

# This script uses the ./images2video.sh script to generate gifs in the scene
# directories and generate a html site with the four video of a test on each
# page.
# The source directory must be a directory containing the output of ./intphys
# and it must be a test.
# utilities.sh contains the fonctions used by this script.

# display a usage message if bad params
[ $# -lt 2 ] \
    && echo \
    && echo "Usage: $0 <source directory> <destination directory>" \
    && echo \
    && echo "Generate gifs in the scene directories and generate a html
     site with the four video of a test on each page. The genreted html
     files are in the destination directory. The source directory must be
     a directory containing the output of ./intphys and it must be a test." \
    && echo \
    && exit 0

DIR=$(cd "$(dirname "$0")" && pwd)
. "$DIR"/utilities.sh

# generate the gifs of the scenes
./images2video.sh $1 gif -s

source_rep="$1"
dest_rep=$(cd $2 && pwd)

# check if the destination repository exists, and create it if not
if [ ! -d "$dest_rep" ]
then
  echo "Creation of the destination repository"
  mkdir "$DIR/$2"
  dest_rep=$(cd $2 && pwd)
fi

# number of gifs
nl=$(wc -l png_dirs.txt | cut -d ' ' -f 1)
# number of tests
NP=$(($nl/4))
# generate the pages
generate_pages png_dirs.txt $dest_rep
# generate the index
generate_index $NP $dest_rep
rm temp.txt
rm png_dirs.txt

echo
echo
echo "index.html generated. You can now run"
echo
echo "  firefox $dest_rep/index.html"
echo
echo "to see the result."
