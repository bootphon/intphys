// Fill out your copyright notice in the Description page of Project Settings.


#include "SpawnManager.h"

AActor* USpawnManager::Spawn(UWorld* World, UClass* Class, const FTransform& Transform)
{
   FActorSpawnParameters SpawnParameters;
   SpawnParameters.SpawnCollisionHandlingOverride =
      ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
   return World->SpawnActor(Class, &Transform, SpawnParameters);
}


bool USpawnManager::IsOverlapping(const AActor* Actor, const AActor* Other)
{
   if(Actor == Other)
   {
      return false;
   }

   FBox ActorBox = Actor->GetComponentsBoundingBox(true);
   FBox OtherBox = Other->GetComponentsBoundingBox(true);
   return ActorBox.Intersect(OtherBox);
}


bool USpawnManager::Intersect(
   const FVector& Min, const FVector& Max, const FTransform& Transform,
   const FVector& OtherMin, const FVector& OtherMax, const FTransform& OtherTransform)
{
   FBox Box = FBox(Min, Max).TransformBy(Transform);
   FBox OtherBox = FBox(OtherMin, OtherMax).TransformBy(OtherTransform);
   return Box.Intersect(OtherBox);
}
