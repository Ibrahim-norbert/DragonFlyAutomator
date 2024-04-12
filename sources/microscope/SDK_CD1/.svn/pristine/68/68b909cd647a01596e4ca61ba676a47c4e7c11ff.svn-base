#include "TTestEmissionAndDichroic.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>


TTestEmissionAndDichroic::TTestEmissionAndDichroic(IASDLoader *ASDLoader)
: ASDLoader_( ASDLoader)
{
	GetDichroicDetails();
	GetFilterWheelDetails(1);
	GetFilterWheelDetails(2);
	ExerciseDichroic();
	ExerciseWheel(1);
	ExerciseWheel(2);
}


TTestEmissionAndDichroic::~TTestEmissionAndDichroic()
{
}

void TTestEmissionAndDichroic::GetDichroicDetails()
{
	IDichroicMirrorInterface *DichroicMirrorInterface = GetASDLoader()->GetASDInterface()->GetDichroicMirror();
	if (DichroicMirrorInterface == 0)
	{
		std::cout << "Failed to detect dichroic/camera splitter" << std::endl;
		return;
	}
	
	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = DichroicMirrorInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to read dichroic/camera splitter limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = DichroicMirrorInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get the dichroic/camera splitter position" << std::endl;
		return;
	}

	std::cout << (MaxValue - MinValue) + 1 << " position dichroic/camera splitter detected" << std::endl;

	IFilterConfigInterface *FilterConfigInterface = DichroicMirrorInterface->GetFilterConfigInterface();
	if (FilterConfigInterface != 0)
	{
		RetrieveDichroicDescription( FilterConfigInterface);
	}
}

