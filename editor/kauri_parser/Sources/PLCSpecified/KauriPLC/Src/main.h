#ifndef MAIN_H
#define MAIN_H

#include <stdint.h>
#include "io_vars.h"
#include "app_conf.h"
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t md5_len;
    char *md5;
    bool is_serial_mb_enabled;
    uint8_t serial_interface;
    uint8_t slave_id;
    uint32_t baudrate;
    
    bool is_mb_tcp_enabled;
} __attribute__((packed)) config;

#endif