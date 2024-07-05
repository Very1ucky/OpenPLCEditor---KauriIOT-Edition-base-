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
#define MODBUS_TCP_CONNECT ((void **)(START_ADDR))[13]
#define MODBUS_TCP_READ_COILS ((void **)(START_ADDR))[14]
#define MODBUS_TCP_READ_DISCRETE_INPUTS ((void **)(START_ADDR))[15]
#define MODBUS_TCP_READ_HOLDING_REGISTERS ((void **)(START_ADDR))[16]
#define MODBUS_TCP_READ_INPUT_REGISTERS ((void **)(START_ADDR))[17]
#define MODBUS_TCP_WRITE_SINGLE_COIL ((void **)(START_ADDR))[18]
#define MODBUS_TCP_WRITE_SINGLE_REGISTER ((void **)(START_ADDR))[19]
#define MODBUS_TCP_DISCONNECT ((void **)(START_ADDR))[20]


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

bool modbus_tcp_connect(char *address, uint16_t port, uint16_t req_timeout) {
    bool (*temp)(char *, uint16_t, uint16_t) = (bool (*)(char *, uint16_t, uint16_t))(MODBUS_TCP_CONNECT);
    return temp(address, port, req_timeout);
}

bool modbus_read_coils(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, bool *response) {
    bool (*temp)(uint16_t, uint8_t, uint16_t, bool, bool *) = (bool (*)(uint16_t, uint8_t, uint16_t, bool, bool *))(MODBUS_TCP_READ_COILS);
    return temp(start_address, slave_id, count, is_tcp, response);
}

bool modbus_read_discrete_inputs(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, bool *response) {
    bool (*temp)(uint16_t, uint8_t, uint16_t, bool, bool *) = (bool (*)(uint16_t, uint8_t, uint16_t, bool, bool *))(MODBUS_TCP_READ_DISCRETE_INPUTS);
    return temp(start_address, slave_id, count, is_tcp, response);
}

bool modbus_read_holding_registers(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, uint16_t *response) {
    bool (*temp)(uint16_t, uint8_t, uint16_t, bool, uint16_t *) = (bool (*)(uint16_t, uint8_t, uint16_t, bool, uint16_t *))(MODBUS_TCP_READ_HOLDING_REGISTERS);
    return temp(start_address, slave_id, count, is_tcp, response);
}

bool modbus_read_input_registers(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, uint16_t *response) {
    bool (*temp)(uint16_t, uint8_t, uint16_t, bool, uint16_t *) = (bool (*)(uint16_t, uint8_t, uint16_t, bool, uint16_t *))(MODBUS_TCP_READ_INPUT_REGISTERS);
    return temp(start_address, slave_id, count, is_tcp, response);
}

bool modbus_write_single_coil(uint16_t address, uint8_t slave_id, bool new_value, bool is_tcp) {
    bool (*temp)(uint16_t, uint8_t, bool, bool) = (bool (*)(uint16_t, uint8_t, bool, bool))(MODBUS_TCP_WRITE_SINGLE_COIL);
    return temp(address, slave_id, new_value, is_tcp);
}

bool modbus_write_single_register(uint16_t address, uint8_t slave_id, uint16_t new_value, bool is_tcp) {
    bool (*temp)(uint16_t, uint8_t, uint16_t, bool) = (bool (*)(uint16_t, uint8_t, uint16_t, bool))(MODBUS_TCP_WRITE_SINGLE_REGISTER);
    return temp(address, slave_id, new_value, is_tcp);
}

bool modbus_tcp_disconnect() {
    bool (*temp)() = (bool (*)())(MODBUS_TCP_DISCONNECT);
    return temp();
}