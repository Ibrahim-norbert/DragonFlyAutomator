#include "TTestPowerDensity.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>



TTestPowerDensity::TTestPowerDensity(IASDLoader *ASDLoader)
: ASDLoader_(ASDLoader),
  MinPos_( 0),
  MaxPos_( 0)
{
	GetPowerDensityDetails();
	ExercisePowerDensity();
	TestRestrictionCallack();
}

TTestPowerDensity::~TTestPowerDensity()
{
}

void TTestPowerDensity::GetPowerDensityDetails()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse Power Density" << std::endl;
		return;
	}

	unsigned int MinValue = 0, MaxValue = 0;
	IIllLensInterface *LensInterface = GetASDLoader()->GetASDInterface3()->GetIllLens(lt_Lens1);
	if (LensInterface == 0)
	{
		std::cout << "Failed to Initialse Power Density" << std::endl;
		return;
	}

	bool RetVal = LensInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Power Density limits" << std::endl;
		return;
	}

	unsigned int Position = MinValue;
	RetVal = LensInterface->GetPosition(Position);
	if (RetVal == false)
	{
		std::cout << "Failed to get Power Density position" << std::endl;
		return;
	}

	std::cout << ((MaxValue - MinValue) + 1) << " position Power Density detected " << std::endl;

	IFilterSet *FilterSet = LensInterface->GetLensConfigInterface();
	if (FilterSet != NULL)
	{
		GetPowerDensityDescription(FilterSet);
	}

}
void TTestPowerDensity::GetPowerDensityDescription(IFilterSet *FilterSet)
{
	char FilterSetName[64];
	unsigned int StringLength = 64;
	FilterSet->GetDescription(FilterSetName, StringLength);
	FilterSetName;

	unsigned int MinPos;
	unsigned int MaxPos;
	FilterSet->GetLimits(MinPos, MaxPos);
	std::cout << "Power Density Index - " << MinPos << " to " << MaxPos << std::endl;
	MinPos_ = MinPos;
	MaxPos_ = MaxPos;


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

void TTestPowerDensity::ExercisePowerDensity()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	IIllLensInterface *LensInterface = GetASDLoader()->GetASDInterface3()->GetIllLens(lt_Lens1);
	if (LensInterface == 0)
	{
		return;
	}

	//set to wide field to ensure all positions are available
	IConfocalModeInterface3 *ImagingModeInterface = GetASDLoader()->GetASDInterface3()->GetImagingMode();
	if (ImagingModeInterface == 0)
	{
		return;
	}
	ImagingModeInterface->ModeWideField();

	unsigned int MinValue = 0, MaxValue = 0;
	bool RetVal = LensInterface->GetLimits(MinValue, MaxValue);
	if (RetVal == false)
	{
		std::cout << "Failed to get Power Density limits" << std::endl;
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
		std::cout << "Power Density not in correct position" << std::endl;
	}
}

class TPowerDensityNotification : public INotify
{
private:
	TTestPowerDensity *Owner_;
public:
	TPowerDensityNotification(TTestPowerDensity *Owner)
	:Owner_(Owner)
	{
	}
	void __stdcall Notify()
	{
		Owner_->SamplePowerDensity();
		Owner_->IndicatePowerDensityChange();
	};
};

void TTestPowerDensity::TestRestrictionCallack()
{
	//Power density is restricted when in Confocal mode 
	//callback will be called when restriction is forced

	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	IIllLensInterface *LensInterface = GetASDLoader()->GetASDInterface3()->GetIllLens(lt_Lens1);
	if (LensInterface == 0)
	{
		return;
	}

	IConfocalModeInterface3 *ImagingModeInterface = GetASDLoader()->GetASDInterface3()->GetImagingMode();
	if (ImagingModeInterface == 0)
	{
		return;
	}



	std::cout << "Test Restriction" << std::endl;
	//in Widefield there is no restriction
	//Confocal may only use positions 1 and 2 (1x and 2x)
	std::cout << "Set Imaging Mode WideField" << std::endl;
	ImagingModeInterface->ModeWideField();
	std::cout << "Power Density Restriction - " << (LensInterface->IsRestrictionEnabled() == true ? "Enabled" : "Disabled") << std::endl;
	unsigned int MinPosition(MinPos_);
	unsigned int MaxPosition(MinPos_);
	LensInterface->GetRestrictedRange(MinPosition, MaxPosition);
	std::cout << "Power Density Restricted Range - " << MinPosition << " to " << MaxPosition << std::endl;
	
	std::cout << "Set Imaging Mode Confocal" << std::endl;
	ImagingModeInterface->ModeConfocalHS();
	std::cout << "Power Density Restriction - " << (LensInterface->IsRestrictionEnabled() == true ? "Enabled" : "Disabled") << std::endl;
	LensInterface->GetRestrictedRange(MinPosition, MaxPosition);
	std::cout << "Power Density Restricted Range - " << MinPosition << " to " << MaxPosition << std::endl;

	INotify *Notify = new TPowerDensityNotification(this);
	LensInterface->RegisterForNotificationOnRangeRestriction( Notify);

	std::cout << "Test Restriction Callback" << std::endl;
	//notification given when trying to set a value that is restricted
	//also when mode is changed

	unsigned int CurrentPosition(MinPos_);
	LensInterface->GetPosition(CurrentPosition);
	std::cout << "Current Position " << CurrentPosition << std::endl;

	std::cout << "Set Imaging Mode WideField" << std::endl;
	ImagingModeInterface->ModeWideField();
	std::cout << "Set Position " << MaxPos_ << std::endl;
	LensInterface->SetPosition( MaxPos_);
	LensInterface->GetPosition(CurrentPosition);
	std::cout << "Current Position " << CurrentPosition << std::endl;

	std::cout << "Set Imaging Mode Confocal" << std::endl;
	ImagingModeInterface->ModeConfocalHS();

	std::cout << "Set Position " << MinPos_ << std::endl;
	LensInterface->SetPosition(MinPos_);
	LensInterface->GetPosition(CurrentPosition);
	std::cout << "Current Position " << CurrentPosition << std::endl;

	std::cout << "Set Position " << MaxPos_ << std::endl;
	LensInterface->SetPosition(MaxPos_);
	LensInterface->GetPosition(CurrentPosition);
	std::cout << "Current Position " << CurrentPosition << std::endl;

	std::cout << "Set Imaging Mode WideField" << std::endl;
	ImagingModeInterface->ModeWideField();
	std::cout << "Set Position " << MaxPos_ << std::endl;
	LensInterface->SetPosition(MaxPos_);
	LensInterface->GetPosition(CurrentPosition);
	std::cout << "Current Position " << CurrentPosition << std::endl;

	delete Notify;
}

void TTestPowerDensity::SamplePowerDensity()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	IIllLensInterface *LensInterface = GetASDLoader()->GetASDInterface3()->GetIllLens(lt_Lens1);
	if (LensInterface == 0)
	{
		return;
	}
	TLensType LensIndex = lt_Lens1;

	unsigned int Position(0);
	LensInterface->GetPosition(Position);
	std::cout << "Power Density notification - current position " << Position << std::endl;

}

void TTestPowerDensity::IndicatePowerDensityChange()
{ 
	std::cout << "Power Density has been restricted by mode change" << std::endl;
}
