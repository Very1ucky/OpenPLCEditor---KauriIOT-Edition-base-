#include "POUS.h"

void BLINK_init__(BLINK *data__, BOOL retain) {
  __INIT_LOCATED(BOOL,__QX1_0,data__->BLINK_LED,retain)
  __INIT_LOCATED_VALUE(data__->BLINK_LED,__BOOL_LITERAL(FALSE))
  __INIT_LOCATED(BOOL,__QX0_0,data__->BLINK_LED0,retain)
  __INIT_LOCATED_VALUE(data__->BLINK_LED0,__BOOL_LITERAL(FALSE))
  TON_init__(&data__->TON0,retain);
  TOF_init__(&data__->TOF0,retain);
  __INIT_VAR(data__->TOF2,__STRING_LITERAL(4,"Test"),retain)
  __INIT_LOCATED(INT,__QW0_7,data__->TOF1,retain)
  __INIT_LOCATED_VALUE(data__->TOF1,10)
  __INIT_VAR(data__->TOF3,__date_to_timespec(1, 1, 1971),retain)
  __INIT_VAR(data__->TOF4,1.4,retain)
  __INIT_VAR(data__->TOF5,__time_to_timespec(1, 500, 50, 36, 4, 1),retain)
  __INIT_VAR(data__->TOF6,__tod_to_timespec(4, 0, 1),retain)
  __INIT_VAR(data__->TOF7,__dt_to_timespec(10, 1, 0, 6, 6, 2024),retain)
  __INIT_VAR(data__->_TMP_NOT10_OUT,__BOOL_LITERAL(FALSE),retain)
}

// Code part
void BLINK_body__(BLINK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->TON0.,IN,,!(__GET_LOCATED(data__->BLINK_LED,)));
  __SET_VAR(data__->TON0.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TON_body__(&data__->TON0);
  __SET_VAR(data__->TOF0.,EN,,__GET_VAR(data__->TON0.ENO,));
  __SET_VAR(data__->TOF0.,IN,,__GET_VAR(data__->TON0.Q,));
  __SET_VAR(data__->TOF0.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TOF_body__(&data__->TOF0);
  __SET_LOCATED(data__->,BLINK_LED,,__GET_VAR(data__->TOF0.Q,));
  __SET_VAR(data__->,_TMP_NOT10_OUT,,!(__GET_VAR(data__->TOF0.Q,)));

  goto __end;

__end:
  return;
} // BLINK_body__() 





void EQ_TIME_COMP_AND_CALC_CHECK_init__(EQ_TIME_COMP_AND_CALC_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->LOCALVAR0,__STRING_LITERAL(4,"Test"),retain)
  __INIT_VAR(data__->LOCALVAR1,__BOOL_LITERAL(FALSE),retain)
  __INIT_EXTERNAL(BOOL,LOCAL_VAR,data__->LOCAL_VAR,retain)
  __INIT_VAR(data__->LOCALVAR4,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->LOCALVAR5,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->LOCALVAR6,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->LOCALVAR2,0,retain)
  __INIT_VAR(data__->LOCALVAR7,0,retain)
  __INIT_VAR(data__->LOCALVAR8,0,retain)
  __INIT_VAR(data__->LOCALVAR9,0,retain)
  __INIT_VAR(data__->LOCALVAR3,__time_to_timespec(1, 0, 0, 0, 0, 0),retain)
  TON_init__(&data__->TON1,retain);
  TOF_init__(&data__->TOF1,retain);
  DERIVATIVE_init__(&data__->LOGGER2,retain);
  __INIT_VAR(data__->TEST,0,retain)
}

