#pragma once

class IASDLoader;//fwrd

class TTestImagingMode
{
public:
	TTestImagingMode(IASDLoader *ASDLoader);
	~TTestImagingMode();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	bool WideFieldAvailable_;
	bool ConfocalHSAvailable_;
	bool ConfocalHCAvailable_;
	bool TIRFAvailable_;

	void GetImagingModeDetails();
	void ExerciseImagingMode();
};

