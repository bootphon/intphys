#include "DepthCapture.h"
#include "Utils.h"


DepthCapture::DepthCapture(const FIntVector& Size, const float& MaxDepth)
   : m_Size(Size), m_NumPixels(Size.X * Size.Y),
     m_MaxDepth(MaxDepth), m_CurrentMaxDepth(0.0), m_Png(Size.X, Size.Y)
{
   m_Buffer.SetNum(m_Size.Z);
   Reset();
}


DepthCapture::~DepthCapture()
{}


void DepthCapture::Reset()
{
   m_CurrentMaxDepth = 0.0;

   for(TArray<float>& Image : m_Buffer)
   {
      Image.Init(0.0, m_NumPixels);
   }
}


void DepthCapture::CaptureInit(AActor* OriginActor)
{
   m_OriginLocation = OriginActor->GetActorLocation();
   m_OriginRotation = FRotationMatrix(OriginActor->GetActorRotation()).GetScaledAxis(EAxis::X);
   m_OriginRotation.Normalize();
}

bool DepthCapture::Capture(
   const FHitResult& Hit, const uint32& ImageIndex, const uint32& PixelIndex)
{
   if(ImageIndex >= m_Size.Z)
   {
      UE_LOG(LogTemp, Error, TEXT("Depth capture failed: too much images captured"));
      return false;
   }

   if(PixelIndex >= m_NumPixels)
   {
      UE_LOG(LogTemp, Error, TEXT("Depth capture failed: too much pixels captured"));
      return false;
   }

   float Depth = FVector::DotProduct(Hit.Location - m_OriginLocation, m_OriginRotation);
   m_CurrentMaxDepth = FMath::Max(m_CurrentMaxDepth, Depth);
   m_Buffer[ImageIndex][PixelIndex] = Depth;

   return true;
}


bool DepthCapture::Save(const FString& Directory)
{
   if(not Utils::VerifyOrCreateDirectory(Directory))
   {
      return false;
   }

   if(m_CurrentMaxDepth > m_MaxDepth)
   {
      UE_LOG(
         LogTemp, Warning,
         TEXT("Max depth in scene exceed expected max depth: %f > %f"),
         m_CurrentMaxDepth, m_MaxDepth);
   }

   for(uint32 z = 0; z < m_Size.Z; ++z)
   {
      for(uint32 y = 0; y < m_Size.Y; ++y)
      {
         const uint32 Y = y * m_Size.X;
         for(uint32 x = 0; x < m_Size.X; ++x)
         {
            // depth normalization, depth field is from white (close) to
            // black (far). A depth at 0 is assumed to be maximal depth.
            float Depth = m_Buffer[z][Y + x];
            if(Depth <= 0.0 or Depth > m_MaxDepth)
            {
               Depth = m_MaxDepth;
            }

            m_Png[y][x] = static_cast<png::gray_pixel>(
               255.f - 255.f * Depth / m_MaxDepth);
         }
      }

      FString Filename = Utils::BuildFilename(Directory, "depth", z, m_Size.Z);
      m_Png.write(TCHAR_TO_UTF8(*Filename));
   }

   return true;
}
