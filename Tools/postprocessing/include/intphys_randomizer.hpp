#pragma once

#include <algorithm>
#include <set>
#include <random>


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

    // generates a random set of 'size' elements in [min, max] without repetitions
    template<class T>
    std::set<T> generate(const std::size_t& size, const T& min, const T& max)
    {
      // uniform distribution in [min, max]
      std::uniform_int_distribution<int> dist(static_cast<int>(min), static_cast<int>(max));

      // fill the output data
      std::set<T> data;
      while(data.size() != size)
        {
          data.insert(static_cast<T>(dist(m_generator)));
        }
      return data;
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
