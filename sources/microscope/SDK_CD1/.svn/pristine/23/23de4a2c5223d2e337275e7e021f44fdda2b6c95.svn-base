#ifndef _FilterWheelSpeedTypes
#define _FilterWheelSpeedTypes

/**
 * Filter wheel speed Options, 
 * move time between adjacent filter position
 */
typedef enum _TFilterWheelSpeed
  {
    /** 200 ms */
    FWS200,
    /** 100 ms */
    FWS100,
    /** 66 ms */
    FWS66, 
    /** 33-40 ms */
    FWS33
  }TFilterWheelSpeed;

/**
 * Filter wheel Mode can be seen as an alternative to selecting 
 * the wheel speed. Here fixed speed and delay combinations 
 * provide fexible options to ease user selection 
 */
typedef enum _TFilterWheelMode  
  {
    /** unknown state caused when speed interface is used to override these settings */
    FWMUnknown,     
    /** FWS33 with no Delay */
    FWMHighSpeed,   
    /** FWS33 with 10ms Delay */
    FWMHighQuality, 
    /** FWS200 with no delay to ensure minimum vibration */
    FWMLowVibration 
  }TFilterWheelMode;

#endif // _FilterWheelSpeedTypes

