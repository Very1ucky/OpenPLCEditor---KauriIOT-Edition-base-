#include "debug.h"
#include "Config0.h"
#include "io_vars.h"
#include "iec_types_all.h"

TIME __CURRENT_TIME = {0, 0};

BOOL __DEBUG;
extern VarsToIOLinker vars_to_io_linker;
extern unsigned long long common_ticktime__;

static const uint32_t IX_len = sizeof(vars_to_io_linker.IX) / sizeof(uint8_t *);
static const uint32_t QX_len = sizeof(vars_to_io_linker.QX) / sizeof(uint8_t *);
static const uint32_t IW_len = sizeof(vars_to_io_linker.IW) / sizeof(uint16_t *);
static const uint32_t QW_len = sizeof(vars_to_io_linker.QW) / sizeof(uint16_t *);

__attribute__((section(".utils"), used))
static void **used_funcs[] = {
    (void *)config_init__,
    (void *)config_run__,
    (void *)set_endianness,
    (void *)get_var_count,
    (void *)get_var_size,
    (void *)get_var_addr,
    (void *)force_var,
    (void *)set_trace,
    (void *)trace_reset,
    (void *)&__CURRENT_TIME,
    (void *)&common_ticktime__,
    (void *)&IX_len,
    (void *)vars_to_io_linker.IX,
    (void *)&QX_len,
    (void *)vars_to_io_linker.QX,
    (void *)&IW_len,
    (void *)vars_to_io_linker.IW,
    (void *)&QW_len,
    (void *)vars_to_io_linker.QW
};