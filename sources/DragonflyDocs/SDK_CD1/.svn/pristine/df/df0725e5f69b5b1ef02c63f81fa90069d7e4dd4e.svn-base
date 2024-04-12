#ifndef _ComponentInterface_H
#define _ComponentInterface_H

#include "types\ConfocalModeTypes.h"
#include "types\FilterWheelSpeedTypes.h"
#include "types\ShutterTypes.h"
#include "types\LensTypes.h"
#include "types\ScopeTypes.h"
//-----------------------------------------------------------
//-----------------------------------------------------------
//-----------------------------------------------------------
//-----------------------------------------------------------
class IFilterWheelSpeedInterface;
class IFilterSet;
class IFilterConfigInterface;
class IEmissionIrisConfigInterface;
class ITIRFConfigInterface;
class IFilterWheelModeInterface;

class INotify
{
public:
  virtual void __stdcall Notify( void) = 0;
};
//-----------------------------------------------------------
//-----------------------------------------------------------
typedef enum EWheelIndex
{
  WheelIndex1 = 1,
  WheelIndex2
}TWheelIndex;

//-----------------------------------------------------------
//-----------------------------------------------------------
/**
 * interface to control shutter devices
 */
class IShutterInterface
{
 public:
   virtual __stdcall ~IShutterInterface( void){ };
   /**
    * open shutter 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall OpenShutter( void) = 0;
   /**
    * close shutter 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall CloseShutter( void) = 0;
   /**
    * get shutter state 
    * 
    * @return true if open
    *         false if closed
    */
   virtual bool __stdcall IsShutterOpen( void) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control ND Filter
 */
class INDFilterInterface
{
 public:
   virtual __stdcall ~INDFilterInterface( void){ };
   /**
    * move ND filter into the light path 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall MoveNDFilterInLightPath( void) = 0;
   /**
    * move ND filter out of the light path 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall MoveNDFilterOutOfLightPath( void) = 0;
   /**
    * get state of the ND filter  
    * 
    * @return true if in the light path
    *         false if out of the light path
    */
   virtual bool __stdcall IsNDFilterInLightPath( void) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control disk 
 */
class IDiskInterface
{
 public:
   virtual __stdcall ~IDiskInterface( void){ };
   /**
    * Get the speed of the confocal disk
    * 
    * @param Speed  retrieve the speed in rpm
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetSpeed( unsigned int &Speed) = 0;
   /**
    * Set the speed of the confocal disk
    * 
    * @param Speed  desired speed in rpm
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetSpeed( unsigned int Speed) = 0;
   /**
    * Increase the speed of the confocal disk by one rpm
    * 
    * @param Speed  desired speed in rpm
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall IncreaseSpeed( void) = 0;
   /**
    * decrease the speed of the confocal disk by one rpm
    *  
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall DecreaseSpeed( void) = 0;
   /**
    * Get the speed limits of the confocal disk
    * 
    * @param Min    retrieve minimum speed for the disk
    * @param Max    retrieve maximum speed for the disk
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &Min, unsigned int &Max) = 0;
   /**
    * start spinning the confocal disk at the last speed
    *  
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall Start( void) = 0;
   /**
    * stop spinning the confocal disk 
    *  
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall Stop( void) = 0;
   /**
    * Test of the confocal disk is spinning
    *  
    * @return true if spinning
    *         false if stopped
    */
   virtual bool __stdcall IsSpinning( void) = 0;
};
/**
 * extending disk interface to get sector rate 
 */
class IDiskInterface2 : public IDiskInterface
{
public:
   virtual __stdcall ~IDiskInterface2( void){ };

