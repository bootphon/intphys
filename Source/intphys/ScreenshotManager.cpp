#include "ScreenshotManager.h"


TSharedPtr<FScreenshot> UScreenshotManager::Screenshot = nullptr;


bool UScreenshotManager::Initialize(
    int Width, int Height, int NumFrames,
    AActor* OriginActor,
    float MaxDepth,
    int32 RandomSeed,
    bool Verbose)
{
   FIntVector Size(Width, Height, NumFrames);
   Screenshot = TSharedPtr<FScreenshot>(
      new FScreenshot(Size, OriginActor,  MaxDepth, RandomSeed, Verbose));
   return true;
}


bool UScreenshotManager::Capture(const TArray<AActor*>& IgnoredActors)
{
    return Screenshot->Capture(IgnoredActors);
}

bool UScreenshotManager::Save(const FString& Directory, TArray<FString>& OutActorsMasks)
{
    return Screenshot->Save(Directory, OutActorsMasks);
}


void UScreenshotManager::Reset(bool DeleteActors)
{
    Screenshot->Reset(DeleteActors);
}


void UScreenshotManager::SetOriginActor(AActor* Actor)
{
    Screenshot->SetOriginActor(Actor);
}


bool UScreenshotManager::IsActorInFrame(AActor* Actor, int FrameIndex)
{
    return Screenshot->IsActorInFrame(Actor, static_cast<uint>(FrameIndex));
}


bool UScreenshotManager::IsActorVisible(AActor* Actor, const TArray<AActor*>& IgnoredActors)
{
    return Screenshot->IsActorVisible(Actor, IgnoredActors);
}
