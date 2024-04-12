#include "TTestEPIPolariser.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>


//note that Polariser has not been impemented in hardware
//Interface here for future addition
TTestEPIPolariser::TTestEPIPolariser(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader)
{
	GetEPIPolariserDetails();
	ExerciseEPIPolariser();
}


TTestEPIPolariser::~TTestEPIPolariser()
{
}

void TTestEPIPolariser::GetEPIPolariserDetails()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse EPI Polariser" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	IEPIPolariserInterface *EPIPolariserInterface = GetASDLoader()->GetASDInterface3()->GetEPIPolariser();
	if (EPIPolariserInterface == 0)
	{
		std::cout << "Failed to Initialse EPI Polariser" << std::endl;
		return;
	}

	bool RetVal = EPIPolariserInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get EPI Polariser limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = EPIPolariserInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get EPI Polariser position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position EPI Polariser detected " << std::endl;
}

void TTestEPIPolariser::ExerciseEPIPolariser()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	IEPIPolariserInterface *EPIPolariserInterface = GetASDLoader()->GetASDInterface3()->GetEPIPolariser();
	if (EPIPolariserInterface == 0)
	{
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = EPIPolariserInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get EPI Polariser limits" << std::endl;
		return;
	}

	unsigned int CurrentPosition(MinValue);
	EPIPolariserInterface->GetPosition(CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = EPIPolariserInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}

	EPIPolariserInterface->GetPosition(CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "EPI Polariser not in correct position" << std::endl;
	}
}

