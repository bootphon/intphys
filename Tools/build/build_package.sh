#!/bin/bash
#
# Build the game as a standalone binary.
#
# We assume $UE_ROOT is defined.

# abspath to the root directory of intphys
INTPHYS_DIR=$(dirname $(dirname $(dirname $(readlink -f $0))))

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
