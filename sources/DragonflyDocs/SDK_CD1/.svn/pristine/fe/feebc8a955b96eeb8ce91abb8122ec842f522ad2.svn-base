#pragma once

class IASDLoader;//fwrd
class IFilterSet;//fwrd

class TTestAperture
{
public:
	TTestAperture(IASDLoader *ASDLoader);
	~TTestAperture();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	void GetApertureDetails();
	void GetApertureDescription(IFilterSet *FilterSet);
	void ExerciseAperture();
};

