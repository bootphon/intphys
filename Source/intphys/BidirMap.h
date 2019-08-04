#pragma once

#include "CoreMinimal.h"


/**
 * A very simple bidirectional map Key <-> Value
 *
 * For use in the MasksCapture class
 */
template<class Key, class Value>
class TBidirMap
{
public:
   TBidirMap()
      : m_KeyMap(), m_ValueMap()
   {}

   ~TBidirMap()
   {}

   uint32 Num() const
   {
      return m_KeyMap.Num();
   }

   void Add(const Key& K, const Value& V)
   {
      m_KeyMap.Add(K, V);
      m_ValueMap.Add(V, K);
   }

   bool ContainsKey(const Key& K) const
   {
      return m_KeyMap.Contains(K);
   }

   bool ContainsValue(const Value& V) const
   {
      return m_ValueMap.Contains(V);
   }

   Value GetValue(const Key& K) const
   {
      return m_KeyMap[K];
   }

   typename TMap<Key, Value>::TConstIterator CreateConstIterator() const
   {
      return m_KeyMap.CreateConstIterator();
   }

private:
   TMap<Key, Value> m_KeyMap;
   TMap<Value, Key> m_ValueMap;
};
