#pragma once

#include <memory>
#include <boost/filesystem.hpp>

#include "scene.hh"
#include "scene_dev.hh"
#include "scene_test.hh"
#include "scene_train.hh"


namespace intphys
{
namespace scene
{
/**
   Factory function instanciating a scene from its directory

   The concrete scene type is either a train_scene, a dev_scene or a test_scene,
   it is guessed according to the `directory` path.

   @param directory the root directory of the scene

   @raise std::runtime_error if the scene type cannot be guessed from `directory`.

   @return a shared pointer to the instanciated scene.
*/
std::shared_ptr<scene> make_scene(const boost::filesystem::path& directory);
}
}
