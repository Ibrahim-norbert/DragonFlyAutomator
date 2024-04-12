#pragma once

class IASDLoader;//fwrd
class IFilterWheelInterface;//fwrd
class IFilterConfigInterface;//fwrd

class TTestEmissionAndDichroic
{
private: 
	IASDLoader *ASDLoader_;
	IASDLoader *GetASDLoader() { return ASDLoader_; };
	

	void GetDichroicDetails();
	void RetrieveDichroicDescription(IFilterConfigInterface *FilterConfigInterface);

	IFilterWheelInterface *GetFilterWheelInterface(int Index);
	void GetFilterWheelDetails(int Index);
	void InitialseEmission( int Index, IFilterWheelInterface *GetFilterWheelInterface);
	void InitialseEmissionFilters(int Index, IFilterWheelInterface *GetFilterWheelInterface);
	void InitialseEmissionSpeed(int Index, IFilterWheelInterface *GetFilterWheelInterface);
	void InitialseEmissionMode(int Index, IFilterWheelInterface *FilterWheelInterface);
	void RetrieveEmissionDescription(IFilterConfigInterface *FilterConfigInterface);

	void ExerciseDichroic( );
	void ExerciseWheel( int Index);
	void SpinTheWheel(unsigned int MinValue, unsigned int MaxValue, IFilterWheelInterface *FilterWheelInterface);

public:
	TTestEmissionAndDichroic( IASDLoader *ASDLoader);
	~TTestEmissionAndDichroic();
};

