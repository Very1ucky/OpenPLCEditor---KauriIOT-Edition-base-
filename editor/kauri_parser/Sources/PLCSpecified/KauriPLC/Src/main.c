#include "main.h"

typedef  void (*pFunction)(void);

const char md5[] = MD5;

const config conf = {.md5_len = strlen(md5),
                    .md5 = md5,
                    .is_serial_mb_enabled = MB_SERIAL_EN,
                    .serial_interface = MB_SERIAL_IFACE,
                    .slave_id = MB_SERIAL_SLAVE_ID,
                    .baudrate = MB_SERIAL_BR,
                    .is_mb_tcp_enabled = MB_TCP_EN,
                    .is_ser_prog_en = MB_SERIAL_IS_PROG_EN,
                    .is_ser_deb_en = MB_SERIAL_IS_DEB_EN,
                    };

void main() {
    uint32_t jump_address = *(uint32_t*) (0x0800010c);
    pFunction JumpToApp = (pFunction) jump_address;

    io_vars_init();

    JumpToApp();
}