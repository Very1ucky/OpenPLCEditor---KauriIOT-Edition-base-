/*******************************************/
/*     FILE GENERATED BY iec2c             */
/* Editing this file is not recommended... */
/*******************************************/
#include "fdsfdsfds.h"
#include "iec_std_lib.h"

// RESOURCE FDSFDSFDS

extern unsigned long long common_ticktime__;

#include "accessor.h"
#include "POUS.h"

#include "Config0.h"
__DECLARE_GLOBAL_LOCATION(BOOL,__QX0_5)
__DECLARE_GLOBAL_LOCATED(BOOL,FDSFDSFDS,LOCAL_VAR)
__DECLARE_GLOBAL(INT,FDSFDSFDS,INT_VAR)
__DECLARE_GLOBAL(TIME,FDSFDSFDS,TIME_VAR)
__DECLARE_GLOBAL(STRING,FDSFDSFDS,STRING_VAR)
__DECLARE_GLOBAL_FB(CTD,FDSFDSFDS,TEMP)
__DECLARE_GLOBAL(TIME,FDSFDSFDS,T0_INT)


BOOL TASK0;
BLINK FDSFDSFDS__INSTANCE1;
#define INSTANCE1 FDSFDSFDS__INSTANCE1

void FDSFDSFDS_init__(void) {
  BOOL retain;
  retain = 0;
  __INIT_GLOBAL_LOCATED(FDSFDSFDS,LOCAL_VAR,__QX0_5,retain)
  __INIT_GLOBAL(BOOL,LOCAL_VAR,__INITIAL_VALUE(__BOOL_LITERAL(TRUE)),retain)
  __INIT_GLOBAL(INT,INT_VAR,__INITIAL_VALUE(10),retain)
  __INIT_GLOBAL(TIME,TIME_VAR,__INITIAL_VALUE(__time_to_timespec(1, 500, 0, 0, 0, 0)),retain)
  __INIT_GLOBAL(STRING,STRING_VAR,__INITIAL_VALUE(__STRING_LITERAL(4,"Test")),retain)
  __INIT_GLOBAL_FB(CTD,TEMP,retain)
  __INIT_GLOBAL(TIME,T0_INT,__INITIAL_VALUE(__time_to_timespec(1, 20, 0, 0, 0, 0)),retain)
  TASK0 = __BOOL_LITERAL(FALSE);
  BLINK_init__(&INSTANCE1,retain);
}

void FDSFDSFDS_run__(unsigned long tick) {
  TASK0 = !(tick % 1);
  if (TASK0) {
    BLINK_body__(&INSTANCE1);
  }
}

