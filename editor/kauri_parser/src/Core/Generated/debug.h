#ifndef DEBUG_H
#define DEBUG_H

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

void set_endianness(uint8_t value);

uint16_t get_var_count(void);

size_t get_var_size(size_t);

void *get_var_addr(size_t);

void force_var(size_t, bool, void *);

void set_trace(size_t, bool, void *);

void trace_reset(void);

#endif