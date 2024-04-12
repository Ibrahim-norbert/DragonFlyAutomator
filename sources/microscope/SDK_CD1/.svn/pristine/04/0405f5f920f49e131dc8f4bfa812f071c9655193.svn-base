#include "TTestTIRFPolariser.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>

//note that Polariser has not been impemented in hardware
//Interface here for future addition
TTestTIRFPolariser::TTestTIRFPolariser(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader)
{
	GetTIRFPolariserDetails();
	ExerciseTIRFPolariser();
}

TTestTIRFPolariser::~TTestTIRFPolariser()
{
}

void TTestTIRFPolariser::GetTIRFPolariserDetails()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse TIRF Polariser" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	ITIRFPolariserInterface *TIRFPolariserInterface = GetASDLoader()->GetASDInterface3()->GetTIRFPolariser();
	if (TIRFPolariserInterface == 0)
	{
		std::cout << "Failed to Initialse TIRF Polariser" << std::endl;
		return;
	}

	bool RetVal = TIRFPolariserInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get TIRF Polariser limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = TIRFPolariserInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get TIRF Polariser position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position TIRF Polariser detected " << std::endl;
}

void TTestTIRFPolariser::ExerciseTIRFPolariser()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	ITIRFPolariserInterface *TIRFPolariserInterface = GetASDLoader()->GetASDInterface3()->GetTIRFPolariser();
	if (TIRFPolariserInterface == 0)
	{
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = TIRFPolariserInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get TIRF Polariser limits" << std::endl;
		return;
	}

	unsigned int CurrentPosition(MinValue);
	TIRFPolariserInterface->GetPosition(CurrentPosition);

	for (unsigned int Index = MinValue; Index <= MaxValue; Index++)
	{
		std::cout << "Move to Position " << Index << std::endl;
		bool RetVal = TIRFPolariserInterface->SetPosition(Index);
		if (RetVal == false)
		{
			std::cout << "Failed to move" << std::endl;
		}
	}

	TIRFPolariserInterface->GetPosition(CurrentPosition);
	if (CurrentPosition != MaxValue)
	{
		std::cout << "TIRF Polariser not in correct position" << std::endl;
	}
}