   /**
    * get the number of scans that can be achieved with a full revolution of the disk
    * i.e. full sweep of the disk pattern over the image
    * note some disks require multiple sectors for a full scan pattern
    *  
    * @param NumberOfScans  retrieves the number of scans per revolution
    *
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetScansPerRevolution( unsigned int *NumberOfScans) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Dichroic Mirror 
 */
class IDichroicMirrorInterface
{
 public:
   virtual __stdcall ~IDichroicMirrorInterface( void){ };
   /**
    * Get the position of the dichroic mirror
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the dichroic mirror
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the dichroic mirror
    * 
    * @param MinPosition
    *               retrieve minimum position for the dichroic mirror
    * @param MaxPosition
    *               retrieve maximum position for the dichroic mirror
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;

   /**
    * Get the configuration innterface of the dichroic mirror
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterConfigInterface * __stdcall GetFilterConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Filter Wheel 
 */
class IFilterWheelInterface
{
 public:
   virtual __stdcall ~IFilterWheelInterface( void){ };
   /**
    * Get the position of the Filter Wheel
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the Filter Wheel
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the Filter Wheel
    * 
    * @param MinPosition
    *               retrieve minimum position for the Filter Wheel
    * @param MaxPosition
    *               retrieve maximum position for the Filter Wheel
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
   //virtual bool Home( void) = 0;do we need this?


   /**
    * Get the speed interface of the filter wheel
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterWheelSpeedInterface * __stdcall GetFilterWheelSpeedInterface( ) = 0;
   
   
   /**
    * Get the configuration interface of the filter wheel
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterConfigInterface * __stdcall GetFilterConfigInterface( ) = 0;

   /**
    * Get the mode interface of the filter wheel
	* used to control the speed of the wheel by use case
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterWheelModeInterface * __stdcall GetFilterWheelModeInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Filter Wheel Speed
 */
class IFilterWheelSpeedInterface
{
public:
  virtual __stdcall ~IFilterWheelSpeedInterface( void){ };
  /**
   * Does the wheel support the highest speed (FWS33)
   * 
   * @return true if supports high speed
   *         false if does not
   */
  virtual bool __stdcall IsHighSpeedAvailable( void) = 0;
  /**
   * get the speed for the filter wheel movement 
   * 
   * @param FilterWheelSpeed
   *               retrieve the speed (see TFilterwheelspeed)
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall GetSpeed( TFilterWheelSpeed &FilterWheelSpeed) = 0;
  /**
   * set the speed for the filter wheel movement 
   * 
   * @param FilterWheelSpeed
   *               desired speed (see TFilterWheelSpeed)
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall SetSpeed( TFilterWheelSpeed FilterWheelSpeed) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Filter Wheel mode
 * used to control the speed of the wheel by use case
*/
class IFilterWheelModeInterface
{
public:
  virtual __stdcall ~IFilterWheelModeInterface( void){ };
  /**
   * get the Mode for the filter wheel movement 
   * 
   * @param FilterWheelMode
   *               retrieve the mode (see TFilterwheelMode)
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall GetMode( TFilterWheelMode &FilterWheelMode) = 0;
  /**
   * set the Mode for the filter wheel movement 
   * 
   * @param FilterWheelMode
   *               desired mode (see TFilterWheelMode)
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall SetMode( TFilterWheelMode FilterWheelMode) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control active Disk pattern
 * simple single pattern disk
*/
class IConfocalModeInterface
{
public:
  virtual __stdcall ~IConfocalModeInterface( void){ };
  /**
   * set the confocal disk position as undefined
   * Do not use - used for initialisation 
   *  
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall ModeNone( void) = 0;
  /**
   * move the confocal disk into the light path
   * for multi pattern disk this indicates high contrast
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall ModeConfocalHC( void) = 0;
  /**
   * move the confocal disk out of the light path
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall ModeWideField( void) = 0;
  /**
   * Get the state of the the confocal disk<p>
   * BrightFieldMode retirve position (see TConfocalMode)
   * 
   * @param BrightFieldMode
   *               retrieve position (see TCOnfocalMode)
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall GetMode( TConfocalMode &BrightFieldMode) = 0;
};
//-----------------------------------------------------------
/**
 * extends IConfocalModeInterface to facilitate extra Disk pattern
*/
class IConfocalModeInterface2 : public IConfocalModeInterface
{
public:
  virtual __stdcall ~IConfocalModeInterface2( void){ };
  //set defaults to not available
  /**
   * move the high sectioning portion of the confocal disk into 
   * the light path, provides the best confocality 
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall ModeConfocalHS( void) = 0;
  /**
   * Does the confocal disk have a high sectioning portion
   * 
   * @return true if supports high sectioning
   *         false if does not
   */
  virtual bool __stdcall IsModeConfocalHSAvailable( void) = 0;
  /**
   * Is the first disk position of the confocal disk for high
   * sectioning (25um)
   * 
   * @return true if first position is for high sectioning
   *         false if is not
   */
  virtual bool __stdcall IsFirstDisk25um( void) = 0;
  /**
   * Retrieve the Pin Hole Size for the Disk Mode
   * 
   * @param ConfocalMode
   *               Specifies the mode for size retrieval
   *               Valid modes - bfmConfocalHC & bfmConfocalHS  
   * @param PinHoleSize_um
   *               retrieves pin hole size
   *               
   * 
   * @return true if supports mode
   *         false if does not
   */
  virtual bool __stdcall GetPinHoleSize_um( TConfocalMode ConfocalMode, int *PinHoleSize_um) = 0;
};
//-----------------------------------------------------------
/**
 * extends IConfocalModeInterface2 to facilitate extra imaging mode (TIRF)
*/
class IConfocalModeInterface3 : public IConfocalModeInterface2
{
public:
  virtual __stdcall ~IConfocalModeInterface3( void){ };
  /**
   * move the confocal disk out of the light path 
   * and prepare for TIRF imaging
   * 
   * @return true if successful
   *         false if fails
   */
  virtual bool __stdcall ModeTIRF( void) = 0;
  /**
   * Is the unit TIRF capable
   * 
   * @return true if supports TIRF
   *         false if does not
   */
  virtual bool __stdcall IsModeTIRFAvailable( void) = 0;
  /**
   * Get the state of the the confocal modes
   * general query for available modes
   * 
   * @param Mode
   *               Specify mode to query(see TConfocalMode)
   * 
   * @return true if available
   *         false if not
   */
  virtual bool __stdcall IsConfocalModeAvailable( TConfocalMode Mode) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Aperture
*/
class IApertureInterface
{
 public:
   virtual __stdcall ~IApertureInterface( void){ };
   /**
    * Get the position of the Aperture
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the Aperture
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the Aperture
    * 
    * @param MinPosition
    *               retrieve minimum position for the Aperture
    * @param MaxPosition
    *               retrieve maximum position for the Aperture
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
   /**
    * check availability of the split field aperture
    * 
    * @return true if present 
    *         false if not
    */
   virtual bool __stdcall IsSplitFieldAperturePresent( void) = 0;

