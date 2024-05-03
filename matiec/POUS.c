void ROTARY_SWITCH_init__(ROTARY_SWITCH *data__, BOOL retain) {
  __INIT_VAR(data__->EN,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->ENO,__BOOL_LITERAL(TRUE),retain)
  __INIT_VAR(data__->READ,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->ERROR,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->OUT,0,retain)
}

// Code part
void ROTARY_SWITCH_body__(ROTARY_SWITCH *data__) {
  // Control execution
  if (!__GET_VAR(data__->EN)) {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(FALSE));
    return;
  }
  else {
    __SET_VAR(data__->,ENO,,__BOOL_LITERAL(TRUE));
  }
  // Initialise TEMP variables

  if ((__GET_VAR(data__->READ,) == __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,OUT,,0);
  };

  goto __end;

__end:
  return;
} // ROTARY_SWITCH_body__() 





