#include <sstream>
#include <stdexcept>

#include "scene_dev.hh"
#include "status.hh"

namespace fs = boost::filesystem;


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
