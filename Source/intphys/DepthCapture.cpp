#include "DepthCapture.h"
#include "Utils.h"


// 65.535 m is the maximal distance that can be encoded on 16 bits with a
// resolution of 1mm per gray level)
const float DepthCapture::MaxDepth = 6553.5;


DepthCapture::DepthCapture(const FIntVector& Size)
   : m_Size(Size)
{
   m_Buffer.Init(png::image<png::gray_pixel_16>(m_Size.X, m_Size.Y), m_Size.Z);
}


DepthCapture::~DepthCapture()
{}


void DepthCapture::Reset()
{
   // fill the images buffer with 0
   for(uint32 z = 0; z < m_Size.Z; ++z)
   {
      for(uint32 y = 0; y < m_Size.Y; ++y)
      {
         for(uint32 x = 0; x < m_Size.X; ++x)
         {
            m_Buffer[z][y][x] = 0;
         }
      }
   }
}


void DepthCapture::CaptureInit(AActor* OriginActor)
{
   m_OriginLocation = OriginActor->GetActorLocation();
   m_OriginRotation = FRotationMatrix(OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
   m_OriginRotation.Normalize();
}

bool DepthCapture::Capture(
   const FHitResult& Hit, const uint32& ImageIndex, const uint32& X, const uint32& Y)
{
   if(ImageIndex >= m_Size.Z)
   {
      UE_LOG(LogTemp, Error, TEXT("Depth capture failed: too much images captured"));
      return false;
   }

   if(X >= m_Size.X or Y >= m_Size.Y)
   {
      UE_LOG(LogTemp, Error, TEXT("Depth capture failed: too much pixels captured"));
      return false;
   }

   float Depth = FVector::DotProduct(Hit.Location - m_OriginLocation, m_OriginRotation);
   if(Depth > MaxDepth)
   {
      UE_LOG(
         LogTemp, Warning,
         TEXT("Max depth in scene exceed expected max depth (capping): %f > %f"),
         Depth, MaxDepth);
      Depth = MaxDepth;
   }
   else if(Depth <= 0.0)
   {
      Depth = MaxDepth;
   }

   m_Buffer[ImageIndex][Y][X] = static_cast<png::gray_pixel_16>(
      65535 * (1 - Depth / MaxDepth));

   return true;
}


bool DepthCapture::Save(const FString& Directory)
{
   if(not Utils::VerifyOrCreateDirectory(Directory))
   {
      return false;
   }

   for(uint32 z = 0; z < m_Size.Z; ++z)
   {
      FString Filename = Utils::BuildFilename(Directory, "depth", z, m_Size.Z);
      m_Buffer[z].write(TCHAR_TO_UTF8(*Filename));
   }

   return true;
}