// Code part
void EQ_TIME_COMP_AND_CALC_CHECK_body__(EQ_TIME_COMP_AND_CALC_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,LOCALVAR0,,__STRING_LITERAL(7,"Test123"));
  __SET_VAR(data__->,LOCALVAR1,,((((!(__BOOL_LITERAL(TRUE)) || !(__BOOL_LITERAL(FALSE))) && !(__BOOL_LITERAL(TRUE))) || (__GET_VAR(data__->LOCALVAR2,) > 1)) || (__GET_VAR(data__->LOCALVAR1,) && !(EQ_TIME(__BOOL_LITERAL(TRUE), NULL, 2, __GET_VAR(data__->LOCALVAR3,), __time_to_timespec(1, 200, 0, 0, 0, 0)) && (__GET_VAR(data__->LOCALVAR7,) <= (11 * 2)))) || (!__GET_VAR(data__->LOCALVAR1,) && (EQ_TIME(__BOOL_LITERAL(TRUE), NULL, 2, __GET_VAR(data__->LOCALVAR3,), __time_to_timespec(1, 200, 0, 0, 0, 0)) && (__GET_VAR(data__->LOCALVAR7,) <= (11 * 2))))));
  __SET_VAR(data__->,LOCALVAR4,,(AND__BOOL__BOOL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (BOOL)__BOOL_LITERAL(TRUE),
    (BOOL)__BOOL_LITERAL(FALSE)) || (OR__BOOL__BOOL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (BOOL)__BOOL_LITERAL(FALSE),
    (BOOL)__GET_VAR(data__->LOCALVAR1,)) && XOR__BOOL__BOOL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (BOOL)__BOOL_LITERAL(TRUE),
    (BOOL)__BOOL_LITERAL(TRUE)))));
  __SET_VAR(data__->,LOCALVAR2,,(((100 - 10) + (33 / 3)) * 5));
  __SET_VAR(data__->,LOCALVAR4,,(3.5 >= 2.0));
  __SET_VAR(data__->,LOCALVAR4,,EQ__BOOL__SINT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (SINT)((-10 * -5) + -2),
    (SINT)(5 * 11)));
  __SET_VAR(data__->,LOCALVAR4,,NE__BOOL__SINT__SINT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (SINT)((-10 * -5) + -2),
    (SINT)(5 * 11)));
  __SET_VAR(data__->,LOCALVAR4,,LE__BOOL__SINT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (SINT)((-10 * -5) + -2),
    (SINT)(5 * 11)));
  __SET_VAR(data__->,LOCALVAR4,,GT__BOOL__SINT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (SINT)((-10 * -5) + -2),
    (SINT)(5 * 11)));
  __SET_VAR(data__->,LOCALVAR5,,EQ_STRING(__BOOL_LITERAL(TRUE), NULL, 2, __GET_VAR(data__->LOCALVAR0,), __STRING_LITERAL(4,"Test")));
  __SET_VAR(data__->,LOCALVAR6,,(__GET_VAR(data__->LOCALVAR2,) < 10));
  __SET_EXTERNAL(data__->,LOCAL_VAR,,__BOOL_LITERAL(FALSE));
  goto __end;
  __SET_VAR(data__->TON1.,IN,,!(__GET_VAR(data__->TOF1.Q,)));
  __SET_VAR(data__->TON1.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TON_body__(&data__->TON1);
  __SET_VAR(data__->TOF1.,IN,,__GET_VAR(data__->TON1.Q,));
  __SET_VAR(data__->TOF1.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TOF_body__(&data__->TOF1);
  if ((__GET_VAR(data__->TOF1.Q,) || LT_STRING(__BOOL_LITERAL(TRUE), NULL, 2, __GET_VAR(data__->LOCALVAR0,), __STRING_LITERAL(4,"Test")))) {
    __SET_VAR(data__->,LOCALVAR1,,__BOOL_LITERAL(TRUE));
  } else {
    __SET_VAR(data__->,LOCALVAR1,,__BOOL_LITERAL(FALSE));
  };
  __SET_VAR(data__->,LOCALVAR7,,(2 + (5 * 2)));

  goto __end;

__end:
  return;
} // EQ_TIME_COMP_AND_CALC_CHECK_body__() 





void ARRAYS_CHECK_init__(ARRAYS_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->LOCALVAR0,0,retain)
}

