#include "Screenshot.h"

#include "ImageUtils.h"
#include "Runtime/Core/Public/HAL/PlatformFilemanager.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMath.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"

THIRD_PARTY_INCLUDES_START
#include "ThirdParty/zlib/zlib-1.2.5/Inc/zlib.h"
#include "ThirdParty/libPNG/libPNG-1.5.27/png.h"
#include <png++/png.hpp>
THIRD_PARTY_INCLUDES_END

#include <fstream>


static FORCEINLINE bool VerifyOrCreateDirectory(const FString& Directory)
{
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();

    if (not PlatformFile.DirectoryExists(*Directory))
    {
        PlatformFile.CreateDirectoryTree(*Directory);

        if (not PlatformFile.DirectoryExists(*Directory))
        {
            return false;
        }
    }

    return true;
}


FScreenshot::FScreenshot(const FIntVector& Size, AActor* OriginActor, bool Verbose)
    : m_Size(Size), m_OriginActor(OriginActor), m_Verbose(Verbose), m_ImageIndex(0)
{
   const uint32 SizeXY = Size.X * Size.Y;
    // allocate memory for storing images
    m_Scene.SetNum(Size.Z);
    for (auto& Image : m_Scene)
        Image.SetNum(SizeXY);

    m_Masks.SetNum(Size.Z);
    for (auto& Image : m_Masks)
        Image.SetNum(SizeXY);
    m_Masks2.SetNum(Size.Z);

    m_Depth.SetNum(SizeXY * Size.Z);

    // zlib estimation of the maximum compressed size of depth data
    m_BinaryBuffer.SetNum(compressBound(m_Depth.Num() * m_Depth.GetTypeSize()));

    // To save pngs, will be resized on demand
    m_WriteBuffer.SetNum(SizeXY);
    m_PngBuffer.SetNum(SizeXY);
}


FScreenshot::~FScreenshot()
{}


void FScreenshot::SetActors(TArray<AActor*>& Actors)
{
    for (auto& actor : Actors)
    {
        if (actor->GetName().Contains(FString(TEXT("Wall"))) == true &&
            m_ActorsSet.Contains(TEXT("Walls")) == false)
        {
            m_ActorsSet.Add(FString(TEXT("Walls")));
        }
        else if (actor->GetName().Contains(FString(TEXT("AxisCylinder"))) == true &&
            m_ActorsSet.Contains(TEXT("AxisCylinders")) == false)
        {
          m_ActorsSet.Add(FString(TEXT("AxisCylinders")));
        }
        else
        {
            m_ActorsSet.Add(actor->GetName());
        }
    }
}


void FScreenshot::SetOriginActor(AActor* Actor)
{
    m_OriginActor = Actor;
}


void FScreenshot::Reset(bool delete_actors)
{
    m_ImageIndex = 0;
    // delete actors only if it's last run
    if (delete_actors)
        m_ActorsSet.Empty();
    m_ActorsMap.Empty();


    m_Depth.Init(0.0, m_Depth.Num());
    for (auto& Image : m_Scene)
      Image.Init(FColor(), Image.Num());
    for (auto& Image : m_Masks)
      Image.Init(0, Image.Num());
    for (auto& Image : m_Masks2)
      Image.Reset();
}


bool FScreenshot::Capture(const TArray<AActor*>& IgnoredActors)
{
    if (m_ImageIndex >= m_Size.Z)
    {
        UE_LOG(LogTemp, Error, TEXT("Screen capture failed: too much images captured"));
        return false;
    }

    bool bDone1 = FScreenshot::CaptureScene();
    bool bDone2 = FScreenshot::CaptureDepthAndMasks(IgnoredActors);

    // Update the counter
    m_ImageIndex++;

    return bDone1 and bDone2;
}


