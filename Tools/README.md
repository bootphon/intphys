# Various tools for intphys dataset generation

This folder contains various scripts to work with the `intphys` program and
datasets generation. Here is a brief description of its content:

* `build` folder contains script to build the `intphys` program. The most
  usefull is `build/build_package.sh`, it compiles the project using the Unreal
  toolchain as a standalone binary.

* `html/html.sh` generates an HTML page with gifs from a dataset directory

* `parallel/intphys_parallel.sh` runs multiple instances of `intphys.py` in
  parallel and is usefull to speedup dataset generation on a multicore machine.

* `images2video.sh` generates a gif or a avi file from png images.

* `make_archives.py` builds the `.tar.gz` archives as published on
  www.intphys.com/download.

* `dataset_pipeline.sh` is a complete pipeline to generate and archive an
  intphys dataset.
