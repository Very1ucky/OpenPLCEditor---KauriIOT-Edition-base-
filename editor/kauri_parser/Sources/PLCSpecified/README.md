# Functions that need to be implemented by the new platform
- Function to provide support for logging (it used in native logger library, it can be used in custom function blocks or in runtime environment to save information about program status and etc.)
```c
int LogMessage(uint8_t level, char* buf, uint32_t size);
```
- Functions to provide support for tcp functional blocks
```c
uint16_t tcp_connect(char *ip_addr, uint16_t port);

uint16_t tcp_send(uint16_t socket_id, char *msg_to_send);

uint16_t tcp_receive(uint16_t socket_id, char *msg_to_receive);

bool tcp_close(uint16_t socket_id);
```
- Functions to provide support for mqtt functional blocks
```c
bool connect_mqtt(char *broker, uint16_t port);

bool connect_mqtt_auth(char *broker, uint16_t port, char *user, char *password);

bool mqtt_send(char *topic, char *message);

bool mqtt_receive(char *topic, char *message);

bool mqtt_subscribe(char *topic);

bool mqtt_unsubscribe(char *topic);

bool mqtt_disconnect();
```
- Functions to provide support for modbus functional blocks
```c
bool modbus_tcp_connect(char *address, uint16_t port, uint16_t req_timeout);

bool modbus_read_coils(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, bool *response);

bool modbus_read_discrete_inputs(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, bool *response);

bool modbus_read_holding_registers(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, uint16_t *response);

bool modbus_read_input_registers(uint16_t start_address, uint8_t slave_id, uint16_t count, bool is_tcp, uint16_t *response);

bool modbus_write_single_coil(uint16_t address, uint8_t slave_id, bool new_value, bool is_tcp);

bool modbus_write_single_register(uint16_t address, uint8_t slave_id, uint16_t new_value, bool is_tcp);

bool modbus_tcp_disconnect();
```
- Function to provide support for rs485 functional blocks
```c
bool rs485_connect(uint32_t baudrate, uint8_t stopbits, bool enable_terminal_resistors);

bool rs485_send_bytes(uint8_t *message, uint8_t message_length);
bool rs485_start_receiving(uint8_t receive_packet_size);

bool rs485_stop_receiving();

uint8_t rs485_get_next_received_packet(uint8_t *packet);

bool rs485_disconnect();
```