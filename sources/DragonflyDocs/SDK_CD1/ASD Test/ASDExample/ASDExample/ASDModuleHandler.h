//---------------------------------------------------------------------------
#ifndef ASDModuleHandlerH
#define ASDModuleHandlerH
//---------------------------------------------------------------------------

#include <windows.h>

#include "types\ASDTypes.h"
class IASDLoader;//fwrd


/**
 * RAII Utility class to help with loading the ASD SDK
 * Feel free to reuse and modify as required for your applications
 */
class TASD_ModuleHandler
{
private:
  HMODULE hDLL_;

  typedef int (__stdcall *TCreateASDLoader)( const char *Port, TASDType ASDType, IASDLoader **ASDLoader);
  typedef int (__stdcall *TDeleteASDLoader)( IASDLoader *ASDLoader);
  TCreateASDLoader CreateASDLoader_;
  TDeleteASDLoader DeleteASDLoader_;

  IASDLoader *ASDLoader_;
public:

  /**
   * Constructor will load the SDK and attempt to connect to the Dragonfly/Damselfy device
   * Will throw an exception if the device does not connect
   * 
   * @param Port    COM Port for the device
   *                Uses USB Virtual comport (see device driver folder)
   * @param ASDType Type of device, currently Dragonfly/Damselfly
   */
  TASD_ModuleHandler( const char *Port, TASDType ASDType);
  /**
   * ensure that the device is disconnected and library released
   */
  ~TASD_ModuleHandler( );
  /**
   * Retrieve the interface for communicating with the device
   * 
   * @return interface to loader class
   */
  IASDLoader *GetASDLoader( ){ return ASDLoader_;};
};
#endif