// Code part
void ARRAYS_CHECK_body__(ARRAYS_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,LOCALVAR0,,0);

  goto __end;

__end:
  return;
} // ARRAYS_CHECK_body__() 





void ST_BLOCK_CHECK_init__(ST_BLOCK_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->LOCALVAR0,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->LOCALVAR2,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->LOCALVAR1,__time_to_timespec(1, 0, 0, 0, 0, 0),retain)
  TP_init__(&data__->TP1,retain);
  TON_init__(&data__->TON1,retain);
  __INIT_VAR(data__->LINE,0,retain)
  __INIT_VAR(data__->LINE_DER,0,retain)
  __INIT_VAR(data__->LINE_INT,0,retain)
  DERIVATIVE_init__(&data__->DER1,retain);
  __INIT_EXTERNAL(TIME,T0_INT,data__->T0_INT,retain)
  __INIT_VAR(data__->INT1,0,retain)
  __INIT_VAR(data__->INT2,0,retain)
  INTEGRAL_init__(&data__->INTEG1,retain);
  __INIT_VAR(data__->LWORD1,0,retain)
}

// Code part
void ST_BLOCK_CHECK_body__(ST_BLOCK_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->TP1.,IN,,__GET_VAR(data__->LOCALVAR2,));
  __SET_VAR(data__->TP1.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TP_body__(&data__->TP1);
  __SET_VAR(data__->,LOCALVAR0,,__GET_VAR(data__->TP1.Q));
  __SET_VAR(data__->,LOCALVAR1,,__GET_VAR(data__->TP1.ET));
  __SET_VAR(data__->TON1.,IN,,!(__GET_VAR(data__->LOCALVAR0,)));
  __SET_VAR(data__->TON1.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TON_body__(&data__->TON1);
  __SET_VAR(data__->,LOCALVAR2,,__GET_VAR(data__->TON1.Q));
  __SET_VAR(data__->,LINE,,(__GET_VAR(data__->LINE,) + (1.0 * 0.01)));
  __SET_VAR(data__->DER1.,RUN,,__BOOL_LITERAL(TRUE));
  __SET_VAR(data__->DER1.,XIN,,__GET_VAR(data__->LINE,));
  __SET_VAR(data__->DER1.,CYCLE,,__GET_EXTERNAL(data__->T0_INT,));
  DERIVATIVE_body__(&data__->DER1);
  __SET_VAR(data__->,LINE_DER,,__GET_VAR(data__->DER1.XOUT));
  __SET_VAR(data__->INTEG1.,RUN,,__BOOL_LITERAL(TRUE));
  __SET_VAR(data__->INTEG1.,R1,,__BOOL_LITERAL(FALSE));
  __SET_VAR(data__->INTEG1.,XIN,,__GET_VAR(data__->LINE,));
  __SET_VAR(data__->INTEG1.,X0,,0.0);
  __SET_VAR(data__->INTEG1.,CYCLE,,__GET_EXTERNAL(data__->T0_INT,));
  INTEGRAL_body__(&data__->INTEG1);
  __SET_VAR(data__->,LINE_INT,,__GET_VAR(data__->INTEG1.XOUT));
  __SET_VAR(data__->,LWORD1,,1);

  goto __end;

__end:
  return;
} // ST_BLOCK_CHECK_body__() 





void NUMERICAL_CHECK_init__(NUMERICAL_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->USINT1,0,retain)
  __INIT_VAR(data__->INT1,0,retain)
  __INIT_VAR(data__->REAL1,0,retain)
  __INIT_VAR(data__->LREAL1,0,retain)
  __INIT_VAR(data__->BOOL1,__BOOL_LITERAL(FALSE),retain)
}

