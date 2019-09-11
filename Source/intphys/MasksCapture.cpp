#include "MasksCapture.h"
#include "Utils.h"


MasksCapture::MasksCapture(const FIntVector& Size, const int32& Seed)
   : m_Size(Size), m_Random(Seed)
{
   Reset(true);
}


MasksCapture::~MasksCapture()
{}


void MasksCapture::Reset(bool DeleteActors)
{
   // fill the images buffer with 0
   m_Buffer.Init(png::image<png::gray_pixel>(m_Size.X, m_Size.Y), m_Size.Z);

   if(DeleteActors)
   {
      m_ActorsMap.Init(TBidirMap<FString, png::gray_pixel>(), m_Size.Z);
   }
}


FString MasksCapture::GetActorName(const AActor* Actor)
{
   FString ActorName = Actor->GetName();
   if(ActorName.Contains(FString(TEXT("Wall"))))
   {
      ActorName = FString(TEXT("Walls"));
   }
   else if(ActorName.Contains(FString(TEXT("AxisCylinder"))))
   {
      ActorName = FString(TEXT("AxisCylinders"));
   }
   else if(ActorName.Contains(FString(TEXT("Pill"))))
   {
      ActorName = FString(TEXT("Pills"));
   }
   return ActorName;
}


bool MasksCapture::Capture(
   const FHitResult& Hit, const uint32& FrameIndex, const uint32& X, const uint32& Y)
{
   return CaptureActor(GetActorName(Hit.GetActor()), FrameIndex, X, Y);
}


bool MasksCapture::CaptureSky(const uint32& FrameIndex, const uint32& X, const uint32& Y)
{
   return CaptureActor(FString(TEXT("Sky")), FrameIndex, X, Y);
}


bool MasksCapture::CaptureActor(const FString& Actor, const uint32& FrameIndex, const uint32& X, const uint32& Y)
{
   // assign a gray level for this actor in that frame
   TBidirMap<FString, png::gray_pixel>& FrameActorsMap = m_ActorsMap[FrameIndex];
   png::gray_pixel GrayLevel;

   if(FrameActorsMap.ContainsKey(Actor))
   {
      // the actor already has an indexed gray level, just pick it
      GrayLevel = FrameActorsMap.GetValue(Actor);
   }
   else
   {
      // the actor is not yet registered for this frame, make sure we have room to
      // store it and pick a random unique gray level
      if(FrameActorsMap.Num() >= 256)
      {
         UE_LOG(LogTemp, Error, TEXT("Too many actors: %d >= 256"), m_ActorsMap.Num());
         return false;
      }

      // TODO very inefficient when the number of actors is large (but for
      // intphys we have max 10 actors per frame)
      GrayLevel = m_Random.RandRange(0, 255);
      while(FrameActorsMap.ContainsValue(GrayLevel))
      {
         GrayLevel = m_Random.RandRange(0, 255);
      }
      FrameActorsMap.Add(Actor, GrayLevel);
   }

   // finally fill the buffer with the right gray level
   m_Buffer[FrameIndex][Y][X] = GrayLevel;

   return true;
}


bool MasksCapture::Save(const FString& Directory, TArray<FString>& OutActorsMasks)
{
   if(not Utils::VerifyOrCreateDirectory(Directory))
   {
      return false;
   }

   // clear the output masks array
   OutActorsMasks.Empty();

   for(uint32 z = 0; z < m_Size.Z; ++z)
   {
      // write the PNG image
      FString Filename = Utils::BuildFilename(Directory, "masks", z, m_Size.Z);
      m_Buffer[z].write(TCHAR_TO_UTF8(*Filename));

      // append the actors masks for that frame
      TArray<FString> Masks;
      for(auto It = m_ActorsMap[z].CreateConstIterator(); It; ++It)
      {
         Masks.Add(
            FString::FromInt(z + 1) + FString(TEXT("__"))
            + It.Key() + FString(TEXT("__"))
            + FString::FromInt(It.Value()));
      }
      Masks.Sort();
      OutActorsMasks.Append(Masks);
   }

   return true;
}


bool MasksCapture::IsActorInFrame(const AActor* Actor, const uint32& FrameIndex) const
{
   return m_ActorsMap[FrameIndex].ContainsKey(GetActorName(Actor));
}
