// ASDExample.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "ASDTest.h"
#include <iostream>

int main()
{
	try
		{
		std::cout << "Connecting to DF Unit" << std::endl;
		//hardwired comport address adjust as required
		TASDExample ASDExample( "\\\\.\\COM7");
		std::cout << "Connection Successful" << std::endl << std::endl;

		std::cout << "Test Emission" << std::endl;
		ASDExample.TestEmissionAndDichroic();
		std::cout << "Test Emission Complete" << std::endl << std::endl;

		std::cout << "Test Disk" << std::endl;	
		ASDExample.TestDisk();
		std::cout << "Test Disk Complete" << std::endl << std::endl;

		std::cout << "Test Imaging Mode" << std::endl;
		ASDExample.TestImagingMode();
		std::cout << "Test Imaging Mode Complete" << std::endl << std::endl;
		std::cout << "Test Aperture" << std::endl;
		ASDExample.TestAperture();
		std::cout << "Test Aperture Complete" << std::endl << std::endl;

		std::cout << "Test Camera Port Mirror" << std::endl;
		ASDExample.TestCameraPortMirror();
		std::cout << "Test Camera Port Mirror Complete" << std::endl << std::endl;

		std::cout << "Test Magnification Lens" << std::endl;
		ASDExample.TestMagnificationLens();
		std::cout << "Test Magnification Lens Complete" << std::endl << std::endl;

		std::cout << "Test Power Density" << std::endl;
		ASDExample.TestPowerDensity();
		std::cout << "Test Power Density Complete" << std::endl << std::endl;

		std::cout << "Test EPI Polariser" << std::endl;
		ASDExample.TestEPIPolariser();
		std::cout << "Test EPI Polariser Complete" << std::endl << std::endl;

		std::cout << "Test TIRF Polariser" << std::endl;
		ASDExample.TestTIRFPolariser();
		std::cout << "Test TIRF Polariser Complete" << std::endl << std::endl;

		std::cout << "Test Super Res" << std::endl;
		ASDExample.TestSuperRes();
		std::cout << "Test Super Res Complete" << std::endl << std::endl;

		std::cout << "Test TIRF" << std::endl;
		ASDExample.TestTIRF();
		std::cout << "Test TIRF Complete" << std::endl << std::endl;
	
		std::cout << "Test Status Code" << std::endl;
		ASDExample.TestStatusCode();
		std::cout << "Test Status Code Complete" << std::endl << std::endl;
		}
	catch(...)
		{ 
		std::cout << "Failed to connect" << std::endl;
		}
	
	//hold so that you can read text
	std::cout << std::endl << "Enter to Exit" << std::endl;
	getchar();

    return 0;
}

