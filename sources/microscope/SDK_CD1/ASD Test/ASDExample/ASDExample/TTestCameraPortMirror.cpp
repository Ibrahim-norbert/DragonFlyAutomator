#include "TTestCameraPortMirror.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>



TTestCameraPortMirror::TTestCameraPortMirror(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader)
{
	GetCameraPortMirrorDetails();
	ExerciseCameraPortMirror();
}


TTestCameraPortMirror::~TTestCameraPortMirror()
{
}

void TTestCameraPortMirror::GetCameraPortMirrorDetails()
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		std::cout << "Failed to Initialse CameraPortMirror" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	ICameraPortMirrorInterface *CameraPortMirrorInterface = GetASDLoader()->GetASDInterface2()->GetCameraPortMirror();
	if (CameraPortMirrorInterface == NULL)
	{
		std::cout << "Failed to Initialse CameraPortMirror" << std::endl;
		return;
	}

	bool RetVal = CameraPortMirrorInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get CameraPortMirror limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = CameraPortMirrorInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get CameraPortMirror position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position CameraPortMirror detected " << std::endl;

	IFilterSet *FilterSet = CameraPortMirrorInterface->GetCameraPortMirrorConfigInterface();
	if (FilterSet != NULL)
	{
		GetCameraPortMirrorDescription(FilterSet);
	}

}
void TTestCameraPortMirror::GetCameraPortMirrorDescription(IFilterSet *FilterSet)
{
	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "CameraPortMirror Index - " << MinPos << " to " << MaxPos << std::endl;

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

void TTestCameraPortMirror::ExerciseCameraPortMirror()
{
	if (GetASDLoader()->GetASDInterface2() == 0)
	{
		std::cout << "Failed to Initialse CameraPortMirror" << std::endl;
		return;
	}

	ICameraPortMirrorInterface *CameraPortMirrorInterface = GetASDLoader()->GetASDInterface2()->GetCameraPortMirror();
	if (CameraPortMirrorInterface == NULL)
	{
		std::cout << "Failed to Initialse CameraPortMirror" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = CameraPortMirrorInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get CameraPortMirror limits" << std::endl;
		return;
	}

	unsigned int CurrentPosition(MinValue);
	CameraPortMirrorInterface->GetPosition(CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = CameraPortMirrorInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}

	CameraPortMirrorInterface->GetPosition(CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "CameraPortMirror not in correct position" << std::endl;
	}
}
