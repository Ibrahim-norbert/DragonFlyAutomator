#pragma once

class IASDLoader;//fwrd
class IFilterSet;//fwrd

class TTestCameraPortMirror
{
public:
	TTestCameraPortMirror(IASDLoader *ASDLoader);
	~TTestCameraPortMirror();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	void GetCameraPortMirrorDetails();
	void GetCameraPortMirrorDescription(IFilterSet *FilterSet);
	void ExerciseCameraPortMirror();
};

