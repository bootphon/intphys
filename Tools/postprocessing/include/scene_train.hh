#pragma once

#include "scene.hh"


namespace intphys
{
namespace scene
{
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
}
}