void TTestEmissionAndDichroic::RetrieveDichroicDescription(IFilterConfigInterface *FilterConfigInterface)
{
	IFilterSet *FilterSet = FilterConfigInterface->GetFilterSet();
	if (FilterSet == 0)
	{
		std::cout << "Cannot retrieve details of the filterset!" << std::endl;
		return;
	}

	//unsigned int FSIndex(0);
	//FlterConfigInterface->GetPositionOfFilterSetInRepository(&FSIndex);
	//std::cout << "Index of the filterset = " << FSIndex << std::endl;

	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "Filter Index - " << MinPos << " to " << MaxPos << std::endl;

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

IFilterWheelInterface *TTestEmissionAndDichroic::GetFilterWheelInterface( int Index)
{
	IFilterWheelInterface *FilterWheelInterface = GetASDLoader()->GetASDInterface()->GetFilterWheel(Index == 1 ? WheelIndex1 : WheelIndex2);
	if (FilterWheelInterface == NULL)
	{
		std::cout << "No wheel detected on camera port " << Index << std::endl;
		return 0;
	}
	return FilterWheelInterface;
}

void TTestEmissionAndDichroic::GetFilterWheelDetails( int Index)
{
	IFilterWheelInterface *FilterWheelInterface = GetFilterWheelInterface(Index);
	if (FilterWheelInterface == 0) 
		{
		return;
		}

	std::cout << std::endl;
	InitialseEmission(Index, FilterWheelInterface);
	InitialseEmissionFilters(Index, FilterWheelInterface);
	InitialseEmissionSpeed(Index, FilterWheelInterface);
	InitialseEmissionMode(Index, FilterWheelInterface);
}

void TTestEmissionAndDichroic::InitialseEmission(int Index, IFilterWheelInterface *FilterWheelInterface)
{
	unsigned int MinValue(1);
	unsigned int MaxValue(1);
	bool RetVal = FilterWheelInterface->GetLimits( MinValue, MaxValue);
	if (RetVal == false)
		{
		std::cout << "Error reading limits for Wheel on camera port " << Index << std::endl;
		return;
		}

	unsigned int Position = MinValue;
	RetVal = FilterWheelInterface->GetPosition(Position);
	if (RetVal == false)
		{
		std::cout << "No Wheel detected on camera port " << Index << std::endl;
		return;
		}
	unsigned int NumberOfPositions = (MaxValue - MinValue) + 1;

	std::cout << NumberOfPositions << " position wheel detected on camera port " << Index << std::endl;
}

void TTestEmissionAndDichroic::InitialseEmissionFilters(int Index, IFilterWheelInterface *FilterWheelInterface)
{
	IFilterConfigInterface *FilterConfigInterface = FilterWheelInterface->GetFilterConfigInterface();
	if (FilterConfigInterface == NULL)
	{
		std::cout << "Error reading configuration of Wheel on camera port " << Index << std::endl;
		return;
	}
	std::cout << "Reading filter set for wheel detected on camera port " << Index << std::endl;

	RetrieveEmissionDescription( FilterConfigInterface);
}

void TTestEmissionAndDichroic::RetrieveEmissionDescription(IFilterConfigInterface *FilterConfigInterface)
{
	IFilterSet *FilterSet = FilterConfigInterface->GetFilterSet();
	if (FilterSet == 0)
	{
		std::cout << "Cannot retrieve details of the filterset!" << std::endl;
		return;
	}
	
	unsigned int FSIndex( 0);
	FilterConfigInterface->GetPositionOfFilterSetInRepository(&FSIndex);
	std::cout << "Index of the filterset = " << FSIndex << std::endl;

	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "Filter Index - " << MinPos << " to " << MaxPos << std::endl;

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

void TTestEmissionAndDichroic::InitialseEmissionSpeed(int Index, IFilterWheelInterface *FilterWheelInterface)
{
	IFilterWheelSpeedInterface *FilterWheelSpeedInterface = FilterWheelInterface->GetFilterWheelSpeedInterface();
	if (FilterWheelSpeedInterface == NULL)
	{
		std::cout << "Error reading speed limits for wheel on camera port " << Index << std::endl;
		return;
	}

	bool HighSpeedAvailable = FilterWheelSpeedInterface->IsHighSpeedAvailable();

	TFilterWheelSpeed Position = FWS66;
	bool RetVal = FilterWheelSpeedInterface->GetSpeed(Position);
	if (RetVal == false)
	{
		std::cout << "Error reading speed for wheel on camera port " << Index << std::endl;
		return;
	}

	std::cout << "Speed available for wheel on camera port " << Index;
	std::cout << (HighSpeedAvailable ? " - 40, 66, 100, 200ms" : " - 66, 100, 200ms") << std::endl;
}

void TTestEmissionAndDichroic::InitialseEmissionMode(int Index, IFilterWheelInterface *FilterWheelInterface)
{
	IFilterWheelModeInterface *FilterWheelModeInterface = FilterWheelInterface->GetFilterWheelModeInterface();
	if (FilterWheelModeInterface == NULL)
	{
		std::cout << "Error reading mode limits for wheel on camera port " << Index << std::endl;
		return;
	}

	TFilterWheelMode Mode = FWMHighQuality;
	bool RetVal = FilterWheelModeInterface->GetMode(Mode);
	if (RetVal == false)
	{
		std::cout << "Error reading mode for wheel on camera port " << Index << std::endl;
		return;
	}

	std::cout << "Modes available for wheel on camera port " << Index;
	std::cout << " - High Quality, High Speed, Low Vibration" << std::endl;
}


void TTestEmissionAndDichroic::ExerciseDichroic()
{
	IDichroicMirrorInterface *DichroicMirrorInterface = GetASDLoader()->GetASDInterface()->GetDichroicMirror();
	if (DichroicMirrorInterface == 0)
	{
		std::cout << "Failed to detect dichroic/camera splitter" << std::endl;
		return;
	}

	unsigned int MinValue(1);
	unsigned int MaxValue(1);
	bool RetVal = DichroicMirrorInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		return;
	}

	unsigned int CurrentFilterIndex(MinValue);
	std::cout << std::endl << "Dichroic" << std::endl;
	for (int FilterIndex = MinValue; FilterIndex <= MaxValue; FilterIndex++)
	{
		std::cout << "Move to Position " << FilterIndex << std::endl;
		if (DichroicMirrorInterface->SetPosition(FilterIndex) == false)
		{
			std::cout << "Move failed!" << std::endl;
		}
		if (DichroicMirrorInterface->GetPosition(CurrentFilterIndex) == false)
		{
			std::cout << "Failed to read position!" << std::endl;
		}
		if (CurrentFilterIndex != FilterIndex)
		{
			std::cout << "Failed to read correct position!" << std::endl;
		}
	}
}

void TTestEmissionAndDichroic::ExerciseWheel(int Index)
{
	IFilterWheelInterface *FilterWheelInterface = GetFilterWheelInterface(Index);
	if (FilterWheelInterface == 0)
	{
		return;
	}
	IFilterWheelModeInterface *FilterWheelModeInterface = FilterWheelInterface->GetFilterWheelModeInterface();
	if (FilterWheelModeInterface == NULL)
	{
		return;
	}

	unsigned int MinValue(1);
	unsigned int MaxValue(1);
	bool RetVal = FilterWheelInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		return;
	}

	std::cout << std::endl << "Wheel " << Index << std::endl;

	std::cout << std::endl << "High Quality" << std::endl;
	FilterWheelModeInterface->SetMode(FWMHighQuality);
	SpinTheWheel( MinValue, MaxValue, FilterWheelInterface);

	std::cout << std::endl << "High Speed" << std::endl;
	FilterWheelModeInterface->SetMode(FWMHighSpeed);
	SpinTheWheel(MinValue, MaxValue, FilterWheelInterface);

	std::cout << std::endl << "Low Vibration" << std::endl;
	FilterWheelModeInterface->SetMode(FWMLowVibration);
	SpinTheWheel(MinValue, MaxValue, FilterWheelInterface);
}

void TTestEmissionAndDichroic::SpinTheWheel(unsigned int MinValue, unsigned int MaxValue, IFilterWheelInterface *FilterWheelInterface)
{
	unsigned int CurrentFilterIndex(MinValue);
	for (int FilterIndex = MinValue; FilterIndex <= MaxValue; FilterIndex++)
	{
		std::cout << "Move to Position " << FilterIndex << std::endl;
		if (FilterWheelInterface->SetPosition(FilterIndex) == false)
		{
			std::cout << "Move failed!" << std::endl;
		}
		if (FilterWheelInterface->GetPosition(CurrentFilterIndex) == false)
		{
			std::cout << "Failed to read position!" << std::endl;
		}
		if (CurrentFilterIndex != FilterIndex)
		{
			std::cout << "Failed to read correct position!" << std::endl;
		}
	}
}