   /**
    * Get the configuration interface of the Aperture
	* (provides details for each position) 
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterSet * __stdcall GetApertureConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control camera port mirror
*/
class ICameraPortMirrorInterface
{
 public:
   virtual __stdcall ~ICameraPortMirrorInterface( void){ };
   /**
    * Get the position of the camera port mirror
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the camera port mirror
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the camera port mirror
    * 
    * @param MinPosition
    *               retrieve minimum position for the camera port
    *               mirror
    * @param MaxPosition
    *               retrieve maximum position for the camera port
    *               mirror
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
   /**
    * check availability of the split field mirror
    * 
    * @return true if present 
    *         false if not
    */
   virtual bool __stdcall IsSplitFieldMirrorPresent( void) = 0;

    /**
    * Get the configuration interface of the Camera Port Mirror
	* (provides details for each position)
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterSet * __stdcall GetCameraPortMirrorConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control active magnification lens for available camera ports
*/
class ILensInterface
{
 public:
   virtual __stdcall ~ILensInterface( void){ };
   /**
    * Get the position of the magnification lens
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the magnification lens
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the magnification lens
    * 
    * @param MinPosition
    *               retrieve minimum position for the magnification
    *               lens
    * @param MaxPosition
    *               retrieve maximum position for the magnification
    *               lens
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;

   /**
    * Get the configuration interface of the Lens
	* (provides details of each position)
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterSet * __stdcall GetLensConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control active magnification lens for illumination
 * note that this can be limited deppending on the current modality
*/
class IIllLensInterface
{
 public:
 public:
   virtual __stdcall ~IIllLensInterface( void){ };
   /**
    * Get the position of the magnification lens
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the magnification lens
    * 
    * @param Position desired position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the magnification lens
    * 
    * @param MinPosition
    *               retrieve minimum position for the magnification
    *               lens
    * @param MaxPosition
    *               retrieve maximum position for the magnification
    *               lens
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;

   /**
    * check whether restriction is enabled
	* will be enabled for specific imaging modes
    * 
    * @return true if restricted
    *         false if not
    */
   virtual bool __stdcall IsRestrictionEnabled( void) = 0;
   /**
    * Get the position limits of the magnification lens
    * 
    * @param MinPosition
    *               retrieves restricted minimum position for the magnification
    *               lens
    * @param MaxPosition
    *               retrieves restricted maximum position for the magnification
    *               lens
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetRestrictedRange( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
   /**
    * register to be notified when range restriction is enabled
    * 
    * @param Notify
    *               Interface for notification
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall RegisterForNotificationOnRangeRestriction( INotify *Notify) = 0;

   /**
    * Get the configuration interface of the Lens
	* (provides details of each position)
	*
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual IFilterSet * __stdcall GetLensConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control limits for the active magnification lens 
 * used when a mode would render the lens useless
*/
class IRestrictionInterface
{
public:
   virtual __stdcall ~IRestrictionInterface( void){ };
   /**
    * Remove the lens restriction
    * 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall RemoveRestriction( void) = 0;
   /**
    * Set the position limits of the magnification lens
    * 
    * @param MinPosition
    *               retrieves restricted minimum position for the magnification
    *               lens
    * @param MaxPosition
    *               retrieves restricted maximum position for the magnification
    *               lens
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetRestriction( unsigned int MinPosition, unsigned int MaxPosition) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control polariser used in conjunction with EPI illumination
*/
class IEPIPolariserInterface
{
 public:
   virtual __stdcall ~IEPIPolariserInterface( void){ };
   /**
    * Get the position of the epi polariser
    * 
    * @param Position retrieve the position
    *                 1 in light path
    *                 2 not in light path
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the epi polariser
    * 
    * @param Position desired position
    *                 1 in light path
    *                 2 not in light path
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the epi polariser
    * 
    * @param MinPosition
    *               retrieve minimum position for the epi polariser
    * @param MaxPosition
    *               retrieve maximum position for the epi polariser
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control polariser used in comjunction with TIRF illlumination
*/
class ITIRFPolariserInterface
{
 public:
   virtual __stdcall ~ITIRFPolariserInterface( void){ };
   /**
    * Get the position of the tirf polariser
    * 
    * @param Position retrieve the position
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the tirf polariser
    * 
    * @param Position desired position
    *                 1 in light path
    *                 2 not in light path
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the tirf polariser
    * 
    * @param MinPosition
    *               retrieve minimum position for the tirf
    *               polariser
    * @param MaxPosition
    *               retrieve maximum position for the tirf
    *               polariser
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
};
//-----------------------------------------------------------
/**
 * interface to activate Super Resolution option
*/
class ISuperResInterface
{
 public:
   virtual __stdcall ~ISuperResInterface( void){ };
   /**
    * Get the position of the Super Resolution
    * 
    * @param Position retrieve the position
    *                 1 in light path
    *                 2 not in light path
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPosition( unsigned int &Position) = 0;
   /**
    * Set the position of the Super Resolution
    * 
    * @param Position desired position
    *                 1 in light path
    *                 2 not in light path
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPosition( unsigned int Position) = 0;
   /**
    * Get the position limits of the Super Resolution
    * 
    * @param MinPosition
    *               retrieve minimum position for the Super
    *               Resolution
    * @param MaxPosition
    *               retrieve maximum position for the Super
    *               Resolution
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control Emission iris
 */
class IEmissionIrisInterface
{
 public:
   virtual __stdcall ~IEmissionIrisInterface( void){ };


