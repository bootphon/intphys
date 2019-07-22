#include "intphys_scene.hh"
#include "intphys_status.hh"

#include <algorithm>
#include <iterator>
#include <string>
#include <sstream>
#include <stdexcept>


namespace fs = boost::filesystem;


void check_run_directory(const fs::path& directory)
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

      // make sure each subdirectory have files with the expected extension
      std::string extension = ".png";
      if(subdir == "depth")
      {
         extension = ".bin";
      }
      bool good_ext = std::all_of(
         fs::directory_iterator(subdirectory),
         fs::directory_iterator(),
         [&](const fs::path& file){return fs::extension(file) == extension;});

      if(not good_ext)
      {
         std::stringstream message;
         message << "files in " << subdirectory << " must have extension " << extension;
         throw std::runtime_error(message.str().c_str());
      }
   }
}


void check_testdev_directory(const fs::path& directory)
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
   const intphys::image::resolution& resolution,
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
      for(const fs::path& bin_file : fs::directory_iterator(run_dir / "depth"))
      {
         intphys::image::normalize_depth(bin_file, max_depth, resolution);
      }

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
         std::set<std::uint8_t> new_colors = random.generate<std::uint8_t>(masks.size(), 0, 255);

         // generate the map (old_color -> new_color)
         std::map<std::uint8_t, std::uint8_t> color_map;
         std::transform(
            masks.begin(), masks.end(), new_colors.begin(),
            std::inserter(color_map, color_map.end()),
            [](std::map<std::string, std::uint8_t>::value_type a, std::uint8_t b){return std::make_pair(a.second, b);});

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


std::shared_ptr<intphys::scene::scene> intphys::scene::make_scene(const fs::path& directory)
{
   const std::string dirname = directory.string();
   if(dirname.find("train") != std::string::npos)
   {
      return std::make_shared<intphys::scene::train_scene>(directory);
   }
   else if (dirname.find("dev") != std::string::npos)
   {
      return std::make_shared<intphys::scene::dev_scene>(directory);
   }
   else if (dirname.find("test") != std::string::npos)
   {
      return std::make_shared<intphys::scene::test_scene>(directory);
   }
   else
   {
      std::stringstream message;
      message << "cannot load a scene from " << directory << "(not train, dev or test)";
      throw std::runtime_error(message.str().c_str());
   }
}


intphys::scene::train_scene::train_scene(const fs::path& directory):
   intphys::scene::scene(directory)
{
   // make sure the directory is correct
   check_run_directory(m_root_directory);
}


intphys::scene::train_scene::~train_scene()
{}


float intphys::scene::train_scene::extract_max_depth() const
{
   return intphys::status::max_depth((m_root_directory / "status.json").string());
}


intphys::scene::dimension intphys::scene::train_scene::extract_dimension() const
{
   // load the first png of the scene and get its resolution
   fs::path png_file = m_root_directory / "scene" / "scene_001.png";
   if(not fs::is_regular_file(png_file))
   {
      std::stringstream message;
      message << "file not found: " << png_file;
      throw std::runtime_error(message.str().c_str());
   }

   intphys::image::resolution res = intphys::image::get_resolution(png_file);

   // count the number of images in the scene
   std::size_t nimages = std::distance(
      fs::directory_iterator(m_root_directory / "scene"), fs::directory_iterator());

   return {res.width, res.height, nimages};
}


inline std::size_t intphys::scene::train_scene::nruns() const
{
   return 1;
}


std::vector<fs::path> intphys::scene::train_scene::run_directories() const
{
   return {m_root_directory};
}


intphys::scene::dev_scene::dev_scene(const fs::path& directory):
   intphys::scene::scene(directory)
{
   // make sure the directory is correct
   check_testdev_directory(m_root_directory);
}

intphys::scene::dev_scene::~dev_scene()
{}


float intphys::scene::dev_scene::extract_max_depth() const
{
   return intphys::status::max_depth((m_root_directory / "1" / "status.json").string());
}


intphys::scene::dimension intphys::scene::dev_scene::extract_dimension() const
{
   // load the first png of the scene and get its resolution
   fs::path png_file = m_root_directory / "1" / "scene" / "scene_001.png";
   if(not fs::is_regular_file(png_file))
   {
      std::stringstream message;
      message << "file not found: " << png_file;
      throw std::runtime_error(message.str().c_str());
   }

   intphys::image::resolution res = intphys::image::get_resolution(png_file);

   // count the number of images in the scene
   std::size_t nimages = std::distance(
      fs::directory_iterator(m_root_directory / "1" / "scene"), fs::directory_iterator());

   return {res.width, res.height, nimages};
}


inline std::size_t intphys::scene::dev_scene::nruns() const
{
   return 4;
}

std::vector<fs::path> intphys::scene::dev_scene::run_directories() const
{
   return {
      m_root_directory / "1",
      m_root_directory / "2",
      m_root_directory / "3",
      m_root_directory / "4"};
}


intphys::scene::test_scene::test_scene(const fs::path& directory):
   intphys::scene::dev_scene(directory)
{}


intphys::scene::test_scene::~test_scene()
{}


inline bool intphys::scene::test_scene::is_test_scene() const
{
   return true;
}


void intphys::scene::test_scene::shuffle(randomizer& random) const
{
   // generate a random permutation
   std::vector<std::string> pre{"1", "2", "3", "4"};
   std::vector<std::string> post(pre);
   random.shuffle(post);

   // move the directories with _temp suffix to avoid race conditions
   for(std::size_t i = 0; i < pre.size(); ++i)
   {
      fs::path temp = m_root_directory / post[i].append("_temp");
      fs::rename(m_root_directory / pre[i], temp);
   }

   // remove the _temp suffix
   for(const fs::path& dir_temp : fs::directory_iterator(m_root_directory))
   {
      std::string sdir = dir_temp.string();
      fs::path dir(sdir.substr(0, sdir.size() - 4));
      fs::rename(dir_temp, dir);
   }
}
