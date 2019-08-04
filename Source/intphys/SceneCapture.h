#pragma once

#include "CoreMinimal.h"

THIRD_PARTY_INCLUDES_START
#include "ThirdParty/libPNG/libPNG-1.5.27/png.h"
#include <png++/png.hpp>
THIRD_PARTY_INCLUDES_END


/**
 * Capture and save screenshots of the scene
 */
class SceneCapture
{
public:
   SceneCapture(const FIntVector& Size);

   ~SceneCapture();

   bool Capture(const uint32& Index);

   bool Save(const FString& Directory);

   void Reset();

private:
   // A triplet (width, height, nimages) of captured images
   FIntVector m_Size;

   // A buffer to store captured images
   TArray<TArray<FColor>> m_Buffer;

   // A buffer to build a RGB PNG image for saving
   png::image<png::rgb_pixel> m_Png;
};