   /**
    * Get the parameters that affect the Emission Iris
    * 
    * @param Magnification
    *               retrieves Magnification 
    * @param NumericalAperture
    *               retrieves Numerical Aperture 
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetIrisConfig( int *Magnification, double *NumericalAperture) = 0;
   
   /**
    * Set the parameters that affect the Emission Iris
    * 
    * @param Magnification
    *               Magnification for the current objective
    * @param NumericalAperture
    *               Numerical Aperture for the current objective
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetIrisConfig( int Magnification, double NumericalAperture) = 0;
   /**
    * Get the configuration interface of the Emission Iris
    * 
    * 
    * @return valid interface if successful
    *         0 if fails
    */
    virtual IEmissionIrisConfigInterface * __stdcall GetEmissionIrisConfigInterface( ) = 0;
};
//-----------------------------------------------------------
/**
 * interface to control TIRF option
*/
class ITIRFInterface
{
 public:
   virtual __stdcall ~ITIRFInterface( void){ };
   /**
    * Get the optical parameters which affect TIRF
    * 
    * @param Magnification
    *               retrieves current Magnification
    * @param NumericalAperture
    *               retrieve current Numerical Aperture
    * @param RefractiveIndex
    *               retrieves current Refractive index
    * @param Scope_ID
    *               retrieves Scope ID (see TScopeType)
    *               Leica(1), Nikon(2), Olympus(3), Zeiss(4)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetOpticalPathway( int *Magnification,  double *NumericalAperture, double *RefractiveIndex, int *Scope_ID) = 0;
   /**
    * Get the extreme wavelengths currently used for TIRF
    * These adjust the internal optics and help to normalise the 
    * penetration across wavelengths
    * 
    * @param MinWavelength_nm
    *               retrieves minimum wavelength
    * @param MaxWavelength_nm
    *               retrives the maximum wavelength
    * 
    * @return true if succesful
    *         false if fails
    */
   virtual bool __stdcall GetBandwidth( int *MinWavelength_nm, int *MaxWavelength_nm) = 0;
   /**
    * Get the current penetration depth for TIRF
    * 
    * @param Depth_nm retirves the current depth in nano meters
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPenetration_nm( int *Depth_nm) = 0;
   /**
    * Get the current Oblique Angle for TIRF
    * 
    * @param ObliqueAngle_mdeg
    *               retrieves current Oblique Angle in milli degrees
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetObliqueAngle_mdeg( int *ObliqueAngle_mdeg) = 0;
   /**
    * Get the current Offset (Fine Adjustment) for TIRF 
    * Allows the user to adjust the critical angle to account for 
    * changes in sample type 
    * 
    * @param Offset retrieves the current offset (no units)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetOffset( int *Offset) = 0;
   /**
    * Get the current Mode for TIRF
    * 
    * @param TIRFMode retirves the current Mode
    *                 Penetration ( 0),
    *                 Oblique( 1),
    *                 AdjustOffset (2)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetTIRFMode( int *TIRFMode) = 0;

   /**
    * Set the optical parameters which affect TIRF
    * use the values retrieved from the unit (see GetOpticalPathway)<p>
    * 
    * @param Magnification
    *                 Magnification for the current Objective
    *                 generally limited to 60, 63, 100, 150
    * @param NumericalAperture
    *                 Numerical Aperture for the current Objective
    *                 1.40 to 1.70
    * @param RefractiveIndex
    *                 Refractive index for the current sample
    *                 1.33 to 1.41
    * @param Scope_ID
    *                 retrieves Scope ID (see TScopeType), helps
    *                 detremine the Tube Length for the current scope
    *                 (mm) Nikon & Zeiss 200, Olympus 180, Leica 160
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetOpticalPathway( int Magnification,  double NumericalAperture, double RefractiveIndex, int Scope_ID) = 0;
   /**
    * Set the extreme wavelengths for the TIRF setup
    * These adjust the internal optics and help to normalise the 
    * penetration across wavelengths
    *  
    * @param MinWavelength_nm
    *               minimum expected wavelength (>=400)
    * @param MaxWavelength_nm
    *               maximum expected wavelength (<=1000)
    *               (see GetBandwidthLimit)
    * 
    * @return true if succesful
    *         false if fails
    */
   virtual bool __stdcall SetBandwidth( int MinWavelength_nm, int MaxWavelength_nm) = 0;
   /**
    * Set the penetration depth for TIRF
    * 
    * @param Depth_nm sets the depth in nano meters
    *                 100 to 1000 (see GetPenetrationLimit)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetPenetration_nm( int Depth_nm) = 0;
   /**
    * Set the current Oblique Angle for TIRF
    * 
    * @param ObliqueAngle_mdeg
    *               sets the Oblique Angle in milli degrees
    *               100 to 20000 (see GetObliqueAngleLimit)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetObliqueAngle_mdeg( int ObliqueAngle_mdeg) = 0;
   /**
    * Set the current Offset (Fine Adjustment) for TIRF
    * Allows the user to adjust the critical angle to account for 
    * changes in sample type 
    *  
    * @param Offset sets the current offset (no units)
    *               -900 to 900 (see GetObliqueAngleLimit)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetOffset( int Offset) = 0;
   /**
    * Set the current Mode for TIRF
    * 
    * @param TIRFMode sets the current Mode
    *                 Penetration ( 0),
    *                 Oblique( 1),
    *                 AdjustOffset (2)
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall SetTIRFMode( int TIRFMode) = 0;


   /**
    * Get the configuration interface of the TIRF component
    * 
    * @return valid interface if successful
    *         0 if fails
    */
   virtual ITIRFConfigInterface * __stdcall GetTIRFConfigInterface( ) = 0;
   /**
    * Get the min and max wavelengths which can be used with TIRF
    * 
    * @param MinWavelength_nm
    *               retrieves minimum wavelength
    * @param MaxWavelength_nm
    *               retrives the maximum wavelength
    *
    * @return true if succesful
    *         false if fails
    */
   virtual bool __stdcall GetBandwidthLimit( int *MinWavelength_nm, int *MaxWavelength_nm) = 0;
   /**
    * Get the range for penetration depth for TIRF
    *
    * @param MinDepth_nm
    *               retrieves minimum Depth
    * @param MaxDepth_nm
    *               retrives the maximum Depth
    *
    *
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetPenetrationLimit( int *MinDepth_nm, int *MaxDepth_nm) = 0;
   /**
    * Get the range for Oblique Angle for TIRF
    *
    * @param MinOblique_mdeg
    *               retrieves minimum Angle
    * @param MaxOblique_mdeg
    *               retrives the maximum Angle
    *
    *
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetObliqueAngleLimit( int *MinObliqueAngle_mdeg, int *MaxObliqueAngle_mdeg) = 0;
   /**
    * Get the range for Offset for TIRF
    *
    * @param MinOffset
    *               retrieves minimum Offset
    * @param MaxOffset
    *               retrives the maximum Offset
    *
    *
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetOffsetLimit( int *MinOffset, int *MaxOffset) = 0;
};
//-----------------------------------------------------------
/**
 * Interface to detect RFID status and control the panel LEDs 
 */
class IStatusInterface
{
public:
  virtual __stdcall ~IStatusInterface(){};
  /**
   * get Status Code
   *     Note if Wheel is present then the wheel Swap option should be defeated
   *         Read error should show a warning icon or similar by the failed item
   * 
   * @param Status
   *               retrieves status Code
   *               Bit 0 = External Disk Sync
   *               Bit 4 = RFID Wheel 1 Present
   *               Bit 5 = RFID Wheel 1 Read Error
   *               Bit 6 = RFID Wheel 2 Present
   *               Bit 7 = RFID Wheel 2 Read Error
   *               Bit 8 = RFID Camera Port Present
   *               Bit 9 = RFID Camera Port Read Error
   * 
   * @return true if successful
   *         false if not
   */
  virtual bool __stdcall GetStatusCode( unsigned int *Status) = 0;

