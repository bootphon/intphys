#pragma once

#include <iostream>
#include <mutex>
#include <string>


namespace intphys
{
class progressbar
{
public:
   progressbar(
      const std::size_t& size,
      const std::string& header,
      std::ostream& out = std::cout);

   ~progressbar();

   void next();

private:
   std::size_t m_size;
   std::size_t m_current;
   std::string m_header;
   std::ostream& m_out;
   std::mutex m_mutex;

   void display() const;
   void clear_bar() const;
};
}
