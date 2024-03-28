import json
import os
import platform as os_platform
import shutil
import subprocess
import sys
import time
import struct
import socket
import serial

from boolean_parser import parse

import wx

import re
import datetime

global compiler_logs
compiler_logs = ''

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
                 "IF": 4,
                 "FOR": 5,
                 "TON": 6,
                 "TOF": 7,
                 "R_TRIG": 8,
                 "F_TRIG": 9,
                 "CTU": 10,
                 "CTD": 11}

loc_types = {"": 0, "IX": 1, "QX": 2, "IW": 3, "QW": 4}

def scrollToEnd(txtCtrl):
    if os_platform.system() != 'Darwin':
        txtCtrl.SetInsertionPoint(-1)
    txtCtrl.ShowPosition(txtCtrl.GetLastPosition())
    txtCtrl.Refresh()
    txtCtrl.Update()


def runCommand(command):
    cmd_response = None

    try:
        cmd_response = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        #cmd_response = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as exc:
        cmd_response = exc.output

    if cmd_response == None:
        return ''

    return cmd_response.decode('utf-8')

def loadHals():
    # load hals list from json file, or construct it
    if (os.name == 'nt'):
        jfile = 'editor\\arduino\\examples\\Baremetal\\hals.json'
    else:
        jfile = 'editor/arduino/examples/Baremetal/hals.json'
    
    f = open(jfile, 'r')
    jsonStr = f.read()
    f.close()
    return(json.loads(jsonStr))

def saveHals(halObj):
    jsonStr = json.dumps(halObj)
    if (os.name == 'nt'):
        jfile = 'editor\\arduino\\examples\\Baremetal\\hals.json'
    else:
        jfile = 'editor/arduino/examples/Baremetal/hals.json'
    f = open(jfile, 'w')
    f.write(jsonStr)
    f.flush()
    f.close()
    
def readBoardInstalled(platform):
    hals = loadHals()
    cli_command = ''
    if os_platform.system() == 'Windows':
        cli_command = 'editor\\arduino\\bin\\arduino-cli-w64'
    elif os_platform.system() == 'Darwin':
        cli_command = 'editor/arduino/bin/arduino-cli-mac'
    else:
        cli_command = 'editor/arduino/bin/arduino-cli-l64'
    for board in hals:
            if hals[board]['platform'] == platform:
                board_details = runCommand(cli_command + ' board details -b ' + platform)
                board_details = board_details.splitlines()
                board_version = '0'
                for line in board_details:
                    if "Board version:" in line:
                        board_version = line.split('Board version:')[1]
                        board_version = ''.join(board_version.split()) #remove white spaces
                        hals[board]['version'] = board_version
                        saveHals(hals)
                        break

def readBoardsInstalled():
    hasToSave = False
    hals = loadHals()
    cli_command = ''
    if os_platform.system() == 'Windows':
        cli_command = 'editor\\arduino\\bin\\arduino-cli-w64'
    elif os_platform.system() == 'Darwin':
        cli_command = 'editor/arduino/bin/arduino-cli-mac'
    else:
        cli_command = 'editor/arduino/bin/arduino-cli-l64'
    boardInstalled = runCommand(cli_command + ' board listall')
    try:
        for board in hals:
            if board in boardInstalled:
                platform = hals[board]['platform']
                board_details = runCommand(cli_command + ' board details -b ' + platform)
                board_details = board_details.splitlines()
                board_version = '0'
                for line in board_details:
                    if "Board version:" in line:
                        board_version = line.split('Board version:')[1]
                        board_version = ''.join(board_version.split()) #remove white spaces
                        hals[board]['version'] = board_version
                        hasToSave = True
                        break
            if board not in boardInstalled:
                hals[board]['version'] = '0'
                hasToSave = True
    
        if hasToSave:
            saveHals(hals)
    except:
        pass

