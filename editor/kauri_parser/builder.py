import os
import platform as os_platform
import time
import struct
import socket
import serial

import boolean_parser as bp

import wx

import re
import datetime



class PlcProgramParser:

    var_type_dict = {"BOOL": {"pos": 0, "size": 1, "str_char": '?'}, 
                    "SINT": {"pos": 1, "size": 1, "str_char": 'b'}, 
                    "INT": {"pos": 2, "size": 2, "str_char": 'h'}, 
                    "DINT": {"pos": 3, "size": 4, "str_char": 'i'}, 
                    "LINT": {"pos": 4, "size": 8, "str_char": 'q'},
                    "USINT": {"pos": 5, "size": 1, "str_char": 'B'},
                    "UINT": {"pos": 6, "size": 2, "str_char": 'H'},
                    "UDINT": {"pos": 7, "size": 4, "str_char": 'I'},
                    "ULINT": {"pos": 8, "size": 8, "str_char": 'Q'}, 
                    "REAL": {"pos": 9, "size": 4, "str_char": 'f'},
                    "LREAL": {"pos": 10, "size": 8, "str_char": 'd'},
                    "TIME": {"pos": 11, "size": 4, "str_char": 'f'},
                    "DATE": {"pos": 12, "size": 4, "str_char": 'f'},
                    "TOD": {"pos": 13, "size": 4, "str_char": 'f'},
                    "DT": {"pos": 14, "size": 4, "str_char": 'f'},
                    "STRING": {"pos": 15, "size": 1, "str_char": 's'},
                    "BYTE": {"pos": 16, "size": 1, "str_char": 'b'},
                    "WORD": {"pos": 17, "size": 2, "str_char": 'h'},
                    "DWORD": {"pos": 17, "size": 4, "str_char": 'i'},
                    "LWORD": {"pos": 19, "size": 8, "str_char": 'q'}}

    act_type_dict = {"SET_VAR": 0, 
                    "NOT": 1,
                    "AND": 2,
                    "OR": 3,
                    "IF_ST": 4,
                    "ELSE_ST": 5,
                    "IF_END": 6,
                    "FOR": 7,
                    "TON": 8,
                    "TOF": 9,
                    "R_TRIG": 10,
                    "F_TRIG": 11,
                    "CTU": 12,
                    "CTD": 13}

    loc_types = {"": 0, "IX": 1, "QX": 2, "IW": 3, "QW": 4}
    
    statement_dict = {"if": r"((?P<ws> +)if \((?P<exp>.*?)\) \{\n(?P<if_con>.*?)(?:(?P=ws)\} else \{\n(?P<el_con>.*;))?\n(?P=ws)\};)"}

    _temp_var_pos = -1
    _temp_var_max_pos = 0
    _predefined_temp_vars = dict()
    _command_list = list()
    
    def scrollToEnd(self, txtCtrl):
        if os_platform.system() != 'Darwin':
            txtCtrl.SetInsertionPoint(-1)
        txtCtrl.ShowPosition(txtCtrl.GetLastPosition())
        txtCtrl.Refresh()
        txtCtrl.Update()
    
    def outputIntoCompileWindow(self, str: str):
        global compiler_logs
        compiler_logs += str   
        wx.CallAfter(self.txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(self.scrollToEnd, self.txtCtrl) 
    
    def build(self, defs, st_file, pous_code, res0_code, program_list, debug_vars_list, port, txtCtrl, update_subsystem, build_path):
        global compiler_logs
        compiler_logs = ''   
        
        self.txtCtrl = txtCtrl
        
        # output definitions (MD5 hash, modbus info, ticktime)
        compiler_logs += "Definitions:\n"
        for def_name, content in defs.items():
                self.outputIntoCompileWindow(f"\t{def_name}: {content}\n")
        self.outputIntoCompileWindow("\n")
        
        # extract instances
        instances = self.extractInstances(program_list, debug_vars_list, pous_code)
        
        compiler_logs += "Predefined variables:\n"
        for val, content in self._predefined_temp_vars.items():
            self.outputIntoCompileWindow(f"\t{val}: {content}\n")
            
        compiler_logs += f"Temp vars count: {self._temp_var_max_pos}\n\n"
        
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
        locations = self.extractLocations(instances)
        # output locations into window output
        compiler_logs += "Locations:\n"                                
        for loc_name, content in locations.items():
            self.outputIntoCompileWindow(f"\t{loc_name}: {content}\n")  
        self.outputIntoCompileWindow("\n")
            
        # extract tasks from c file with resources
        tasks = self.extractTasks(res0_code)
        # output tasks into window output
        compiler_logs += "Tasks:\n"                                
        for task_name, content in tasks.items():
            self.outputIntoCompileWindow(f"\t{task_name}: {content}\n")
        
        self.createFirmware(build_path, instances, locations, defs, tasks)
        
        if port is not None:
            self.sendFwViaSerial(port, os.path.join(build_path, "firmware.ki"))
         
    def extractInstances(self, program_list: list, debug_vars_list: list, pous_code: str) -> dict:
        # extract instances from program_list
        instances = dict()
        for prog in program_list:
            instances[prog['C_path']] = {"type": prog['type'], "vars": {}, "actions": []}
        # extract vars from debug_vars_list
        var_number = 0
        for var in debug_vars_list:
            temp = var['C_path'].partition('.')
            init_value = ''
            if temp[2].endswith(".EN") or temp[2].endswith(".ENO"):
                init_value = True
            var_dict = {"number": var_number, "type": var["type"], "location": '', "init_value": init_value}
            instances[temp[0]]["vars"][temp[2]] = var_dict
            var_number += 1
        # parse POUS.c file to get vars init values, locations and instances actions
        for path, inst in instances.items():
            # vars init values and locations part
            init_pattern = rf'{inst["type"]}_init__\({inst["type"]} \*data__, BOOL retain\) {{(.*?)}}\n\n'
            init_sec = re.search(init_pattern, pous_code, flags=re.S)[1]
            self.extractInitDataFromSec(init_sec, inst)
            
            # actions part
            body_pattern = rf'{inst["type"]}_body__\({inst["type"]} \*data__\) {{.*?\n.*?\n(.*?)}} // {inst["type"]}_body__\(\)'
            body_sec = re.search(body_pattern, pous_code, flags=re.S)[1]
            inst["actions"] = self.extractActionsFromSec(body_sec, inst)   
    
        return instances        
      
    def extractInitDataFromSec(self, sec: str, inst: dict):
        for line in sec.split("\n"):
            com = line.strip()
            parts = line.split(',')
            if com.startswith("__INIT_LOCATED("):
                var = inst["vars"][parts[2].split("->")[1]]
                var["location"] = parts[1][2:].replace('_', ".")
            elif com.startswith("__INIT_LOCATED_VALUE(") or com.startswith("__INIT_VAR("):
                var = inst["vars"][parts[0].split("->")[1]]
                var["init_value"] = self.extractValue(com) 
           
    def extractValue(self, str_to_search: str):
         
        if not str_to_search.startswith("_") and not str_to_search[0].isdigit():
            return None
         
        result = ""

        re_search = re.search("__BOOL_LITERAL\((.*?)\)", str_to_search)

        if re_search is not None:
            result = re_search[1].lower() in "true"
            return result

        re_search = re.search("__time_to_timespec\((.*?)\)", str_to_search)

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

        re_search = re.search("__date_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            date_parts = list(map(int, re_search[1].replace(" ", "").split(",")))
            dt = datetime.datetime(date_parts[2], date_parts[1], date_parts[0])
            result = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
            return result

        re_search = re.search("__tod_to_timespec\((.*?)\)", str_to_search)

        if re_search is not None:
            tod_parts = list(map(float, re_search[1].replace(" ", "").split(",")))
            result = tod_parts[2] * 60 * 60 + tod_parts[1] * 60 + tod_parts[0]
            return result

        re_search = re.search("__dt_to_timespec\((.*?)\)", str_to_search)

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

        re_search = re.search('__STRING_LITERAL\(.+,"(.*?)"\)', str_to_search)

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
                
    def extractActionsFromSec(self, sec: str, inst: dict) -> list:
        actions = list()
        cur_sec = sec

        sts_blocks = []
        for st_name, st_regex in self.statement_dict.items():
            found_blocks = re.findall(st_regex, cur_sec, flags=re.S)
            for found_block in found_blocks:
                sts_blocks.append({"index": cur_sec.find(found_block[0]), "type": st_name, "body": found_block})
            
        sts_blocks = sorted(sts_blocks, key=lambda d: d['index'], reverse=True)
        
        if len(sts_blocks) == 0:
            actions += self.extractActionsFromBlock(cur_sec, inst)
        else:
            str_to_split = cur_sec
            all_blocks = []
            while len(sts_blocks) > 0:
                block = sts_blocks.pop()
                splitted = str_to_split.split(block["body"][0])
                if splitted[0] != '':
                    all_blocks.append({"type": None, "body": splitted[0]})
                if len(splitted) > 1:
                    str_to_split = splitted[1]
                else:
                    str_to_split = ""
                
                all_blocks.append({"type": block["type"], "body": block["body"]})
                    
            if str_to_split != "":
                all_blocks.append({"type": None, "body": str_to_split})
                
            for block in all_blocks:
                bl_type = block["type"]
                if bl_type is None:
                    actions += self.extractActionsFromBlock(block["body"], inst)
                else:
                    bl_ins_pos = 0
                    bl_vars = []
                    bl_var_pos = 0
                    if bl_type == "if":
                        expr = block["body"][2]
                        true_sec = block["body"][3]
                        false_sec = block["body"][4]
                        (bl_var_pos, bl_is_val) = self.extractVarPos(expr, "BOOL", inst)
                        bl_vars.append(self.getVarDict(bl_var_pos, bl_is_val))
                        if bl_var_pos < 0:
                            actions += self.extractBoolStrActs(expr, bl_var_pos, inst)
                        
                        bl_ins_pos = len(actions)
                        
                        true_acts = self.extractActionsFromSec(true_sec, inst)
                        false_acts = self.extractActionsFromSec(false_sec, inst)
                        
                        actions += true_acts
                        actions += false_acts
                        
                        bl_vars.append(self.getVarDict(self.getPredefinedVarPos(len(true_acts), "INT"), True))
                        bl_vars.append(self.getVarDict(self.getPredefinedVarPos(len(false_acts), "INT"), True))
                    
                    
                    actions.insert(bl_ins_pos, {"act_type": bl_type, "vars": bl_vars})
        return actions  
            
    def extractActionsFromBlock(self, block: str, inst: dict) -> list:
        actions = list()
        for com in block.split(";"):
            stripped_com = com.strip().replace('\n', '')
            self._command_list = [{"com": stripped_com, "pushEnd": True, "var_pos": 0}]
            act_type = ""
            act_vars = []
            act_var_pos = 0
            self._temp_var_pos = -1
            while len(self._command_list) > 0:
                command = self._command_list.pop()
                if command["pushEnd"]:
                    not_end_push_pos = len(actions) - 1
                
                str_com_text = command["com"]
                if str_com_text.startswith("__SET_VAR(") or str_com_text.startswith("__SET_LOCATED("):
                    act_type = "SET_VAR"
                    com_args = re.search("\((.*?),(.*?),(.*?),(.*)\)", str_com_text)
                    
                    var_name = com_args[1].split("->")[1]+com_args[2]
                    var = inst["vars"][var_name]
                    act_vars.append(self.getVarDict(var["number"], False))
                    act_var_pos = var["number"]
                    act_is_val = True
                    
                    var_to_set_com = com_args[4]
                    (act_var_var_pos, act_is_val) = self.extractVarPos(var_to_set_com, var["type"], inst)
                    act_vars.append(self.getVarDict(act_var_var_pos, act_is_val))
                    if act_var_var_pos < 0:
                        if var["type"] == 'BOOL':
                            bool_acts = self.extractBoolStrActs(var_to_set_com, act_var_var_pos, inst)
                            for bool_act in reversed(bool_acts):
                                actions.insert(not_end_push_pos, bool_act)
                        else:
                            self._command_list.append({"com": var_to_set_com.strip().replace("\n", ""), "pushEnd": False, "var_pos": act_var_var_pos})
                elif "_body__" in str_com_text:
                    act_type = str_com_text.split('_')[0]
                    var_to_set = re.search("\(.*->(.*)\)", str_com_text)[1]
                    act_var_pos = inst["vars"][var_to_set +  ".EN"]["number"]
                    act_vars.append(self.getVarDict(act_var_pos, False))
                    
                if act_type != "":
                    action = {"act_type": act_type, "vars": act_vars}
                    if command["pushEnd"]:
                        actions.append(action)
                    else:
                        actions.insert(not_end_push_pos, action)
        return actions              
            
    def sendFwViaSerial(self, port, fw_path):
        send_client = ModbusSendClient(modbus_type='RTU', serial_port=port, baudrate=115200, slave_id=1)
        send_client.connect()
        f = open(fw_path, 'rb')
        data_byte = f.read(251)
        send_client._send_modbus_request(103, bytes())
        while data_byte:
            send_client._send_modbus_request(102, data_byte)
            data_byte = f.read(251)
        f.close()
        send_client._send_modbus_request(104, bytes())
        send_client.disconnect()        
        
    def extractLocations(self, instances: dict) -> dict:
        locations = dict()
        for loc_type in self.loc_types.keys():
            if loc_type != '':
                locations[loc_type] = {"count": 0, "locations": {}}
        
        for inst in instances.values():
            for var_name, content in inst["vars"].items():
                loc_type = content["location"][:2]
                loc_port_pos_str = content["location"][2:]
                if loc_type != '':
                    # TODO check locations format
                    location_parts = list(map(int, loc_port_pos_str.split('.')))
                    if len(location_parts) == 1:
                        location_pos = location_parts[0]
                    else:
                        location_pos = location_parts[0]*8+location_parts[1]
                    
                    if locations[loc_type]["locations"].get(location_pos) is None:
                        locations[loc_type]["count"] += 1
                        locations[loc_type]["locations"][location_pos] = [content["number"]]
                    else:
                        locations[loc_type]["locations"][location_pos].append(content["number"])
            
        for loc_name, content in locations.items():    
            content["locations"] = {key:content["locations"][key] for key in sorted(content["locations"])}    
            
        return locations
        
    def extractTasks(self, res0_code: str) -> dict:
        tasks = {}
        tasks_pattern = r'_run__\(unsigned long tick\) \{(.*?)\}\n\n'
        tasks_sec = re.search(tasks_pattern, res0_code, flags=re.S)[1]
        
        tasks_parts = re.findall(r"(\w*?) = !\(tick \% (.*?)\);", tasks_sec)
        for task_parts in tasks_parts:
            tasks[task_parts[0]] = {"TICK_COUNT": int(task_parts[1]), "INSTANCES": []}
        for task in tasks.keys():
            tasks_inst_parts = re.findall(rf"if \({task}\) {{.*?\(&INSTANCE(.*?)\).*?}}", tasks_sec, flags=re.S)
            for task_inst_parts in tasks_inst_parts:
                tasks[task]["INSTANCES"].append(int(task_inst_parts[0]))

        return tasks
        
    def createFirmware(self, build_path: str, instances: dict, locations: dict, defs: dict, tasks: dict):
        try:
            os.remove(os.path.join(build_path, "firmware.ki"))
        except FileNotFoundError:
            None
        f = open(os.path.join(build_path, "firmware.ki"), 'wb')
        
        header_bytes = bytes()
        # md5
        md5_len = len(defs["MD5"])
        header_bytes = struct.pack('<H'+str(md5_len)+"s", md5_len, bytes(defs["MD5"], 'utf-8'))
        # total vars mc size and count
        (varsSize, varsCount) = self.getInstsVarsSizeAndCount(instances)
        
        for val, content in self._predefined_temp_vars.items():
            varsSize += self.getTypeMaxSize(content["type"])
        
        header_bytes += struct.pack('<II', varsSize, varsCount)
        # temp vars count
        header_bytes += struct.pack("<I", self._temp_var_max_pos)
        # ticktime
        ticktime = defs["TICKTIME"]/1e9
        header_bytes += struct.pack("<f", ticktime)
        # instances count
        header_bytes += struct.pack("<I", len(instances))
        # modbus serial
        header_bytes += struct.pack('<?IB', defs["MODBUS_SERIAL"]["ENABLED"], 
                                    int(defs["MODBUS_SERIAL"]["BAUD_RATE"]), 
                                    int(defs["MODBUS_SERIAL"]["SLAVE_ID"]))
        # TODO parse another fields of mb tcp
        header_bytes += struct.pack("<?", defs["MODBUS_TCP"]["ENABLED"])
        
        predefined_vars_bytes = struct.pack("<I", len(self._predefined_temp_vars.keys()))
        for val, content in self._predefined_temp_vars.items():
            (var_len, pack_str) = self.getVarLenAndPackStr(content["type"], False, val)
            type_info = self.var_type_dict[content["type"]]
            var_type = type_info["pos"]
            predefined_vars_bytes += struct.pack("<BH"+pack_str, var_type, var_len, val)
        
        instances_bytes = bytes()
        for path, inst in instances.items():
            instances_bytes += self.getBytesFromInst(inst)
            
        # parse locations into bytes
        locations_bytes = bytes()
        for loc_name, content in locations.items():
            loc_type_num = self.loc_types[loc_name]
            location_bytes = struct.pack("<BI", loc_type_num, content["count"])
            for pos_in_ports, poses_in_vars in content["locations"].items():
                location_bytes += struct.pack("<II", pos_in_ports, len(poses_in_vars))
                for pos_in_vars in poses_in_vars:
                    location_bytes += struct.pack("<I", pos_in_vars)
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
        f.write(instances_bytes)
        f.write(locations_bytes)
        f.write(tasks_bytes)
        f.close()  

    def getInstsVarsSizeAndCount(self, insts: dict) -> tuple:
        # TODO add array support
        vars_size = 0
        vars_count = 0
        for path, inst in insts.items():
            variables = inst["vars"]
            vars_count += len(variables.keys())
            
            for var_name, content in variables.items():
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
            var_bytes = bytes()
            pack_str = "<B"
            type_info = self.var_type_dict[content["type"]]
            var_type = type_info["pos"]
        
            var_bytes += struct.pack("<B", var_type)
        
            init_value = content["init_value"]
            
            # TODO think about arrays        
            if init_value == '':
                init_value_length = 0
                var_bytes += struct.pack("<H", init_value_length)
            else:
                (init_value_length, pack_str) = self.getVarLenAndPackStr(content["type"], False, init_value)
                if content["type"] == "STRING":
                    init_value = bytes(init_value, 'utf-8')
                var_bytes += struct.pack("<H"+pack_str, init_value_length, init_value)
            
            instance_bytes += var_bytes
        # parse actions into bytes
        for action in inst["actions"]:
            action_bytes = bytes()
            
            act_type = self.act_type_dict[action["act_type"]]
            action_bytes += struct.pack("<B", act_type)
            
            action_bytes += struct.pack("<B", len(action["vars"]))
            # TODO arrays, strings
            for act_var in action["vars"]:
                action_bytes += struct.pack("<Bi", act_var["is_val"], act_var["var_pos"])
            instance_bytes += action_bytes
        return instance_bytes


    def getVarLenAndPackStr(self, base_type: str, is_array: bool, value) -> tuple:
        length = 0
        pack_str = ""
        type_info = self.var_type_dict[base_type]
        
        length = type_info["size"]
        pack_str = type_info["str_char"]
        
        if is_array or base_type == "STRING":
            length = length*len(value)
            pack_str = str(len(value)) + pack_str
            
        return (length, pack_str)

    def extractBoolStrActs(self, str_to_parse: str, var_pos, inst: dict) -> list:
        res = re.findall(r'(\w+[^\&\|\!]*)', str_to_parse)
        str_to_parse = str_to_parse.replace("&&", "and").replace("||", "or").replace("!", "not ")
        acts = dict()
        act_pos = 0
        for r in res:
            r = r.strip()
            r = r[:len(r)-r.count(')') + r.count('(')]
            str_to_parse = str_to_parse.replace(r, f'True={act_pos}', 1)
            acts[act_pos] = r
            act_pos += 1
        parse_res = bp.parse(str_to_parse)
        actions = list()
        conds = [{"pos": var_pos, "cond": parse_res}]
        while (len(conds) > 0):
            cond = conds.pop()
            if type(cond["cond"]) in (bp.parsers.sqla.SQLAOr, bp.parsers.sqla.SQLAAnd, bp.parsers.sqla.SQLANot):
                actions.insert(0, {"act_type": cond["cond"].logicop.upper(), "vars": [self.getVarDict(cond["pos"], True)]})
                action = actions[0]
                for c in cond["cond"].conditions:
                    if type(c) == bp.parsers.sqla.SQLACondition:
                        (vp, is_val) = self.extractVarPos(acts[int(c.value)], "BOOL", inst)
                        if vp < 0:
                            self._command_list.insert(0, {"com": acts[int(c.value)], "pushEnd": False, "var_pos": vp})
                    else:
                        vp = self.getNextTempVar()
                        is_val = False
                        conds.append({"pos": vp, "cond": c})
                    action["vars"].append(self.getVarDict(vp, is_val))
        return actions
           
    def getNextTempVar(self) -> int:
        res = self._temp_var_pos       
        self._temp_var_pos -= 1
        self._temp_var_max_pos = max(abs(res), self._temp_var_max_pos)
        
        return res 
    
    def extractVarPos(self, com: str, var_type: str, inst: dict) -> tuple:
        var_to_set = self.extractValue(com)
        if var_to_set is not None:
            var_pos = self._predefined_temp_vars.get(var_to_set)
            is_val = True
            if var_pos is None:
                var_pos = len(self._predefined_temp_vars.keys())
                self._predefined_temp_vars[var_to_set] = {
                    "number": var_pos,
                    "type": var_type,
                }
            else:
                var_pos = var_pos["number"]
        elif com.startswith("__GET") and len(re.findall(r"\w+\(.+?\)", com)) < 2:
            var_to_set = re.search("\(.*->(.*),\)", com)[1]
            var_pos = inst["vars"][var_to_set]["number"]
            is_val = False
        else:
            var_pos = self._temp_var_pos
            is_val = False
            self._temp_var_pos -= 1

        return (var_pos, is_val)
    
    def getVarDict(self, var_pos: int, is_val: bool):
        return {"var_pos": var_pos, "is_val": is_val} 
    
    def getPredefinedVarPos(self, var_val, var_type):
        vvar_pos = self._predefined_temp_vars.get(var_val)
            
        if vvar_pos is None:
            vvar_pos = len(self._predefined_temp_vars.keys())
            self._predefined_temp_vars[var_val] = {"number": vvar_pos, "type": var_type}
        else:
            vvar_pos = vvar_pos["number"]
        

class ModbusSendClient:
    # Table of CRC values for high-order byte
    _auchCRCHi = [
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
        0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
        0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
        0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
        0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
        0x40]
    # Table of CRC values for low-order byte
    _auchCRCLo = [
        0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
        0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
        0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
        0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
        0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
        0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
        0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
        0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
        0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
        0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
        0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
        0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
        0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
        0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
        0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
        0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
        0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
        0x40]


    def __init__(self, modbus_type, host='', port=None, serial_port=None, baudrate=19200, slave_id=1):
        self.modbus_type = modbus_type
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.transaction_id = 0  # Initialize transaction ID
        self.sock = None # TCP socket
        self.serial = None # Serial port
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
        if self.modbus_type == 'TCP':
            self._increment_transaction_id()
            transaction_id = self.transaction_id
            protocol_id = 0  # Modbus protocol ID is always 0x0000
            slave_id = self.slave_id

            # Construct the Modbus TCP frame
            header = struct.pack(">HHHBB", transaction_id, protocol_id, 2 + len(data), slave_id, function_code)
            request = header + data

        elif self.modbus_type == 'RTU':
            slave_id = self.slave_id

            # Construct the Modbus RTU frame without CRC
            #print("Assembling request with fc {}".format(str(function_code)))
            #header = 
            #request = bytes([slave_id, function_code]) + data
            request = struct.pack('>BB', slave_id, function_code) + data


        else:
            print("Unsupported Modbus type.")
            return None

        return request

    def _send_modbus_request(self, function_code, data):
        request = self._assemble_request(function_code, data)
        if self.modbus_type == 'RTU':
            # Add CRC for Modbus RTU
            #crc = binascii.crc_hqx(data, 0xFFFF)
            crc = self._calculate_crc(request)

            #crc_bytes = crc.to_bytes(2, 'big')
            crc_bytes = struct.pack('>H', crc)  # Convert crc to bytes using struct.pack
            request += crc_bytes

        
        return self._send_request(request)
        
    def _send_request(self, request):
        try:
            if self.modbus_type == 'TCP':
                if not self.sock:
                    #raise Exception("Not connected.")
                    print("Device is not connected")
                    return None

                
                self.sock.send(request)
                response = self.sock.recv(1024)
                return response

            elif self.modbus_type == 'RTU':
                if not self.serial:
                    #raise Exception("Not connected.")
                    print("Device is not connected")
                    return None

                #if should_print == True:
                #    print('request:')
                #    res_hex = ' '.join([hex(ord(byte))[2:].zfill(2) for byte in request])
                #    print(res_hex)

                ## Wait until timeout for the response to arrive
                #start_time = time.time()
                #
                #while (time.time() - start_time) < self.timeout:
                #    if self.serial.in_waiting >= expected_response_length:
                #        response = self.serial.read(expected_response_length)
                #        return response
                #
                ## If no response is received within the timeout, return an empty string
                #return ''

                self.serial.write(request)
                response = self.serial.read(1024)
                if response is None or len(response) < 2:
                    return None
                
                # TCP header is bigeer. Pad serial response 6 bytes to the right so that it matches TCP response
                inserted_bytes = b'\x00\x00\x00\x00\x00\x00'
                response = inserted_bytes + response
                # Remove the last two bytes (CRC)
                response = response[:-2]
                return response

            else:
                print("Unsupported Modbus type.")
                return None

        except Exception as e:
            #print(f"Error sending request: {str(e)}")
            print("Error sending request: {}".format(str(e)))
            print("Trying to reconnect...")
            self.disconnect()
            self.connect()
            return None

    def connect(self):
        if self.modbus_type == 'TCP':
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.host, self.port))
                time.sleep(1) #make sure connection happens
            except Exception as e:
                #print(f"TCP connection error: {str(e)}")
                print("TCP connection error: {}\n".format(str(e)))
                return False

        elif self.modbus_type == 'RTU':
            try:
                self.serial = serial.Serial(port=self.serial_port, baudrate=self.baudrate, timeout=0.3)
                time.sleep(2) #make sure connection happens
            except Exception as e:
                #print(f"Serial port connection error: {str(e)}")
                print("Serial port connection error: {}".format(str(e)))
                return False
        
        return True

    def disconnect(self):
        if self.modbus_type == 'TCP':
            if self.sock:
                self.sock.close()
                self.sock = None

        elif self.modbus_type == 'RTU':
            if self.serial:
                self.serial.close()
                self.serial = None