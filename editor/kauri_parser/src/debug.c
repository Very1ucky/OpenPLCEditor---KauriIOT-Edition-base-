/*
 * This file is part of OpenPLC Runtime
 *
 * Copyright (C) 2023 Autonomy, GP Orcullo
 * Based on the work by GP Orcullo on Beremiz for uC
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <stdbool.h>

#include "iec_types_all.h"
#include "POUS.h"

#define SAME_ENDIANNESS      0
#define REVERSE_ENDIANNESS   1

uint8_t endianness;


extern __IEC_BOOL_p FDSFDSFDS__LOCAL_VAR;
extern __IEC_INT_t FDSFDSFDS__INT_VAR;
extern __IEC_TIME_t FDSFDSFDS__TIME_VAR;
extern __IEC_STRING_t FDSFDSFDS__STRING_VAR;
extern CTD FDSFDSFDS__TEMP;
extern PROGRAM0 FDSFDSFDS__INSTANCE1;

static const struct {
    void *ptr;
    __IEC_types_enum type;
} debug_vars[] = {
    {&(FDSFDSFDS__LOCAL_VAR), BOOL_O_ENUM},
    {&(FDSFDSFDS__INT_VAR), INT_ENUM},
    {&(FDSFDSFDS__TIME_VAR), TIME_ENUM},
    {&(FDSFDSFDS__STRING_VAR), STRING_ENUM},
    {&(FDSFDSFDS__TEMP.EN), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CD), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.LD), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.PV), INT_ENUM},
    {&(FDSFDSFDS__TEMP.Q), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CV), INT_ENUM},
    {&(FDSFDSFDS__TEMP.CD_T.EN), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CD_T.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CD_T.CLK), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CD_T.Q), BOOL_ENUM},
    {&(FDSFDSFDS__TEMP.CD_T.M), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR0), STRING_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR1), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCAL_VAR), BOOL_P_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR4), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR5), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR6), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR2), DINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR7), UINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR8), UINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR9), UINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.LOCALVAR3), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.EN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.PT), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.Q), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.ET), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.STATE), SINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.PREV_IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.CURRENT_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TON1.START_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.EN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.PT), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.Q), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.ET), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.STATE), SINT_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.PREV_IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.CURRENT_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE1.TOF1.START_TIME), TIME_ENUM},
};

#define VAR_COUNT               47

uint16_t get_var_count(void)
{
    return VAR_COUNT;
}

size_t get_var_size(size_t idx)
{
    switch (debug_vars[idx].type) {
    case UINT_ENUM:
        return sizeof(UINT);
    case BOOL_ENUM:
    case BOOL_O_ENUM:
    case BOOL_P_ENUM:
        return sizeof(BOOL);
    case STRING_ENUM:
        return sizeof(STRING);
    case INT_ENUM:
        return sizeof(INT);
    case DINT_ENUM:
        return sizeof(DINT);
    case TIME_ENUM:
        return sizeof(TIME);
    case SINT_ENUM:
        return sizeof(SINT);
    default:
        return 0;
    }
}

void *get_var_addr(size_t idx)
{
    void *ptr = debug_vars[idx].ptr;

    switch (debug_vars[idx].type) {
    case UINT_ENUM:
        return (void *)&((__IEC_UINT_t *) ptr)->value;
    case BOOL_ENUM:
        return (void *)&((__IEC_BOOL_t *) ptr)->value;
    case BOOL_O_ENUM:
    case BOOL_P_ENUM:
        return (void *)((((__IEC_BOOL_p *) ptr)->flags & __IEC_FORCE_FLAG) 
                        ? &(((__IEC_BOOL_p *) ptr)->fvalue) 
                        : ((__IEC_BOOL_p *) ptr)->value);
    case STRING_ENUM:
        return (void *)&((__IEC_STRING_t *) ptr)->value;
    case INT_ENUM:
        return (void *)&((__IEC_INT_t *) ptr)->value;
    case DINT_ENUM:
        return (void *)&((__IEC_DINT_t *) ptr)->value;
    case TIME_ENUM:
        return (void *)&((__IEC_TIME_t *) ptr)->value;
    case SINT_ENUM:
        return (void *)&((__IEC_SINT_t *) ptr)->value;
    default:
        return 0;
    }
}

void force_var(size_t idx, bool forced, void *val)
{
    void *ptr = debug_vars[idx].ptr;

    if (forced) {
        size_t var_size = get_var_size(idx);
        switch (debug_vars[idx].type) {
        case UINT_ENUM: {
            memcpy(&((__IEC_UINT_t *) ptr)->value, val, var_size);
            //((__IEC_UINT_t *) ptr)->value = *((UINT *) val);
            ((__IEC_UINT_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case BOOL_ENUM: {
            memcpy(&((__IEC_BOOL_t *) ptr)->value, val, var_size);
            //((__IEC_BOOL_t *) ptr)->value = *((BOOL *) val);
            ((__IEC_BOOL_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case BOOL_O_ENUM: {
            memcpy((((__IEC_BOOL_p *) ptr)->value), val, var_size);
            //*(((__IEC_BOOL_p *) ptr)->value) = *((BOOL *) val);
            ((__IEC_BOOL_p *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case BOOL_P_ENUM: {
            memcpy(&((__IEC_BOOL_p *) ptr)->fvalue, val, var_size);
            //((__IEC_BOOL_p *) ptr)->fvalue = *((BOOL *) val);
            ((__IEC_BOOL_p *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case STRING_ENUM: {
            memcpy(&((__IEC_STRING_t *) ptr)->value, val, var_size);
            //((__IEC_STRING_t *) ptr)->value = *((STRING *) val);
            ((__IEC_STRING_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case INT_ENUM: {
            memcpy(&((__IEC_INT_t *) ptr)->value, val, var_size);
            //((__IEC_INT_t *) ptr)->value = *((INT *) val);
            ((__IEC_INT_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case DINT_ENUM: {
            memcpy(&((__IEC_DINT_t *) ptr)->value, val, var_size);
            //((__IEC_DINT_t *) ptr)->value = *((DINT *) val);
            ((__IEC_DINT_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case TIME_ENUM: {
            memcpy(&((__IEC_TIME_t *) ptr)->value, val, var_size);
            //((__IEC_TIME_t *) ptr)->value = *((TIME *) val);
            ((__IEC_TIME_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case SINT_ENUM: {
            memcpy(&((__IEC_SINT_t *) ptr)->value, val, var_size);
            //((__IEC_SINT_t *) ptr)->value = *((SINT *) val);
            ((__IEC_SINT_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        default:
            break;
        }
    } else {
        switch (debug_vars[idx].type) {
        case UINT_ENUM:
            ((__IEC_UINT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case BOOL_ENUM:
            ((__IEC_BOOL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case BOOL_O_ENUM:
        case BOOL_P_ENUM:
            ((__IEC_BOOL_p *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case STRING_ENUM:
            ((__IEC_STRING_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case INT_ENUM:
            ((__IEC_INT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case DINT_ENUM:
            ((__IEC_DINT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case TIME_ENUM:
            ((__IEC_TIME_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case SINT_ENUM:
            ((__IEC_SINT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        default:
            break;
        }
    }
}

void swap_bytes(void *ptr, size_t size) 
{
    uint8_t *bytePtr = (uint8_t *)ptr;
    size_t i;
    for (i = 0; i < size / 2; ++i) 
    {
        uint8_t temp = bytePtr[i];
        bytePtr[i] = bytePtr[size - 1 - i];
        bytePtr[size - 1 - i] = temp;
    }
}

void trace_reset(void)
{
    for (size_t i=0; i < VAR_COUNT; i++) 
    {
        force_var(i, false, 0);
    }
}

void set_trace(size_t idx, bool forced, void *val)
{
    if (idx >= 0 && idx < VAR_COUNT) 
    {
        if (endianness == REVERSE_ENDIANNESS)
        {
            // Aaaaarghhhh... Stupid AVR is Big Endian.
            swap_bytes(val, get_var_size(idx));
        }

        force_var(idx, forced, val);
    }
}

void set_endianness(uint8_t value)
{
    if (value == SAME_ENDIANNESS || value == REVERSE_ENDIANNESS)
    {
        endianness = value;
    }
}
