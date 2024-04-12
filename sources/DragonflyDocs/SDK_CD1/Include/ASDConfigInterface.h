#ifndef _ASDConfigInterface_H
#define _ASDConfigInterface_H

//----------------------------------------------------------
//----------------------------------------------------------
class IFilterSet
{
public:
   /**
    * Get the Desription of the Filter Set
    * 
    * @param Description retrieves the description for the filter set
    * @param StringLength size of buffer used for retrieval
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetDescription( char *Description, unsigned int StringLength) = 0;
   /**
    * Get the Encoded Desription of the Filter at index position
    * 
    * @param Position index of the filter in the set
    * @param Description retrieves the description for the selected filter
    * @param StringLength size of buffer used for retrieval
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetFilterDescription( unsigned int Position, char *Description, unsigned int StringLength) = 0;
   /**
    * Get the position limits of the Set
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
};
//----------------------------------------------------------
class IFilterRepository
{
public:
   /**
    * Get the interface to the filter set at index Position
    * 
    * @param Position index of the set in the repository
    * @param FiterSet retrieves the interface to the FiterSet
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetFilterSet( unsigned int Position, IFilterSet **FiterSet) = 0;
   /**
    * Get the position limits of the Repository
    * 
    * @param MinPosition
    *               retrieve minimum position for the repository
    * @param MaxPosition
    *               retrieve maximum position for the repository
    * 
    * @return true if successful
    *         false if fails
    */
   virtual bool __stdcall GetLimits( unsigned int &MinPosition, unsigned int &MaxPosition) = 0;
};
//----------------------------------------------------------
class IFilterConfigInterface
{
public:
   /**
    * Get the interface to the selected FW Set
    * 
    * @return interface to Set if successful
    *         0 if fails
    */
  virtual IFilterSet *__stdcall GetFilterSet( ) = 0;
   /**
    * Get the Position of the Set within the repository
    * 
    * @param Position retrieves index 
    *
    * @return true if successful
    *         false if fails
    */
  virtual bool __stdcall GetPositionOfFilterSetInRepository( unsigned int *Position) = 0;
   /**
    * Select a filter  set from the repository 
    * 
    * @param Position index of the set in the repository
    * 
    * @return true if successful
    *         false if fails
    */
  virtual bool __stdcall ExchangeFilterSet( unsigned int Position) = 0;
   /**
    * Get the interface to the filter  repository 
    * 
    * @return interface to repository if successful
    *         0 if fails
    */
  virtual IFilterRepository * __stdcall GetFilterRepository( ) = 0;
};
//----------------------------------------------------------
//----------------------------------------------------------
//----------------------------------------------------------
//----------------------------------------------------------
#endif // _ASDConfigInterface_H
