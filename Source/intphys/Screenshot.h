// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"

#include "SceneCapture.h"
#include "DepthCapture.h"
#include "MasksCapture.h"


/**
 * This class implements the functions exposed in ScreenshotManager.h, see here
 * for documentation.
 */
class FScreenshot
{
public:
   FScreenshot(
      const FIntVector& Size, AActor* OriginActor, const int32& RandomSeed,
      bool Verbose = false);

   ~FScreenshot();

   void SetOriginActor(AActor* Actor);

   bool Capture(const TArray<AActor*>& IgnoredActors);

   bool Save(const FString& Directory, TArray<FString>& OutActorsMasks);

   void Reset(bool DeleteActors);

   bool IsActorInFrame(const AActor* Actor, const uint32& ImageIndex);

   bool IsActorVisible(const AActor* Actor, const TArray<AActor*>& IgnoredActors);

private:
   // A triplet (width, height, nframes) of captured images
   FIntVector m_Size;

   // The actor giving the point of view for capture
   AActor* m_OriginActor;

   // Output log messages when true (when false only output errors)
   bool m_Verbose;

   // Index of the current frame (next to be captured)
   uint m_FrameIndex;

   // Capture screenshots of the scene, depth field and objects masks
   SceneCapture m_Scene;
   DepthCapture m_Depth;
   MasksCapture m_Masks;

   // Take the scene's depth field and object masking, push them to memory
   bool CaptureDepthAndMasks(const TArray<AActor*>& IgnoredActors);
};
