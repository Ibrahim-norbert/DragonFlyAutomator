#ifndef _ConfocalModeTypes_H
#define _ConfocalModeTypes_H

/**
 * Various imaging modalities available for the Dragonfly units 
 */
typedef enum EConfocalMode
{
  bfmNone,
  /** High Contrast */
  bfmConfocalHC,
  /** Wide field */
  bfmWideField,
  /** High Sectioning */
  bfmConfocalHS,
  /** TIRF mode for Dragonfly */
  bfmTIRF 
}TConfocalMode;

#endif
