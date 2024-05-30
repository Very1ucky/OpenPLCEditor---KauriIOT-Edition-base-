#include <stdint.h>

#define START_ADDR 0x0800010c
#define LOG_MES_ADDR ((void **)(START_ADDR))[1]
#define TCP_CON_ADDR ((void **)(START_ADDR))[2]
#define TCP_SEND_ADDR ((void **)(START_ADDR))[3]
#define TCP_RECIEVE_ADDR ((void **)(START_ADDR))[4]
#define TCP_CLOSE_ADDR ((void **)(START_ADDR))[5]

int LogMessage(uint8_t level, char* buf, uint32_t size) {
    int (*log_message)(uint8_t, char*, uint32_t) = (int (*)(uint8_t, char*, uint32_t))(LOG_MES_ADDR);
    return log_message(level, buf, size);
}

uint16_t tcp_connect(char *ip_addr, uint16_t port) {
    uint16_t (*temp)(char*, uint16_t) = (uint16_t (*)(char*, uint16_t))(TCP_CON_ADDR);
    return temp(ip_addr, port);
}

uint16_t tcp_send(uint16_t socket_id, char *msg_to_send) {
    uint16_t (*temp)(uint16_t, char *) = (uint16_t (*)(uint16_t, char*))(TCP_SEND_ADDR);
    return temp(socket_id, msg_to_send);
}

uint16_t tcp_receive(uint16_t socket_id, char *msg_to_receive) {
    uint16_t (*temp)(uint16_t, char *) = (uint16_t (*)(uint16_t, char*))(TCP_RECIEVE_ADDR);
    return temp(socket_id, msg_to_receive);
}

bool tcp_close(uint16_t socket_id) {
    bool (*temp)(uint16_t) = (bool (*)(uint16_t))(TCP_CLOSE_ADDR);
    return temp(socket_id);
}