// Code part
void NUMERICAL_CHECK_body__(NUMERICAL_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,INT1,,ABS__INT__INT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (INT)(-1 * 10)));
  __SET_VAR(data__->,REAL1,,SQRT__REAL__REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (REAL)-25.0));
  __SET_VAR(data__->,LREAL1,,EXP__REAL__REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (REAL)3.0));
  __SET_VAR(data__->,BOOL1,,(OR__BOOL__BOOL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (BOOL)(TAN__REAL__REAL(
      (BOOL)__BOOL_LITERAL(TRUE),
      NULL,
      (REAL)__GET_VAR(data__->REAL1,)) > ASIN__REAL__REAL(
      (BOOL)__BOOL_LITERAL(TRUE),
      NULL,
      (REAL)__GET_VAR(data__->REAL1,))),
    (BOOL)__BOOL_LITERAL(FALSE)) && !((LOG__REAL__REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (REAL)__GET_VAR(data__->LREAL1,)) == COS__REAL__REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (REAL)(10.0 * 3.0))))));

  goto __end;

__end:
  return;
} // NUMERICAL_CHECK_body__() 





void ARIPTH_CHECK_init__(ARIPTH_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->USINT1,0,retain)
  __INIT_VAR(data__->DINT1,5,retain)
  __INIT_VAR(data__->INT1,0,retain)
  __INIT_VAR(data__->INT2,0,retain)
  __INIT_VAR(data__->INT3,0,retain)
  __INIT_VAR(data__->REAL1,0,retain)
  __INIT_VAR(data__->TIME1,__time_to_timespec(1, 0, 0, 0, 0, 0),retain)
}

// Code part
void ARIPTH_CHECK_body__(ARIPTH_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,INT1,,(((3 - 7) == 0)?0:(((10 - 2) + ((5 * 2) / 3)) % (3 - 7))));
  __SET_VAR(data__->,INT2,,((MUL__INT__INT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (UINT)2,
    (INT)3,
    (INT)ADD__INT__INT(
      (BOOL)__BOOL_LITERAL(TRUE),
      NULL,
      (UINT)2,
      (INT)4,
      (INT)(__GET_VAR(data__->INT1,) * 2))) + DIV__INT__INT__INT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (INT)4,
    (INT)3)) - SUB__INT__INT__INT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (INT)2,
    (INT)1)));
  __SET_VAR(data__->,INT3,,MOD__INT__INT__INT(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (INT)5,
    (INT)2));
  __SET_VAR(data__->,REAL1,,EXPT__REAL__REAL__REAL(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (REAL)10.1,
    (REAL)3.3));
  __SET_VAR(data__->,TIME1,,MOVE__TIME__TIME(
    (BOOL)__BOOL_LITERAL(TRUE),
    NULL,
    (TIME)__time_to_timespec(1, 500, 0, 0, 0, 0)));
  __SET_VAR(data__->,DINT1,, -(__GET_VAR(data__->DINT1,)));

  goto __end;

__end:
  return;
} // ARIPTH_CHECK_body__() 





void TIME_CHECK_init__(TIME_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->LOCALVAR0,__time_to_timespec(1, 0, 0, 0, 0, 0),retain)
  __INIT_VAR(data__->LOCALVAR1,__time_to_timespec(1, 0, 0, 0, 0, 0),retain)
  __INIT_VAR(data__->LOCALVAR2,__tod_to_timespec(0, 0, 0),retain)
  __INIT_VAR(data__->LOCALVAR3,__date_to_timespec(1, 1, 1970),retain)
  __INIT_VAR(data__->LOCALVAR4,__dt_to_timespec(0, 0, 0, 1, 1, 1970),retain)
}

