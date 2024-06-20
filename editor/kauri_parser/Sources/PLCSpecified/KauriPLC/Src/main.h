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
    bool is_ser_prog_en;
    bool is_ser_deb_en;
    
    bool is_net_feat_enabled;
    uint8_t mac_addr[6];
    bool is_dhcp_enabled;
    uint8_t ip_addr[4];
    uint8_t subnet[4];
    uint8_t gateway[4];

    bool is_mb_tcp_enabled;
    bool is_tcp_prog_en;
    bool is_tcp_deb_en;
} __attribute__((packed)) config;

#endif