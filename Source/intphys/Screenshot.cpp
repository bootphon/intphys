#include "Screenshot.h"
#include "Utils.h"
#include "RayTracer.h"


FScreenshot::FScreenshot(const FIntVector& Size, const float& MaxDepth, AActor* OriginActor, bool Verbose)
   : m_Size(Size), m_OriginActor(OriginActor), m_Verbose(Verbose),
     m_ImageIndex(0), m_Scene(Size), m_Depth(Size, MaxDepth), m_Masks(Size)
{}


FScreenshot::~FScreenshot()
{}


void FScreenshot::SetActors(TArray<AActor*>& Actors)
{
   m_Masks.SetActors(Actors);
}


void FScreenshot::SetOriginActor(AActor* Actor)
{
   m_OriginActor = Actor;
}


void FScreenshot::Reset(bool DeleteActors)
{
   m_ImageIndex = 0;
   m_Scene.Reset();
   m_Depth.Reset();
   m_Masks.Reset(DeleteActors);
}


bool FScreenshot::Capture(const TArray<AActor*>& IgnoredActors)
{
   if (m_ImageIndex >= m_Size.Z)
   {
      UE_LOG(LogTemp, Error, TEXT("Screen capture failed: too much images captured"));
      return false;
   }

   // update the location/rotation of the origin actor
   m_Depth.CaptureInit(m_OriginActor);

   bool bDone1 = m_Scene.Capture(m_ImageIndex);
   bool bDone2 = this->CaptureDepthAndMasks(IgnoredActors);

   // Update the counter
   m_ImageIndex++;

   return bDone1 and bDone2;
}


bool FScreenshot::Save(const FString& Directory, TArray<FString>& OutActorsMasks)
{
   // Save the captured images
   bool bScene = m_Scene.Save(FPaths::Combine(Directory, FString("scene")));
   bool bDepth = m_Depth.Save(FPaths::Combine(Directory, FString("depth")));
   bool bMasks = m_Masks.Save(FPaths::Combine(Directory, FString("masks")), OutActorsMasks);

   bool bDone = bScene and bDepth and bMasks;
   if (not bDone)
   {
      UE_LOG(LogTemp, Error, TEXT("Failed to save captured images"));
   }
   return bDone;
}


bool FScreenshot::IsActorInFrame(const AActor* Actor, const uint32& ImageIndex)
{
   if (ImageIndex >= m_ImageIndex)
   {
      return false;
   }

   return m_Masks.IsActorInFrame(Actor, ImageIndex);
}


bool FScreenshot::IsActorInLastFrame(const AActor* Target, const TArray<AActor*>& IgnoredActors)
{
   RayTracer Tracer(m_OriginActor, IgnoredActors);
   FHitResult HitResult;
   for(uint32 y = 0; y < m_Size.Y; ++y)
   {
      for(uint32 x = 0; x < m_Size.X; ++x)
      {
         if(Tracer.Trace(HitResult, x, y))
         {
            if(HitResult.GetActor() == Target)
            {
               return true;
            }
         }
      }
   }

   return false;
}


bool FScreenshot::CaptureDepthAndMasks(const TArray<AActor*>& IgnoredActors)
{
   RayTracer Tracer(m_OriginActor, IgnoredActors);
   FHitResult HitResult;
   bool bHitDetected = false;

   for(uint32 y = 0; y < m_Size.Y; ++y)
   {
      for(uint32 x = 0; x < m_Size.X; ++x)
      {
         if(Tracer.Trace(HitResult, x, y))
         {
            bHitDetected = true;
            m_Depth.Capture(HitResult, m_ImageIndex, y * m_Size.X + x);
            m_Masks.Capture(HitResult, m_ImageIndex, x, y);
         }
      }
   }

   if(not bHitDetected)
   {
      UE_LOG(LogTemp, Error, TEXT("No hit detected during raytracing"));
   }

   return bHitDetected;
}
