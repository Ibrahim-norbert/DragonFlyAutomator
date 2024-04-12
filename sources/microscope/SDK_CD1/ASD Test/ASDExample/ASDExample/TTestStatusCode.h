#pragma once

class IASDLoader;//fwrd

class TTestStatusCode
{
public:
	TTestStatusCode(IASDLoader *ASDLoader);
	~TTestStatusCode();
private:
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };

	bool CheckStatusOfExternalDiskSync(unsigned int StatusCode);
	bool CheckStatusOfWheel1RFIDPresent(unsigned int StatusCode);
	bool CheckStatusOfWheel1RFIDReadFailure(unsigned int StatusCode);
	bool CheckStatusOfWheel2RFIDPresent(unsigned int StatusCode);
	bool CheckStatusOfWheel2RFIDReadFailure(unsigned int StatusCode);
	bool CheckStatusOfCameraPortRFIDPresent(unsigned int StatusCode);
	bool CheckStatusOfCameraPortRFIDReadFailure(unsigned int StatusCode);

	void SampleStatus(void);
};

