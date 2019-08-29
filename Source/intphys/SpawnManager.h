// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SpawnManager.generated.h"

/**
 *
 */
UCLASS()
class INTPHYS_API USpawnManager : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

  UFUNCTION(BlueprintCallable, Category="IntPhys")
  static AActor* Spawn(UWorld* World, UClass* Class, const FTransform& Transform);
};
