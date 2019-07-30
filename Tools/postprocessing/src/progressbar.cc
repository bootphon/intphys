#include "progressbar.hh"

#include <iostream>

intphys::progressbar::progressbar(
   const std::size_t& size,
   const std::string& header,
   std::ostream& out)
   : m_size(size), m_current(0), m_header(header), m_out(out), m_mutex()
{
   display();
}


intphys::progressbar::~progressbar()
{}


void intphys::progressbar::next()
{
   // avoid data race when incrementing the progress counter
   std::lock_guard<std::mutex> guard(m_mutex);
   if(m_current < m_size)
   {
      ++m_current;
      display();
   }
}


void intphys::progressbar::display() const
{
   float percent = 100 * m_current / m_size;
   if(percent < 100.0)
   {
      m_out << m_header << "... " << static_cast<std::size_t>(percent) << "%\r" << std::flush;
   }
   else
   {
      m_out << m_header << "... done" << std::endl;
   }
}
