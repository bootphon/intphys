#pragma once

#include "CoreMinimal.h"

THIRD_PARTY_INCLUDES_START
#include "ThirdParty/libPNG/libPNG-1.5.27/png.h"
#include <png++/png.hpp>
THIRD_PARTY_INCLUDES_END


/**
 * Capture and save depth fields of the scene
 */
class DepthCapture
{
public:
   DepthCapture(const FIntVector& Size);

   ~DepthCapture();

   void Reset();

   void CaptureInit(AActor* OriginActor);

   bool Capture(const FHitResult& Hit, const uint32& ImageIndex, const uint32& X, const uint32& Y);

   bool Save(const FString& Directory);

private:
   // the maximal distance that can be encoded is (2^16 - 1) / 10 (in cm)
   static const float MaxDepth;

   // A triplet (width, height, nimages) of captured images
   FIntVector m_Size;

   // The current location and rotation of the origin actor
   FVector m_OriginLocation;
   FVector m_OriginRotation;

   // A buffer to store the captured depth field and save PNGs
   TArray<png::image<png::gray_pixel_16>> m_Buffer;
};
