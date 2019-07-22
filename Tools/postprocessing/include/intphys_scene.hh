#pragma once

#include <memory>
#include <vector>
#include <boost/filesystem.hpp>

#include "intphys_image.hh"
#include "intphys_randomizer.hpp"


namespace intphys
{
namespace scene
{

// the dimension of a scene is the resolution of an individual image times the
// number of images in the scene
struct dimension
{
   std::size_t x;  // image width
   std::size_t y;  // image height
   std::size_t z;  // number of images
};

class scene
{
public:
   scene(const boost::filesystem::path& directory);

   virtual ~scene();

   virtual float extract_max_depth() const = 0;

   virtual intphys::scene::dimension extract_dimension() const = 0;

   // returns 1 if this is a TrainScene, 4 otherwise
   virtual std::size_t nruns() const = 0;

   // returns the directories of the scene's runs
   virtual std::vector<boost::filesystem::path> run_directories() const = 0;

   // returns true if this is a TestScene, false otherwise
   virtual bool is_test_scene() const;

   void postprocess(const float& max_depth,
                    const intphys::image::resolution& resolution,
                    intphys::randomizer& random);

protected:
   boost::filesystem::path m_root_directory;
};


class train_scene : public scene
{
public:
   train_scene(const boost::filesystem::path& directory);

   virtual ~train_scene();

   float extract_max_depth() const;

   intphys::scene::dimension extract_dimension() const;

   std::size_t nruns() const;

   std::vector<boost::filesystem::path> run_directories() const;
};


/**
   A dev_scene is made of a quaduplet of runs, each of them stored in
   subdirectories 1, 2, 3 and 4 respectively.
 */
class dev_scene : public scene
{
public:
   dev_scene(const boost::filesystem::path& directory);

   virtual ~dev_scene();

   float extract_max_depth() const;

   intphys::scene::dimension extract_dimension() const;

   std::size_t nruns() const;

   std::vector<boost::filesystem::path> run_directories() const;
};


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


/**
   Factory function instanciating a scene from its directory

   The concrete scene type is either a TrainScene, a DevScene or a TestScene, it is
   guessed according to the `directory` path.

   @param directory the root directory of the scene

   @raise std::runtime_error if the scene type cannot be guessed from `directory`.

   @return a shared pointer to the instanciated scene.
*/
std::shared_ptr<scene> make_scene(const boost::filesystem::path& directory);

}}
