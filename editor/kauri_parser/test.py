import unittest
import builder


class TestBuilderClass(unittest.TestCase):

    parser = builder.PlcProgramParser()

    def test_blink_program(self):
        acts = self.parser.extractActionsFromSec("""  __SET_VAR(data__->TON0.,IN,,!(__GET_LOCATED(data__->BLINK_LED,)));
  __SET_VAR(data__->TON0.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TON_body__(&data__->TON0);
  __SET_VAR(data__->TOF0.,EN,,__GET_VAR(data__->TON0.ENO,));
  __SET_VAR(data__->TOF0.,IN,,__GET_VAR(data__->TON0.Q,));
  __SET_VAR(data__->TOF0.,PT,,__time_to_timespec(1, 500, 0, 0, 0, 0));
  TOF_body__(&data__->TOF0);
  __SET_LOCATED(data__->,BLINK_LED,,__GET_VAR(data__->TOF0.Q,));""", {'type': 'BLINK', 'vars': {'BLINK_LED': {'number': 0, 'type': 'BOOL', 'location': '', 'init_value': False}, 'TON0.EN': {'number': 1, 'type': 'BOOL', 'location': '', 'init_value': True}, 'TON0.ENO': {'number': 2, 'type': 'BOOL', 'location': '', 'init_value': True}, 'TON0.IN': {'number': 3, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TON0.PT': {'number': 4, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TON0.Q': {'number': 5, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TON0.ET': {'number': 6, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TON0.STATE': {'number': 7, 'type': 'SINT', 'location': '', 'init_value': ''}, 'TON0.PREV_IN': {'number': 8, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TON0.CURRENT_TIME': {'number': 9, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TON0.START_TIME': {'number': 10, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TOF0.EN': {'number': 11, 'type': 'BOOL', 'location': '', 'init_value': True}, 'TOF0.ENO': {'number': 12, 'type': 'BOOL', 'location': '', 'init_value': True}, 'TOF0.IN': {'number': 13, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TOF0.PT': {'number': 14, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TOF0.Q': {'number': 15, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TOF0.ET': {'number': 16, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TOF0.STATE': {'number': 17, 'type': 'SINT', 'location': '', 'init_value': ''}, 'TOF0.PREV_IN': {'number': 18, 'type': 'BOOL', 'location': '', 'init_value': ''}, 'TOF0.CURRENT_TIME': {'number': 19, 'type': 'TIME', 'location': '', 'init_value': ''}, 'TOF0.START_TIME': {'number': 20, 'type': 'TIME', 'location': '', 'init_value': ''}}, 'actions': [{'act_type': 'NOT', 'vars': [{'var_pos': -1, 'is_val': True}, {'var_pos': 0, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 1, 'is_val': False}, {'var_pos': 0, 'is_val': True}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 3, 'is_val': False}, {'var_pos': -1, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 4, 'is_val': False}, {'var_pos': 1, 'is_val': True}]}, {'act_type': 'TON', 'vars': [{'var_pos': 1, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 11, 'is_val': False}, {'var_pos': 2, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 13, 'is_val': False}, {'var_pos': 5, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 14, 'is_val': False}, {'var_pos': 1, 'is_val': True}]}, {'act_type': 'TOF', 'vars': [{'var_pos': 11, 'is_val': False}]}, {'act_type': 'SET_VAR', 'vars': [{'var_pos': 0, 'is_val': False}, {'var_pos': 15, 'is_val': False}]}]})
        print("BLink test:")
        for act in acts:
            print(act)
        print(self.parser._predefined_temp_vars)
        print()
        self.assertEqual(len(acts), 9)
        
        
    def test_if_sts_parse(self):
        acts = self.parser.extractActionsFromSec(
            """  __SET_VAR(data__->,LOCALVAR0,,__STRING_LITERAL(7,"Test123"));
  if (!__BOOL_LITERAL(TRUE)) {
    __SET_VAR(data__->,LOCALVAR1,,__BOOL_LITERAL(TRUE));
  } else {
    if (__BOOL_LITERAL(TRUE))) {
      __SET_VAR(data__->,LOCALVAR1,,__BOOL_LITERAL(FALSE));
      if (!__BOOL_LITERAL(FALSE)) {
        __SET_VAR(data__->,LOCALVAR1,,__BOOL_LITERAL(FALSE));
      };
    };
  };
    __SET_VAR(data__->,LOCALVAR0,,__STRING_LITERAL(280,"Test123"));""",
            {
                "vars": {
                    "LOCALVAR1": {"number": 1, "type": "BOOL"},
                    "LOCALVAR0": {"number": 0, "type": "STRING"},
                }
            },
        )
        
        print("Nested if test:")
        for act in acts:
            print(act)
        print(self.parser._predefined_temp_vars)
        print()
        
        self.assertEqual(len(acts), 10)
        
        
if __name__ == "__main__":
    unittest.main()