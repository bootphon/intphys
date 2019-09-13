// Fill out your copyright notice in the Description page of Project Settings.


#include "Exit.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMisc.h"


void UExit::ExitEngine(bool force)
{
   FGenericPlatformMisc::RequestExit(force);
}


bool UExit::Intersect(AActor* Actor, AActor* Other)
{
   FBox Box = Actor->GetComponentsBoundingBox(false);
   FBox OtherBox = Other->GetComponentsBoundingBox(false);
   if(Box.Intersect(OtherBox))
   {
      return true;
   }
   return false;
}
