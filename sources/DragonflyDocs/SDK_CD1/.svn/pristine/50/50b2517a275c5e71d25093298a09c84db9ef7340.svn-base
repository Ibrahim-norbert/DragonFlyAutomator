#pragma once

class IASDLoader;//fwrd
class IFilterSet;//fwrd

class TTestTIRF
{
public:
	TTestTIRF(IASDLoader *ASDLoader);
	~TTestTIRF();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	int Magnification_;
	double NumericalAperture_;
	double RefractiveIndex_; 
	int Scope_;
	
	void GetTIRFDetails();
	void ExerciseTIRF();
};

