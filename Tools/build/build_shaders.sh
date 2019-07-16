#!/bin/bash
#
# Build all the shaders and assets used in the game. From
# https://docs.unrealengine.com/latest/INT/Engine/Basics/DerivedDataCache
#
# We assume $UE_ROOT is defined.

# abspath to the root directory of intphys
INTPHYS_DIR=$(dirname $(dirname $(readlink -f $0)))

# we need to go in a deep directory because UEPython expect to find
# ue_site.py from ../../../../intphys
cd $INTPHYS_DIR/Plugins/UnrealEnginePython/Source

$UE_ROOT/Engine/Binaries/Linux/UE4Editor \
    $INTPHYS_DIR/intphys.uproject \
    -run=DerivedDataCache -fill -DDC=CreatePak || exit 1

exit 0
