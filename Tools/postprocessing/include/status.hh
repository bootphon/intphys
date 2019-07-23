#pragma once

#include <map>
#include <string>

#include "rapidjson/document.h"


namespace intphys
{
/**
   Make operations on a status.json file in an intphys dataset
 */
class status
{
public:
   status(const std::string& filename);
   ~status();

   // save the status to the given filename as a JSON file
   void save(const std::string& filename) const;

   /**
      Extract the max depth defined in the status

      This method does not load the whole JSON file, but read the first lines
      until the max depth is fount.
   */
   static float max_depth(const std::string& filename);

   // update the max depth in the status
   void max_depth(const float& max_depth);

   // returns the masks in the status header as a color map
   std::map<std::string, std::uint8_t> get_header_masks() const;

   // erase the masks entry in the status header
   void erase_header_masks();

   // update the masks values in the status for the specified frame
   void update_frame_masks(
      const std::size_t frame_index,
      const std::map<std::string, std::uint8_t> masks);

protected:
   rapidjson::Document m_status;
};
}
