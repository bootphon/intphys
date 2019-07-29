#!/bin/bash
#
# Build the game as a standalone binary.


# We assume $UE_ROOT is defined.
[ -z "$UE_ROOT" ] && echo "error: UE_ROOT environment variable is not defined" && exit 1

# abspath to the root directory of intphys
INTPHYS_DIR=$(dirname $(dirname $(dirname $(readlink -f $0))))


## Step 1: build the postprocessing binary

cd $INTPHYS_DIR/Tools/postprocessing
mkdir -p build
cd build
cmake .. || exit 1
make -j $(nproc) || exit 1


## Step 2: build the intphys binary

# where we are packaging the project
PACKAGE_DIR=$INTPHYS_DIR/Package
mkdir -p $PACKAGE_DIR

# package the game, from
# https://wiki.unrealengine.com/How_to_package_your_game_with_commands
cd $UE_ROOT/Engine/Build/BatchFiles/
./RunUAT.sh BuildCookRun -project=$INTPHYS_DIR/intphys.uproject \
            -noP4 -platform=Linux -clientconfig=Development -serverconfig=Development \
            -cook -allmaps -build -stage -pak -archive -archivedirectory="$PACKAGE_DIR" || exit 1

exit 0
