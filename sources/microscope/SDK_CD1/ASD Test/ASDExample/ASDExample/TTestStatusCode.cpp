#include "TTestStatusCode.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>


TTestStatusCode::TTestStatusCode(IASDLoader *ASDLoader)
	: ASDLoader_(ASDLoader) 
{
	SampleStatus();
}


TTestStatusCode::~TTestStatusCode()
{
}

//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfExternalDiskSync(unsigned int StatusCode)
{
	return (StatusCode & 0x1) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfWheel1RFIDPresent(unsigned int StatusCode)
{
	return (StatusCode & 0x10) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfWheel1RFIDReadFailure(unsigned int StatusCode)
{
	if (CheckStatusOfWheel1RFIDPresent(StatusCode) == false)
	{
		return false;
	}
	return (StatusCode & 0x20) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfWheel2RFIDPresent(unsigned int StatusCode)
{
	return (StatusCode & 0x40) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfWheel2RFIDReadFailure(unsigned int StatusCode)
{
	if (CheckStatusOfWheel2RFIDPresent(StatusCode) == false)
	{
		return false;
	}
	return (StatusCode & 0x80) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfCameraPortRFIDPresent(unsigned int StatusCode)
{
	return (StatusCode & 0x100) > 0;
}
//--------------------------------------------------------------------------
bool TTestStatusCode::CheckStatusOfCameraPortRFIDReadFailure(unsigned int StatusCode)
{
	if (CheckStatusOfCameraPortRFIDPresent(StatusCode) == false)
	{
		return false;
	}
	return (StatusCode & 0x200) > 0;
}
//--------------------------------------------------------------------------
void TTestStatusCode::SampleStatus(void)
{
	unsigned int StatusCode = 0;
	bool retVal = GetASDLoader()->GetASDInterface3()->GetStatus()->GetStatusCode(&StatusCode);
	if (retVal == false)
	{
		return;
	}

	//External Disk Sync
	bool ExternalDiskSyncActive = CheckStatusOfExternalDiskSync(StatusCode);
	std::cout << "External Disk Sync " << (ExternalDiskSyncActive ? "Active" : "Not Active") << std::endl;

	//Wheel 1 RFID
	bool Wheel1RFIDPresent = CheckStatusOfWheel1RFIDPresent(StatusCode);
	std::cout << "Wheel 1 RFID " << (Wheel1RFIDPresent ? "Present" : "Not Present") << std::endl;

	bool Wheel1RFIDReadFailure = CheckStatusOfWheel1RFIDReadFailure(StatusCode);
	std::cout << "Wheel 1 RFID Read Failure " << (Wheel1RFIDReadFailure ? "True" : "False") << std::endl;

	//Wheel 2 RFID
	bool Wheel2RFIDPresent = CheckStatusOfWheel2RFIDPresent(StatusCode);
	std::cout << "Wheel 2 RFID " << (Wheel2RFIDPresent ? "Present" : "Not Present") << std::endl;

	bool Wheel2RFIDReadFailure = CheckStatusOfWheel2RFIDReadFailure(StatusCode);
	std::cout << "Wheel 2 RFID Read Failure " << (Wheel2RFIDReadFailure ? "True" : "False") << std::endl;

	//Dichroic RFID
	bool CameraPortRFIDPresent = CheckStatusOfCameraPortRFIDPresent(StatusCode);
	std::cout << "Camera Port RFID Present " << (CameraPortRFIDPresent ? "Present" : "Not Present") << std::endl;

	bool CameraPortRFIDReadFailure = CheckStatusOfCameraPortRFIDReadFailure(StatusCode);
	std::cout << "Camera Port RFID Read Failure " << (CameraPortRFIDReadFailure ? "True" : "False") << std::endl;
}
