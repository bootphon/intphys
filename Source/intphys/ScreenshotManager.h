// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Screenshot.h"
#include "ScreenshotManager.generated.h"



/**
 * Exposes functions to Python for taking and saving screenshots of the scene.
 *
 * The ScreenshotManager captures screenshots of a scene from a given point of
 * view, as well as depth field and object masks. It also provides methods to
 * check if a given object is visible in the scene.
 *
 * Because blueprint function library does not wrap classes, the screenshot
 * manager holds a static instance of FScreenshot, it must be setup with a call
 * to Initialize(...) before calling any other function.
 */
UCLASS()
class INTPHYS_API UScreenshotManager : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

private:
    static TSharedPtr<FScreenshot> Screenshot;

public:
    /**
     * Initializes a screenshot manager
     *
     * @param Width - width of the captured frames (in number of pixels)
     *
     * @param Height - height of the captured frames (in number of pixels)
     *
     * @param NumFrames - number of frames to capture to make a complete scene
     *
     * @param OriginActor - the actor from which point of view to capture the
     * scene (usually a camera).
     *
     * @param RandomSeed - the seed to initialize a random number generator
     *
     * @param Verbose - when true, display log messages. When false, only
     * warnings and errors are reported.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Initialize(
        int Width, int Height, int NumFrames,
        AActor* OriginActor,
        int32 RandomSeed,
        bool Verbose = false);

    /**
     * Takes a screenshot of the scene, the depth field and the objects masks
     *
     * @param IgnoredActors - Actors to ignore during the capture (they will be
     * invisible). Works for depth and masks but has no effect on scene
     * screenshot.
     *
     * @return true if the capture succeeded, false on error.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Capture(const TArray<AActor*>& IgnoredActors);

    /**
     * Saves the captured images to disk.
     *
     * Creates 3 subdirectories "scene", "depth" and "masks" in Directory and
     * writes the captured images as PNG files in it.
     *
     * @param Directory - the diectory where to write the captured images.
     *
     * @param [output] OutActorsMasks - the gray level corresponding to each
     * actor in the scene for each frame. A more natural format would be
     * TArray<TMap<Actor, GrayLevel>> but blueprint functions do not support
     * nested containers. This array is parsed in Python side to populate the
     * status.json file.
     *
     * @return true on success, false otherwise
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool Save(const FString& Directory, TArray<FString>& OutActorsMasks);

    /**
     * Clears the buffers of captured images
     *
     * @param ResetMasks - when true reset the actors masks index (a mapping of
     * each actor to a unique gray level). To use when Reset is called on the
     * last run of a scene, or when restarting a new scene.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void Reset(bool ResetMasks);

    /**
     * Set the actor from where the screenshots are captured.
     *
     * This usually a camera.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static void SetOriginActor(AActor* Actor);

    /**
     * Returns true if the Actor is visible in the captured frame indexed by
     * FrameIndex.
     *
     * This is VERY FAST, just a containment test in a map.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool IsActorInFrame(AActor* Actor, int FrameIndex);

    /**
     * Returns true if the Actor is visible in the scene.
     *
     * This is VERY SLOW, throw a ray trace per pixel until the actor is fount.
     */
    UFUNCTION(BlueprintCallable, Category="IntPhys")
    static bool IsActorVisible(AActor* Actor, const TArray<AActor*>& IgnoredActors);
};
