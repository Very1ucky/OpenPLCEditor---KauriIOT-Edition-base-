#ifndef IO_VARS_H
#define GLUE_VARS_H

#include "iec_std_lib.h"

typedef struct {
    IEC_BOOL *IX[0];
    IEC_BOOL *QX[9];
    IEC_UINT *IW[0];
    IEC_UINT *QW[8];
} VarsToIOLinker;

void io_vars_init();

#endif