def setLangArduino():
    cli_command = ''
    if os_platform.system() == 'Windows':
        cli_command = 'editor\\arduino\\bin\\arduino-cli-w64'
    elif os_platform.system() == 'Darwin':
        cli_command = 'editor/arduino/bin/arduino-cli-mac'
    else:
        cli_command = 'editor/arduino/bin/arduino-cli-l64'

    # Initialize arduino-cli config - if it hasn't been initialized yet
    runCommand(cli_command + ' config init')

    # Disabling this as it is causing more problems than solutions
    """
    dump = runCommand(cli_command + ' config dump')
    dump = dump.splitlines()
    arduino_dir = ''
    for line in dump:
        if 'data:' in line:
            #get the directory of arduino ide
            arduino_dir = line.split('data:')[1]
            arduino_dir = ''.join(arduino_dir.split()) #remove white spaces

        if 'locale:' in line:
            if 'en' not in line:
                #remove the line from dump variable
                dump.remove(line)
            else:
                return #already set to english
                
    dump.append('locale: en')
    dump = '\n'.join(dump)
    #write on the config file all the lines# Open the file in write mode
    with open(arduino_dir + '/arduino-cli.yaml', 'w') as f:
        # Write the variable to the file
        f.write(str(dump))

    #runCommand('echo ' + dump + ' > ' + arduino_dir + '/arduino-cli.yaml')
    """


