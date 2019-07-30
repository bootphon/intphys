/**
   Parallel implementation of the std::for_each algorithm
   from https://github.com/t-lutz/ParallelSTL/blob/master/include/experimental/bits/parallel/algos/par/for_each.h
*/
#pragma once

#include <algorithm>
#include <iterator>
#include <thread>
#include <utility>
#include <vector>


namespace intphys
{
namespace detail
{
template<class InputIterator>
inline std::vector<std::pair<InputIterator, InputIterator>>
chunk_range(const std::size_t njobs, InputIterator first, InputIterator last)
{
   const std::size_t range_size = std::distance(first, last);
   const std::size_t partitions = std::min(
      {
         static_cast<std::size_t>(std::thread::hardware_concurrency()),
         range_size,
         njobs
      });

   std::vector<std::pair<InputIterator, InputIterator>> chunks;
   chunks.reserve(partitions);

   const std::size_t segment_size = range_size / std::max(partitions, std::size_t{1});

   // last element of the previous partition
   InputIterator end = first;

   for(unsigned i = 0; i + 1 < partitions; ++i)
   {
      InputIterator begin = end;
      std::advance(end, segment_size);
      chunks.emplace_back(std::make_pair(begin, end));
   }

   // push the last chunk (could be slightly larger because of rounding or empty
   // if first == last)
   chunks.emplace_back(std::make_pair(end, last));

   return chunks;
}
}


template<class InputIterator, class UnaryFunction>
void for_each(const std::size_t& njobs, InputIterator first, InputIterator last, UnaryFunction f)
{
   // when njobs == 1, execute a sequential for_each
   if(njobs == 1)
   {
      std::for_each(first, last, f);
   }
   else
   {
      // divide the [first, last] range into chunks
      const auto chunks = intphys::detail::chunk_range(njobs, first, last);

      std::vector<std::thread> threads_pool;
      threads_pool.reserve(chunks.size());

      for(const auto& chunk : chunks)
      {
         threads_pool.emplace_back(
            std::thread(
               std::for_each<InputIterator, UnaryFunction>,
               chunk.first, chunk.second,
               std::forward<UnaryFunction>(f)));
      }

      for(auto& thread : threads_pool)
      {
         thread.join();
      }
   }
}
}
