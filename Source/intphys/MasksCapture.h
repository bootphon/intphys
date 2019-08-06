#pragma once

#include "CoreMinimal.h"
#include "BidirMap.h"

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
   MasksCapture(const FIntVector& Size, const int32& Seed);

   ~MasksCapture();

   void Reset(bool DeleteActors);

   bool Capture(const FHitResult& Hit, const uint32& FrameIndex, const uint32& X, const uint32& Y);

   bool CaptureSky(const uint32& FrameIndex, const uint32& X, const uint32& Y);

   bool Save(const FString& Directory, TArray<FString>& OutActorsMasks);

   bool IsActorInFrame(const AActor* Actor, const uint32& FrameIndex) const;

private:
   // A triplet (width, height, nimages) of captured images
   FIntVector m_Size;

   // Actors present in each frame, mapped to their gray level
   TArray<TBidirMap<FString, png::gray_pixel>> m_ActorsMap;

   // A random number generator
   FRandomStream m_Random;

   // A buffer to store object masks and save PNGs
   TArray<png::image<png::gray_pixel>> m_Buffer;

   // returns the normalized name of the actor
   static FString GetActorName(const AActor* Actor);

   // Returns the index of an actor in the actors map (add the actor if not
   // already indexed)
   uint8 GetActorIndex(const FString& Actor);

   bool CaptureActor(const FString& Actor, const uint32& FrameIndex, const uint32& X, const uint32& Y);

   // // Returns a map (actor index -> random gray level) and update the output masks
   // TMap<uint8, uint8> Scramble(const uint32& FrameIndex, TArray<FString>& OutActorsMasks);

   // TArray<uint8> RandomGrayLevels(const uint32& NumLevels) const;
};