// Code part
void TIME_CHECK_body__(TIME_CHECK *data__) {
  // Initialise TEMP variables

  __SET_VAR(data__->,LOCALVAR2,,__time_add(__GET_VAR(data__->LOCALVAR2,), __time_to_timespec(1, 500, 0, 0, 0, 0)));
  __SET_VAR(data__->,LOCALVAR4,,__time_add(__GET_VAR(data__->LOCALVAR4,), __time_to_timespec(1, 500, 0, 0, 0, 0)));
  __SET_VAR(data__->,LOCALVAR0,,__time_div(__time_mul(__time_add(__time_to_timespec(1, 200, 0, 0, 0, 0), __GET_VAR(data__->LOCALVAR1,)), 5.0), 2));
  __SET_VAR(data__->,LOCALVAR1,,__time_sub(__date_to_timespec(1, 1, 1971), __date_to_timespec(1, 1, 1971)));

  goto __end;

__end:
  return;
} // TIME_CHECK_body__() 





void IF_ELSE_CHECK_init__(IF_ELSE_CHECK *data__, BOOL retain) {
  __INIT_VAR(data__->LOCALVAR0,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->LOCALVAR1,0,retain)
  __INIT_VAR(data__->LOCALVAR2,0,retain)
  __INIT_VAR(data__->LOCALVAR3,0,retain)
}

// Code part
void IF_ELSE_CHECK_body__(IF_ELSE_CHECK *data__) {
  // Initialise TEMP variables

  for(__GET_VAR(data__->LOCALVAR1,) = 1; ((-2) > 0)? (__GET_VAR(data__->LOCALVAR1,) <= (5)) : (__GET_VAR(data__->LOCALVAR1,) >= (5)); __GET_VAR(data__->LOCALVAR1,) += (-2)) {
    __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
  };
  while ((__GET_VAR(data__->LOCALVAR1,) > 5)) {
    __SET_VAR(data__->,LOCALVAR0,,__BOOL_LITERAL(TRUE));
  };
  do {
    __SET_VAR(data__->,LOCALVAR0,,__BOOL_LITERAL(TRUE));
  } while((__GET_VAR(data__->LOCALVAR1,) > 5));
  {
    INT __case_expression = __GET_VAR(data__->LOCALVAR1,);
    if ((__case_expression == 1)) {
      {
        INT __case_expression = __GET_VAR(data__->LOCALVAR2,);
        if ((__case_expression == 1)) {
          __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
        }
        else if ((__case_expression >= 2 && __case_expression <= 5)) {
          __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
        }
        else if ((__case_expression == 6) ||
                 (__case_expression >= 9 && __case_expression <= 20)) {
          __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
        }
        else {
          __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
        }
      };
    }
    else if ((__case_expression >= 2 && __case_expression <= 5)) {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
    else if ((__case_expression == 6) ||
             (__case_expression >= 9 && __case_expression <= 20)) {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
    else {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
  };
  {
    INT __case_expression = __GET_VAR(data__->LOCALVAR1,);
    if ((__case_expression == 1)) {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
    else if ((__case_expression >= 2 && __case_expression <= 5)) {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
    else if ((__case_expression == 6) ||
             (__case_expression >= 9 && __case_expression <= 20)) {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
    else {
      __SET_VAR(data__->,LOCALVAR2,,(__GET_VAR(data__->LOCALVAR2,) * 2));
    }
  };

  goto __end;

__end:
  return;
} // IF_ELSE_CHECK_body__() 





void PROGRAM1_init__(PROGRAM1 *data__, BOOL retain) {
  __INIT_VAR(data__->A,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->B,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->C,__BOOL_LITERAL(FALSE),retain)
}

// Code part
void PROGRAM1_body__(PROGRAM1 *data__) {
  // Initialise TEMP variables

  __IL_DEFVAR_T __IL_DEFVAR;
  __IL_DEFVAR_T __IL_DEFVAR_BACK;
  __IL_DEFVAR.BOOLvar = __GET_VAR(data__->A,);
  __IL_DEFVAR.BOOLvar &= !__GET_VAR(data__->B,);
  __SET_VAR(data__->,C,,__IL_DEFVAR.BOOLvar);

  goto __end;

__end:
  return;
} // PROGRAM1_body__() 





