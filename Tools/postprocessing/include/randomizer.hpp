#pragma once

#include <algorithm>
#include <random>
#include <set>
#include <type_traits>
#include <vector>



namespace intphys
{
  class randomizer
  {
  public:
    randomizer(uint seed)
      : m_generator(seed)
    {}

    ~randomizer()
    {}

    // Generates a random set of 'size' integer elements in [min, max] without
    // repetitions. T must be an integer type.
    template<class T>
    std::vector<T> generate(const std::size_t& size, const T& min, const T& max)
    {
      static_assert(std::is_integral<T>::value, "must be an integer type");

      // uniform distribution in [min, max]
      std::uniform_int_distribution<int> dist(static_cast<int>(min), static_cast<int>(max));

      // fill the output data (a set ensures we have no repetitions)
      std::set<T> data;
      while(data.size() != size)
        {
          data.insert(static_cast<T>(dist(m_generator)));
        }

      // data in a set is ordered, need to be shuffled
      std::vector<T> vdata(data.begin(), data.end());
      std::shuffle(vdata.begin(), vdata.end(), m_generator);
      return vdata;
    }

    // randomly permute an iterable in place
    template<class T>
    void shuffle(T& data)
    {
      std::shuffle(data.begin(), data.end(), m_generator);
    }

  private:
    std::mt19937 m_generator;
  };
}
