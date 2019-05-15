// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"


class FScreenshot
{
public:
    FScreenshot(const FIntVector& Size, AActor* OriginActor, bool Verbose = false);

    ~FScreenshot();

    void SetOriginActor(AActor* Actor);

    void SetActors(TArray<AActor*>& Actors);

    bool Capture(const TArray<AActor*>& IgnoredActors);

    bool Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap);

    void Reset(bool delete_actors);

    bool IsActorInFrame(const AActor* Actor, const uint FrameIndex);

    bool IsActorInLastFrame(const AActor* Actor, const TArray<AActor*>& IgnoredActors);

private:
    // Types of the captured images (they are all saved after a
    // conversion to TArray<uint8>)
    typedef TArray<FColor> FImageScene;
    typedef TArray<float> FImageDepth;
    typedef TArray<uint8> FImageMasks;

    // A triplet (width, height, nimages) of captured images
    FIntVector m_Size;

    // The actor giving the point of view for capture
    AActor* m_OriginActor;

    // Output some log messages when true
    bool m_Verbose;

    // Index of the current image (next to be captured)
    uint m_ImageIndex;

    // World and scene view for depth and mask capture
    UWorld* m_World;
    FSceneView* m_SceneView;

    // Buffers used to store the captured images
    TArray<FImageScene> m_Scene;
    TArray<FImageDepth> m_Depth;
    TArray<FImageMasks> m_Masks;
    TArray<TMap<uint8, uint64>> m_Masks2;

    // Buffers used in WritePng
    TArray<FColor> m_WriteBuffer;
    TArray<uint8> m_CompressedWriteBuffer;

    // Map the actors names to int ids
    TSet<FString> m_ActorsSet;
    TMap<FString, uint8> m_ActorsMap;

    // Take a screenshot of the scene and push it in memory
    bool CaptureScene();

    // Take the scene's depth field and object masking, push them to memory
    bool CaptureDepthAndMasks(const TArray<AActor*>& IgnoredActors);

    // Save all the scene images to disk
    bool SaveScene(const FString& Directory);

    // Save all the depth images to disk
    bool SaveDepth(const FString& Directory, float& OutMaxDepth);

    // Save all the masks images to disk
    bool SaveMasks(const FString& Directory, TMap<FString, uint8>& OutMasksMap);

    // Write an image as a PNG file in RGBA format. The alpha channel
    // of the image is forced to 255.
    bool WritePng(const TArray<FColor>& Bitmap, const FString& Filename);

    // Prefix the PNG filenames with zeros : 13 -> "0013"
    FString ZeroPadding(uint Index) const;
};