def build(defs, st_file, pous_code, res0_code, program_list, debug_vars_list, port, txtCtrl, update_subsystem, build_path):
    global compiler_logs
    compiler_logs = ''   
    
    # output definitions (MD5 hash, modbus info, ticktime)
    compiler_logs += "Definitions:\n"
    for def_name, content in defs.items():
            compiler_logs += f"\t{def_name}: {content}\n"   
            wx.CallAfter(txtCtrl.SetValue, compiler_logs)
            wx.CallAfter(scrollToEnd, txtCtrl)
    compiler_logs += "\n"
    
    # extract instances
    instances = extractInstances(program_list, debug_vars_list, pous_code)
    # output instances values into debug window
    for path, inst in instances.items():
        compiler_logs += "Instance: " + path + "\n"
        wx.CallAfter(txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(scrollToEnd, txtCtrl)
        
        compiler_logs += "\tVars:\n"
        for var_name, content in inst["vars"].items():
            compiler_logs += f"\t\t{var_name}: {content}\n"   
            wx.CallAfter(txtCtrl.SetValue, compiler_logs)
            wx.CallAfter(scrollToEnd, txtCtrl)
            
        compiler_logs += "\tActions:\n"
        for act in inst["actions"]:
            compiler_logs += f"\t\t{act}\n"
            wx.CallAfter(txtCtrl.SetValue, compiler_logs)
            wx.CallAfter(scrollToEnd, txtCtrl)  
        compiler_logs += "\n"
        wx.CallAfter(txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(scrollToEnd, txtCtrl)
        
    # extract locations from instances
    locations = extractLocations(instances)
    # output locations into window output
    compiler_logs += "Locations:\n"                                
    for loc_name, content in locations.items():
        compiler_logs += f"\t{loc_name}: {content}\n"   
        wx.CallAfter(txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(scrollToEnd, txtCtrl)     
    compiler_logs += "\n"
    wx.CallAfter(txtCtrl.SetValue, compiler_logs)
    wx.CallAfter(scrollToEnd, txtCtrl)
        
    # extract tasks from c file with resources
    tasks = extractTasks(res0_code)
    # output tasks into window output
    compiler_logs += "Tasks:\n"                                
    for task_name, content in tasks.items():
        compiler_logs += f"\t{task_name}: {content}\n"   
        wx.CallAfter(txtCtrl.SetValue, compiler_logs)
        wx.CallAfter(scrollToEnd, txtCtrl) 
    
    createFirmware(build_path, instances, locations, defs, tasks)
    
    if port is not None:
        sendFwViaSerial(port, os.path.join(build_path, "firmware.ki"))
    
        
def sendFwViaSerial(port, fw_path):
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

_temp_var_pos = -1
_predefined_temp_vars = dict()
_command_list = dict()
def extractInstances(program_list: list, debug_vars_list: list, pous_code: str) -> tuple:
    # extract instances from program_list
    instances = dict()
    _predefined_temp_vars = dict()
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
        init_sec = re.search(init_pattern, pous_code, flags=re.S)[1].split("\n")
    
        for line in init_sec:
            com = line.strip()
            parts = line.split(',')
            if com.startswith("__INIT_LOCATED("):
                var = inst["vars"][parts[2].split("->")[1]]
                var["location"] = parts[1][2:].replace('_', ".")
            elif com.startswith("__INIT_LOCATED_VALUE(") or com.startswith("__INIT_VAR("):
                var = inst["vars"][parts[0].split("->")[1]]
                var["init_value"] = extractValue(com)
        
        # actions part
        body_pattern = rf'{inst["type"]}_body__\({inst["type"]} \*data__\) {{.*?\n.*?\n(.*?)}} // {inst["type"]}_body__\(\)'
        body_sec = re.search(body_pattern, pous_code, flags=re.S)[1].split(";")
        last_com_pos = 0
        for com in body_sec:
            com = com.strip().replace('\n', '')
            _command_list = [{"com": com, "pushEnd": True, "var_pos": 0}]
            act_type = ""
            vars = []
            var_pos = 0
            _temp_var_pos = -1
            while len(_command_list) > 0:
                command = _command_list.pop()
                com_text = command["com"]
                if com_text.startswith("__SET_VAR(") or com_text.startswith("__SET_LOCATED("):
                    act_type = "SET_VAR"
                    com_args = re.search("\((.*?),(.*?),(.*?),(.*)\)", com_text)
                    
                    var_name = com_args[1].split("->")[1]+com_args[2]
                    var = inst["vars"][var_name]
                    var_pos = var["number"]
                    is_val = True
                    
                    var_to_set_com = com_args[4]
                    (vvar_pos, is_val) = extract_var_pos(var_to_set_com, var["type"], inst)
                    if vvar_pos < 0:
                        if var["type"] == 'BOOL':
                            extract_bool_str_acts(var_to_set_com, vvar_pos, actions)
                        else:
                            _command_list.append({"com": var_to_set_com, "pushEnd": False, "var_pos": vvar_pos})
                    vars = [{"var_val_or_num": vvar_pos, "is_val": is_val}]
                    
                elif com_text.startswith("TON_body__("):
                    act_type = "TON"
                    var_to_set = re.search("\(.*->(.*)\)", com_text)[1]
                    var_pos = inst["vars"][var_to_set +  ".EN"]["number"]
                elif com_text.startswith("TOF_body__("):
                    act_type = "TOF"
                    var_to_set = re.search("\(.*->(.*)\)", com_text)[1]
                    var_pos = inst["vars"][var_to_set +  ".EN"]["number"]
                elif com_text.startswith("if ("):
                    None
                elif com_text.startswith("NOT("):
                    var_pos = command["var_pos"]
                    act_type = "NOT"
                    
                    if isValue(com_text[2:]):
                        vars = [{"var_val_or_num": extractValue(com_text), "is_val": True}]
                    elif com_text[2:].startswith("__GET"):
                        var_to_set = re.search("\(.*->(.*),\)", com_text)[1]
                        vars = [{"var_val_or_num": inst["vars"][var_to_set]["number"], "is_val": False}]
                elif com_text.startswith("OR("):
                    
                elif com_text.startswith("AND("):
                    
                if act_type != "":
                    action = {"act_type": act_type, "vars": vars, "var_pos": var_pos}
                    if command["pushEnd"]:
                        inst["actions"].append(action)
                        last_com_pos = len(inst["actions"])-1
                    else:
                        inst["actions"].insert(last_com_pos, action)
    return (instances, _predefined_temp_vars)                    

def extract_var_pos(com: str, var_type: str, inst: dict) -> tuple:
    if isValue(com):
        var_to_set = extractValue(com)
        vvar_pos = _predefined_temp_vars.get(var_to_set)
        is_val = True
        if vvar_pos is not None:
            vvar_pos = len(_predefined_temp_vars.keys())
            _predefined_temp_vars[var_to_set] = {"number": vvar_pos, "type": var_type}
    elif com.startswith("__GET"):
        var_to_set = re.search("\(.*->(.*),\)", com)[1]
        vvar_pos = inst["vars"][var_to_set]["number"]
        is_val = False
    else:
        vvar_pos = _temp_var_pos
        is_val = False
        _temp_var_pos -= 1
        
    return (vvar_pos, is_val)

def extract_bool_str_acts(str_to_parse: str):
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
    res = parse(str_to_parse)
    
    
def extractLocations(instances: dict) -> dict:
    locations = dict()
    for loc_type in loc_types.keys():
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
    
def extractTasks(res0_code: str) -> dict:
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
    
def createFirmware(build_path: str, instances: dict, locations: dict, defs: dict, tasks: dict):
    try:
        os.remove(os.path.join(build_path, "firmware.ki"))
    except FileNotFoundError:
        None
    f = open(os.path.join(build_path, "firmware.ki"), 'wb')
    
    header_bytes = bytes()
    # md5
    md5_len = len(defs["MD5"])
    header_bytes = struct.pack('<H'+str(md5_len)+"s", md5_len, bytes(defs["MD5"], 'utf-8'))
    # total vars mc size
    (varsSize, varsCount) = getVarsSizeAndCount(instances)
    header_bytes += struct.pack('<II', varsSize, varsCount)
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
    
    instances_bytes = bytes()
    for path, inst in instances.items():
        instances_bytes += getBytesFromInst(inst)
        
    # parse locations into bytes
    locations_bytes = bytes()
    for loc_name, content in locations.items():
        loc_type_num = loc_types[loc_name]
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
    f.write(instances_bytes)
    f.write(locations_bytes)
    f.write(tasks_bytes)
    f.close()  

def getVarsSizeAndCount(insts: dict) -> tuple:
    # TODO add array support
    vars_size = 0
    vars_count = 0
    for path, inst in insts.items():
        variables = inst["vars"]
        vars_count += len(variables.keys())
        
        for var_name, content in variables.items():
            type_info = var_type_dict[content["type"]]
            if content["type"] == "STRING":
                vars_size += 255
            else:
                vars_size += type_info["size"]
    return (vars_size, vars_count)    

def getBytesFromInst(inst: dict) -> bytes:
    vars_count = len(inst["vars"])
    actions_count = len(inst["actions"])
    
    instance_bytes = struct.pack("<II", vars_count, actions_count)
    
    # parse vars into bytes
    for var_name, content in inst["vars"].items():
        var_bytes = bytes()
        pack_str = "<B"
        type_info = var_type_dict[content["type"]]
        var_type = type_info["pos"]
    
        var_bytes += struct.pack("<B", var_type)
    
        init_value = content["init_value"]
        
        # TODO think about arrays        
        if init_value == '':
            init_value_length = 0
            var_bytes += struct.pack("<H", init_value_length)
        else:
            (init_value_length, pack_str) = getVarLenAndPackStr(content["type"], False, init_value)
            if content["type"] == "STRING":
                init_value = bytes(init_value, 'utf-8')
            var_bytes += struct.pack("<H"+pack_str, init_value_length, init_value)
        
        instance_bytes += var_bytes
    # parse actions into bytes
    for action in inst["actions"]:
        action_bytes = bytes()
        
        act_type = act_type_dict[action["act_type"]]
        action_bytes += struct.pack("<B", act_type)
        
        action_bytes += struct.pack("<i", action["var_pos"])
        # TODO arrays, strings
        for act_var in action["vars"]:
            # if is_val == true then var_val_or_num is var value and need to know its type
            if act_var["is_val"]:
                var_type = None
                var_val = act_var["var_val_or_num"]
                for inst_var in inst["vars"].values():
                    if inst_var["number"] == action["var_pos"]:
                        var_type = inst_var["type"]
                (length, pack_str) = getVarLenAndPackStr(var_type, False, var_val)
                action_bytes += struct.pack("<H" + pack_str, length, var_val)
            # else just save val pos in vars and val length = 0
            else:
                action_bytes += struct.pack("<Hi", 0, act_var["var_val_or_num"])
        instance_bytes += action_bytes
    return instance_bytes


def getVarLenAndPackStr(base_type: str, is_array: bool, value) -> tuple:
    length = 0
    pack_str = ""
    type_info = var_type_dict[base_type]
    
    length = type_info["size"]
    pack_str = type_info["str_char"]
    
    if is_array or base_type == "STRING":
        length = length*len(value)
        pack_str = str(len(value)) + pack_str
        
    return (length, pack_str)
    

def isValue(str_to_detect: str):
        if str_to_detect.startswith("__BOOL_LITTERAL") or str_to_detect.startswith("__time_to_timespec") or\
            str_to_detect.startswith("__date_to_timespec") or str_to_detect.startswith("__tod_to_timespec") or\
            str_to_detect.startswith("__dt_to_timespec"):
            return True
        return False    

def extractValue(str_to_search: str):
    
    result = ''
    
    re_search = re.search("__BOOL_LITERAL\((.*?)\)", str_to_search)
    
    if re_search is not None:
        result = re_search[1].lower() in 'true'
        if result is False:
            result = ''
        return result

    re_search = re.search("__time_to_timespec\((.*?)\)", str_to_search)
    
    if re_search is not None:
        time_parts = list(map(float, re_search[1].replace(' ', '').split(',')))
        result = (time_parts[1]/1e3+time_parts[2]+time_parts[3]*60+time_parts[4]*60*60+time_parts[5]*60*60*24)
        if result == 0:
            result = ''
        return result
    
    re_search = re.search("__date_to_timespec\((.*?)\)", str_to_search)
    
    if re_search is not None:
        date_parts = list(map(int, re_search[1].replace(' ', '').split(',')))
        dt = datetime.datetime(date_parts[2], date_parts[1], date_parts[0])
        result = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
        if result == 0:
            result = ''
        return result    
    
    re_search = re.search("__tod_to_timespec\((.*?)\)", str_to_search)
    
    if re_search is not None:
        tod_parts = list(map(float, re_search[1].replace(' ', '').split(',')))
        result = (tod_parts[2]*60*60+tod_parts[1]*60+tod_parts[0])
        if result == 0:
            result = ''
        return result    
    
    re_search = re.search("__dt_to_timespec\((.*?)\)", str_to_search)
    
    if re_search is not None:
        dt_parts = list(map(int, re_search[1].replace(' ', '').split(',')))
        dt = datetime.datetime(dt_parts[5], dt_parts[4], dt_parts[3], dt_parts[2], dt_parts[1], dt_parts[0])
        result = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
        if result == 0:
            result = ''
        return result    
    
    re_search = re.search("__STRING_LITERAL\(.,\"(.*?)\"\)", str_to_search)
    
    if re_search is not None:
        result = re_search[1]
        return result
    
    parts = str_to_search.split(',')
    
    for part in parts:
        part = part.replace(')', '')
        try:
            result = int(part)
            if result == 0:
                result = ''
            return result
        except ValueError:
            try:
                result = float(part)
                if result == 0:
                    result = ''
                return result
            except ValueError:
                None
        
    return None

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
                if response == None or len(response) < 2:
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