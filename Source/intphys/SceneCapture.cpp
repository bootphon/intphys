#include "SceneCapture.h"
#include "Utils.h"


SceneCapture::SceneCapture(const FIntVector& Size)
   : m_Size(Size), m_Buffer(), m_Png(Size.X, Size.Y)
{
   m_Buffer.SetNum(m_Size.Z);
   Reset();
}


SceneCapture::~SceneCapture()
{}


void SceneCapture::Reset()
{
   for(TArray<FColor>& Image : m_Buffer)
   {
      Image.Init(FColor(), m_Size.X * m_Size.Y);
   }
}


bool SceneCapture::Capture(const uint32& Index)
{
   bool bDone = false;
   TSharedPtr<SWindow> WindowPtr = GEngine->GameViewport->GetWindow();
   if (WindowPtr.IsValid() && FSlateApplication::IsInitialized())
   {
      FIntVector OutSize;
      bDone = FSlateApplication::Get().TakeScreenshot(
         WindowPtr.ToSharedRef(), m_Buffer[Index], OutSize);
   }

   return bDone;
}


bool SceneCapture::Save(const FString& Directory)
{
   if(not Utils::VerifyOrCreateDirectory(Directory))
   {
      return false;
   }

   for (uint32 z = 0; z < m_Size.Z; ++z)
   {
      FString Filename = Utils::BuildFilename(Directory, "scene", z, m_Size.Z);

      const TArray<FColor>& Image = m_Buffer[z];

      uint32 Index = 0;
      for(uint32 j = 0; j < m_Size.Y; ++j)
      {
         for(uint32 i = 0; i < m_Size.X; ++i)
         {
            const FColor& Pixel = Image[Index];
            m_Png[j][i] = png::rgb_pixel(Pixel.R, Pixel.G, Pixel.B);
            ++Index;
         }
      }

      // write the image
      m_Png.write(TCHAR_TO_UTF8(*Filename));
   }

   return true;
}
