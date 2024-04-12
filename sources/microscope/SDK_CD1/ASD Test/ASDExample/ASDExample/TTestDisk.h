#pragma once

class IASDLoader;//fwrd

class TTestDisk
{
public:
	TTestDisk(IASDLoader *ASDLoader);
	~TTestDisk();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	void GetDiskDetails();
	void ExerciseDisk();
};
