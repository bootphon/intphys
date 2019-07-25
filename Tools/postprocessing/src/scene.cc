#include <algorithm>
#include <iterator>
#include <string>
#include <sstream>
#include <stdexcept>

#include "scene.hh"
#include "status.hh"


namespace fs = boost::filesystem;


void intphys::scene::scene::check_run_directory(const fs::path& directory)
{
   // make sure it contains a status.json file
   if(not fs::is_regular_file(directory / "status.json"))
   {
      std::stringstream message;
      message << "status.json not found in " << directory;
      throw std::runtime_error(message.str().c_str());
   }

   // make sure it contains depth, masks and scene subdirectories
   for(const std::string& subdir : {"depth", "masks", "scene"})
   {
      fs::path subdirectory = directory / subdir;
      if(not fs::is_directory(subdirectory))
      {
         std::stringstream message;
         message << subdir << "subdirectory not found in " << directory;
         throw std::runtime_error(message.str().c_str());
      }

      // make sure each subdirectory have files with the expected content
      if(subdir == "depth")
      {
         const fs::path depth_file = subdirectory / "depth.bin";
         if(not fs::is_regular_file(depth_file))
         {
            std::stringstream message;
            message << "file " << depth_file << " not found";
            throw std::runtime_error(message.str().c_str());
         }
      }
      else
      {

         const bool good_ext = std::all_of(
            fs::directory_iterator(subdirectory),
            fs::directory_iterator(),
            [&](const fs::path& file){return fs::extension(file) == ".png";});

         if(not good_ext)
         {
            std::stringstream message;
            message << "files in " << subdirectory << " must have extension .png";
            throw std::runtime_error(message.str().c_str());
         }
      }
   }
}


void intphys::scene::scene::check_testdev_directory(const fs::path& directory)
{
   // make sure it contains 1, 2, 3, 4 subdirectories
   for(const std::string& subdir : {"1", "2", "3", "4"})
   {
      if(not fs::is_directory(directory / subdir))
      {
         std::stringstream message;
         message << subdir << "subdirectory not found in " << directory;
         throw std::runtime_error(message.str().c_str());
      }

      check_run_directory(directory / subdir);
   }
}



intphys::scene::scene::scene(const fs::path& directory):
   m_root_directory(directory)
{}


intphys::scene::scene::~scene()
{}


inline bool intphys::scene::scene::is_test_scene() const
{
   return false;
}


void intphys::scene::scene::postprocess(
   const float& max_depth,
   const intphys::scene::dimension& dimension,
   intphys::randomizer& random)
{
   for(const fs::path& run_dir : run_directories())
   {
      // load status.json
      intphys::status status((run_dir / "status.json").string());

      // postprocess the scene images (remove alpha channel)
      for(const fs::path& png_file : fs::directory_iterator(run_dir / "scene"))
      {
         intphys::image::remove_alpha_channel(png_file);
      }

      // postprocess depth (create normalized gray images from raw data, and
      // update the status)
      const fs::path depth_file = run_dir / "depth" / "depth.bin";
      intphys::image::normalize_depth(
         depth_file, max_depth,
         intphys::image::resolution{dimension.x, dimension.y},
         dimension.z);

      // update the max depth in the JSON with the global max depth (in the
      // whole dataset)
      status.max_depth(max_depth);

      // postprocess masks (from gray-like RGBA to pure grayscale, scramble the
      // masks gray levels by randomizing them at each frame of the scene)
      std::map<std::string, std::uint8_t> masks = status.get_header_masks();
      status.erase_header_masks();

      std::size_t frame_index = 0;
      for(const fs::path& png_file : fs::directory_iterator(run_dir / "masks"))
      {
         // generate random new colors for the frame's masks
         std::vector<std::uint8_t> new_colors = random.generate<std::uint8_t>(masks.size(), 0, 255);

         // generate the map (old_color -> new_color)
         std::map<std::uint8_t, std::uint8_t> color_map;
         std::transform(
            masks.begin(), masks.end(), new_colors.begin(),
            std::inserter(color_map, color_map.end()),
            [](std::map<std::string, std::uint8_t>::value_type a, std::uint8_t b)
            { return std::make_pair(a.second, b); });

         // generate new masks images and insert the sub-json into the status,
         // at the right frame
         image::scramble_masks(png_file, color_map);
         std::map<std::string, std::uint8_t> new_masks;
         for(const auto& v : masks)
         {
            new_masks[v.first] = color_map[v.second];
         }
         status.update_frame_masks(frame_index++, new_masks);
      }

      // save the updated JSON
      status.save((run_dir / "status.json").string());
   }
}
