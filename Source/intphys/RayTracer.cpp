#include "RayTracer.h"
#include "Runtime/Engine/Classes/Kismet/GameplayStatics.h"


RayTracer::RayTracer(const AActor* Origin, const TArray<AActor*>& IgnoredActors)
   : m_CollisionQueryParams("ClickableTrace", false),
     m_World(Origin->GetWorld()),
     m_PlayerController(UGameplayStatics::GetPlayerController(Origin->GetWorld(), 0))
{
   for(AActor* Actor : IgnoredActors)
   {
      m_CollisionQueryParams.AddIgnoredActor(Actor);
   }
}


RayTracer::~RayTracer()
{}


bool RayTracer::Trace(FHitResult& OutHit, const uint32& X, const uint32& Y) const
{
   FVector RayOrigin, RayDirection;
   UGameplayStatics::DeprojectScreenToWorld(
      m_PlayerController,
      FVector2D(X, Y),
      RayOrigin,
      RayDirection);

   return m_World->LineTraceSingleByChannel(
      OutHit,
      RayOrigin,
      RayOrigin + RayDirection * 1000000.f,
      ECollisionChannel::ECC_Visibility,
      m_CollisionQueryParams);
}
