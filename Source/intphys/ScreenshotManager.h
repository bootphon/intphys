// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Screenshot.h"
#include "ScreenshotManager.generated.h"


/**
 * Exposes functions to Python for taking and saving screenshots.
 *
 * This class exposes a Screenshot singleton instance. The
 * static methods delegates operations to that instance.
 */
UCLASS()
class INTPHYS_API UScreenshotManager : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

private:
    static TSharedPtr<FScreenshot> Screenshot;

public:
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Initialize(
        int Width, int Height, int NImages,
        float MaxDepth,
        AActor* OriginActor,
        bool Verbose = false);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Capture(const TArray<AActor*>& IgnoredActors);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Save(const FString& Directory, TArray<FString>& OutActorsMasks);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void Reset(bool delete_actors);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void SetOriginActor(AActor* Actor);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void SetActors(TArray<AActor*>& Actors);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool IsActorInFrame(AActor* Actor, int FrameIndex);

    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool IsActorInLastFrame(AActor* Actor, const TArray<AActor*>& IgnoredActors);
};
