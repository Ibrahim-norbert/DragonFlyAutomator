#pragma once

class IASDLoader;//fwrd
class IFilterSet;//fwrd

class TTestPowerDensity
{
public:
	TTestPowerDensity(IASDLoader *ASDLoader);
	~TTestPowerDensity();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	unsigned int MinPos_;
	unsigned int MaxPos_;

	void GetPowerDensityDetails();
	void GetPowerDensityDescription(IFilterSet *FilterSet);
	void ExercisePowerDensity();
	void TestRestrictionCallack();
public:
	void SamplePowerDensity();
	void IndicatePowerDensityChange();
};