  /**
   * check Standby State
   * note that the button on the front panel may be used to put
   * the unit into standby mode
   * 
   * @return true if active
   *         false if not
   */
  virtual bool __stdcall IsStandbyActive( void) = 0;

  /**
   * Activate Standby State
   *
   * @return true if successful
   *         false if not
   */
  virtual bool __stdcall ActivateStandby( void) = 0;
  /**
   * Wake up the unit
   *
   * @return true if successful
   *         false if not
   */
  virtual bool __stdcall WakeFromStandby( void) = 0;
};
/**
 * interface to controll the front panel LED
 * Allows this to be turned off if required
 */
class IFrontPanelLEDInterface
{
public:
  virtual __stdcall ~IFrontPanelLEDInterface(){};
  /**
   * check front Panel LED state
   * LED is illuminated when active
   * 
   * @return true if active
   *         false if not
   */
  virtual bool __stdcall IsFrontPanelLEDActive( void) = 0;
  /**
   * Activate Front Panel LED
   * 
   * @return true if successful
   *         false if not
   */
  virtual bool __stdcall ActivateFrontPanelLED( void) = 0;
  /**
   * Disable the front Panel LED
   *
   * @return true if successful
   *         false if not
   */
  virtual bool __stdcall DisableFrontPanelLED( void) = 0;
};
//-----------------------------------------------------------
//-----------------------------------------------------------
//-----------------------------------------------------------
//-----------------------------------------------------------
#endif // _ASDInterface_H

