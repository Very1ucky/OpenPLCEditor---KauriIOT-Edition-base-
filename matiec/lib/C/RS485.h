

typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,CONNECT)
  __DECLARE_VAR(BOOL,ENABLE_TERMINAL_RESISTORS)
  __DECLARE_VAR(UDINT,BAUDRATE)
  __DECLARE_VAR(USINT,STOPBITS)
  __DECLARE_VAR(BOOL,SUCCESS)

  // FB private variables - TEMP, private and located variables

} RS485_CONNECT;

static void RS485_CONNECT_init__(RS485_CONNECT *data__, BOOL retain);
// Code part
static void RS485_CONNECT_body__(RS485_CONNECT *data__);

// FUNCTION_BLOCK RS485_SEND_BYTES
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,SEND)
  __DECLARE_VAR(USINT,MESSAGE_SIZE)
  __DECLARE_VAR(__ARRAY_OF_BYTE_128,MESSAGE)
  __DECLARE_VAR(BOOL,SUCCESS)

  // FB private variables - TEMP, private and located variables

} RS485_SEND_BYTES;

static void RS485_SEND_BYTES_init__(RS485_SEND_BYTES *data__, BOOL retain);
// Code part
static void RS485_SEND_BYTES_body__(RS485_SEND_BYTES *data__);
// FUNCTION_BLOCK RS485_START_RECEIVING
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,START)
  __DECLARE_VAR(USINT,RECEIVE_PACKET_SIZE)
  __DECLARE_VAR(BOOL,SUCCESS)

  // FB private variables - TEMP, private and located variables

} RS485_START_RECEIVING;

static void RS485_START_RECEIVING_init__(RS485_START_RECEIVING *data__, BOOL retain);
// Code part
static void RS485_START_RECEIVING_body__(RS485_START_RECEIVING *data__);
// FUNCTION_BLOCK RS485_DISCONNECT
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,DISCONNECT)
  __DECLARE_VAR(BOOL,SUCCESS)

  // FB private variables - TEMP, private and located variables

} RS485_DISCONNECT;

static void RS485_DISCONNECT_init__(RS485_DISCONNECT *data__, BOOL retain);
// Code part
static void RS485_DISCONNECT_body__(RS485_DISCONNECT *data__);
// FUNCTION_BLOCK RS485_GET_NEXT_RECEIVED_PACKET
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,GET)
  __DECLARE_VAR(USINT,RECEIVED_PACKET_SIZE)
  __DECLARE_VAR(__ARRAY_OF_BYTE_128,RECEIVED_PACKET)

  // FB private variables - TEMP, private and located variables

} RS485_GET_NEXT_RECEIVED_PACKET;

static void RS485_GET_NEXT_RECEIVED_PACKET_init__(RS485_GET_NEXT_RECEIVED_PACKET *data__, BOOL retain);
// Code part
static void RS485_GET_NEXT_RECEIVED_PACKET_body__(RS485_GET_NEXT_RECEIVED_PACKET *data__);
// FUNCTION_BLOCK RS485_STOP_RECEIVING
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,STOP)
  __DECLARE_VAR(BOOL,SUCCESS)

  // FB private variables - TEMP, private and located variables

} RS485_STOP_RECEIVING;

static void RS485_STOP_RECEIVING_init__(RS485_STOP_RECEIVING *data__, BOOL retain);
// Code part
static void RS485_STOP_RECEIVING_body__(RS485_STOP_RECEIVING *data__);

static void RS485_CONNECT_init__(RS485_CONNECT *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->CONNECT,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->ENABLE_TERMINAL_RESISTORS,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->BAUDRATE,115200,retain)
  __INIT_VAR(data__->STOPBITS,1,retain)
  __INIT_VAR(data__->SUCCESS,__BOOL_LITERAL(FALSE),retain)
}

// Code part
static void RS485_CONNECT_body__(RS485_CONNECT *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,SUCCESS,,__BOOL_LITERAL(FALSE));

  goto __end;

__end:
  return;
} // RS485_CONNECT_body__() 

static void RS485_SEND_BYTES_init__(RS485_SEND_BYTES *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->SEND,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->MESSAGE_SIZE,0,retain)
  {
    static const __ARRAY_OF_BYTE_128 temp = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}};
    __SET_VAR(data__->,MESSAGE,,temp);
  }
  __INIT_VAR(data__->SUCCESS,__BOOL_LITERAL(FALSE),retain)
}

// Code part
static void RS485_SEND_BYTES_body__(RS485_SEND_BYTES *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,SUCCESS,,__BOOL_LITERAL(FALSE));

  goto __end;

__end:
  return;
} // RS485_SEND_BYTES_body__() 





static void RS485_START_RECEIVING_init__(RS485_START_RECEIVING *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->START,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->RECEIVE_PACKET_SIZE,0,retain)
  __INIT_VAR(data__->SUCCESS,__BOOL_LITERAL(FALSE),retain)
}

// Code part
static void RS485_START_RECEIVING_body__(RS485_START_RECEIVING *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,SUCCESS,,__BOOL_LITERAL(FALSE));

  goto __end;

__end:
  return;
} // RS485_START_RECEIVING_body__() 





static void RS485_DISCONNECT_init__(RS485_DISCONNECT *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->DISCONNECT,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SUCCESS,__BOOL_LITERAL(FALSE),retain)
}

// Code part
static void RS485_DISCONNECT_body__(RS485_DISCONNECT *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,SUCCESS,,__BOOL_LITERAL(FALSE));

  goto __end;

__end:
  return;
} // RS485_DISCONNECT_body__() 





static void RS485_GET_NEXT_RECEIVED_PACKET_init__(RS485_GET_NEXT_RECEIVED_PACKET *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->GET,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->RECEIVED_PACKET_SIZE,0,retain)
  {
    static const __ARRAY_OF_BYTE_128 temp = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}};
    __SET_VAR(data__->,RECEIVED_PACKET,,temp);
  }
}

// Code part
static void RS485_GET_NEXT_RECEIVED_PACKET_body__(RS485_GET_NEXT_RECEIVED_PACKET *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,RECEIVED_PACKET_SIZE,,0);

  goto __end;

__end:
  return;
} // RS485_GET_NEXT_RECEIVED_PACKET_body__() 





static void RS485_STOP_RECEIVING_init__(RS485_STOP_RECEIVING *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->STOP,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SUCCESS,__BOOL_LITERAL(FALSE),retain)
}

// Code part
static void RS485_STOP_RECEIVING_body__(RS485_STOP_RECEIVING *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  __SET_VAR(data__->,SUCCESS,,__BOOL_LITERAL(FALSE));

  goto __end;

__end:
  return;
} // RS485_STOP_RECEIVING_body__() 