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
   DepthCapture(const FIntVector& Size, const float& MaxDepth);

   ~DepthCapture();

   void Reset();

   void CaptureInit(AActor* OriginActor);

   bool Capture(const FHitResult& Hit, const uint32& ImageIndex, const uint32& PixelIndex);

   bool Save(const FString& Directory);

private:
   // A triplet (width, height, nimages) of captured images
   FIntVector m_Size;

   // The number of pixels in an image (m_Size.X * m_Size.Y)
   uint32 m_NumPixels;

   // The theoretical maximal depth in the scene
   float m_MaxDepth;

   // The maximal depth encountered during capture
   float m_CurrentMaxDepth;

   // The current location and rotation of the origin actor
   FVector m_OriginLocation;
   FVector m_OriginRotation;

   // A buffer to store the captured depth field
   TArray<TArray<float>> m_Buffer;

   // A buffer to build a grayscale PNG for saving
   png::image<png::gray_pixel> m_Png;
};
