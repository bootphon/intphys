#pragma once

#include "CoreMinimal.h"


class Utils
{
public:
   // Creates a directory if not already existing, returns false on failure
   static bool VerifyOrCreateDirectory(const FString& Directory);

   // Build a filename in the form "Directory/Basename_Index.png"
   static FString BuildFilename(
      const FString& Directory, const FString& Prefix,
      const uint32& Index, const uint32& MaxIndex);

private:
   // Converts an integer to a string prefixed with zeros : (13, 1000) -> "0013"
   static FString ZeroPadding(const uint32& Index, const uint32& MaxIndex);
};
