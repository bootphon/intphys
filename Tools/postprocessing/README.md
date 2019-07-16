# Postprocessing for intphys datasets generation

## Installation

First install the dependencies. On Debian/Ubuntu:

    sudo apt install \
        libboost-filesystem-dev \
        libboost-program-options-dev \
        nlohmann-json-dev \
        libpng++-dev \
        cmake

Then compile the program:

    cmake .
    make

Finally call it:

    ./postprocessing <directory> -j <njobs>
