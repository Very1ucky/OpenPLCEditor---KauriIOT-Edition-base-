/************************************************************************
 *                DECLARATION OF COMMUNICATION BLOCKS                   *
************************************************************************/
// TCP_CONNECT
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,CONNECT)
  __DECLARE_VAR(STRING,IP_ADDRESS)
  __DECLARE_VAR(UINT,PORT)
  __DECLARE_VAR(BOOL,UDP)
  __DECLARE_VAR(UINT,SOCKET_ID)

  // FB private variables - TEMP, private and located variables

} TCP_CONNECT;


// TCP_SEND
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,SEND)
  __DECLARE_VAR(UINT,SOCKET_ID)
  __DECLARE_VAR(STRING,MSG)
  __DECLARE_VAR(UINT,BYTES_SENT)

  // FB private variables - TEMP, private and located variables

} TCP_SEND;


// TCP_RECEIVE
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,RECEIVE)
  __DECLARE_VAR(UINT,SOCKET_ID)
  __DECLARE_VAR(UINT,BYTES_RECEIVED)
  __DECLARE_VAR(STRING,MSG)

  // FB private variables - TEMP, private and located variables

} TCP_RECEIVE;


// TCP_CLOSE
// Data part
typedef struct {
  // FB Interface - IN, OUT, IN_OUT variables
  __DECLARE_VAR(BOOL,EN)
  __DECLARE_VAR(BOOL,ENO)
  __DECLARE_VAR(BOOL,CLOSE)
  __DECLARE_VAR(UINT,SOCKET_ID)
  __DECLARE_VAR(INT,SUCCESS)
 
  // FB private variables - TEMP, private and located variables

} TCP_CLOSE;


/************************************************************************
 *                 END OF COMMUNICATION LIB BLOCKS                      *
************************************************************************/

/************************************************************************
 *              DECLARATION OF COMMUNICATION LIB BLOCKS                 *
************************************************************************/

static void TCP_CONNECT_init__(TCP_CONNECT *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->CONNECT,0,retain)
  __INIT_VAR(data__->IP_ADDRESS,__STRING_LITERAL(0,""),retain)
  __INIT_VAR(data__->PORT,0,retain)
  __INIT_VAR(data__->UDP,0,retain)
  __INIT_VAR(data__->SOCKET_ID,0,retain)
}

// Code part
static void TCP_CONNECT_body__(TCP_CONNECT *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }

  __SET_VAR(data__->,SOCKET_ID,,tcp_connect(data__->IP_ADDRESS, data__->PORT));

  goto __end;

__end:
  return;
} // TCP_CONNECT_body__()


static void TCP_SEND_init__(TCP_SEND *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->SEND,0,retain)
  __INIT_VAR(data__->SOCKET_ID,0,retain)
  __INIT_VAR(data__->MSG,__STRING_LITERAL(0,""),retain)
  __INIT_VAR(data__->BYTES_SENT,0,retain)
}

// Code part
static void TCP_SEND_body__(TCP_SEND *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }

  __SET_VAR(data__->,BYTES_SENT,,tcp_send(data__->SOCKET_ID, data__->MSG));

  goto __end;

__end:
  return;
} // TCP_SEND_body__()


static void TCP_RECEIVE_init__(TCP_RECEIVE *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->RECEIVE,0,retain)
  __INIT_VAR(data__->SOCKET_ID,0,retain)
  __INIT_VAR(data__->BYTES_RECEIVED,0,retain)
  __INIT_VAR(data__->MSG,__STRING_LITERAL(0,""),retain)
}

// Code part
static void TCP_RECEIVE_body__(TCP_RECEIVE *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  
  __SET_VAR(data__->,BYTES_RECEIVED,,tcp_receive(data__->SOCKET_ID, data__->MSG));

  goto __end;

__end:
  return;
} // TCP_RECEIVE_body__()


static void TCP_CLOSE_init__(TCP_CLOSE *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->CLOSE,0,retain)
  __INIT_VAR(data__->SOCKET_ID,0,retain)
  __INIT_VAR(data__->SUCCESS,0,retain)
}

// Code part
static void TCP_CLOSE_body__(TCP_CLOSE *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  
  __SET_VAR(data__->,SUCCESS,,tcp_close(data__->SOCKET_ID));

  goto __end;

__end:
  return;
} // TCP_CLOSE_body__()

/************************************************************************
 *                  END OF COMMUNICATION LIB BLOCK                      *
************************************************************************/