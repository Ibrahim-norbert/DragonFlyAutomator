//---------------------------------------------------------------------------
#ifndef ASDLoaderH
#define ASDLoaderH
//---------------------------------------------------------------------------
#include "types\ASDTypes.h"

//forward for the available Interfaces
//see ASDInterface.h for definition
class IASDInterface;
class IASDInterface2;
class IASDInterface3;

/**
 * Interface used to access the spinning disk or Multi-Modal 
 * units. 
 * Use CreateASDLoader to create an instance of this object. 
 * Use DeleteASDLoader to delete and instance of this object.
 */
class IASDLoader
{
protected:
 //do not allow this to be destroyed externally
  __stdcall ~IASDLoader( void){ };
public:
  /**
   * Get the ASD Interface
   * 
   * @return ASD Interface
   *         NULL if none exists
   */
  virtual IASDInterface * __stdcall GetASDInterface( void) = 0;
  /**
   * Get the ASD Interface 2
   * 
   * @return ASD Interface 2
   *         NULL if none exists
   */
  virtual IASDInterface2 * __stdcall GetASDInterface2( void) = 0;
  /**
   * Get the ASD Interface 3
   * 
   * @return ASD Interface 3
   *         NULL if none exists
   */
  virtual IASDInterface3 * __stdcall GetASDInterface3( void) = 0;
};

/**
 * Create an instance of the ASDLoader
 * Use this object to query the available interfaces
 * Must use DeleteASDLoader to destroy this object
 * This version connects to several spinning disk and Multi-Modal devices
 * For ease of integration, interface is the same as the ALC device
 * 
 * @param Port
 *               RS232 (or USB Virtual) port for the device 
 * 
 * @param ASDType
 *               type of device  
 *               see TASDType for available device types 
 * 
 * @param ASDLoader
 *               retrieves interface to the object that is created
 * 
 * @return true if successful
 *         false if fails
 */
extern "C" bool __stdcall CreateASDLoader( const char *Port, TASDType ASDType, IASDLoader **ASDLoader);
/**
 * Delete an instance of the ASDLoader
 * Note this will automatically disconnect the device
 * 
 * @param ASDLoader
 *                  interface to an existing ASDLoader
 * 
 * @return true if successful
 *         fals if fails
 */
extern "C" bool __stdcall DeleteASDLoader( IASDLoader *ASDLoader);

#endif
