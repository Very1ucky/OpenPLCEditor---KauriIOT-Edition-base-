
#ifndef __POUS_H
#define __POUS_H

#include "accessor.h"
#include "iec_std_lib.h"

__DECLARE_STRUCT_TYPE(DATATYPE0,
  BOOL BOOL1;
  )
// PROGRAM BLINK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_LOCATED(BOOL,BLINK_LED)
  __DECLARE_LOCATED(BOOL,BLINK_LED0)
  TON TON0;
  TOF TOF0;
  __DECLARE_VAR(STRING,TOF2)
  __DECLARE_LOCATED(INT,TOF1)
  __DECLARE_VAR(DATE,TOF3)
  __DECLARE_VAR(REAL,TOF4)
  __DECLARE_VAR(TIME,TOF5)
  __DECLARE_VAR(TOD,TOF6)
  __DECLARE_VAR(DT,TOF7)
  __DECLARE_VAR(BOOL,_TMP_NOT10_OUT)

} BLINK;

void BLINK_init__(BLINK *data__, BOOL retain);
// Code part
void BLINK_body__(BLINK *data__);
// PROGRAM EQ_TIME_COMP_AND_CALC_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(STRING,LOCALVAR0)
  __DECLARE_VAR(BOOL,LOCALVAR1)
  __DECLARE_EXTERNAL(BOOL,LOCAL_VAR)
  __DECLARE_VAR(BOOL,LOCALVAR4)
  __DECLARE_VAR(BOOL,LOCALVAR5)
  __DECLARE_VAR(BOOL,LOCALVAR6)
  __DECLARE_VAR(DINT,LOCALVAR2)
  __DECLARE_VAR(UINT,LOCALVAR7)
  __DECLARE_VAR(UINT,LOCALVAR8)
  __DECLARE_VAR(UINT,LOCALVAR9)
  __DECLARE_VAR(TIME,LOCALVAR3)
  TON TON1;
  TOF TOF1;
  DERIVATIVE LOGGER2;
  __DECLARE_VAR(REAL,TEST)

} EQ_TIME_COMP_AND_CALC_CHECK;

void EQ_TIME_COMP_AND_CALC_CHECK_init__(EQ_TIME_COMP_AND_CALC_CHECK *data__, BOOL retain);
// Code part
void EQ_TIME_COMP_AND_CALC_CHECK_body__(EQ_TIME_COMP_AND_CALC_CHECK *data__);
// PROGRAM ARRAYS_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(DINT,LOCALVAR0)

} ARRAYS_CHECK;

void ARRAYS_CHECK_init__(ARRAYS_CHECK *data__, BOOL retain);
// Code part
void ARRAYS_CHECK_body__(ARRAYS_CHECK *data__);
// PROGRAM ST_BLOCK_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(BOOL,LOCALVAR0)
  __DECLARE_VAR(BOOL,LOCALVAR2)
  __DECLARE_VAR(TIME,LOCALVAR1)
  TP TP1;
  TON TON1;
  __DECLARE_VAR(REAL,LINE)
  __DECLARE_VAR(REAL,LINE_DER)
  __DECLARE_VAR(REAL,LINE_INT)
  DERIVATIVE DER1;
  __DECLARE_EXTERNAL(TIME,T0_INT)
  __DECLARE_VAR(LINT,INT1)
  __DECLARE_VAR(INT,INT2)
  INTEGRAL INTEG1;
  __DECLARE_VAR(LWORD,LWORD1)

} ST_BLOCK_CHECK;

void ST_BLOCK_CHECK_init__(ST_BLOCK_CHECK *data__, BOOL retain);
// Code part
void ST_BLOCK_CHECK_body__(ST_BLOCK_CHECK *data__);
// PROGRAM NUMERICAL_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(USINT,USINT1)
  __DECLARE_VAR(INT,INT1)
  __DECLARE_VAR(REAL,REAL1)
  __DECLARE_VAR(REAL,LREAL1)
  __DECLARE_VAR(BOOL,BOOL1)

} NUMERICAL_CHECK;

void NUMERICAL_CHECK_init__(NUMERICAL_CHECK *data__, BOOL retain);
// Code part
void NUMERICAL_CHECK_body__(NUMERICAL_CHECK *data__);
// PROGRAM ARIPTH_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(USINT,USINT1)
  __DECLARE_VAR(DINT,DINT1)
  __DECLARE_VAR(INT,INT1)
  __DECLARE_VAR(INT,INT2)
  __DECLARE_VAR(INT,INT3)
  __DECLARE_VAR(REAL,REAL1)
  __DECLARE_VAR(TIME,TIME1)

} ARIPTH_CHECK;

void ARIPTH_CHECK_init__(ARIPTH_CHECK *data__, BOOL retain);
// Code part
void ARIPTH_CHECK_body__(ARIPTH_CHECK *data__);
// PROGRAM TIME_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(TIME,LOCALVAR0)
  __DECLARE_VAR(TIME,LOCALVAR1)
  __DECLARE_VAR(TOD,LOCALVAR2)
  __DECLARE_VAR(DATE,LOCALVAR3)
  __DECLARE_VAR(DT,LOCALVAR4)

} TIME_CHECK;

void TIME_CHECK_init__(TIME_CHECK *data__, BOOL retain);
// Code part
void TIME_CHECK_body__(TIME_CHECK *data__);
// PROGRAM IF_ELSE_CHECK
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(BOOL,LOCALVAR0)
  __DECLARE_VAR(INT,LOCALVAR1)
  __DECLARE_VAR(INT,LOCALVAR2)
  __DECLARE_VAR(REAL,LOCALVAR3)

} IF_ELSE_CHECK;

void IF_ELSE_CHECK_init__(IF_ELSE_CHECK *data__, BOOL retain);
// Code part
void IF_ELSE_CHECK_body__(IF_ELSE_CHECK *data__);
// PROGRAM PROGRAM1
// Data part
typedef struct {
  // PROGRAM Interface - IN, OUT, IN_OUT variables

  // PROGRAM private variables - TEMP, private and located variables
  __DECLARE_VAR(BOOL,A)
  __DECLARE_VAR(BOOL,B)
  __DECLARE_VAR(BOOL,C)

} PROGRAM1;

void PROGRAM1_init__(PROGRAM1 *data__, BOOL retain);
// Code part
void PROGRAM1_body__(PROGRAM1 *data__);
#endif //__POUS_H
