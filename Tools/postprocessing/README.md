# Postprocessing for intphys datasets generation

## Installation

First install the dependencies. On Debian/Ubuntu:

    sudo apt install \
        libboost-filesystem-dev \
        libboost-program-options-dev \
        rapidjson-dev \
        libpng++-dev \
        cmake

Then compile the program:

    mkdir -p ./build
    cd ./build
    cmake ..
    make -j4

Finally call it:

    ./build/postprocessing <directory> -j <njobs>
