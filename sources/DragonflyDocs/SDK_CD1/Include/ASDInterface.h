#ifndef _ASDInterface_H
#define _ASDInterface_H

#include "types\ConfocalModeTypes.h"
#include "types\FilterWheelSpeedTypes.h"
#include "types\ShutterTypes.h"
#include "types\LensTypes.h"
#include "types\ScopeTypes.h"
#include "ComponentInterface.h"

//-----------------------------------------------------------
//-----------------------------------------------------------
 //-----------------------------------------------------------
//-----------------------------------------------------------
/**
 * Basic interface for the standard items available on a 
 * spinning disk or multi modal device
 * provides access to the available properties
 */
class IASDInterface
  {
public:
  virtual __stdcall ~IASDInterface( void){ };
  /**
   * 
   * @return 
   */
  virtual const char *__stdcall GetSerialNumber( void) const = 0;
  /**
   * retrieve the product ID for the device
   * 
   * @return product ID
   */
  virtual const char *__stdcall GetProductID( void) const = 0;
  /**
   * retrieve Software version for the device
   * 
   * @return software version
   */
  virtual const char *__stdcall GetSoftwareVersion( void) const = 0;
  /**
   * retrieve software build time
   * 
   * @return software build stime
   */
  virtual const char *__stdcall GetSoftwareBuildTime( void) const = 0;



  /**
   * check availability of the Dichroic
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsDichroicAvailable( void) = 0;
  /**
   * Get the Dichroic Interface
   * 
   * @return Dichroic Interface 
   *         NULL if none exists
   */
  virtual IDichroicMirrorInterface *__stdcall GetDichroicMirror( void) = 0;

  /**
   * check availability of the Disk
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsDiskAvailable( void) = 0;
  /**
   * Get the Disk Interface
   * 
   * @return Disk Interface
   *         NULL if none exists
   */
  virtual IDiskInterface *__stdcall GetDisk( void) = 0;

  /**
   * check availability of the Filter Wheel
   * 
   * @param FilterIndex
   *               Index for the wheel
   *               see TWheelIndex
   * 
   * @return true if present
   *         false if not
   */
  virtual bool __stdcall IsFilterWheelAvailable( TWheelIndex FilterIndex) = 0;
  /**
   * Get the Filter Wheel Interface
   * 
   * @param FilterIndex
   *               Index for the wheel
   *               see TWheelIndex
   * 
   * @return Filter Wheel Interface
   *         NULL if none exists
   */
  virtual IFilterWheelInterface *__stdcall GetFilterWheel( TWheelIndex FilterIndex) = 0;

  /**
   * check availability of the Bright Field Port
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsBrightFieldPortAvailable( void) = 0;

  /**
   * Get the Bright Field Interface
   * 
   * @return Bright Field Interface
   *         NULL if none exists
   */
  virtual IConfocalModeInterface2 *__stdcall GetBrightFieldPort( void) = 0;
  
/**
   * Get the newer Disk Interface
   * 
   * @return Disk Interface
   *         NULL if none exists
   */
  virtual IDiskInterface2 *__stdcall GetDisk_v2( void) = 0;
  };
//-----------------------------------------------------------
//-----------------------------------------------------------
/**
 * Extending IASDinterface for none standard properties
 */
class IASDInterface2 : public IASDInterface
  {
public:
  /**
   * check availability of the Aperture
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsApertureAvailable( void) = 0;
  /**
   * Get the Aperture Interface
   * 
   * @return Aperture Interface
   *         NULL if none exists
   */
  virtual IApertureInterface *__stdcall GetAperture( void) = 0;

  /**
   * check availability of the Camera port mirror
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsCameraPortMirrorAvailable( void) = 0;
  /**
   * Get the Camera port mirror Interface
   * 
   * @return Camera port mirror Interface
   *         NULL if none exists
   */
  virtual ICameraPortMirrorInterface *__stdcall GetCameraPortMirror( void) = 0;

  /**
   * check availability of the magnification lens
   * see TLensType
   * 
   * @param LensIndex index of the lens
   * 
   * @return true if present
   *         false if not
   */
  virtual bool __stdcall IsLensAvailable( TLensType LensIndex) = 0;
  /**
   * Get the magnification lens Interface
   * 
   * @param LensIndex index of the lens
   * 
   * @return magnification lens
   *         Interface NULL if none exists
   */
  virtual ILensInterface *__stdcall GetLens( TLensType LensIndex) = 0;

  /**
   * Get the Model ID for the device
   * 
   * @return Model ID
   *         0 if none exists
   */
  virtual int __stdcall GetModelID( void) = 0;
};
//-----------------------------------------------------------
//-----------------------------------------------------------
/**
 * Extending IASDInterface2 for Multi-Modal properties
 */
