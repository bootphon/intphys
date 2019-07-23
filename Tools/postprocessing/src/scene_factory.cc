#include <sstream>
#include <stdexcept>

#include "scene_factory.hh"

namespace fs = boost::filesystem;


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
