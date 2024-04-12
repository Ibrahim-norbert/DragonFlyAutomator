#include "TTestImagingMode.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include <iostream>


TTestImagingMode::TTestImagingMode(IASDLoader *ASDLoader)
: ASDLoader_( ASDLoader),
  ConfocalHSAvailable_(false),
  ConfocalHCAvailable_(false),
  WideFieldAvailable_(false),
  TIRFAvailable_(false)
{
	GetImagingModeDetails();
	ExerciseImagingMode();
}


TTestImagingMode::~TTestImagingMode()
{
}

void TTestImagingMode::GetImagingModeDetails()
{
	TConfocalMode MinValue = bfmNone, MaxValue = bfmWideField;
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse Image Mode" << std::endl;
		return;
	}

	IConfocalModeInterface3 *ImagingModeInterface = GetASDLoader()->GetASDInterface3()->GetImagingMode();
	if (ImagingModeInterface == 0)
	{
		std::cout << "Failed to Initialse Image Mode" << std::endl;
		return;
	}
		
	if( ImagingModeInterface->IsConfocalModeAvailable(bfmWideField))
	{
		WideFieldAvailable_ = true;
	}
	if (ImagingModeInterface->IsConfocalModeAvailable(bfmTIRF))
	{
		TIRFAvailable_ = true;
	}
	if (ImagingModeInterface && ImagingModeInterface->IsConfocalModeAvailable(bfmConfocalHC))
	{
		ConfocalHCAvailable_ = true;
	}
	if (ImagingModeInterface && ImagingModeInterface->IsConfocalModeAvailable(bfmConfocalHS))
	{
		ConfocalHSAvailable_ = true;
	}

	int HSPinHoleSize_um = 25;
	int HCPinHoleSize_um = 40;
	if (ImagingModeInterface)
	{
		int tempHCPinHoleSize_um = 0;
		if (ImagingModeInterface->GetPinHoleSize_um(bfmConfocalHC, &tempHCPinHoleSize_um))
		{
			HCPinHoleSize_um = tempHCPinHoleSize_um;
		}
		int tempHSPinHoleSize_um = 0;
		if (ImagingModeInterface->GetPinHoleSize_um(bfmConfocalHS, &tempHSPinHoleSize_um))
		{
			HSPinHoleSize_um = tempHSPinHoleSize_um;
		}
	}

	TConfocalMode Mode = bfmNone;
	bool RetVal = ImagingModeInterface->GetMode(Mode);
	if (RetVal == false)
	{
		std::cout << "Failed to read current imaging mode" << std::endl;
		return;
	}

	std::string CurrentImagingMode = "Unknown";
	std::cout << "Imaging Modes Available";
	if (ConfocalHSAvailable_)
	{
		std::cout << " - Confocal (High Sectioning " << HSPinHoleSize_um << "um) ";
		if (Mode == bfmConfocalHS)
		{ 
			CurrentImagingMode = " - Confocal (High Sectioning)";
		}
	}

	if(ConfocalHCAvailable_)
	{
		std::cout << " - Confocal (High Contrast " << HCPinHoleSize_um << "um) ";
		if (Mode == bfmConfocalHC)
		{
			CurrentImagingMode = " - Confocal (High Contrast)";
		}
	}
	
	if(TIRFAvailable_)
	{
		std::cout << " - TIRF ";
		if (Mode == bfmTIRF)
		{
			CurrentImagingMode = " - TIRF";
		}
	}
	
	if(WideFieldAvailable_)
	{
		std::cout << " - Wide Field ";
		if (Mode == bfmWideField)
		{
			CurrentImagingMode = " - Wide Field ";
		}
	}

	std::cout << std::endl << "Current Imaging Mode" << CurrentImagingMode.c_str() << std::endl;
}

void TTestImagingMode::ExerciseImagingMode()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	IConfocalModeInterface3 *ImagingModeInterface = GetASDLoader()->GetASDInterface3()->GetImagingMode();
	if (ImagingModeInterface == 0)
	{
		return;
	}

	bool retVal(false);
	if (ConfocalHCAvailable_)
	{
		std::cout << "Move to Confocal (High Contrast)" << std::endl;
		retVal = ImagingModeInterface->ModeConfocalHC();
		if( retVal == false)
		{
			std::cout << "Failed to move to Confocal (High Contrast)" << std::endl;
		}
	}
	if (WideFieldAvailable_)
	{
		std::cout << "Move to Widefield" << std::endl;
		retVal = ImagingModeInterface->ModeWideField();
		if (retVal == false)
		{
			std::cout << "Failed to move to Widefield" << std::endl;
		}
	}
	if (ConfocalHSAvailable_)
	{
		std::cout << "Move to Confocal (High Sectioning)" << std::endl;
		retVal = ImagingModeInterface->ModeConfocalHS();
		if (retVal == false)
		{
			std::cout << "Failed to move to Confocal (High Sectioning)" << std::endl;
		}
	}
	if (TIRFAvailable_)
	{
		std::cout << "Move to TIRF" << std::endl;
		retVal = ImagingModeInterface->ModeTIRF();
		if (retVal == false)
		{
			std::cout << "Failed to move to TIRF" << std::endl;
		}
	}

	TConfocalMode Mode = bfmNone;
	bool RetVal = ImagingModeInterface->GetMode(Mode);
	if( Mode != bfmTIRF)
	{
		std::cout << "Failed to get the current position" << std::endl;
	}
}
