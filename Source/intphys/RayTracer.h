#pragma once

#include "CoreMinimal.h"


class RayTracer
{
public:
   RayTracer(const AActor* Origin, const TArray<AActor*>& IgnoredActors);

   ~RayTracer();

   bool Trace(FHitResult& OutHit, const uint32& X, const uint32& Y) const;

private:
   FCollisionQueryParams m_CollisionQueryParams;
   UWorld* m_World;
   APlayerController* m_PlayerController;
};
