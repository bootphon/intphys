#pragma once

#include <memory>
#include <vector>
#include <boost/filesystem.hpp>

#include "scene_factory.hh"
#include "randomizer.hpp"


namespace intphys
{
   class dataset
   {
   public:
      dataset(const boost::filesystem::path& directory);

      ~dataset();

      // returns the train, test and dev scenes contained in the dataset
      const std::vector<std::shared_ptr<intphys::scene::scene>>& scenes() const;

      // returns the total number of runs in the dataset (1 run per train scene,
      // 4 runs per dev/test scene)
      std::size_t nruns() const;

      // returns the total number of images in the dataset
      std::size_t nimages() const;

      // returns the maximum depth fount in the dataset
      float extract_max_depth(const std::size_t& njobs) const;

      const intphys::scene::dimension& scenes_dimension() const;

      /**
       postprocess all the scenes in the dataset

       @param njobs the number of parallel threads to launch
       @param random the random number generator
       @param max_depth the maximum depth found in the dataset, if 0.0, extract it
           from scenes's status.json
      */
      void postprocess(const std::size_t& njobs, intphys::randomizer& random, float max_depth) const;

      /**
         postprocess all the scenes in the dataset, extract the max depth

         @param njobs the number of parallel threads to launch
         @param random the random number generator
      */
      void postprocess(const std::size_t& njobs, intphys::randomizer& random) const;

   private:
      // the root directory of the intphys dataset
      boost::filesystem::path m_root_directory;

      // scenes in the dataset, can be train, test or dev scenes
      std::vector<std::shared_ptr<intphys::scene::scene>> m_scenes;

      // dimension of each scene as width x height x nimages
      intphys::scene::dimension m_scene_dimension;

      // make sure the root directory is valid, raise if not
      void check_root_directory() const;
   };
}
