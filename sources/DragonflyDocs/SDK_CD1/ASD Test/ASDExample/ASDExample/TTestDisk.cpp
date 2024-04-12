#include "TTestDisk.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>


TTestDisk::TTestDisk(IASDLoader *ASDLoader)
: ASDLoader_(ASDLoader)
{
	GetDiskDetails( );
	ExerciseDisk( );
}


TTestDisk::~TTestDisk()
{
}

void TTestDisk::GetDiskDetails()
{
	unsigned int MinValue = 0, MaxValue = 0;
	IDiskInterface2 *DiskInterface = GetASDLoader()->GetASDInterface()->GetDisk_v2();
	if (DiskInterface == 0)
	{
		std::cout << "Failed to Initialse Disk" << std::endl;
		return;
	}
	bool RetVal = DiskInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Disk limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = DiskInterface->GetSpeed(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to read Disk speed" << std::endl;
		return;
	}

	std::cout << "Disk Speed - "<< MinValue << " to "<< MaxValue << std::endl;
	std::cout << "Current Speed - " << Position << std::endl;

	unsigned int ScansPerRevolution;
	RetVal = DiskInterface->GetScansPerRevolution(&ScansPerRevolution);
	if (RetVal == false)
	{
		ScansPerRevolution = 4;
	}
	std::cout << "Scans Per Revolution " << ScansPerRevolution << std::endl;
}

void TTestDisk::ExerciseDisk()
{
	unsigned int MinValue = 0, MaxValue = 0;
	IDiskInterface2 *DiskInterface = GetASDLoader()->GetASDInterface()->GetDisk_v2();
	if (DiskInterface == 0)
	{
		return;
	}
	bool RetVal = DiskInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		return;
	}

	if( DiskInterface->IsSpinning() == false)
	{
		std::cout << "Start Disk" << std::endl;
		DiskInterface->Start();
	}

	unsigned int DesiredSpeed(4000);
	if (DiskInterface->SetSpeed(DesiredSpeed) == false)
	{
		std::cout << "Failed to set the Disk Speed " << std::endl;
		return;
	}

	unsigned int CurrentSpeed(0);
	while (CurrentSpeed != DesiredSpeed)
	{
		if (DiskInterface->GetSpeed(CurrentSpeed) == false)
		{
			std::cout << "Failed to get the Disk Speed " << std::endl;
		}
	}
	std::cout << "At Desired Speed - " << DesiredSpeed << std::endl;

	unsigned int DesiredSpeed2(5000);
	if (DiskInterface->SetSpeed(DesiredSpeed2) == false)
	{
		std::cout << "Failed to set the Disk Speed " << std::endl;
		return;
	}

	unsigned int CurrentSpeed2(0);
	while (CurrentSpeed2 != DesiredSpeed2)
	{
		if (DiskInterface->GetSpeed(CurrentSpeed2) == false)
		{
			std::cout << "Failed to get the Disk Speed " << std::endl;
		}
	}
	std::cout << "At Desired Speed - " << DesiredSpeed2 << std::endl;

	std::cout << "Stop Disk" << std::endl;
	DiskInterface->Stop();
	
	if (DiskInterface->IsSpinning() == true) 
	{
		std::cout << "Failed to Stop the Disk" << std::endl;
		return;
	}

	unsigned int DesiredSpeed3(0);
	unsigned int CurrentSpeed3(0);
	while (CurrentSpeed3 != DesiredSpeed3)
	{
		if (DiskInterface->GetSpeed(CurrentSpeed3) == false)
		{
			std::cout << "Failed to get the Disk Speed " << std::endl;
		}
	}
	std::cout << "At Desired Speed - " << DesiredSpeed3 << std::endl;
}
