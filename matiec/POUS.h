#ifndef __POUS_H
#define __POUS_H

#include "accessor.h"
#include "iec_std_lib.h"

// FUNCTION_BLOCK ROTARY_SWITCH
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,READ)
  __DECLARE_VAR(BOOL,ERROR)
  __DECLARE_VAR(INT,OUT)

  // FB private variables - TEMP, private and located variables

} ROTARY_SWITCH;

void ROTARY_SWITCH_init__(ROTARY_SWITCH *data__, BOOL retain);
// Code part
void ROTARY_SWITCH_body__(ROTARY_SWITCH *data__);
#endif //__POUS_H
