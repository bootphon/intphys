#include <algorithm>
#include <mutex>
#include <stdexcept>
#include <sstream>
#include <string>
#include <vector>

#include "dataset.hh"
#include "foreach.hpp"
#include "image.hh"
#include "progressbar.hh"


namespace fs = boost::filesystem;


intphys::dataset::dataset(const fs::path& directory)
   : m_root_directory(directory),
     m_scenes()
{
   check_root_directory();

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

   // explore train subdirectory
   const fs::path train_directory = m_root_directory / "train";
   if(fs::is_directory(train_directory))
   {
      for(const fs::path& subdir : fs::directory_iterator(train_directory))
      {
         m_scenes.push_back(intphys::scene::make_scene(subdir));
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


float intphys::dataset::extract_max_depth(const std::size_t& njobs) const
{
   intphys::progressbar show_progress(m_scenes.size(), "extracting depth");

   auto max_depth = [&](const float& a, std::shared_ptr<intphys::scene::scene> b)
   {
      float max = std::max(a, b->extract_max_depth());
      show_progress.next();
      return max;
   };

   return std::accumulate(m_scenes.begin(), m_scenes.end(), 0.0, max_depth);
}


const intphys::scene::dimension& intphys::dataset::scenes_dimension() const
{
   return m_scene_dimension;
}


std::size_t intphys::dataset::nruns() const
{
   auto add_runs = [](const std::size_t& a, std::shared_ptr<intphys::scene::scene> b)
   {
      return a + b->nruns();
   };

   return std::accumulate(m_scenes.begin(), m_scenes.end(), 0, add_runs);
}

std::size_t intphys::dataset::nimages() const
{
   // for each run we have (scene + depth + masks) * scene_dimension
   return nruns() * m_scene_dimension.z * 3;
}


void intphys::dataset::postprocess(
   const std::size_t& njobs, randomizer& random) const
{
   // extract the maximum depth in all scenes of the dataset
   float max_depth = extract_max_depth(njobs);

   // postprocess the scenes
   postprocess(njobs, random, max_depth);
}


void intphys::dataset::postprocess(
   const std::size_t& njobs, randomizer& random, float max_depth) const
{
   intphys::progressbar show_progress(m_scenes.size(), "postprocessing scenes");

   intphys::for_each(
      njobs, m_scenes.begin(), m_scenes.end(),
      [&](const std::shared_ptr<intphys::scene::scene> scene)
      {
         scene->postprocess(max_depth, m_scene_dimension, random);
         if(scene->is_test_scene())
         {
            // need to cast from IScene to TestScene
            dynamic_cast<intphys::scene::test_scene*>(scene.get())->shuffle(random);
         }

         show_progress.next();
      });
}
