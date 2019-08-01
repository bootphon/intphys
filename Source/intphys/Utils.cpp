#include "Utils.h"

#include "Runtime/Core/Public/HAL/PlatformFilemanager.h"


FString Utils::ZeroPadding(const uint32& Index, const uint32& MaxIndex)
{
   FString SIndex = FString::FromInt(Index);
   FString SMax = FString::FromInt(MaxIndex);

   return FString::ChrN(SMax.Len() - SIndex.Len(), '0') + SIndex;
}


FString Utils::BuildFilename(
   const FString& Directory, const FString& Prefix,
   const uint32& Index, const uint32& MaxIndex)
{
   FString FileIndex = Utils::ZeroPadding(Index + 1, MaxIndex);
   return FPaths::Combine(
      Directory,
      FString::Printf(TEXT("%s_%s.png"), *Prefix, *FileIndex));
}


bool Utils::VerifyOrCreateDirectory(const FString& Directory)
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
