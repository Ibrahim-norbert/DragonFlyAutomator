#pragma once

class IASDLoader;//fwrd
class IFilterSet;//fwrd

class TTestMagnificationLens
{
public:
	TTestMagnificationLens(IASDLoader *ASDLoader);
	~TTestMagnificationLens();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	void GetMagnificationLensDetails(int LensIndex);
	void GetMagnificationLensDescription(IFilterSet *FilterSet);
	void ExerciseMagnificationLens(int LensIndex);
};