bool FScreenshot::Save(const FString& Directory, float& OutMaxDepth, TMap<FString, uint8>& OutActorsMap)
{
    // Create the subdirectories where to write the PNGs
    for (const auto& Name : {TEXT("scene"), TEXT("masks"), TEXT("depth")})
    {
        FString SubDirectory = FPaths::Combine(Directory, FString(Name));
        bool bDone = VerifyOrCreateDirectory(SubDirectory);
        if(not bDone)
          {
            UE_LOG(LogTemp, Error, TEXT("Failed to create directory %s"), *SubDirectory);
            return false;
          }
    }

    // Save the images
    bool bScene = SaveScene(FPaths::Combine(Directory, FString("scene")));
    bool bMasks = SaveMasks(FPaths::Combine(Directory, FString("masks")), OutActorsMap);
    bool bDepth = SaveDepth(FPaths::Combine(Directory, FString("depth")), OutMaxDepth);

    bool bDone = bScene and bMasks and bDepth;
    if (not bDone)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to save captured images"));
    }

    return bDone;
}


bool FScreenshot::IsActorInFrame(const AActor* Actor, const uint FrameIndex)
{
    if (FrameIndex >= m_ImageIndex)
    {
        UE_LOG(LogTemp, Warning, TEXT("%d and %d"), FrameIndex, m_ImageIndex);
     	return false;
    }
    int8 ActorIndex = -1;
    ActorIndex = static_cast<uint8>(m_ActorsSet.Add(Actor->GetName()).AsInteger() + 1);
    if (ActorIndex <= 0)
        UE_LOG(LogTemp, Warning, TEXT("Didn't found %s in actors array"), *Actor->GetName());

    // it is not really optimized, but anyway
    int max = 0;
    int target_nb = -1;
    for (int i = 0; i != m_Masks2.Num(); i++)
    {
        for (auto & elem : m_Masks2[i])
        {
            if (elem.Key == ActorIndex)
            {
              if (elem.Value > max)
                {
                  max = elem.Value;
                }
              if (i == FrameIndex)
                {
                  target_nb = elem.Value;
                }
            }
        }
    }

    return m_Masks[FrameIndex].Contains(ActorIndex);
}


