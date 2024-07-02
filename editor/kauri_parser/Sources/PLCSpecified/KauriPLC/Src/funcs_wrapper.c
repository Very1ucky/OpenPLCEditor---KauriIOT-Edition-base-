#include <stdint.h>
#include <stdbool.h>

#define START_ADDR 0x08000000 + 0x184
#define LOG_MES_ADDR ((void **)(START_ADDR))[1]
#define TCP_CON_ADDR ((void **)(START_ADDR))[2]
#define TCP_SEND_ADDR ((void **)(START_ADDR))[3]
#define TCP_RECIEVE_ADDR ((void **)(START_ADDR))[4]
#define TCP_CLOSE_ADDR ((void **)(START_ADDR))[5]
#define MQTT_CONNECT ((void **)(START_ADDR))[6]
#define MQTT_CONNECT_AUTH ((void **)(START_ADDR))[7]
#define MQTT_SEND ((void **)(START_ADDR))[8]
#define MQTT_RECEIVE ((void **)(START_ADDR))[9]
#define MQTT_SUBSCRIBE ((void **)(START_ADDR))[10]
#define MQTT_UNSUBSCRIBE ((void **)(START_ADDR))[11]
#define MQTT_DISCONNECT ((void **)(START_ADDR))[12]


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

bool connect_mqtt(char *broker, uint16_t port) {
    bool (*temp)(char *, uint16_t) = (bool (*)(char *, uint16_t))(MQTT_CONNECT);
    return temp(broker, port);
}

bool connect_mqtt_auth(char *broker, uint16_t port, char *user, char *password) {
    bool (*temp)(char *, uint16_t, char *, char *) = (bool (*)(char *, uint16_t, char *, char *))(MQTT_CONNECT_AUTH);
    return temp(broker, port, user, password);
}

bool mqtt_send(char *topic, char *message) {
    bool (*temp)(char *, char *) = (bool (*)(char *, char *))(MQTT_SEND);
    return temp(topic, message);
}

bool mqtt_receive(char *topic, char *message) {
    bool (*temp)(char *, char *) = (bool (*)(char *, char *))(MQTT_RECEIVE);
    return temp(topic, message);
}

bool mqtt_subscribe(char *topic) {
    bool (*temp)(char *) = (bool (*)(char *))(MQTT_SUBSCRIBE);
    return temp(topic);
}

bool mqtt_unsubscribe(char *topic) {
    bool (*temp)(char *) = (bool (*)(char *))(MQTT_UNSUBSCRIBE);
    return temp(topic);
}

bool mqtt_disconnect() {
    bool (*temp)() = (bool (*)())(MQTT_DISCONNECT);
    return temp();
}