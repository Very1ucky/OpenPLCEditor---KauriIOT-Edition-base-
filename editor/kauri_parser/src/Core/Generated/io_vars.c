#include "io_vars.h"

#define __LOCATED_VAR(type, name, ...) type __##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR
#define __LOCATED_VAR(type, name, ...) type* name = &__##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR

VarsToIOLinker vars_to_io_linker;

void io_vars_init()
{
   vars_to_io_linker.QX[8] = __QX1_0;
   vars_to_io_linker.QX[0] = __QX0_0;
   vars_to_io_linker.QW[7] = __QW0_7;
   vars_to_io_linker.QX[5] = __QX0_5;

}
        