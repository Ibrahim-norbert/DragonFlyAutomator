#include "TTestTIRF.h"
#include "ASDLoader.h"
#include "ASDInterface.h"
#include "ASDConfigInterface.h"
#include <iostream>



TTestTIRF::TTestTIRF(IASDLoader *ASDLoader)
: ASDLoader_(ASDLoader),
  Magnification_( 1),
  NumericalAperture_( 1.2),
  RefractiveIndex_( 1.3),
  Scope_( 1)
{
	GetTIRFDetails();
	ExerciseTIRF();
}


TTestTIRF::~TTestTIRF()
{
}


void TTestTIRF::GetTIRFDetails()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		std::cout << "Failed to Initialse TIRF" << std::endl;
		return;
	}

	ITIRFInterface *TIRFInterface = GetASDLoader()->GetASDInterface3()->GetTIRF();
	if (TIRFInterface == NULL)
	{
		std::cout << "Failed to Initialse TIRF" << std::endl;
		return;
	}

	int Magnification(0);
	double NumericalAperture(0.0);
	double RefractiveIndex(0.0);
	int Scope(st_None);
	if (TIRFInterface->GetOpticalPathway(&Magnification, &NumericalAperture, &RefractiveIndex, &Scope) == false)
	{
		std::cout << "Failed to get TIRF Parameters" << std::endl;
		return;
	}

	std::string ScopeName = "Unknown";
	if (Scope == st_Leica)
	{
		ScopeName = "Leica";
	}
	if (Scope == st_Nikon)
	{
		ScopeName = "Nikon";
	}
	if (Scope == st_Olympus)
	{
		ScopeName = "Olympus";
	}
	if (Scope == st_Zeiss)
	{
		ScopeName = "Zeiss";
	}
	
	std::cout << "TIRF setup for : " << std::endl;
	std::cout << "Mag " << Magnification << std::endl;
	std::cout << "NA " << NumericalAperture << std::endl;
	std::cout << "RI " << RefractiveIndex << std::endl; 
	std::cout << "Scope " << ScopeName.c_str() << std::endl;
	
	Magnification_ = Magnification;
	NumericalAperture_ = NumericalAperture;
	RefractiveIndex_ = RefractiveIndex;
	Scope_ = Scope;
	
	int MinWavelength_nm(0);
	int MaxWavelength_nm(0);
	if( TIRFInterface->GetBandwidth( &MinWavelength_nm, &MaxWavelength_nm) == false)
	{
		std::cout << "Failed to get TIRF Bandwidth" << std::endl;
		return;
	}
	std::cout << "TIRF bandwidth currently " << MinWavelength_nm << "nm to " << MaxWavelength_nm << "nm"<< std::endl;
}

void TTestTIRF::ExerciseTIRF()
{
	if (GetASDLoader()->GetASDInterface3() == 0)
	{
		return;
	}

	ITIRFInterface *TIRFInterface = GetASDLoader()->GetASDInterface3()->GetTIRF();
	if (TIRFInterface == 0)
	{
		return;
	}

	//note use only values read from the unit
	if (TIRFInterface->SetOpticalPathway(Magnification_, NumericalAperture_, RefractiveIndex_, Scope_) == false)
	{
		std::cout << "Failed to set Optical Pathway" << std::endl;
		return;
	}

	int MinWavelength_nm( 488);
	int MaxWavelength_nm( 640);
	if( TIRFInterface->SetBandwidth(MinWavelength_nm, MaxWavelength_nm) == false)
	{
		std::cout << "Failed to set Bandwidth" << std::endl;
		return;
	}

	int TIRFMode = 0;//penetration - supercritical illumination will adjust the thichness/penetration of the TIRF plane
	if( TIRFInterface->SetTIRFMode(TIRFMode) == false)
	{
		std::cout << "Failed to set TIRF Mode" << std::endl;
		return;
	}

	int Depth_nm = 200;//200nm
	if( TIRFInterface->SetPenetration_nm(Depth_nm) == false)
	{
		std::cout << "Failed to set Penetration(nm)" << std::endl;
		return;
	}

	TIRFMode = 1;//Oblique - subcritical illumination for hilo/bright field like illumination 
	if (TIRFInterface->SetTIRFMode(TIRFMode) == false)
	{
		std::cout << "Failed to set TIRF Mode" << std::endl;
		return;
	}

	int ObliqueAngle_mdeg = 500;
	if( TIRFInterface->SetObliqueAngle_mdeg(ObliqueAngle_mdeg) == false)
	{
		std::cout << "Failed to set ObliqueAngle(mdeg)" << std::endl;
		return;
	}

	//Adjust Offset for Critical Angle to compensate for refractive index changes between samples
	TIRFMode = 2;
	if (TIRFInterface->SetTIRFMode(TIRFMode) == false)
	{
		std::cout << "Failed to set TIRF Mode" << std::endl;
		return;
	}
	
	int Offset = 20;
	if( TIRFInterface->SetOffset(Offset) == false)
	{
		std::cout << "Failed to set Offset" << std::endl;
		return;
	}

}
