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
