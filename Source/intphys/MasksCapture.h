#pragma once

#include "CoreMinimal.h"

THIRD_PARTY_INCLUDES_START
#include "ThirdParty/libPNG/libPNG-1.5.27/png.h"
#include <png++/png.hpp>
THIRD_PARTY_INCLUDES_END


/**
 * Capture and save objects masks of the scene
 */
class MasksCapture
{
public:
   MasksCapture(const FIntVector& Size);

   ~MasksCapture();

   void Reset(bool DeleteActors);

   void SetActors(const TArray<AActor*>& Actors);

   bool Capture(const FHitResult& Hit, const uint32& ImageIndex, const uint32& x, const uint32& y);

   bool Save(const FString& Directory, TArray<FString>& OutActorsMasks);

   bool IsActorInFrame(const AActor* Actor, const uint32& ImageIndex);

private:
   // A triplet (width, height, nimages) of captured images
   FIntVector m_Size;

   // Map the actors names to int ids
   TSet<FString> m_ActorsSet;
   TMap<FString, uint8> m_ActorsMap;

   // A buffer to store object masks and save PNGs
   TArray<png::image<png::gray_pixel>> m_Buffer;
};
