#include <chrono>
#include <iostream>
#include <string>
#include <stdexcept>
#include <boost/program_options.hpp>

#include "intphys_dataset.hh"
#include "intphys_randomizer.hpp"


/**
   Reads the directory to postprocess and njobs from command line options

   From command line, the -h or --help option displays a brief help message.
*/
void parse_options(
   int& argc, char** argv,
   std::string& directory, uint8_t& njobs, unsigned& seed)
{
   namespace po = boost::program_options;

   po::options_description desc("Allowed options");
   desc.add_options()
      ("help,h", "produce help message")

      ("njobs,j", po::value<uint8_t>(&njobs)->default_value(1),
       "number of parallel subprocesses (default to 1)")

      ("seed,s", po::value<unsigned>(&seed)->default_value(
         std::chrono::system_clock::now().time_since_epoch().count()),
       "seed for random number generation (default to a value based on current time)")

      ("directory", po::value<std::string>(&directory)->required(),
       "directory where the dataset is stored, "
       "must contain subdirectories among 'train', 'test' and 'dev'. "
       "Some can be missing (e.g. only 'train' subdirectory).");

   // directory is a required positional argument
   po::positional_options_description positional_options;
   positional_options.add("directory", 1);

   // parse the options
   po::variables_map vm;
   po::store(po::command_line_parser(argc, argv).options(desc)
             .positional(positional_options).run(), vm);

   // display an help message when requested
   if(vm.count("help"))
   {
      std::cout
         << "Usage: " << argv[0]
         << " [-h|--help] [-j|--njobs <int>] [-s|--seed <int>] <directory>" << std::endl
         << "Postprocess an intphys dataset. "
         << "Works on the <directory> in-place. "
         << std::endl << std::endl << desc << std::endl;
      exit(0);
   }

   po::notify(vm);
}


/**
   Entry point of the program.

   Parse command line arguments, load the dataset and postprocess it in place.
*/
int main(int argc, char** argv)
{
   try
   {
      // parse the input directory from command line
      std::string directory;
      uint8_t njobs;
      unsigned seed;
      parse_options(argc, argv, directory, njobs, seed);

      // initialize the dataset (parses the dataset's subdirectories to build a
      // list of train, test and dev scenes)
      intphys::dataset dataset(directory);

      // display a bit of information to the user
      const auto& dim = dataset.scenes_dimension();
      std::cout
         << "found " << dataset.scenes().size() << " scenes for a total of "
         << dataset.nimages() <<" images, dimension of each scene is "
         << dim.x << "x" << dim.y << "x" << dim.z << std::endl;

      // initialize the random engine
      intphys::randomizer random(seed);

      // postprocess all the scenes in the dataset
      dataset.postprocess(njobs, random);
   }
   catch(std::exception& e)
   {
      std::cerr << "error: " << e.what() << std::endl;
      return -1;
   }

   return 0;
}
