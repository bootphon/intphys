#pragma once

#include "scene_dev.hh"

namespace intphys
{
namespace scene
{

/**
   A test_scene is like a dev_scene but have an additional shuffle_runs method
   to permute possible and impossible runs randomly.
*/
class test_scene : public dev_scene
{
public:
   test_scene(const boost::filesystem::path& directory);
   virtual ~test_scene();

   // returns true
   bool is_test_scene() const;

   /**
      Permute possible and impossible runs in the scene

      A test scene is made of subdirectories 1, 2, 3 and 4, where 1 and 2 are
      possible cases and 3 and 4 impossible cases. This method simply shuffle
      1, 2, 3, 4 subdirectories in a random way.

      @param random the random number generator
   */
   void shuffle(intphys::randomizer& random) const;
};

}}
