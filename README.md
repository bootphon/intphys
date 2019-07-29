# intphys-2.0

#### Data generation for the Intuitive Physics Challenge - http://www.intphys.com

Developed with
[Unreal Engine](https://www.unrealengine.com/what-is-unreal-engine-4)
4.18 and the [UnrealEnginePython](https://github.com/20tab/UnrealEnginePython)
plugin.

The 2.0 version of intphys is a reimplementation of intphys-1.0 based on
UE-4.19 using the Python scripting language (*intphys-1.0* was developed
with UE-4.8 and Lua).

**Important note**

This software is used for generation of the datasets used in the
[Intuitive Physics Challenge](https://intphys.com/challenge.html), it
allows users to generate more train scenes but **the code for test
scenes generation is kept private**.

## Video exemples

#### Train samples

Train samples are always physically possible and have high variability

<img src="Exemples/gif/train_1.gif" width="150"> <img src="Exemples/gif/train_2.gif" width="150"> <img src="Exemples/gif/train_3.gif" width="150"> <img src="Exemples/gif/train_4.gif" width="150">


#### Test samples

Test samples have a constrained variability and come as quadruplets: 2
possibles cases and 2 impossibles ones

<img src="Exemples/gif/test_1.gif" width="150"> <img src="Exemples/gif/test_2.gif" width="150"> <img src="Exemples/gif/test_3.gif" width="150"> <img src="Exemples/gif/test_4.gif" width="150">


#### Metadata

Each video comes with it's associated depth field and object masking
(each object have a unique id), along with a detailed status in JSON
format.

<img src="Exemples/gif/meta_1.gif" width="150"> <img src="Exemples/gif/meta_2.gif" width="150"> <img src="Exemples/gif/meta_3.gif" width="150">


## Installation details

This installation process succeeded on Debian stable (Jessie), Ubuntu
16.04 and Ubuntu 18.04. It may be fine for other Unices as well, but
this have not been tested.

* **Setup an Epic Games account** at
  https://github.com/EpicGames/Signup/, needed to clone the Unreal
  Engine repository from github.

* **Setup the compiler**. You need `clang-3.8` on Ubuntu 16.04 or
  below, or `clang-3.9` on Ubuntu 18.04 (because 3.8 is no more
  available on that distribution). The compilation will fail if using
  a more recent version of `clang`.

  Make sure you have `clang` installed and that `/usr/bin/clang++`
  effectively points to the 3.8 or 3.9 version. To check it, have a
  `/usr/bin/clang++ --version`, it should output something like:

        clang version 3.9.1-19ubuntu1 (tags/RELEASE_391/rc2)
        Target: x86_64-pc-linux-gnu
        Thread model: posix
        InstalledDir: /usr/bin

  If this is not the case, install it and update `clang` to
  point to the right version (here 3.9 as example, adapt it for 3.8):

        sudo apt install clang-3.9
        sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-3.9 100
        sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-3.9 100

* **Install Unreal Engine** as documented
  [here](https://github.com/EpicGames/UnrealEngine/blob/release/Engine/Build/BatchFiles/Linux/README.md).

  * First clone the Engine sources, version 4.19:

        git clone https://github.com/EpicGames/UnrealEngine -b 4.19
        cd UnrealEngine

  * If compiling with `clang-3.9` you may need to modify a file in the
    engine sources (the next step may fail, see
    [here](https://github.com/20tab/UnrealEnginePython/pull/417#issuecomment-393077579)
    for details). Edit the file
    *Engine/Source/ThirdParty/FBX/2018.1.1/include/fbxsdk/core/fbxproperty.h* and replace the line 1188 as:

          return StaticInit(pObject, pName, FbxGetDataTypeFromEnum(eFbxEnum), pValue, pForceSet, pFlags);
          // return StaticInit(pObject, pName, FbxGetDataTypeFromEnum(FbxTypeOf(*((FbxReference*)0))), pValue, pForceSet, pFlags);

  * Then compile the engine:

        ./Setup.sh
        ./GenerateProjectFiles.sh
        make

* **Install dependencies** required for intphys dataset generation and
  postprocessing:

        sudo apt-get install \
            cmake \
            libboost-iostreams-dev \
            libboost-filesystem-dev \
            libboost-program-options-dev \
            libpng++-dev \
            rapidjson-dev


* **Install intphys** in a separate directory. Clone the repository and
  its UnrealEnginePython submodule from github:

        git clone git@github.com:bootphon/intphys.git
        cd intphys
        git submodule update --init Plugins/UnrealEnginePython

* You need **Python>=3.6** installed as `/usr/bin/python3.6` (else you
  need to tweak the UnrealEnginePython plugin
  [here](https://github.com/20tab/UnrealEnginePython/blob/master/Source/UnrealEnginePython/UnrealEnginePython.Build.cs#L11)
  so that it can find python>=3.6 in a non-standard path, for exemple
  in a virtual environment). You also need the dataclasses module (in
  the standard library with python>=3.7). To install it on ubuntu
  16.04, have a:

        sudo add-apt-repository ppa:jonathonf/python-3.6
        sudo apt-get update
        sudo apt-get install python3.6 python3.6-dev
        /usr/bin/python3.6 -m pip install dataclasses

* **Setup your `~/.bashrc`**: The intphys code reads the path to
  UnrealEngine and the path to the Python scripts from the `UE_ROOT`
  and `PYTHONPATH` environment variables repectively. Add that to your
  `~/.bashrc`:

        export UE_ROOT=/absolute/path/to/UnrealEngine
		export PYTHONPATH=$PYTHONPATH:/absolute/path/to/intphys/Content/Scripts

* **Build `intphys` package**: We now need to package the intphys
  project into a standalone binary program. Just have a:

        ./Tools/build/build_package.sh


## Usage

### Scenes generation

* Use the `intphys.py` program to run the game and generate data. To
  discover the arguments, have a:

        ./intphys.py --help

* The basic usage is calling `intphys.py scenes.json -o
  ./output_data`. This reads the scenes to be generated from the
  `scenes.json` file and write them in the folder `./output_data`.

* Generate scenes using the packaged game:

        ./intphys.py Examples/train.json

* When developing you may want to run the project within UE4Editor
  (`--editor` option) or as a standalone game (`--standalone-game`
  option). The `--verbose` option is usefull for dev as well.

* You can also use `Tools/parallel/intphys_parallel.sh` to call several
  instances of `intphys.py` in parallel and speedup the dataset generation.

### Postprocessing

The generated scenes require a postprocessing step (reduce the size of PNG
images, scramble the masks and normalize the depth). This is done by the C++
program in `./Tools/postprocessing`, see README there for more information.


## Additional utils

In the `Tools` directory are stored few utility scripts, see README there for
more information.


## Tweaks

Here are some tweaks and error reports usefull for intphys
development.


### UE4 crash: cannot open OpenGL context

Occured after an update of the nvidia graphic drivers. Just reboot and
try again. `sudo glxinfo` helps.


### Precompiled headers

After a system update you may issue an error when running
`./Tools/build/build_package.sh` about `.gch` precompiled headers. The issue is
like:

    fatal error: file '/usr/include/linux/version.h' has been modified since the precompiled header '.../UE4Editor/Development/Engine/SharedPCH.Engine.h.gch' was built
    note: please rebuild precompiled header '.../UE4Editor/Development/Engine/SharedPCH.Engine.h.gch'

In that case remove all the `.gch` files and recompile the engine:

    cd $UE_ROOT
    find Engine/Intermediate -type f -name "*.gch" -delete
    ./GenerateProjectFiles.sh && make
