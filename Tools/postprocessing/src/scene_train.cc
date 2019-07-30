#include <sstream>
#include <stdexcept>

#include "scene_train.hh"
#include "status.hh"


namespace fs = boost::filesystem;


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
