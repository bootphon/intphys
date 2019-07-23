#include <fstream>
#include <sstream>
#include <stdexcept>

#include "rapidjson/prettywriter.h"

#include "status.hh"


intphys::status::status(const std::string& filename)
{
   std::ifstream is(filename);
   std::string json_data(
      (std::istreambuf_iterator<char>(is)),
      std::istreambuf_iterator<char>());

   m_status.Parse(json_data.c_str());
}


intphys::status::~status()
{}


void intphys::status::save(const std::string& filename) const
{
   rapidjson::StringBuffer buffer;
   rapidjson::PrettyWriter<rapidjson::StringBuffer> writer(buffer);
   m_status.Accept(writer);

   std::ofstream os(filename);
   os << std::string(buffer.GetString()) << std::endl;
}


float intphys::status::max_depth(const std::string& filename)
{
   // delimiter to split the max_depth string in the json
   const std::string delimiter(": ");

   // open the status.json of each scene and read it line per line
   std::ifstream status(filename);
   std::string line;
   while(std::getline(status, line))
   {
      // extract the depth from the "max_depth" json entry
      if(line.find("max_depth") != std::string::npos)
      {
         std::string token = line.substr(line.find(delimiter) + 2, line.size() - 1);
         return std::atof(token.c_str());
      }
   }

   // should never occur
   std::stringstream message;
   message << "cannot extract max_depth from " << filename;
   throw std::runtime_error(message.str().c_str());
}


void intphys::status::max_depth(const float& max_depth)
{
   m_status["header"]["max_depth"].SetFloat(max_depth);
}


std::map<std::string, std::uint8_t> intphys::status::get_header_masks() const
{
   std::map<std::string, std::uint8_t> color_map;
   for(auto it = m_status["header"]["masks"].MemberBegin();
       it != m_status["header"]["masks"].MemberEnd(); ++it)
   {
      color_map[it->name.GetString()] = it->value.GetUint();
   }

   return color_map;
}


void intphys::status::erase_header_masks()
{
   m_status["header"].RemoveMember("masks");
}


void intphys::status::update_frame_masks(
   const std::size_t frame_index,
   const std::map<std::string, std::uint8_t> masks)
{
   rapidjson::Value new_masks(rapidjson::kObjectType);
   for(const auto& v : masks)
   {
      // must copy the name of the mask for rapidjson
      char name[v.first.size()];
      strcpy(name, v.first.c_str());

      new_masks.AddMember(
         rapidjson::Value().SetString(name, v.first.size(), m_status.GetAllocator()),
         rapidjson::Value().SetUint(v.second),
         m_status.GetAllocator());
   }

   m_status["frames"][frame_index].AddMember("masks", new_masks, m_status.GetAllocator());
}
