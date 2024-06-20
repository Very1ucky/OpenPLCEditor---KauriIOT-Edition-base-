#include "main.h"

typedef  void (*pFunction)(void);

const char md5[] = MD5;

const config conf = {.md5_len = strlen(md5),
                    .md5 = md5,
                    .is_serial_mb_enabled = MB_SERIAL_EN,
                    #if MB_SERIAL_EN == 1
                    .serial_interface = MB_SERIAL_IFACE,
                    .slave_id = MB_SERIAL_SLAVE_ID,
                    .baudrate = MB_SERIAL_BR,
                    
                    .is_ser_prog_en = MB_SERIAL_IS_PROG_EN,
                    .is_ser_deb_en = MB_SERIAL_IS_DEB_EN,
                    #endif

                    .is_net_feat_enabled = NET_FEAT_EN,
                    #if NET_FEAT_EN == 1
                    .mac_addr = NET_MAC,
                    .is_dhcp_enabled = DHCP_EN,
                    .ip_addr = NET_IP,
                    .subnet = NET_SUBNET,
                    .gateway = NET_GATEWAY,
                    .is_mb_tcp_enabled = MB_TCP_EN,
                    #if MB_TCP_EN == 1
                    .is_tcp_prog_en = MB_TCP_IS_PROG_EN,
                    .is_tcp_deb_en = MB_TCP_IS_DEB_EN,
                    #endif
                    #endif
                    };

void main() {
    uint32_t jump_address = *(uint32_t*) (0x08000000+0x184);
    pFunction JumpToApp = (pFunction) jump_address;

    io_vars_init();

    JumpToApp();
}