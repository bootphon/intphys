#include <cmath>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/filter/zlib.hpp>
#include <boost/iostreams/read.hpp>
#include <png++/png.hpp>

#include "image.hh"


namespace fs = boost::filesystem;


intphys::image::resolution intphys::image::get_resolution(const fs::path& png_file)
{
   // simply load the image and returns its resolution
   png::image<png::rgb_pixel> im(png_file.string());
   return {im.get_width(), im.get_height()};
}


void intphys::image::remove_alpha_channel(const fs::path& png_file)
{
   try
   {
      // write the converted image to a temp file
      fs::path model = fs::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%";
      fs::path temp_file = fs::unique_path(model);

      // force read to RGB will drop the alpha channel
      png::image<png::rgb_pixel> im(png_file.string());

      // write the converted image to the temp file and move the temp to
      // original file
      im.write(temp_file.string());
      fs::remove(png_file);
      fs::copy(temp_file, png_file);
      fs::remove(temp_file);
   }
   catch(std::exception& e)
   {
      std::stringstream message;
      message << "failed to process " << png_file << ": " << e.what();
      throw std::runtime_error(message.str().c_str());
   }
}


void intphys::image::normalize_depth(
   const fs::path& bin_file,
   const float& max_depth,
   const intphys::image::resolution& resolution,
   const std::size_t& nimages)
{
   try
   {
      // open the raw depth binary file (will be uncompressed, normalized and
      // split into nimages PNG files
      std::ifstream file(bin_file.string(), std::ios_base::in | std::ios_base::binary);

      // read the size of the data
      std::size_t size = 0;
      file.read(reinterpret_cast<char*>(&size), sizeof(size));
      if(size != resolution.width * resolution.height * nimages)
      {
         std::stringstream message;
         message << "depth size mismatch, excepted "
                 << resolution.width * resolution.height * nimages
                 << " but is " << size;
         throw std::runtime_error(message.str().c_str());
      }

      // initialize binary file reader
      boost::iostreams::filtering_streambuf<boost::iostreams::input> reader;
      reader.push(boost::iostreams::zlib_decompressor());
      reader.push(file);

      // allocate the output image and read buffer
      std::vector<float> buffer(resolution.width * resolution.height);
      png::image<png::gray_pixel> image(resolution.width, resolution.height);

      for(std::size_t z = 0; z < nimages; ++z)
      {
         // read the image
         boost::iostreams::read(
            reader,
            reinterpret_cast<char*>(buffer.data()), sizeof(float) * buffer.size());

         for(std::size_t y = 0; y < resolution.height; ++y)
         {
            for(std::size_t x = 0; x < resolution.width; ++x)
            {
               std::size_t index = x + y * resolution.height;
               float d = buffer[index];

               // depth normalization, depth field is from white (close) to
               // black (far). A depth at 0 is assumed to be maximal depth.
               if(d <= 0.0 or d > max_depth)
               {
                  d = max_depth;
               }
               d = std::sqrt(d / max_depth);

               image[y][x] = static_cast<png::gray_pixel>(255.f - 255.f * d);
            }
         }

         // write the normalized image
         fs::path png_file = "depth_" + detail::zfill(z + 1, std::to_string(nimages).size()) + ".png";
         image.write((bin_file.parent_path() / png_file).string());
      }

      // deleta the input raw binary file
      fs::remove(bin_file);
   }
   catch(std::exception& e)
   {
      std::stringstream message;
      message << "failed to process depth: " << e.what();
      throw std::runtime_error(message.str().c_str());
   }
}


void intphys::image::scramble_masks(
   const fs::path& png_file,
   const std::map<std::uint8_t, std::uint8_t>& color_map)
{
   try
   {
      // write the converted image to a temp file
      fs::path model = fs::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%";
      const fs::path temp_file = fs::unique_path(model);

      // force read to grayscale will convert from RGBA
      png::image<png::gray_pixel> im(png_file.string());

      // scramble the gray levels using the color map
      for(std::size_t y = 0; y < im.get_height(); ++y)
      {
         for(std::size_t x = 0; x < im.get_width(); ++x)
         {
            png::gray_pixel& p = im[y][x];
            p = color_map.at(p);
         }
      }

      // write the converted image to the temp file and move the temp to
      // original file
      im.write(temp_file.string());
      fs::remove(png_file);
      fs::copy(temp_file, png_file);
      fs::remove(temp_file);
   }
   catch(std::exception& e)
   {
      std::stringstream message;
      message << "failed to process " << png_file << ": " << e.what();
      throw std::runtime_error(message.str().c_str());
   }
}
