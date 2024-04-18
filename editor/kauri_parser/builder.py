import os
import platform as os_platform
import time
import struct
import socket
from numpy import isin
import pycparser.ast_transforms
import pycparser.c_ast
import serial

import wx

import re
import datetime

import pycparser
from pycparser import parse_file


class PlcProgramParser:

    var_type_dict = {
        "BOOL": {"pos": 0, "size": 1, "str_char": "?"},
        "SINT": {"pos": 1, "size": 1, "str_char": "b"},
        "INT": {"pos": 2, "size": 2, "str_char": "h"},
        "DINT": {"pos": 3, "size": 4, "str_char": "i"},
        "LINT": {"pos": 4, "size": 8, "str_char": "q"},
        "USINT": {"pos": 5, "size": 1, "str_char": "B"},
        "UINT": {"pos": 6, "size": 2, "str_char": "H"},
        "UDINT": {"pos": 7, "size": 4, "str_char": "I"},
        "ULINT": {"pos": 8, "size": 8, "str_char": "Q"},
        "REAL": {"pos": 9, "size": 4, "str_char": "f"},
        "LREAL": {"pos": 10, "size": 8, "str_char": "d"},
        "TIME": {"pos": 11, "size": 4, "str_char": "f"},
        "DATE": {"pos": 12, "size": 4, "str_char": "f"},
        "TOD": {"pos": 13, "size": 4, "str_char": "f"},
        "DT": {"pos": 14, "size": 4, "str_char": "f"},
        "STRING": {"pos": 15, "size": 1, "str_char": "s"},
        "BYTE": {"pos": 16, "size": 1, "str_char": "B"},
        "WORD": {"pos": 17, "size": 2, "str_char": "H"},
        "DWORD": {"pos": 17, "size": 4, "str_char": "I"},
        "LWORD": {"pos": 19, "size": 8, "str_char": "Q"},
    }

    act_type_dict = {
        "SET_VAR": 0,
        "NOT": 1,
        "AND": 2,
        "OR": 3,
        "IF": 4,
        "FOR": 5,
        "WHILE": 6,
        "TON": 7,
        "TOF": 8,
        "R_TRIG": 9,
        "F_TRIG": 10,
        "CTU": 11,
        "CTD": 12,
        "SUB": 13,
        "ADD": 14,
        "DIV": 15,
        "MULT": 16,
        "EQ": 17,
        "GT": 18,
        "LT": 19,
        "GE": 20,
        "LE": 21,
        "NE": 22,
    }

    loc_types = {"": 0, "IX": 1, "QX": 2, "IW": 3, "QW": 4}

    statement_dict = {
        "IF": r"((?P<ws> +)if \((?P<exp>.*?)\) \{\n(?P<if_con>.*?)(?:(?P=ws)\} else \{\n(?P<el_con>.*;))?\n(?P=ws)\};)"
    }

    _global_vars = dict()

    _temp_var_pos = -1
    _temp_var_max_pos = 0
    _predefined_temp_vars = dict()
    _command_list = list()

    _common_var_type = None

    _code_to_op = {
        "GT": ">",
        "LT": "<",
        "GE": ">=",
        "LE": "<=",
        "EQ": "==",
        "NE": "!=",
        "AND": "&&",
        "OR": "||",
        "XOR": "&&",
    }
    _op_to_code = {
        ">": "GT",
        "<": "LT",
        ">=": "GE",
        "<=": "LE",
        "==": "EQ",
        "!=": "NE",
        "&&": "AND",
        "||": "OR",
        "!": "NOT",
        "+": "ADD",
        "-": "SUB",
        "*": "MULT",
        "/": "DIV",
    }

    def scrollToEnd(self, txtCtrl):
        if os_platform.system() != "Darwin":
            txtCtrl.SetInsertionPoint(-1)
        txtCtrl.ShowPosition(txtCtrl.GetLastPosition())
        txtCtrl.Refresh()
        txtCtrl.Update()

    def outputIntoCompileWindow(self, str: str):
        global compiler_logs
        compiler_logs += str
        wx.CallAfter(self.txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(self.scrollToEnd, self.txtCtrl)

    def build(
        self,
        defs,
        st_file,
        pous_code,
        resource_code,
        resource_name,
        program_list,
        debug_vars_list,
        port,
        txtCtrl,
        update_subsystem,
        build_path,
    ):
        global compiler_logs
        compiler_logs = ""

        pous_code = self.transformPousCode(pous_code)
        with open(os.path.join(build_path, "POUS.c"), "w") as f:
            f.write(pous_code)

        with open(os.path.join(build_path, "res.txt"), "w") as f:
            pous_ast = parse_file(
                os.path.join(build_path, "POUS.c"),
                use_cpp=True,
                cpp_path="E:/Projects/OpenPLC_Editor/mingw/bin/clang.exe",
                cpp_args=["-E", "E:/Users/Downloads/utils/fake_libc_include"],
            )
            f.write(str(pous_ast))

        self._predefined_temp_vars = dict()
        self._temp_var_pos = -1
        self._temp_var_max_pos = 0

        self.txtCtrl = txtCtrl

        # output definitions (MD5 hash, modbus info, ticktime)
        compiler_logs += "Definitions:\n"
        for def_name, content in defs.items():
            self.outputIntoCompileWindow(f"\t{def_name}: {content}\n")
        self.outputIntoCompileWindow("\n")

        # extract instances
        (global_vars, instances) = self.extractInstancesAndGlobVars(
            program_list, debug_vars_list, pous_ast, resource_code
        )
        compiler_logs += "Predefined variables:\n"
        for val, content in self._predefined_temp_vars.items():
            self.outputIntoCompileWindow(f"\t{val}: {content}\n")

        compiler_logs += f"Temp vars count: {self._temp_var_max_pos}\n\n"

        compiler_logs += "Global vars:\n"
        for val, content in global_vars.items():
            self.outputIntoCompileWindow(f"\t{val}: {content}\n")

        # output instances values into debug window
        for path, inst in instances.items():
            self.outputIntoCompileWindow("Instance: " + path + "\n")

            compiler_logs += "\tVars:\n"
            for var_name, content in inst["vars"].items():
                self.outputIntoCompileWindow(f"\t\t{var_name}: {content}\n")

            compiler_logs += "\tActions:\n"
            for act in inst["actions"]:
                self.outputIntoCompileWindow(f"\t\t{act}\n")
            self.outputIntoCompileWindow("\n")

        # extract locations from instances
        locations = self.extractLocations(instances, global_vars)
        # output locations into window output
        compiler_logs += "Locations:\n"
        for loc_name, content in locations.items():
            self.outputIntoCompileWindow(f"\t{loc_name}: {content}\n")
        self.outputIntoCompileWindow("\n")

        # extract tasks from c file with resources
        tasks = self.extractTasks(resource_code, resource_name, instances)
        # output tasks into window output
        compiler_logs += "Tasks:\n"
        for task_name, content in tasks.items():
            self.outputIntoCompileWindow(f"\t{task_name}: {content}\n")

        self.createFirmware(build_path, global_vars, instances, locations, defs, tasks)

        if port is not None:
            self.sendFwViaSerial(port, os.path.join(build_path, "firmware.ki"))

    def transformPousCode(self, pous_code):

        res = re.search(r"\n\nvoid .*_init", pous_code, flags=re.S)
        pous_code = pous_code[pous_code.find(res[0]) :]

        res = re.findall(r"void .*_(?:init|body)__\((.*?)\) \{", pous_code)
        for r in res:
            pous_code = pous_code.replace(r, "")

        res = re.findall(
            r"((EQ|GT|GE|LT|LE|NE)_.*?\(.*?, .*?, .*?, (.*?), (.*?\)?)\))", pous_code
        )
        res += re.findall(r"((EQ|GT|GE|LT|LE)_.*?\(\n.*?,\n.*?,\n.*?,\n\W*\(.*?\)(.*?),\n\W*\(.*?\)([^\n]*?\)?)\))", pous_code, flags=re.S)
        res += re.findall(r"((NE)_.*?\(\n.*?,\n.*?,\n\W*\(.*?\)(.*?),\n\W*\(.*?\)([^\n]*?\)?)\))", pous_code, flags=re.S)
        for r in res:
            op = self._code_to_op[r[1]]
            pous_code = pous_code.replace(r[0], f"{r[2]} {op} {r[3]}")

        res = re.findall(
            r"((AND|OR|XOR).*?\(\n.*?,\n.*?,\n.*?,\n\W*\(.*?\)(.*?),\n\W*\(.*?\)([^\n]*?\)?)\))",
            pous_code,
            flags=re.S,
        )
        for r in res:
            op = self._code_to_op[r[1]]
            pous_code = pous_code.replace(r[0], f"{r[2]} {op} {r[3]}")

        res = re.findall(
            r"((?:__SET_VAR|__SET_LOCATED|__SET_EXTERNAL)\(data__->(.*?),,(.*?)\);)",
            pous_code,
        )
        for r in res:
            to_var = r[1].replace(",", "")
            from_var = r[2]
            pous_code = pous_code.replace(r[0], f"__SET_VAR({to_var}, {from_var});")

        res = re.findall(r"(__GET_VAR\(data__->(.*?),\))", pous_code)
        res += re.findall(r"(__GET_LOCATED\(data__->(.*?),\))", pous_code)
        for r in res:
            pous_code = pous_code.replace(r[0], f"__GET_VAR({r[1]})")

        res = re.findall(
            r"(__INIT_LOCATED\(.*?,__(.*?),data__->(.*?),retain\))", pous_code
        )
        for r in res:
            pous_code = pous_code.replace(r[0], f"__INIT_LOCATED({r[2]},{r[1]});")

        res = re.findall(
            r"(__INIT_EXTERNAL\(.*?,.*?,data__->(.*?),retain\))", pous_code
        )
        for r in res:
            pous_code = pous_code.replace(r[0], f"__INIT_EXTERNAL({r[1]});")

        res = re.findall(r"(__INIT_VAR\(data__->(.*?),(.*?),retain\))", pous_code)
        res += re.findall(r"(__INIT_LOCATED_VALUE\(data__->(.*?),(.*)\))", pous_code)
        for r in res:
            pous_code = pous_code.replace(r[0], f"__INIT_VAR({r[1]},{r[2]});")

        res = re.findall(r"(_init__\(&data__->(.*?),retain\))", pous_code)
        for r in res:
            pous_code = pous_code.replace(r[0], f"_init__({r[1]})")

        res = re.findall(r"(_body__\(&data__->(.*?)\))", pous_code)
        for r in res:
            pous_code = pous_code.replace(r[0], f"_body__({r[1]})")

        res = re.findall(
            r"(  goto __end;\n\n__end:\n\W*return;\n)", pous_code, flags=re.S
        )
        for r in res:
            pous_code = pous_code.replace(r, "")

        print(pous_code)

        return pous_code

    def extractInstancesAndGlobVars(
        self,
        program_list: list,
        debug_vars_list: list,
        pous_ast: pycparser.c_ast.FileAST,
        res_code: str,
    ) -> tuple:
        # extract instances from program_list
        instances = dict()
        global_vars = dict()
        inst_number = 0
        for prog in program_list:
            instances[prog["C_path"]] = {
                "number": inst_number,
                "type": prog["type"],
                "vars": {},
                "actions": [],
            }
            inst_number += 1
        # extract vars from debug_vars_list
        var_number = 0
        for var in debug_vars_list:
            temp = var["C_path"].partition(".")
            init_value = None
            if instances.get(temp[0]) is not None:
                var_name = temp[2]
            else:
                var_name = var["C_path"].split("__")[1]

            if var_name.endswith(".EN") or var_name.endswith(".ENO"):
                init_value = True
            var_dict = {
                "number": var_number,
                "type": var["type"],
                "location": None,
                "init_value": init_value,
                "visibility": "LOCAL",
            }

            if instances.get(temp[0]) is not None:
                instances[temp[0]]["vars"][var_name] = var_dict
            else:
                var_dict["visibility"] = "GLOBAL"
                var_dict["linked_vars_poses"] = []
                global_vars[var_name] = var_dict
            var_number += 1
        # extrac global vars init values and locations
        for var, content in global_vars.items():
            if len(var.split(".")) == 1:
                loc_data = re.search(
                    rf"__INIT_GLOBAL_LOCATED\(.*?,{var},__(.*?),retain\)", res_code
                )
                if loc_data is not None:
                    content["location"] = loc_data[1].replace("_", ".")

                init_value_data = re.search(
                    rf"{var},__INITIAL_VALUE\((.*?)\),retain", res_code
                )
                if init_value_data is not None:
                    var = self.extractValueFromStr(init_value_data[1])
                    if var is not None and (var == 0 or var == ""):
                        var = None
                    content["init_value"] = var

        for path, inst in instances.items():
            # vars init values and locations part
            for func_def in pous_ast.ext:
                if func_def.decl.name == f"{inst['type']}_init__":
                    init_sec = func_def.body
            self.extractInitDataFromSec(init_sec, inst["vars"], global_vars)

            # actions part
            for func_def in pous_ast.ext:
                if func_def.decl.name == f"{inst['type']}_body__":
                    body_sec = func_def.body
            inst["actions"] = self.extractActionsFromSec(body_sec, inst["vars"])

        return (global_vars, instances)

    def extractInitDataFromSec(
        self, sec: pycparser.c_ast.Compound, inst_vars: dict, global_vars: dict
    ):
        for func in sec.block_items:
            if type(func) == pycparser.c_ast.FuncCall:
                func_name = func.name.name
                if func_name == "__INIT_LOCATED":
                    var = inst_vars[func.args.exprs[0].name]
                    var["location"] = func.args.exprs[1].name.replace("_", ".")
                elif func_name == "__INIT_VAR":
                    var = inst_vars[func.args.exprs[0].name]
                    var["init_value"] = self.extractVarInfoFromExpr(func.args.exprs[1])[
                        0
                    ]
                    if var["init_value"] is not None and (
                        var["init_value"] == 0 or var["init_value"] == ""
                    ):
                        var["init_value"] = None
                elif func_name == "__INIT_EXTERNAL":
                    glob_var_name = func.args.exprs[0].name
                    global_vars[glob_var_name]["linked_vars_poses"].append(
                        inst_vars[glob_var_name]["number"]
                    )
                    inst_vars[glob_var_name]["visibility"] = "GLOBAL"
            else:
                raise SyntaxError()

    def extractActionsFromSec(
        self, sec: pycparser.c_ast.Compound, inst_vars: dict
    ) -> list:
        actions = list()

        for sec_op in sec.block_items:
            self._temp_var_pos = -1
            if type(sec_op) == pycparser.c_ast.FuncCall:
                actions += self.extractFuncActions(sec_op, inst_vars)
            else:
                bl_ins_pos = 0
                bl_vars = []
                bl_var_pos = 0
                bl_type = ""
                if type(sec_op) == pycparser.c_ast.If:
                    bl_type = "IF"
                    cond = sec_op.cond
                    true_sec = sec_op.iftrue
                    false_sec = sec_op.iffalse

                    (bl_var_pos, bl_is_val, bool_acts) = self.extractFuncArgActions(
                        cond, inst_vars
                    )
                    actions += bool_acts
                    bl_vars.append(self.getVarDict(bl_var_pos, bl_is_val))

                    bl_ins_pos = len(actions)

                    true_acts = self.extractActionsFromSec(true_sec, inst_vars)
                    false_acts = self.extractActionsFromSec(false_sec, inst_vars)

                    actions += true_acts
                    actions += false_acts

                    bl_vars.append(
                        self.getVarDict(
                            self.getPredefinedVarPos(len(true_acts), "UINT"), True
                        )
                    )
                    bl_vars.append(
                        self.getVarDict(
                            self.getPredefinedVarPos(len(false_acts), "UINT"), True
                        )
                    )

                if bl_type != "":
                    actions.insert(bl_ins_pos, {"act_type": bl_type, "vars": bl_vars})

        return actions

    def extractFuncActions(
        self, func: pycparser.c_ast.FuncCall, inst_vars: dict
    ) -> list:
        actions = list()

        func_name = func.name.name
        act_type = ""
        act_vars = []
        if func_name == "__SET_VAR":
            act_type = "SET_VAR"
            var_name = self.extractVarName(func.args.exprs[0])
            var = inst_vars[var_name]
            act_vars.append(self.getVarDict(var["number"], False))

            (act_var_var_pos, act_is_val, acts) = self.extractFuncArgActions(
                func.args.exprs[1], inst_vars, var["type"]
            )
            act_vars.append(self.getVarDict(act_var_var_pos, act_is_val))
            actions += acts
        elif "_body__" in func_name:
            act_type = func_name.split("_")[0]
            var_to_set = self.extractVarName(func.args.exprs[0])
            act_var_pos = inst_vars[var_to_set + ".EN"]["number"]
            act_vars.append(self.getVarDict(act_var_pos, False))

        actions.append({"act_type": act_type, "vars": act_vars})

        return actions
    
    def extractFuncArgActions(
        self, exp_to_pars, inst_vars: dict, common_type=None
    ) -> tuple:

        actions = list()
        (var_pos, is_val, var_type) = self.extractVarData(
            exp_to_pars, inst_vars, True, common_type
        )

        if var_pos >= 0:
            return (var_pos, is_val, actions)

        conds = [{"pos": var_pos, "cond": exp_to_pars}]
        if self.isDigitType(common_type):
            conds.insert(0, "Change pred types")
        while len(conds) > 0:
            cond = conds.pop()
            if type(cond) == str:
                self.fillNoneTypesOfPredVars(common_type)
                common_type = None
                continue
            cond_type = type(cond["cond"])
            if cond_type in (pycparser.c_ast.BinaryOp, pycparser.c_ast.UnaryOp):
                if cond["cond"].op in ('>', '<', ">=", "<=", "==", "!="):
                    conds.append("Change pred types")
                actions.insert(
                    0,
                    {
                        "act_type": self._op_to_code[cond["cond"].op],
                        "vars": [self.getVarDict(cond["pos"], False)],
                    },
                )
                action = actions[0]

            values = []
            if cond_type == pycparser.c_ast.BinaryOp:
                values = [cond["cond"].left, cond["cond"].right]
            elif cond_type == pycparser.c_ast.UnaryOp:
                values = [cond["cond"].expr]

            for c in values:
                if type(c) in (
                    pycparser.c_ast.Constant,
                    pycparser.c_ast.ID,
                    pycparser.c_ast.FuncCall,
                ) or (type(c) == pycparser.c_ast.UnaryOp and c.op == '-'):
                    (vp, iv, var_type) = self.extractVarData(c, inst_vars, False)
                    if not self.isDigitType(var_type):
                        self.fillNoneTypesOfPredVars(var_type)
                    if (
                        common_type is None
                        or self.var_type_dict[var_type]["size"]
                        > self.var_type_dict[common_type]["size"]
                        or (
                            self.var_type_dict[var_type]["size"]
                            == self.var_type_dict[common_type]["size"]
                            and self.isUnsignedType(common_type)
                        )
                    ):
                        common_type = var_type
                    if vp < 0:
                        com_acts = self.extractFuncActions(c, inst_vars, vp)
                        for com_act in reversed(com_acts):
                            actions.insert(0, com_act)
                else:
                    vp = self.getNextTempVar()
                    iv = False
                    conds.append({"pos": vp, "cond": c})
                if cond_type in (pycparser.c_ast.BinaryOp, pycparser.c_ast.UnaryOp):
                    action["vars"].append(self.getVarDict(vp, iv))

        return (var_pos, is_val, actions)

    def isDigitType(self, var_type: str) -> bool:
        return var_type not in ("BOOL", "STRING")
    
    def isUnsignedType(self, var_type: str) -> bool:
        return var_type in ("USINT", "UINT", "ULINT", "UDINT", "BYTE", "WORD", "LWORD", "DWORD", "BOOL")
    
    def fillNoneTypesOfPredVars(self, type_to_fill: str):
        pred_vars_keys = list(self._predefined_temp_vars.keys())
        for pred_var_key in pred_vars_keys:
            if pred_var_key[1] is None:
                temp = dict(self._predefined_temp_vars.pop(pred_var_key))
                if self._predefined_temp_vars.get((pred_var_key[0], type_to_fill)) is None:
                    self._predefined_temp_vars[(pred_var_key[0], type_to_fill)] = temp

    def getNextTempVar(self) -> int:
        res = self._temp_var_pos
        self._temp_var_pos -= 1
        self._temp_var_max_pos = max(abs(res), self._temp_var_max_pos)

        return res

    def extractVarData(
        self, expr, inst_vars: dict, fill_num_pred_type: bool, type_to_fill=None
    ) -> tuple:
        var_info = self.extractVarInfoFromExpr(expr)
        var_type = None
        if var_info is not None:
            pred_type = var_info[1]
            var_type = pred_type
            if fill_num_pred_type is False and self.isDigitType(var_type):
                pred_type = None
            elif type_to_fill is not None:
                pred_type = type_to_fill
            var_pos = self.getPredefinedVarPos(var_info[0], pred_type)
            is_val = True
        elif self.isItVariable(expr):
            var_name = self.extractVarName(expr.args.exprs[0])
            var_pos = inst_vars[var_name]["number"]
            var_type = inst_vars[var_name]["type"]
            is_val = False
        else:
            var_pos = self.getNextTempVar()
            is_val = False

        return (var_pos, is_val, var_type)

    def isItVariable(self, var) -> bool:
        return type(var) == pycparser.c_ast.FuncCall and var.name.name == "__GET_VAR"

    def getVarDict(self, var_pos: int, is_val: bool):
        return {"var_pos": var_pos, "is_val": is_val}

    def getPredefinedVarPos(self, var_val, var_type):
        var_pos = self._predefined_temp_vars.get((var_val, var_type))

        if var_pos is None:
            var_pos = len(self._predefined_temp_vars.keys())
            self._predefined_temp_vars[(var_val, var_type)] = {"number": var_pos}
        else:
            var_pos = var_pos["number"]

        return var_pos

    def extractVarInfoFromExpr(self, expression) -> tuple:
        if type(expression) == pycparser.c_ast.UnaryOp and expression.op == '-':
            expression = expression.expr
            expression.value = '-' + expression.value
        if type(expression) == pycparser.c_ast.Constant:

            if expression.type == "int":
                res_value = int(expression.value)
                if res_value >= 0:
                    if res_value <= 2**8 - 1:
                        res_type = "USINT"
                    elif res_value <= 2**16 - 1:
                        res_type = "UINT"
                    elif res_value <= 2**32 - 1:
                        res_type = "LINT"
                    else:
                        res_type = "DINT"
                else:
                    if res_value >= -2 ** (8 - 1):
                        res_type = "SINT"
                    elif res_value >= -2 ** (16 - 1):
                        res_type = "INT"
                    elif res_value >= -2 ** (32 - 1):
                        res_type = "LINT"
                    else:
                        res_type = "DINT"
            elif expression.type == "double":
                res_value = float(expression.value)
                if res_value > 3.3e38 or res_value < -3.3e38:
                    res_type = "LREAL"
                else:
                    res_type = "REAL"
            else:
                raise TypeError()

            return (res_value, res_type)
        elif type(expression) == pycparser.c_ast.FuncCall:
            expr_name = expression.name.name
            if expr_name == "__BOOL_LITERAL":
                res_type = "BOOL"
                res_value = expression.args.exprs[0].name.lower() in "true"
            elif expr_name == "__time_to_timespec":
                res_type = "TIME"
                time_parts = list(
                    map(lambda const: float(const.value), expression.args.exprs)
                )
                res_value = (
                    time_parts[1] / 1e3
                    + time_parts[2]
                    + time_parts[3] * 60
                    + time_parts[4] * 60 * 60
                    + time_parts[5] * 60 * 60 * 24
                )
                if time_parts[0] < 0:
                    res_value *= -1
            elif expr_name == "__date_to_timespec":
                res_type = "DATE"
                date_parts = list(
                    map(lambda const: int(const.value), expression.args.exprs)
                )
                dt = datetime.datetime(date_parts[2], date_parts[1], date_parts[0])
                res_value = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            elif expr_name == "__tod_to_timespec":
                res_type = "TOD"
                tod_parts = list(
                    map(lambda const: float(const.value), expression.args.exprs)
                )
                res_value = tod_parts[2] * 60 * 60 + tod_parts[1] * 60 + tod_parts[0]
            elif expr_name == "__dt_to_timespec":
                res_type = "DT"
                dt_parts = list(
                    map(lambda const: int(const.value), expression.args.exprs)
                )
                dt = datetime.datetime(
                    dt_parts[5],
                    dt_parts[4],
                    dt_parts[3],
                    dt_parts[2],
                    dt_parts[1],
                    dt_parts[0],
                )
                res_value = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            elif expr_name == "__STRING_LITERAL":
                res_type = "STRING"
                res_value = expression.args.exprs[1].value[1:-1]
            else:
                return None

            return (res_value, res_type)

        else:
            return None

    def extractVarName(self, var) -> str:
        res = ""
        while type(var) != pycparser.c_ast.ID:
            res += var.name.name + "."
            var = var.field
        return res + var.name

    def sendFwViaSerial(self, port, fw_path):
        send_client = ModbusSendClient(
            modbus_type="RTU", serial_port=port, baudrate=115200, slave_id=1
        )
        send_client.connect()
        f = open(fw_path, "rb")
        data_byte = f.read(251)
        send_client._send_modbus_request(103, bytes())
        while data_byte:
            send_client._send_modbus_request(102, data_byte)
            data_byte = f.read(251)
        f.close()
        send_client._send_modbus_request(104, bytes())
        send_client.disconnect()

    def extractLocations(self, instances: dict, global_vars: dict) -> dict:
        locations = dict()
        for loc_type in self.loc_types.keys():
            if loc_type != "":
                locations[loc_type] = {}

        list_of_vars_dicts = list(map(lambda inst: inst["vars"], instances.values()))
        list_of_vars_dicts.append(global_vars)

        for vars_dict in list_of_vars_dicts:
            for var_name, content in vars_dict.items():
                location = None
                if content["location"] is not None:
                    location = content["location"]
                    var_number = content["number"]
                elif content["visibility"] == "GLOBAL":
                    location = global_vars[var_name]["location"]
                    var_number = global_vars[var_name]["number"]

                if location is not None:
                    loc_type = location[:2]
                    loc_port_pos_str = location[2:]
                    # TODO check locations format
                    location_parts = list(map(int, loc_port_pos_str.split(".")))
                    if len(location_parts) == 1:
                        location_pos = location_parts[0]
                    else:
                        location_pos = location_parts[0] * 8 + location_parts[1]

                    locations[loc_type][location_pos] = var_number

        for loc_type, content in locations.items():
            locations[loc_type] = {key: content[key] for key in sorted(content.keys())}

        return locations

    def extractTasks(self, res0_code: str, resource_name: str, instances: dict) -> dict:
        tasks = {}
        tasks_pattern = r"_run__\(unsigned long tick\) \{(.*?)\}\n\n"
        tasks_sec = re.search(tasks_pattern, res0_code, flags=re.S)[1]

        tasks_parts = re.findall(r"(\w*?) = !\(tick \% (.*?)\);", tasks_sec)
        for task_parts in tasks_parts:
            tasks[task_parts[0]] = {"TICK_COUNT": int(task_parts[1]), "INSTANCES": []}
        for task in tasks.keys():
            inst_task_names = re.findall(
                rf"if \({task}\) {{.*?_body__\(&(.*?)\).*?}}", tasks_sec, flags=re.S
            )
            for inst_task_name in inst_task_names:
                tasks[task]["INSTANCES"].append(
                    instances[resource_name.upper() + "__" + inst_task_name]["number"]
                )

        return tasks

    def createFirmware(
        self,
        build_path: str,
        global_vars: dict,
        instances: dict,
        locations: dict,
        defs: dict,
        tasks: dict,
    ):
        try:
            os.remove(os.path.join(build_path, "firmware.ki"))
        except FileNotFoundError:
            None
        f = open(os.path.join(build_path, "firmware.ki"), "wb")

        header_bytes = bytes()
        # md5
        md5_len = len(defs["MD5"])
        header_bytes = struct.pack(
            "<H" + str(md5_len) + "s", md5_len, bytes(defs["MD5"], "utf-8")
        )

        varsSize, varsCount = self.getProgramVarsSizeAndCount(global_vars, instances)

        header_bytes += struct.pack("<II", varsSize, varsCount)
        # temp vars count
        header_bytes += struct.pack("<I", self._temp_var_max_pos)
        # ticktime
        ticktime = defs["TICKTIME"] / 1e9
        header_bytes += struct.pack("<f", ticktime)
        # instances count
        header_bytes += struct.pack("<I", len(instances))
        # modbus serial
        header_bytes += struct.pack(
            "<?IB",
            defs["MODBUS_SERIAL"]["ENABLED"],
            int(defs["MODBUS_SERIAL"]["BAUD_RATE"]),
            int(defs["MODBUS_SERIAL"]["SLAVE_ID"]),
        )
        # TODO parse another fields of mb tcp
        header_bytes += struct.pack("<?", defs["MODBUS_TCP"]["ENABLED"])

        # parse predefined vars
        predefined_vars_bytes = struct.pack(
            "<I", len(self._predefined_temp_vars.keys())
        )
        for (val, pred_var_type), content in self._predefined_temp_vars.items():
            (var_len, pack_str) = self.getVarLenAndPackStr(pred_var_type, False, val)
            type_info = self.var_type_dict[pred_var_type]
            var_type = type_info["pos"]
            if pred_var_type == "STRING":
                val = bytes(val, "utf-8")
            predefined_vars_bytes += struct.pack(
                "<BH" + pack_str, var_type, var_len, val
            )

        # parse global vars
        global_vars_bytes = struct.pack("<I", len(global_vars.keys()))
        for var_name, content in global_vars.items():

            var_bytes = bytes()
            pack_str = "<B"
            type_info = self.var_type_dict[content["type"]]
            var_type = type_info["pos"]

            var_bytes += struct.pack("<B", var_type)

            init_value = content["init_value"]

            # TODO think about arrays
            if init_value is None:
                init_value_length = 0
                var_bytes += struct.pack("<H", init_value_length)
            else:
                (init_value_length, pack_str) = self.getVarLenAndPackStr(
                    content["type"], False, init_value
                )
                if content["type"] == "STRING":
                    init_value = bytes(init_value, "utf-8")
                var_bytes += struct.pack("<H" + pack_str, init_value_length, init_value)

            global_vars_bytes += var_bytes

            linked_vars_count = len(content["linked_vars_poses"])
            global_vars_bytes += struct.pack("<I", linked_vars_count)
            for linked_var_pos in content["linked_vars_poses"]:
                global_vars_bytes += struct.pack("<I", linked_var_pos)

        # parse instances into bytes
        instances_bytes = bytes()
        for path, inst in instances.items():
            instances_bytes += self.getBytesFromInst(inst)

        # parse locations into bytes
        locations_bytes = bytes()
        for loc_name, content in locations.items():
            loc_type_num = self.loc_types[loc_name]
            location_bytes = struct.pack("<BI", loc_type_num, len(content.keys()))
            for pos_in_ports, pos_in_vars in content.items():
                location_bytes += struct.pack("<II", pos_in_ports, pos_in_vars)
            locations_bytes += location_bytes

        # parse tasks into bytes
        tasks_bytes = struct.pack("<I", len(tasks))
        for task_name, content in tasks.items():
            # tick count per task
            tasks_bytes += struct.pack("<I", content["TICK_COUNT"])
            # instances count
            tasks_bytes += struct.pack("<I", len(content["INSTANCES"]))
            # instances positions
            for inst in content["INSTANCES"]:
                tasks_bytes += struct.pack("<I", inst)

        f.write(header_bytes)
        f.write(predefined_vars_bytes)
        f.write(global_vars_bytes)
        f.write(instances_bytes)
        f.write(locations_bytes)
        f.write(tasks_bytes)
        f.close()

    def getProgramVarsSizeAndCount(self, global_vars: dict, instances: dict) -> tuple:
        (varsSize, varsCount) = self.getInstsVarsSizeAndCount(instances)
        # add predefined vars size to varsSize
        for (val, var_type), content in self._predefined_temp_vars.items():
            varsSize += self.getTypeMaxSize(var_type)
        # add global vars size to varsSize
        for var_name, content in global_vars.items():
            varsSize += self.getTypeMaxSize(content["type"])
        varsCount += len(global_vars)
        return varsSize, varsCount

    def getInstsVarsSizeAndCount(self, insts: dict) -> tuple:
        # TODO add array support
        vars_size = 0
        vars_count = 0
        for path, inst in insts.items():
            variables = inst["vars"]
            vars_count += len(variables.keys())

            for var_name, content in variables.items():
                if content["visibility"] == "LOCAL":
                    vars_size += self.getTypeMaxSize(content["type"])
        return (vars_size, vars_count)

    def getTypeMaxSize(self, type: str) -> int:
        type_info = self.var_type_dict[type]
        if type == "STRING":
            return 255
        else:
            return type_info["size"]

    def getBytesFromInst(self, inst: dict) -> bytes:
        vars_count = len(inst["vars"])
        actions_count = len(inst["actions"])

        instance_bytes = struct.pack("<II", vars_count, actions_count)

        # parse vars into bytes
        for var_name, content in inst["vars"].items():
            if content["visibility"] == "GLOBAL":
                continue
            var_bytes = bytes()
            type_info = self.var_type_dict[content["type"]]
            var_type = type_info["pos"]

            var_bytes += struct.pack("<B", var_type)

            init_value = content["init_value"]

            # TODO think about arrays
            if init_value is None:
                init_value_length = 0
                var_bytes += struct.pack("<H", init_value_length)
            else:
                (init_value_length, pack_str) = self.getVarLenAndPackStr(
                    content["type"], False, init_value
                )
                if content["type"] == "STRING":
                    init_value = bytes(init_value, "utf-8")
                var_bytes += struct.pack("<H" + pack_str, init_value_length, init_value)

            instance_bytes += var_bytes
        # parse actions into bytes
        for action in inst["actions"]:
            action_bytes = bytes()

            act_type = self.act_type_dict[action["act_type"]]
            action_bytes += struct.pack("<B", act_type)

            action_bytes += struct.pack("<B", len(action["vars"]))
            # TODO arrays, strings
            for act_var in action["vars"]:
                action_bytes += struct.pack(
                    "<Bi", act_var["is_val"], act_var["var_pos"]
                )
            instance_bytes += action_bytes
        return instance_bytes

    def getVarLenAndPackStr(self, base_type: str, is_array: bool, value) -> tuple:
        length = 0
        pack_str = ""
        type_info = self.var_type_dict[base_type]

        length = type_info["size"]
        pack_str = type_info["str_char"]

        if is_array or base_type == "STRING":
            length = length * len(value)
            pack_str = str(len(value)) + pack_str

        return (length, pack_str)

    def extractValueFromStr(self, str_to_search: str):

        if not (
            str_to_search.startswith(
                (
                    "__BOOL_LITERAL",
                    "__time_to_timespec",
                    "__date_to_timespec",
                    "__tod_to_timespec",
                    "__dt_to_timespec",
                    "__STRING_LITERAL",
                )
            )
            or str_to_search[0].isdigit()
        ):
            return None

        result = ""

        re_search = re.search(r"__BOOL_LITERAL\((.*?)\)", str_to_search)

        if re_search is not None:
            result = re_search[1].lower() in "true"
            return result

        re_search = re.search(r"__time_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            time_parts = list(map(float, re_search[1].replace(" ", "").split(",")))
            result = (
                time_parts[1] / 1e3
                + time_parts[2]
                + time_parts[3] * 60
                + time_parts[4] * 60 * 60
                + time_parts[5] * 60 * 60 * 24
            )
            return result

        re_search = re.search(r"__date_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            date_parts = list(map(int, re_search[1].replace(" ", "").split(",")))
            dt = datetime.datetime(date_parts[2], date_parts[1], date_parts[0])
            result = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            return result

        re_search = re.search(r"__tod_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            tod_parts = list(map(float, re_search[1].replace(" ", "").split(",")))
            result = tod_parts[2] * 60 * 60 + tod_parts[1] * 60 + tod_parts[0]
            return result

        re_search = re.search(r"__dt_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            dt_parts = list(map(int, re_search[1].replace(" ", "").split(",")))
            dt = datetime.datetime(
                dt_parts[5],
                dt_parts[4],
                dt_parts[3],
                dt_parts[2],
                dt_parts[1],
                dt_parts[0],
            )
            result = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            return result

        re_search = re.search(r'__STRING_LITERAL\(.+,"(.*?)"\)', str_to_search)

        if re_search is not None:
            result = re_search[1]
            return result

        parts = str_to_search.split(",")

        for part in parts:
            part = part.replace(")", "")
            try:
                result = int(part)
                return result
            except ValueError:
                try:
                    result = float(part)
                    return result
                except ValueError:
                    None

        return None


class ModbusSendClient:
    # Table of CRC values for high-order byte
    _auchCRCHi = [
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x01,
        0xC0,
        0x80,
        0x41,
        0x00,
        0xC1,
        0x81,
        0x40,
    ]
    # Table of CRC values for low-order byte
    _auchCRCLo = [
        0x00,
        0xC0,
        0xC1,
        0x01,
        0xC3,
        0x03,
        0x02,
        0xC2,
        0xC6,
        0x06,
        0x07,
        0xC7,
        0x05,
        0xC5,
        0xC4,
        0x04,
        0xCC,
        0x0C,
        0x0D,
        0xCD,
        0x0F,
        0xCF,
        0xCE,
        0x0E,
        0x0A,
        0xCA,
        0xCB,
        0x0B,
        0xC9,
        0x09,
        0x08,
        0xC8,
        0xD8,
        0x18,
        0x19,
        0xD9,
        0x1B,
        0xDB,
        0xDA,
        0x1A,
        0x1E,
        0xDE,
        0xDF,
        0x1F,
        0xDD,
        0x1D,
        0x1C,
        0xDC,
        0x14,
        0xD4,
        0xD5,
        0x15,
        0xD7,
        0x17,
        0x16,
        0xD6,
        0xD2,
        0x12,
        0x13,
        0xD3,
        0x11,
        0xD1,
        0xD0,
        0x10,
        0xF0,
        0x30,
        0x31,
        0xF1,
        0x33,
        0xF3,
        0xF2,
        0x32,
        0x36,
        0xF6,
        0xF7,
        0x37,
        0xF5,
        0x35,
        0x34,
        0xF4,
        0x3C,
        0xFC,
        0xFD,
        0x3D,
        0xFF,
        0x3F,
        0x3E,
        0xFE,
        0xFA,
        0x3A,
        0x3B,
        0xFB,
        0x39,
        0xF9,
        0xF8,
        0x38,
        0x28,
        0xE8,
        0xE9,
        0x29,
        0xEB,
        0x2B,
        0x2A,
        0xEA,
        0xEE,
        0x2E,
        0x2F,
        0xEF,
        0x2D,
        0xED,
        0xEC,
        0x2C,
        0xE4,
        0x24,
        0x25,
        0xE5,
        0x27,
        0xE7,
        0xE6,
        0x26,
        0x22,
        0xE2,
        0xE3,
        0x23,
        0xE1,
        0x21,
        0x20,
        0xE0,
        0xA0,
        0x60,
        0x61,
        0xA1,
        0x63,
        0xA3,
        0xA2,
        0x62,
        0x66,
        0xA6,
        0xA7,
        0x67,
        0xA5,
        0x65,
        0x64,
        0xA4,
        0x6C,
        0xAC,
        0xAD,
        0x6D,
        0xAF,
        0x6F,
        0x6E,
        0xAE,
        0xAA,
        0x6A,
        0x6B,
        0xAB,
        0x69,
        0xA9,
        0xA8,
        0x68,
        0x78,
        0xB8,
        0xB9,
        0x79,
        0xBB,
        0x7B,
        0x7A,
        0xBA,
        0xBE,
        0x7E,
        0x7F,
        0xBF,
        0x7D,
        0xBD,
        0xBC,
        0x7C,
        0xB4,
        0x74,
        0x75,
        0xB5,
        0x77,
        0xB7,
        0xB6,
        0x76,
        0x72,
        0xB2,
        0xB3,
        0x73,
        0xB1,
        0x71,
        0x70,
        0xB0,
        0x50,
        0x90,
        0x91,
        0x51,
        0x93,
        0x53,
        0x52,
        0x92,
        0x96,
        0x56,
        0x57,
        0x97,
        0x55,
        0x95,
        0x94,
        0x54,
        0x9C,
        0x5C,
        0x5D,
        0x9D,
        0x5F,
        0x9F,
        0x9E,
        0x5E,
        0x5A,
        0x9A,
        0x9B,
        0x5B,
        0x99,
        0x59,
        0x58,
        0x98,
        0x88,
        0x48,
        0x49,
        0x89,
        0x4B,
        0x8B,
        0x8A,
        0x4A,
        0x4E,
        0x8E,
        0x8F,
        0x4F,
        0x8D,
        0x4D,
        0x4C,
        0x8C,
        0x44,
        0x84,
        0x85,
        0x45,
        0x87,
        0x47,
        0x46,
        0x86,
        0x82,
        0x42,
        0x43,
        0x83,
        0x41,
        0x81,
        0x80,
        0x40,
    ]

    def __init__(
        self,
        modbus_type,
        host="",
        port=None,
        serial_port=None,
        baudrate=19200,
        slave_id=1,
    ):
        self.modbus_type = modbus_type
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.transaction_id = 0  # Initialize transaction ID
        self.sock = None  # TCP socket
        self.serial = None  # Serial port
        self.timeout = 5

    def _increment_transaction_id(self):
        self.transaction_id = (self.transaction_id + 1) % 65536

    def _calculate_crc(self, message):
        CRCHi = 0xFF
        CRCLo = 0xFF

        for byte in message:
            index = CRCHi ^ byte
            CRCHi = CRCLo ^ self._auchCRCHi[index]
            CRCLo = self._auchCRCLo[index]

        return (CRCHi << 8) | CRCLo

    def _assemble_request(self, function_code, data):
        if self.modbus_type == "TCP":
            self._increment_transaction_id()
            transaction_id = self.transaction_id
            protocol_id = 0  # Modbus protocol ID is always 0x0000
            slave_id = self.slave_id

            # Construct the Modbus TCP frame
            header = struct.pack(
                ">HHHBB",
                transaction_id,
                protocol_id,
                2 + len(data),
                slave_id,
                function_code,
            )
            request = header + data

        elif self.modbus_type == "RTU":
            slave_id = self.slave_id

            # Construct the Modbus RTU frame without CRC
            request = struct.pack(">BB", slave_id, function_code) + data

        else:
            print("Unsupported Modbus type.")
            return None

        return request

    def _send_modbus_request(self, function_code, data):
        request = self._assemble_request(function_code, data)
        if self.modbus_type == "RTU":
            # Add CRC for Modbus RTU
            # crc = binascii.crc_hqx(data, 0xFFFF)
            crc = self._calculate_crc(request)

            # crc_bytes = crc.to_bytes(2, 'big')
            crc_bytes = struct.pack(">H", crc)  # Convert crc to bytes using struct.pack
            request += crc_bytes

        return self._send_request(request)

    def _send_request(self, request):
        try:
            if self.modbus_type == "TCP":
                if not self.sock:
                    # raise Exception("Not connected.")
                    print("Device is not connected")
                    return None

                self.sock.send(request)
                response = self.sock.recv(1024)
                return response

            elif self.modbus_type == "RTU":
                if not self.serial:
                    # raise Exception("Not connected.")
                    print("Device is not connected")
                    return None

                # if should_print == True:
                #    print('request:')
                #    res_hex = ' '.join([hex(ord(byte))[2:].zfill(2) for byte in request])
                #    print(res_hex)

                ## Wait until timeout for the response to arrive
                # start_time = time.time()
                #
                # while (time.time() - start_time) < self.timeout:
                #    if self.serial.in_waiting >= expected_response_length:
                #        response = self.serial.read(expected_response_length)
                #        return response
                #
                ## If no response is received within the timeout, return an empty string
                # return ''

                self.serial.write(request)
                response = self.serial.read(1024)
                if response is None or len(response) < 2:
                    return None

                # TCP header is bigeer. Pad serial response 6 bytes to the right so that it matches TCP response
                inserted_bytes = b"\x00\x00\x00\x00\x00\x00"
                response = inserted_bytes + response
                # Remove the last two bytes (CRC)
                response = response[:-2]
                return response

            else:
                print("Unsupported Modbus type.")
                return None

        except Exception as e:
            # print(f"Error sending request: {str(e)}")
            print("Error sending request: {}".format(str(e)))
            print("Trying to reconnect...")
            self.disconnect()
            self.connect()
            return None

    def connect(self):
        if self.modbus_type == "TCP":
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.host, self.port))
                time.sleep(1)  # make sure connection happens
            except Exception as e:
                # print(f"TCP connection error: {str(e)}")
                print("TCP connection error: {}\n".format(str(e)))
                return False

        elif self.modbus_type == "RTU":
            try:
                self.serial = serial.Serial(
                    port=self.serial_port, baudrate=self.baudrate, timeout=0.3
                )
                time.sleep(2)  # make sure connection happens
            except Exception as e:
                # print(f"Serial port connection error: {str(e)}")
                print("Serial port connection error: {}".format(str(e)))
                return False

        return True

    def disconnect(self):
        if self.modbus_type == "TCP":
            if self.sock:
                self.sock.close()
                self.sock = None

        elif self.modbus_type == "RTU":
            if self.serial:
                self.serial.close()
                self.serial = None
