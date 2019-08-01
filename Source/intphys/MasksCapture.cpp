#include "MasksCapture.h"
#include "Utils.h"

#include <algorithm>


MasksCapture::MasksCapture(const FIntVector& Size)
   : m_Size(Size)
{
   Reset(false);
}


MasksCapture::~MasksCapture()
{}


void MasksCapture::Reset(bool DeleteActors)
{
   m_Buffer.Init(png::image<png::gray_pixel>(m_Size.X, m_Size.Y), m_Size.Z);

   // delete actors only if it's last run
   if(DeleteActors)
   {
      m_ActorsSet.Empty();
   }
   m_ActorsMap.Empty();
}


void MasksCapture::SetActors(const TArray<AActor*>& Actors)
{
   for(AActor* Actor : Actors)
   {
      if(Actor->GetName().Contains(FString(TEXT("Wall")))
         and not m_ActorsSet.Contains(TEXT("Walls")))
      {
         m_ActorsSet.Add(FString(TEXT("Walls")));
      }
      else if(Actor->GetName().Contains(FString(TEXT("AxisCylinder")))
              and not m_ActorsSet.Contains(TEXT("AxisCylinders")))
      {
         m_ActorsSet.Add(FString(TEXT("AxisCylinders")));
      }
      else
      {
         m_ActorsSet.Add(Actor->GetName());
      }
   }
}

bool MasksCapture::Capture(
   const FHitResult& Hit, const uint32& ImageIndex, const uint32& X, const uint32& Y)
{
   // retrieve the actor name from the hit
   FString ActorName = Hit.GetActor()->GetName();
   if(ActorName.Contains(FString(TEXT("Wall"))))
   {
      ActorName = FString(TEXT("Walls"));
   }
   else if(ActorName.Contains(FString(TEXT("AxisCylinder"))))
   {
      ActorName = FString(TEXT("AxisCylinders"));
   }

   // retrieve the actor index from its name
   int8 ActorIndex = -1;
   ActorIndex = static_cast<uint8>(m_ActorsSet.Add(ActorName).AsInteger() + 1);
   if(ActorIndex <= 0)
   {
      UE_LOG(LogTemp, Warning, TEXT("Unknown actor %s"), *ActorName);
   }

   // update the name -> index mapping
   m_ActorsMap.Add(ActorName, ActorIndex);

   // capture the actor for the current pixel
   m_Buffer[ImageIndex][Y][X] = ActorIndex;

   return true;
}


bool MasksCapture::Save(const FString& Directory, TArray<FString>& OutActorsMasks)
{
   if(not Utils::VerifyOrCreateDirectory(Directory))
   {
      UE_LOG(LogTemp, Error, TEXT("Cannot create dircetory %s"), *Directory);
      return false;
   }

   // clear the output masks array
   OutActorsMasks.Empty();

   // // build the (actors name -> gray level) and (actor id -> gray level)
   // // mappings
   // OutActorsMasks.Empty(m_ActorsSet.Num() + 1);
   // OutActorsMasks.Add(FString(TEXT("Sky")), 0);
   // for(const auto& Elem : m_ActorsMap)
   // {
   //    OutActorsMasks.Add(Elem.Key, Elem.Value * 255.0 / m_ActorsSet.Num());
   // }

   for(uint32 z = 0; z < m_Size.Z; ++z)
   {
      FString Filename = Utils::BuildFilename(Directory, "masks", z, m_Size.Z);
      png::image<png::gray_pixel>& Image = m_Buffer[z];

      // normalize masks from [0, nactors-1] to [0, 255]
      for (uint32 j = 0; j < m_Size.Y; ++j)
      {
         for (uint32 i = 0; i < m_Size.X; ++i)
         {
            Image[j][i] *= (255.0 / m_ActorsSet.Num());
         }
      }

      // write the PNG image
      Image.write(TCHAR_TO_UTF8(*Filename));
   }

   return true;
}


bool MasksCapture::IsActorInFrame(const AActor* Actor, const uint32& ImageIndex)
{
   int8 ActorIndex = -1;
   ActorIndex = static_cast<uint8>(m_ActorsSet.Add(Actor->GetName()).AsInteger() + 1);
   if (ActorIndex <= 0)
   {
      UE_LOG(LogTemp, Warning, TEXT("Unknown actor %s"), *Actor->GetName());
      return false;
   }

   // look for ActorIndex in the masks image
   for(uint32 i = 0; i < m_Buffer[ImageIndex].get_height(); ++i)
   {
      // Row is a std::vector<png::gray_pixel>
      const auto& Row = m_Buffer[ImageIndex].get_row(i);
      if(Row.end() != std::find(Row.begin(), Row.end(), ActorIndex))
      {
         return true;
      }
   }

   return false;
}
