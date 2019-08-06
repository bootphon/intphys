// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Exit.generated.h"

/**
 * Exit the UE Engine from Python code
 */
UCLASS()
class INTPHYS_API UExit : public UBlueprintFunctionLibrary
{
   GENERATED_BODY()

public:
   UFUNCTION(BlueprintCallable, Category="IntPhys")
   static void ExitEngine(bool force);
};