class IASDInterface3 : public IASDInterface2
  {
public:
  /**
   * check availability of the Illumination Lens
   * 
   * @param LensIndex index of the lens
   *  
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsIllLensAvailable( TLensType LensIndex) = 0;
  /**
   * Get the Illumination Lens Interface
   * 
   * @param LensIndex index of the lens
   * 
   * @return Illumination Lens Interface
   *         NULL if none exists
   */
  virtual IIllLensInterface *__stdcall GetIllLens( TLensType LensIndex) = 0;

  /**
   * check availability of the EPI polariser
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsEPIPolariserAvailable( void) = 0;
  /**
   * Get the EPI polariser Interface
   * 
   * @return EPI polariser Interface
   *         NULL if none exists
   */
  virtual IEPIPolariserInterface *__stdcall GetEPIPolariser( void) = 0;
  /**
   * check availability of the TIRF Polariser
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsTIRFPolariserAvailable( void) = 0;
  /**
   * Get the TIRF Polariser Interface
   * 
   * @return TIRF Polariser Interface
   *         NULL if none exists
   */
  virtual ITIRFPolariserInterface *__stdcall GetTIRFPolariser( void) = 0;
  /**
   * check availability of the Emission Iris
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsEmissionIrisAvailable( void) = 0;
  /**
   * Get the Emission Iris Interface
   * 
   * @return Emission Iris Interface
   *         NULL if none exists
   */
  virtual IEmissionIrisInterface *__stdcall GetEmissionIris( void) = 0;
  /**
   * check availability of the Super Resolution components
   * 
   * @return true if present 
   *         false if not
   */
  virtual bool __stdcall IsSuperResAvailable( void) = 0;
  /**
   * Get the SuperRes Interface
   * 
   * @return SuperRes Interface
   *         NULL if none exists
   */
  virtual ISuperResInterface *__stdcall GetSuperRes( void) = 0;

  /**
   * check availability of the Imaging Mode interface
   * this extends Bright Field Port to include TIRF
   *
   * @return true if present
   *         false if not
   */
  virtual bool __stdcall IsImagingModeAvailable( void) = 0;

  /**
   * Get the Imaging Mode Interface
   * this extends Imaging Modes to include TIRF
   *
   * @return Imaging Mode Interface
   *         NULL if none exists
   */
  virtual IConfocalModeInterface3 *__stdcall GetImagingMode( void) = 0;

  /**
   * check availability of the TIRF interface
   *
   * @return true if present
   *         false if not
   */
  virtual bool __stdcall IsTIRFAvailable( void) = 0;

  /**
   * Get the TIRF Interface
   *
   * @return TIRF Interface
   *         NULL if none exists
   */
  virtual ITIRFInterface *__stdcall GetTIRF( void) = 0;

  /**
   * Get the Status Interface
   *
   * @return Status Interface
   *         NULL if none exists - not expected
   */
  virtual IStatusInterface *__stdcall GetStatus( void) = 0;

  /**
   * Get the FrontPanelLED Interface
   *
   * @return FrontPanelLED Interface
   *         NULL if none exists - not expected
   */
  virtual IFrontPanelLEDInterface *__stdcall GetFrontPanelLED( void) = 0;

};
//-----------------------------------------------------------
//-----------------------------------------------------------
#endif // _ASDInterface_H

