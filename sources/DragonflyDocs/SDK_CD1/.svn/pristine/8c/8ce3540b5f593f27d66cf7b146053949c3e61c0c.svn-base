//---------------------------------------------------------------------------
#include <windows.h>
#pragma hdrstop

#include "ASDModuleHandler.h"

//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
TASD_ModuleHandler::TASD_ModuleHandler( const char *Port, TASDType ASDType)
: CreateASDLoader_( NULL),
  DeleteASDLoader_( NULL),
  ASDLoader_( NULL),
  hDLL_( NULL)
{
  // throw to prevent the class from being created
  // if the library not found
  // or fails to get the function pointer
#if defined _M_X64
  hDLL_ = LoadLibraryA( "AB_ASDx64.dll");
#else
  hDLL_ = LoadLibraryA( "AB_ASD.dll");
#endif
  if( hDLL_ == 0 )
    {
    throw "";
    }

  CreateASDLoader_ = ( TCreateASDLoader)GetProcAddress( hDLL_, "CreateASDLoader");

  if( CreateASDLoader_ == 0 )
    {
    throw "";
    }

  DeleteASDLoader_ = ( TDeleteASDLoader)GetProcAddress( hDLL_, "DeleteASDLoader");
  if( DeleteASDLoader_ == 0 )
    {
    throw "";
    }

  CreateASDLoader_( Port, ASDType, &ASDLoader_);
  if( ASDLoader_ == 0)
    {
    throw "";
    }
}
//---------------------------------------------------------------------------
TASD_ModuleHandler::~TASD_ModuleHandler(void)
{
	try
		{
		if( ASDLoader_ != 0 )
			{
			DeleteASDLoader_( ASDLoader_);
			}
    ASDLoader_ = 0;

		if( hDLL_ != 0 )
      {
			FreeLibrary( hDLL_);
      }
		hDLL_ = 0;
		}
	catch(...)
		{
		}
}
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