bool FScreenshot::IsActorInLastFrame(const AActor* Target, const TArray<AActor*>& IgnoredActors)
{
    FCollisionQueryParams CollisionQueryParams("ClickableTrace", false);
    for (auto& Actor : IgnoredActors)
    {
        CollisionQueryParams.AddIgnoredActor(Actor);
    }

    // Intitialize world and player controler
    m_World = m_OriginActor->GetWorld();
    if (m_World == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Screenshot: World is null"));
        return false;
    }

    APlayerController* PlayerControler = UGameplayStatics::GetPlayerController(m_World, 0);
    if (PlayerControler == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Screenshot: PlayerControler is null"));
        return false;
    }

    // get the origin location and rotation for distance computation
    FVector OriginLoc = m_OriginActor->GetActorLocation();
    FVector OriginRot = FRotationMatrix(m_OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
    OriginRot.Normalize();

    // for each pixel of the view, cast a ray in the scene and get the
    // resulting hit actor and hit distance
    FHitResult HitResult;
    for (int y = 0; y < m_Size.Y; ++y)
    {
        for (int x = 0; x < m_Size.X; ++x)
        {
            FVector RayOrigin, RayDirection;
            UGameplayStatics::DeprojectScreenToWorld(
                PlayerControler, FVector2D(x, y), RayOrigin, RayDirection);

            bool bHit = m_World->LineTraceSingleByChannel(
                HitResult, RayOrigin, RayOrigin + RayDirection * 1000000.f,
                ECollisionChannel::ECC_Visibility, CollisionQueryParams);

            if(bHit)
            {
                uint PixelIndex = y * m_Size.X + x;
                if (HitResult.GetActor() == Target)
                    return true;
            }
        }
    }

    return false;
}


bool FScreenshot::CaptureScene()
{
    TSharedPtr<SWindow> WindowPtr = GEngine->GameViewport->GetWindow();
    if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
    {
        FIntVector OutSize;
        bool bDone = FSlateApplication::Get().TakeScreenshot(
            WindowPtr.ToSharedRef(), m_Scene[m_ImageIndex], OutSize);

        // Force no transparency
        if (bDone)
        {
            for (FColor& Pixel : m_Scene[m_ImageIndex])
            {
                Pixel.A = 255;
            }
        }

        return bDone;
    }
    else
    {
        return false;
    }
}


bool FScreenshot::CaptureDepthAndMasks(const TArray<AActor*>& IgnoredActors)
{
    FCollisionQueryParams CollisionQueryParams("ClickableTrace", false);
    for (auto& Actor : IgnoredActors)
    {
        CollisionQueryParams.AddIgnoredActor(Actor);
    }

    // Intitialize world and player controler
    m_World = m_OriginActor->GetWorld();
    if (m_World == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Screenshot: World is null"));
        return false;
    }

    APlayerController* PlayerControler = UGameplayStatics::GetPlayerController(m_World, 0);
    if (PlayerControler == NULL)
    {
        UE_LOG(LogTemp, Error, TEXT("Screenshot: PlayerControler is null"));
        return false;
    }

    // get the origin location and rotation for distance computation
    FVector OriginLoc = m_OriginActor->GetActorLocation();
    FVector OriginRot = FRotationMatrix(m_OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
    OriginRot.Normalize();

    // for each pixel of the view, cast a ray in the scene and get the
    // resulting hit actor and hit distance
    uint DepthIndex = m_ImageIndex * m_Size.X * m_Size.Y;
    FHitResult HitResult;
    bool bHitDetected = false;
    for (int y = 0; y < m_Size.Y; ++y)
    {
        for (int x = 0; x < m_Size.X; ++x)
        {
            FVector RayOrigin, RayDirection;
            UGameplayStatics::DeprojectScreenToWorld(
                PlayerControler, FVector2D(x, y), RayOrigin, RayDirection);

            bool bHit = m_World->LineTraceSingleByChannel(
                HitResult, RayOrigin, RayOrigin + RayDirection * 1000000.f,
                ECollisionChannel::ECC_Visibility, CollisionQueryParams);

            if(bHit)
            {
                bHitDetected = true;
                uint PixelIndex = y * m_Size.X + x;

                // compute depth
                float HitDistance = FVector::DotProduct(HitResult.Location - OriginLoc, OriginRot);
                m_Depth[DepthIndex + PixelIndex] = HitDistance;

                // compute mask
                FString ActorName = HitResult.GetActor()->GetName();
                if (ActorName.Contains(FString(TEXT("Wall"))) == true)
                    ActorName = FString(TEXT("Walls"));
                else if (ActorName.Contains(FString(TEXT("AxisCylinder"))) == true)
                    ActorName = FString(TEXT("AxisCylinders"));
                int8 ActorIndex = -1;
                ActorIndex = static_cast<uint8>(m_ActorsSet.Add(ActorName).AsInteger() + 1);
                if (ActorIndex <= 0)
                    UE_LOG(LogTemp, Warning, TEXT("Didn't found %s in actors array"), *ActorName);
                m_ActorsMap.Add(ActorName, ActorIndex);
                m_Masks[m_ImageIndex][PixelIndex] = ActorIndex;
                bool exists = false;
                for (auto &elem : m_Masks2[m_ImageIndex])
                {
                    if (elem.Key == ActorIndex)
                    {
                        exists = true;
                        elem.Value += 1;
                    }
                }
                if (exists == false)
                    m_Masks2[m_ImageIndex].Add(ActorIndex, 1);
            }
        }
    }

    if (not bHitDetected)
    {
        UE_LOG(LogTemp, Error, TEXT("Screenshot:DepthAndMask: No hit detected during raytracing"));
    }

    return bHitDetected;
}


bool FScreenshot::SaveScene(const FString& Directory)
{
    for (uint i = 0; i < m_Size.Z; ++i)
    {
        // build the filename
        FString FileIndex = FScreenshot::ZeroPadding(i+1);
        FString Filename = FPaths::Combine(
            Directory, FString::Printf(TEXT("scene_%s.png"), *FileIndex));

        // write the image
        bool bDone = FScreenshot::WritePng(m_Scene[i], Filename);
        if (not bDone)
        {
            return false;
        }
    }

    return true;
}


bool FScreenshot::SaveDepth(const FString& Directory, float& OutMaxDepth)
{
    // Extract the global max depth and send it to the Python level saver
    OutMaxDepth = FMath::Max(m_Depth);
    if (m_Verbose)
    {
        UE_LOG(LogTemp, Log, TEXT("Max depth is %f"), OutMaxDepth);
    }

    // save the depth images a single binary file containing raw depth as floats
    // (during prostprocessing, will be split into one image per frame and
    // normalized by the maximum depth of the whole dataset)

    // build the filename
    FString Filename = FPaths::Combine(Directory, FString("depth.bin"));
    if (not WriteBinary(m_Depth, Filename))
    {
       return false;
    }
    return true;
}


bool FScreenshot::SaveMasks(const FString& Directory, TMap<FString, uint8>& OutActorsMap)
{
    // build the (actors name -> gray level) and (actor id -> gray
    // level) mappings
    OutActorsMap.Empty(m_ActorsSet.Num() + 1);
    OutActorsMap.Add(FString(TEXT("Sky")), 0);
    for (const auto& Elem : m_ActorsMap)
    {
        OutActorsMap.Add(Elem.Key, Elem.Value * 255.0 / m_ActorsSet.Num());
    }

    if (m_Verbose)
    {
        FString MasksStr;
        for (auto& Elem : OutActorsMap)
        {
            MasksStr += FString::Printf(TEXT("(%s, %d) "), *Elem.Key, Elem.Value);
        }
        UE_LOG(LogTemp, Log, TEXT("Actors masks are %s"), *MasksStr);
    }

    for (uint i = 0; i < m_Size.Z; ++i)
    {
        // build the filename
        FString FileIndex = FScreenshot::ZeroPadding(i+1);
        FString Filename = FPaths::Combine(
            Directory, FString::Printf(TEXT("masks_%s.png"), *FileIndex));

        // normalize masks from [0, nactors-1] to [0, 255]
        FImageMasks& Image = m_Masks[i];
        for (uint j = 0; j < Image.Num(); ++j)
        {
            auto Color = Image[j] * 255.0 / m_ActorsSet.Num();
            m_WriteBuffer[j] = FColor(Color, Color, Color, 255);
        }

        // write the image
        bool bDone = FScreenshot::WritePng(m_WriteBuffer, Filename);
        if (not bDone)
        {
            return false;
        }
    }

    return true;
}


bool FScreenshot::WritePng(const TArray<FColor>& Bitmap, const FString& Filename)
{
    // Convert the raw pixels Bitmap to a PNG compressed array
    FImageUtils::CompressImageArray(m_Size.X, m_Size.Y, Bitmap, m_PngBuffer);

    // Write the PNG array to disk
    bool bDone = FFileHelper::SaveArrayToFile(m_PngBuffer, *Filename);

    if (not bDone)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to write %s"), *Filename);
    }

    return bDone;
}


bool FScreenshot::WriteBinary(const TArray<float>& Bitmap, const FString& Filename)
{
   // compress the data, get back the compressed size. Compression level from 0
   // (no compression) to 9 (highest compression rate), default is 6.
   unsigned long CompressedSize = m_BinaryBuffer.Num();
   int CompressionLevel = 9;
   int ret = compress2(
      (Bytef*)m_BinaryBuffer.GetData(), &CompressedSize,
      (Bytef*)Bitmap.GetData(), Bitmap.Num() * Bitmap.GetTypeSize(),
      CompressionLevel);
   if(ret != Z_OK)
   {
      UE_LOG(LogTemp, Error, TEXT("Failed to compress %s"), *Filename);
      return false;
   }

   // save it as a binary file (will be read as a std::vector<float> by the
   // postprocessor and then normalized and converted to a PNG file).
   std::ofstream DepthFile(
      std::string(TCHAR_TO_UTF8(*Filename)), std::ios::out | std::ofstream::binary);

   // write the total size of the uncompressed data (in number of floats) as a header
   const std::size_t Size = static_cast<std::size_t>(Bitmap.Num());
   DepthFile.write(reinterpret_cast<const char*>(&Size), sizeof(std::size_t));

   // write the compressed data
   DepthFile.write(reinterpret_cast<const char*>(m_BinaryBuffer.GetData()), CompressedSize);
   DepthFile.close();

   if(DepthFile.fail())
   {
      UE_LOG(LogTemp, Error, TEXT("Failed to write %s"), *Filename);
      return false;
   }

   return true;
}


FString FScreenshot::ZeroPadding(uint Index) const
{
    FString SIndex = FString::FromInt(Index);
    FString SMax = FString::FromInt(m_Size.Z);

    return FString::ChrN(SMax.Len() - SIndex.Len(), '0') + SIndex;
}
