// Fill out your copyright notice in the Description page of Project Settings.


#include "Exit.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMisc.h"


void UExit::ExitEngine(bool force)
{
   FGenericPlatformMisc::RequestExit(force);
}
