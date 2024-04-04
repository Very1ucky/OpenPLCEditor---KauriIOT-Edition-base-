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


extern BLINK FDSFDSFDS__INSTANCE0;

static const struct {
    void *ptr;
    __IEC_types_enum type;
} debug_vars[] = {
    {&(FDSFDSFDS__INSTANCE0.BLINK_LED), BOOL_O_ENUM},
    {&(FDSFDSFDS__INSTANCE0.BLINK_LED0), BOOL_O_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.EN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.PT), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.Q), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.ET), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.STATE), SINT_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.PREV_IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.CURRENT_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TON0.START_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.EN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.ENO), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.PT), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.Q), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.ET), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.STATE), SINT_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.PREV_IN), BOOL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.CURRENT_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF0.START_TIME), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF1), INT_O_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF2), STRING_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF3), DATE_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF4), REAL_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF5), TIME_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF6), TOD_ENUM},
    {&(FDSFDSFDS__INSTANCE0.TOF7), DT_ENUM},
};

#define VAR_COUNT               29

uint16_t get_var_count(void)
{
    return VAR_COUNT;
}

size_t get_var_size(size_t idx)
{
    switch (debug_vars[idx].type) {
    case DATE_ENUM:
        return sizeof(DATE);
    case REAL_ENUM:
        return sizeof(REAL);
    case TIME_ENUM:
        return sizeof(TIME);
    case STRING_ENUM:
        return sizeof(STRING);
    case BOOL_ENUM:
    case BOOL_O_ENUM:
        return sizeof(BOOL);
    case DT_ENUM:
        return sizeof(DT);
    case TOD_ENUM:
        return sizeof(TOD);
    case INT_O_ENUM:
        return sizeof(INT);
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
    case DATE_ENUM:
        return (void *)&((__IEC_DATE_t *) ptr)->value;
    case REAL_ENUM:
        return (void *)&((__IEC_REAL_t *) ptr)->value;
    case TIME_ENUM:
        return (void *)&((__IEC_TIME_t *) ptr)->value;
    case STRING_ENUM:
        return (void *)&((__IEC_STRING_t *) ptr)->value;
    case BOOL_ENUM:
        return (void *)&((__IEC_BOOL_t *) ptr)->value;
    case BOOL_O_ENUM:
        return (void *)((((__IEC_BOOL_p *) ptr)->flags & __IEC_FORCE_FLAG) 
                        ? &(((__IEC_BOOL_p *) ptr)->fvalue) 
                        : ((__IEC_BOOL_p *) ptr)->value);
    case DT_ENUM:
        return (void *)&((__IEC_DT_t *) ptr)->value;
    case TOD_ENUM:
        return (void *)&((__IEC_TOD_t *) ptr)->value;
    case INT_O_ENUM:
        return (void *)((((__IEC_INT_p *) ptr)->flags & __IEC_FORCE_FLAG) 
                        ? &(((__IEC_INT_p *) ptr)->fvalue) 
                        : ((__IEC_INT_p *) ptr)->value);
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
        case DATE_ENUM: {
            memcpy(&((__IEC_DATE_t *) ptr)->value, val, var_size);
            //((__IEC_DATE_t *) ptr)->value = *((DATE *) val);
            ((__IEC_DATE_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case REAL_ENUM: {
            memcpy(&((__IEC_REAL_t *) ptr)->value, val, var_size);
            //((__IEC_REAL_t *) ptr)->value = *((REAL *) val);
            ((__IEC_REAL_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case TIME_ENUM: {
            memcpy(&((__IEC_TIME_t *) ptr)->value, val, var_size);
            //((__IEC_TIME_t *) ptr)->value = *((TIME *) val);
            ((__IEC_TIME_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case STRING_ENUM: {
            memcpy(&((__IEC_STRING_t *) ptr)->value, val, var_size);
            //((__IEC_STRING_t *) ptr)->value = *((STRING *) val);
            ((__IEC_STRING_t *) ptr)->flags |= __IEC_FORCE_FLAG;
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
        case DT_ENUM: {
            memcpy(&((__IEC_DT_t *) ptr)->value, val, var_size);
            //((__IEC_DT_t *) ptr)->value = *((DT *) val);
            ((__IEC_DT_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case TOD_ENUM: {
            memcpy(&((__IEC_TOD_t *) ptr)->value, val, var_size);
            //((__IEC_TOD_t *) ptr)->value = *((TOD *) val);
            ((__IEC_TOD_t *) ptr)->flags |= __IEC_FORCE_FLAG;
            break;
        }
        case INT_O_ENUM: {
            memcpy((((__IEC_INT_p *) ptr)->value), val, var_size);
            //*(((__IEC_INT_p *) ptr)->value) = *((INT *) val);
            ((__IEC_INT_p *) ptr)->flags |= __IEC_FORCE_FLAG;
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
        case DATE_ENUM:
            ((__IEC_DATE_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case REAL_ENUM:
            ((__IEC_REAL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case TIME_ENUM:
            ((__IEC_TIME_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case STRING_ENUM:
            ((__IEC_STRING_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case BOOL_ENUM:
            ((__IEC_BOOL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case BOOL_O_ENUM:
            ((__IEC_BOOL_p *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case DT_ENUM:
            ((__IEC_DT_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case TOD_ENUM:
            ((__IEC_TOD_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;
            break;
        case INT_O_ENUM:
            ((__IEC_INT_p *) ptr)->flags &= ~__IEC_FORCE_FLAG;
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
