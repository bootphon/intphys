#pragma once

#include <memory>
#include <vector>
#include <boost/filesystem.hpp>

#include "image.hh"
#include "randomizer.hpp"


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

   static void check_run_directory(const boost::filesystem::path& directory);
   static void check_testdev_directory(const boost::filesystem::path& directory);
};

}}
