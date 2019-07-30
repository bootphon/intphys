#pragma once

#include "scene.hh"

namespace intphys
{
namespace scene
{

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

}}
