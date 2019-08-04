#include "RayTracer.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"


RayTracer::RayTracer(
   UWorld* World,
   const TArray<AActor*>& IgnoredActors,
   const int32& PlayerIndex,
   const float& MaxDistance)
   : m_World(World),
     m_CollisionQueryParams("ClickableTrace", false),
     m_PlayerController(UGameplayStatics::GetPlayerController(World, PlayerIndex)),
     m_MaxDistance(MaxDistance)
{
   // register the actors to ignore during ray tracing
   for(const AActor* Actor : IgnoredActors)
   {
      m_CollisionQueryParams.AddIgnoredActor(Actor);
   }
}


RayTracer::~RayTracer()
{}


bool RayTracer::Trace(FHitResult& OutHit, const FVector2D& PixelCoordinates) const
{
   FVector RayOrigin, RayDirection;
   UGameplayStatics::DeprojectScreenToWorld(
      m_PlayerController,
      PixelCoordinates,
      RayOrigin,
      RayDirection);

   return m_World->LineTraceSingleByChannel(
      OutHit,
      RayOrigin,
      RayOrigin + RayDirection * m_MaxDistance,
      ECollisionChannel::ECC_Visibility,
      m_CollisionQueryParams);
}
