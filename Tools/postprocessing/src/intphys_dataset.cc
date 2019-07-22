#include <algorithm>
#include <stdexcept>
#include <sstream>
#include <string>
#include <vector>

#include <boost/progress.hpp>

#include "intphys_dataset.hh"
#include "intphys_image.hh"


namespace fs = boost::filesystem;


intphys::dataset::dataset(const fs::path& directory)
   : m_root_directory(directory),
     m_scenes()
{
   check_root_directory();

   // explore train subdirectory
   const fs::path train_directory = m_root_directory / "train";
   if(fs::is_directory(train_directory))
   {
      for(const fs::path& subdir : fs::directory_iterator(train_directory))
      {
         m_scenes.push_back(intphys::scene::make_scene(subdir));
      }
   }

   // explore test and dev directories
   for(const std::string test : {"test", "dev"})
   {
      // dataset/test level
      const fs::path test_directory = m_root_directory / test;
      if(fs::is_directory(test_directory))
      {
         // dataset/test/O1 level
         for(const fs::path& subdir : fs::directory_iterator(test_directory))
         {
            // dataset/test/O1/001 level
            for(const fs::path& subsubdir : fs::directory_iterator(subdir))
            {
               m_scenes.push_back(intphys::scene::make_scene(subsubdir));
            }
         }
      }
   }

   // retrieve the dimension of the scenes (we assume they are all the same and
   // get nly dimension of the first one)
   m_scene_dimension = m_scenes[0]->extract_dimension();
}


intphys::dataset::~dataset()
{}


const std::vector<std::shared_ptr<intphys::scene::scene>>& intphys::dataset::scenes() const
{
   return m_scenes;
}


void intphys::dataset::check_root_directory() const
{
   // make sure the directory exists
   if(not fs::exists(m_root_directory) or not fs::is_directory(m_root_directory))
   {
      std::stringstream message;
      message << m_root_directory << " is not an existing directory";
      throw std::runtime_error(message.str().c_str());
   }

   // make sure the subflders in the root directory are either train, test or
   // dev, but nothin else
   std::vector<std::string> expected{"train", "test", "dev"};
   std::vector<fs::path> subdirs;
   for(const fs::path& subdir : fs::directory_iterator(m_root_directory))
   {
      if(std::find(expected.begin(), expected.end(), subdir.filename().string()) == expected.end())
      {
         std::stringstream message;
         message << m_root_directory << " contains an unvalid subdirectory: " << subdir.filename();
         throw std::runtime_error(message.str().c_str());
      }
   }
}


float intphys::dataset::extract_max_depth() const
{
   float max_depth = 0.0;

   for(const auto& scene : m_scenes)
   {
      float current_depth = scene->extract_max_depth();
      max_depth = std::max(max_depth, current_depth);
   }

   return max_depth;
}


const intphys::scene::dimension& intphys::dataset::scenes_dimension() const
{
   return m_scene_dimension;
}


std::size_t intphys::dataset::nimages() const
{
   std::size_t nruns = 0;
   for(const auto& scene : m_scenes)
   {
      nruns += scene->nruns();
   }

   return nruns * m_scene_dimension.z * 3;
}


void intphys::dataset::postprocess(const uint& njobs, randomizer& random) const
{
   // extract the maximum depth in all scenes of the dataset
   float max_depth = extract_max_depth();

   // postprocess the scenes
   postprocess(njobs, random, max_depth);
}


void intphys::dataset::postprocess(const uint& njobs, randomizer& random, float max_depth) const
{
   intphys::image::resolution resolution{m_scene_dimension.x, m_scene_dimension.y};

   boost::progress_display show_progress(m_scenes.size());
   for(const auto& scene : m_scenes)
   {
      scene->postprocess(max_depth, resolution, random);

      if(scene->is_test_scene())
      {
         // need to cast from IScene to TestScene
         dynamic_cast<intphys::scene::test_scene*>(scene.get())->shuffle(random);
      }

      ++show_progress;
   }
}
