// Fill out your copyright notice in the Description page of Project Settings.

#include "Friction.h"
#include "Runtime/Engine/Classes/PhysicalMaterials/PhysicalMaterial.h"
#include "Runtime/Core/Public/GenericPlatform/GenericPlatformMisc.h"
#if ENGINE_MINOR_VERSION >= 21
#include "Runtime/Engine/Public/Physics/PhysicsInterfacePhysX.h"
#endif

void UFriction::ExitEngine(bool force)
{
    FGenericPlatformMisc::RequestExit(force);
}

bool UpdatePhysicalMaterial(UPhysicalMaterial* PhysicalMaterial)
{
#if ENGINE_MINOR_VERSION < 21
    PhysicalMaterial->UpdatePhysXMaterial();
    return true;
#else
    // Interface changed after UE-4.20. This compile but have not been tested
    FPhysicsMaterialHandle PhysicalHandle = PhysicalMaterial->GetPhysicsMaterial();
    FPhysicsInterface_PhysX::UpdateMaterial(PhysicalHandle, PhysicalMaterial);
    return true;
#endif
}

bool UFriction::SetFriction(UMaterial* Material, float &Friction)
{
    UPhysicalMaterial *PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }
    PhysicalMaterial->Friction = Friction;
    return UpdatePhysicalMaterial(PhysicalMaterial);
}

bool UFriction::SetRestitution(UMaterial* Material, float &Restitution)
{
    UPhysicalMaterial* PhysicalMaterial = Material->GetPhysicalMaterial();
    if (PhysicalMaterial == nullptr)
    {
        return false;
    }
    PhysicalMaterial->Restitution = Restitution;
    return UpdatePhysicalMaterial(PhysicalMaterial);
}

void UFriction::SetMassScale(UStaticMeshComponent* Component, float MassScale)
{
    if(!Component) return;
    FBodyInstance* BodyInst = Component->GetBodyInstance();
    if(!BodyInst) return;
    BodyInst->MassScale = MassScale;
    BodyInst->UpdateMassProperties();
}

bool UFriction::SetVelocity(AActor *Actor, FVector Velocity)
{
    if (Actor == nullptr)
    {
        return false;
    }
    Actor->GetRootComponent()->ComponentVelocity = Velocity;
    return true;
}
