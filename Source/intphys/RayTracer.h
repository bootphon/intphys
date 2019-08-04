#pragma once

#include "CoreMinimal.h"


/**
 * Trace rays from a player point of view (i.e. a camera) an retrieve
 * information on the first visible actor encountered on the ray trajectory.
 */
class RayTracer
{
public:
   /**
    * @param World
    *     The world in witch to send the rays. From any spawned Actor, get a
    *     pointer to it's containing world with Actor->GetWorld().
    *
    * @param IgnoredActors
    *     An array of actors being ignored on the ray trajectory. Do not ignore any
    *     actor by default.
    *
    * @param PlayerIndex
    *     The index of the player controller to consider for ray tracing. Default
    *     to the first player (may be the only one).
    *
    * @param MaxDistance
    *     The maximal distance done by a ray.
    */
   RayTracer(
      UWorld* World,
      const TArray<AActor*>& IgnoredActors = TArray<AActor*>(),
      const int32& PlayerIndex = 0,
      const float& MaxDistance = 1000000.f);

   ~RayTracer();

   /**
    * Send a ray from the given screen pixel
    *
    * @param [output] OutHit
    *     Store information on the detected hit
    *
    * @param PixelCoordinates
    *     The screen location from where to send the ray
    *
    * @return True if a hit occured, false otherwise
    */
   bool Trace(FHitResult& OutHit, const FVector2D& PixelCoordinates) const;

private:
   UWorld* m_World;

   FCollisionQueryParams m_CollisionQueryParams;

   APlayerController* m_PlayerController;

   float m_MaxDistance;
};
