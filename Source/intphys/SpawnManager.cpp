// Fill out your copyright notice in the Description page of Project Settings.


#include "SpawnManager.h"

AActor* USpawnManager::Spawn(UWorld* World, UClass* Class, const FTransform& Transform)
{
   FActorSpawnParameters SpawnParameters;
   SpawnParameters.SpawnCollisionHandlingOverride =
      ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
   return World->SpawnActor(Class, &Transform, SpawnParameters);
}
