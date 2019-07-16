#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>

#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>
#include <png++/png.hpp>
#include <json.hpp>

namespace po = boost::program_options;
namespace fs = boost::filesystem;

using json = nlohmann::json;
using gray_image = png::image<png::gray_pixel>;


/**
   Reads the input directory to postprocess from command line options

   From command line, the -h or --help option displays a brief help message.
*/
void parse_options(int argc, char** argv, fs::path& input_directory)
{
  const char* help =
    "input directory where the scene is stored, "
    "must contain 'depth', 'masks' and 'scene' subdirs "
    "and a 'status.json' file";

  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h", "produce help message")
    ("directory", po::value<fs::path>(&input_directory)->required(), help);

  po::positional_options_description positional_options;
  positional_options.add("directory", 1);

  po::variables_map vm;
  po::store(po::command_line_parser(argc, argv).options(desc)
            .positional(positional_options).run(), vm);

  if( vm.count("help") )
    {
      std::cout << "Postprocess scene images. "
                << "To be applied on the intphys 2019 dataset."
                << std::endl << std::endl << desc << std::endl;
      exit(0);
    }

  po::notify(vm);
}


/**
   Ensures the directory contains a status.json file and the 3 subdirectories
   "depth", "masks" and "scenes".

   Raises a runtime error on the first encountered error.
*/
void check_input_directory(fs::path& directory)
{
  // make sure the directory exists
  if(not fs::exists(directory) or not fs::is_directory(directory))
    {
      std::stringstream message;
      message << directory << " is not an existing directory";
      throw std::runtime_error(message.str().c_str());
    }

  // make sure it contains status.json
  if(not fs::is_regular_file(directory / "status.json"))
    {
      std::stringstream message;
      message << "status.json not found in " << directory;
      throw std::runtime_error(message.str().c_str());
    }

    // make sure it contains depth, masks and scene subdirectories
    for(const std::string& subdir : {"depth", "masks", "scene"})
      {
        if(not fs::is_directory(directory / subdir))
          {
            std::stringstream message;
            message << subdir << "subdirectory not found in " << directory;
            throw std::runtime_error(message.str().c_str());
          }
      }
}


void normalize_depth(const fs::path& input_file, const fs::path& output_file, const float& max_depth)
{
  std::ifstream file(input_file.string(), std::ios::out | std::ofstream::binary);

  // read the size of the image
  std::size_t size = 0;
  file.read(reinterpret_cast<char*>(&size), sizeof(size));

  // read the image
  std::vector<float> raw_depth(size);
  file.read(reinterpret_cast<char*>(raw_depth.data()), sizeof(float) * size);

  // allocate the output image. TODO Here we assume the image is a square.
  size = std::sqrt(size);
  gray_image depth(size, size);
  for(std::size_t i = 0; i < size; ++i)
    {
      for(std::size_t j = 0; j < size; ++j)
        {
          std::size_t index = i + j * size;

          // depth normalization, depth field is from white (close) to black
          // (far).
          float d = raw_depth[index];
          if(d == 0.0 or d > max_depth)
            {
              d = max_depth;
            }

          std::uint8_t p = static_cast<std::uint8_t>(
             255.f - 255.f * std::sqrt(d) / std::sqrt(max_depth));
          depth.set_pixel(i, j, p);
        }
    }

  depth.write(output_file.string());
}


/**
   Loads the PNG files in the directory. Makes sure we have exactly 100 PNG
   images in the directory, and nothing else. Images are loaded as grayscale
   images.
*/
std::vector<gray_image> load_pngs(fs::path directory)
{
  // get all the files in the input directory
  std::vector<fs::path> input_files;
  for(auto& file : fs::directory_iterator(directory))
    {
      input_files.push_back(file);
    }

  // sort them by name
  std::sort(input_files.begin(), input_files.end());

  // make sure we have 100 images
  if(input_files.size() != 100)
    {
      std::stringstream message;
      message << "must be 100 images in directory " << directory
              << " but found " << input_files.size();
      throw std::runtime_error(message.str().c_str());
    }

  // make sure they have the expected filename
  for(auto& file : input_files)
    {
      std::string filename(file.filename().string());
      if(std::string(filename, filename.size() - 4) != ".png")
        {
          std::stringstream message;
          message << "png filename must be *.png but is " << filename;
          throw std::runtime_error(message.str().c_str());
        }
    }

  // load the pngs
  std::vector<gray_image> input_images;
  for(auto& file : input_files)
    {
      input_images.push_back(gray_image(file.string()));
    }

  return input_images;
}


void write_pngs(fs::path& output_directory, std::vector<gray_image>& output_pngs)
{
  if(not fs::create_directory(output_directory))
    {
      std::stringstream message;
      message << "cannot create output directory " << output_directory;
      throw std::runtime_error(message.str().c_str());
    }

  std::size_t index_size = std::to_string(output_pngs.size()).size();
  std::vector<fs::path> output_files;
  for(std::size_t i = 0; i < output_pngs.size(); ++i)
    {
      // from int(2) to string("002")
      std::string index = std::to_string(i+1);
      if(index.size() < index_size)
        {
          index = std::string(index_size - index.size(), '0') + index;
        }

      fs::path filename = output_directory / fs::path("masks_" + index + ".png");
      output_pngs[i].write(filename.string());
    }
}


void scramble(std::vector<gray_image>& input_images, std::vector<gray_image>& output_images)
{
  for(std::size_t i = 0; i < input_images.size(); ++i)
    {
      output_images[i] = input_images[i];
    }
}


/**
   Loads the JSON filename as a json instance
*/
json load_json(fs::path filename)
{
  if(not fs::is_regular_file(filename))
    {
      std::stringstream message;
      message << filename << "not found";
      throw std::runtime_error(message.str().c_str());
    }

  std::ifstream is(filename.string());
  return json::parse(is);
}



int main(int argc, char** argv)
{
  try
    {
      // // parse the input directory from command line
      // fs::path input_directory;
      // parse_options(argc, argv, input_directory);
      // check_input_directory(input_directory);

      // json status = load_json(input_directory / "status.json");


      fs::path input_depth = "/home/mathieu/dev/intphys/data/1_train_train_nobj3/depth/depth_050.bin";
      fs::path output_depth = "/home/mathieu/dev/intphys/data/1_train_train_nobj3/depth/depth_050.png";
      float max_depth = 1201.70;
      normalize_depth(input_depth, output_depth, max_depth);


      // postprocess_masks(input_directory / "masks", status);

      // // read the png images from input_directory
      // std::vector<gray_image> input_pngs = load_pngs(input_directory);

      // // allocate output images
      // gray_image empty(input_pngs[0].get_height(), input_pngs[0].get_width());
      // std::vector<gray_image> output_pngs(input_pngs.size(), empty);

      // // scramble the images
      // scramble(input_pngs, output_pngs);

      // // write the output images
      // // write_pngs(output_directory, output_pngs);
    }
  catch(std::exception& e)
    {
      std::cerr << "error: " << e.what() << std::endl;
      return -1;
    }

  return 0;
}
