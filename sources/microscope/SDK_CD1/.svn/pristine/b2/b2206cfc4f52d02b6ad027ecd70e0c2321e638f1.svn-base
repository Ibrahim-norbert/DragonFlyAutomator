#include "TTestMagnificationLens.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>


TTestMagnificationLens::TTestMagnificationLens(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader)
{
	GetMagnificationLensDetails(1);
	ExerciseMagnificationLens(1);
	GetMagnificationLensDetails(2);
	ExerciseMagnificationLens(2);
}


TTestMagnificationLens::~TTestMagnificationLens()
{
}

void TTestMagnificationLens::GetMagnificationLensDetails(int LensIndex)
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		std::cout << "Failed to Initialse Magnification Lens " << LensIndex << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	ILensInterface *LensInterface = GetASDLoader()->GetASDInterface2()->GetLens( LensIndex == 1 ? lt_Lens1 : lt_Lens2);
	if (LensInterface == 0)
	{
		std::cout << "Failed to Initialse Magnification Lens " << LensIndex << std::endl;
		return;
	}

	bool RetVal = LensInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get the limits for Magnification Lens " << LensIndex << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = LensInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get the position for Magnification Lens " << LensIndex << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position Magnification Lens detected on port " << LensIndex << std::endl;

	IFilterSet *FilterSet = LensInterface->GetLensConfigInterface();
	if (FilterSet != NULL)
	{
		GetMagnificationLensDescription(FilterSet);
	}

}

void TTestMagnificationLens::GetMagnificationLensDescription(IFilterSet *FilterSet)
{
	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "Magnification Lens Index - " << MinPos << " to " << MaxPos << std::endl;

	char Description[64];
	for (unsigned int Index = MinPos; Index <= MaxPos; Index++)
	{
		if (FilterSet->GetFilterDescription(Index, Description, StringLength) == false)
		{
			strcpy(Description, "Empty");
		}
		std::cout << Index << " - " << Description << std::endl;
	}

}

void TTestMagnificationLens::ExerciseMagnificationLens(int LensIndex)
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		return;
	}

	ILensInterface *LensInterface = GetASDLoader()->GetASDInterface2()->GetLens( LensIndex == 1 ? lt_Lens1 : lt_Lens2);
	if (LensInterface == 0)
	{
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = LensInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get limits for Magnification Lens " << LensIndex << std::endl;
		return;
	}

	unsigned int CurrentPosition(MinValue);
	LensInterface->GetPosition(CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = LensInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}

	LensInterface->GetPosition(CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "Magnification Lens " << LensIndex << " is not in correct position" << std::endl;
	}
}
