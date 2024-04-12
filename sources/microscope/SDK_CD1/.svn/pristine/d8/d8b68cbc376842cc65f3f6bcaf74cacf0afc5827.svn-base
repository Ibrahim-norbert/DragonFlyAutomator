#include "ASDTest.h"
#include "TTestEmissionAndDichroic.h"
#include "TTestDisk.h"
#include "TTestImagingMode.h"
#include "TTestAperture.h"
#include "TTestCameraPortMirror.h"
#include "TTestMagnificationLens.h"
#include "TTestPowerDensity.h"
#include "TTestEPIPolariser.h"
#include "TTestTIRFPolariser.h"
#include "TTestSuperRes.h"
#include "TTestTIRF.h"
#include "TTestStatusCode.h"
//-------------------------------------------------------
//-------------------------------------------------------
TASDExample::TASDExample(std::string COMPort)
//adjust COM Port as required
: ModuleHandler_( COMPort.c_str(), TASDType::ASD_DF)
{
}
//-------------------------------------------------------
TASDExample::~TASDExample()
{
}
//-------------------------------------------------------
//-------------------------------------------------------
void TASDExample::TestEmissionAndDichroic()
{
	TTestEmissionAndDichroic TestEmissionAndDichroic(ModuleHandler_.GetASDLoader());
}
void TASDExample::TestDisk()
{
	TTestDisk TestDisk(ModuleHandler_.GetASDLoader());
}
void TASDExample::TestImagingMode()
{
	TTestImagingMode TestImagingMode(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestAperture()
{
	TTestAperture TestAperture(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestCameraPortMirror()
{
	TTestCameraPortMirror TestCameraPortMirror(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestMagnificationLens()
{
	TTestMagnificationLens TestMagnificationLens(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestPowerDensity()
{
	TTestPowerDensity TestPowerDensity(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestEPIPolariser()
{
	TTestEPIPolariser TestEPIPolariser(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestTIRFPolariser()
{
	TTestTIRFPolariser TestTIRFPolariser(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestSuperRes()
{
	TTestSuperRes TestSuperRes(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestTIRF()
{
	TTestTIRF TestTIRF(ModuleHandler_.GetASDLoader());
}

void TASDExample::TestStatusCode()
{
	TTestStatusCode StatusCode(ModuleHandler_.GetASDLoader());
}
