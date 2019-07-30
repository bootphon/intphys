#include <sstream>
#include <stdexcept>

#include "scene_test.hh"
#include "status.hh"


namespace fs = boost::filesystem;


intphys::scene::test_scene::test_scene(const fs::path& directory):
   intphys::scene::dev_scene(directory)
{}


intphys::scene::test_scene::~test_scene()
{}


inline bool intphys::scene::test_scene::is_test_scene() const
{
   return true;
}


void intphys::scene::test_scene::shuffle(randomizer& random) const
{
   // generate a random permutation
   std::vector<std::string> pre{"1", "2", "3", "4"};
   std::vector<std::string> post(pre);
   random.shuffle(post);

   // move the directories with _temp suffix to avoid race conditions
   for(std::size_t i = 0; i < pre.size(); ++i)
   {
      fs::path temp = m_root_directory / post[i].append("_temp");
      fs::rename(m_root_directory / pre[i], temp);
   }

   // remove the _temp suffix
   for(const fs::path& dir_temp : fs::directory_iterator(m_root_directory))
   {
      std::string sdir = dir_temp.string();
      fs::path dir(sdir.substr(0, sdir.size() - 5));
      fs::rename(dir_temp, dir);
   }
}
