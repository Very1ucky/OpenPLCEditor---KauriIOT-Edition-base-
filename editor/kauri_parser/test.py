import unittest
import builder


class TestBuilderClass(unittest.TestCase):

    parser = builder.PlcProgramParser()

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
        
        for act in acts:
            print(act)
        print(self.parser._predefined_temp_vars)
        
        self.assertEqual(len(acts), 10)
        
        
if __name__ == "__main__":
    unittest.main()