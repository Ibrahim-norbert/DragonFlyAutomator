#include "TTestSuperRes.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>



TTestSuperRes::TTestSuperRes(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader)
{
	GetSuperResDetails();
	ExerciseSuperRes();
}

TTestSuperRes::~TTestSuperRes()
{
}

void TTestSuperRes::GetSuperResDetails()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse Super Res" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	ISuperResInterface *SuperResInterface = GetASDLoader()->GetASDInterface3()->GetSuperRes();
	if (SuperResInterface == 0)
	{
		std::cout << "Failed to Initialse Super Res" << std::endl;
		return;
	}

	bool RetVal = SuperResInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Super Res limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = SuperResInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get Super Res position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position Super Res detected " << std::endl;
}

void TTestSuperRes::ExerciseSuperRes()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse Super Res" << std::endl;
		return;
	}

	ISuperResInterface *SuperResInterface = GetASDLoader()->GetASDInterface3()->GetSuperRes();
	if (SuperResInterface == 0)
	{
		std::cout << "Failed to Initialse Super Res" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = SuperResInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Super Res limits" << std::endl;
		return;
	}

	unsigned int CurrentPosition(MinValue);
	SuperResInterface->GetPosition(CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = SuperResInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}

	SuperResInterface->GetPosition(CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "Super Res not in correct position" << std::endl;
	}
}

