#pragma once

#include <map>
#include <boost/filesystem.hpp>


namespace intphys
{
   namespace image
   {
      // the resolution of an image, in number of pixels
      struct resolution
      {
         std::size_t width;
         std::size_t height;
      };

      // get the resolution of an image
      resolution get_resolution(const boost::filesystem::path& png_file);

      // converts a RGBA image to RGB
      void remove_alpha_channel(const boost::filesystem::path& png_file);

      // deserialize binary file as a vector<float> of raw depth values, normalize
      // them in 0 (far) to 1 (close) and write them in a grayscale image of the
      // given resolution.
      void normalize_depth(
         const boost::filesystem::path& bin_file,
         const float& max_depth,
         const image::resolution& resolution);

      void scramble_masks(
         const boost::filesystem::path& png_file,
         const std::map<std::uint8_t, std::uint8_t>& color_map);
   }
}
