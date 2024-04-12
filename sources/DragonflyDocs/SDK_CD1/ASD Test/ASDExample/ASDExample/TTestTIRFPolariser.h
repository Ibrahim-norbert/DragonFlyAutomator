#pragma once

class IASDLoader;//fwrd

class TTestTIRFPolariser
{
public:
	TTestTIRFPolariser(IASDLoader *ASDLoader);
	~TTestTIRFPolariser();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	void GetTIRFPolariserDetails();
	void ExerciseTIRFPolariser();
};

