#include "TTestAperture.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>



TTestAperture::TTestAperture(IASDLoader *ASDLoader)
: ASDLoader_( ASDLoader)
{
	GetApertureDetails();
	ExerciseAperture();
}

TTestAperture::~TTestAperture()
{
}

void TTestAperture::GetApertureDetails()
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		std::cout << "Failed to Initialse Aperture" << std::endl;
		return;
	}

	if( GetASDLoader()->GetASDInterface2()->IsApertureAvailable( ) == false)
	{
		std::cout << "Aperture not available" << std::endl;
		return;
	}

	IApertureInterface *ApertureInterface = GetASDLoader()->GetASDInterface2()->GetAperture();
	if (ApertureInterface == NULL)
	{
		std::cout << "Failed to Initialse Aperture" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = ApertureInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Aperture limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = ApertureInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get Aperture position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position aperture detected " << std::endl;

	IFilterSet *FilterSet = ApertureInterface->GetApertureConfigInterface();
	if (FilterSet != NULL)
	{
		GetApertureDescription(FilterSet);
	}

}
void TTestAperture::GetApertureDescription(IFilterSet *FilterSet)
{
	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "Aperture Index - " << MinPos << " to " << MaxPos << std::endl;

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

void TTestAperture::ExerciseAperture()
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		std::cout << "Failed to Initialse Aperture" << std::endl;
		return;
	}

	IApertureInterface *ApertureInterface = GetASDLoader()->GetASDInterface2()->GetAperture();
	if (ApertureInterface == NULL)
	{
		std::cout << "Failed to Initialse Aperture" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = ApertureInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Aperture limits" << std::endl;
		return;
	}

	unsigned int CurrentPosition( MinValue);
	ApertureInterface->GetPosition( CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = ApertureInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}
	
	ApertureInterface->GetPosition( CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "Aperture not in correct position" << std::endl;
	}
}
