#!/bin/bash
#
# Compile and link the C++ code in the Source folder of the intphys
# project. This also compile the UnrealEnginePython plugin. After the
# build is complete the game can be launched within the editor or in
# standalone mode.
#
# We assume $UE_ROOT is defined.

# abspath to the root directory of intphys
INTPHYS_DIR=$(dirname $(dirname $(readlink -f $0)))
PROJ_NAME=intphys

${UE_ROOT}/Engine/Build/BatchFiles/Linux/RunMono.sh \
          ${UE_ROOT}/Engine/Binaries/DotNET/UnrealBuildTool.exe \
          $PROJ_NAME -Module=$PROJ_NAME Linux Development \
          -editorrecompile -canskiplink "${INTPHYS_DIR}/${PROJ_NAME}.uproject" -progress || exit 1

exit 0
