import os
import platform as os_platform
import re
import socket
import struct
import subprocess
import time
from tarfile import ExtractError

import serial
import util.paths as paths
import wx


class PlcProgramBuilder:
    
    path_to_generated_files = os.path.join(paths.AbsDir(__file__), "Sources", "Generated")
    
    def scrollToEnd(self, txtCtrl):
        if os_platform.system() != "Darwin":
            txtCtrl.SetInsertionPoint(-1)
        txtCtrl.ShowPosition(txtCtrl.GetLastPosition())
        txtCtrl.Refresh()
        txtCtrl.Update()

    def outputIntoCompileWindow(self, str: str):
        # global compiler_logs
        # compiler_logs += str
        wx.CallAfter(self.txtCtrl.AppendText, str)
        wx.CallAfter(self.scrollToEnd, self.txtCtrl)

    def build(self, board_type, defs, resource_name, build_path, port, txtCtrl):
        self.txtCtrl = txtCtrl

        self._setupSrcFiles(defs, resource_name, build_path)
        binary_path = self._buildBinary(board_type)

        if binary_path is not None and port is not None:
            self._sendFwViaSerial(port, binary_path, defs)

        self.outputIntoCompileWindow("\n")

    def _buildBinary(self, board_type) -> str:
        self.outputIntoCompileWindow("Start to build project\n")
        make_path = os.path.join(
            paths.AbsDir(__file__), "Sources", "PLCSpecified", "KauriPLC", "STM32Make.make"
        )
        files_path = os.path.join(paths.AbsDir(__file__), "Sources", "PLCSpecified", "KauriPLC")
        build_command = f"make -C {files_path} -f {make_path}"
        try:
            res = subprocess.check_output(
                build_command, stderr=subprocess.STDOUT, shell=True, env=os.environ
            )
        except subprocess.CalledProcessError as err:
            self.outputIntoCompileWindow("Build failed\n")
            self.outputIntoCompileWindow(f"Build output: \n{err.stdout}")
            return None
        else:
            res = re.findall(r"B\s+?([.\d]+)\%", res.decode())
            self.outputIntoCompileWindow("Project successfully build\n")
            self.outputIntoCompileWindow(f"RAM used: {res[0]}%\n")
            self.outputIntoCompileWindow(f"FLASH used: {res[1]}%\n")

        return os.path.join(files_path, "build", "PLC_Logic.bin")

    def _sendFwViaSerial(self, port, fw_path, defs):
        md5_len = len(defs["MD5"])
        config_bytes = struct.pack(
            "<H" + str(md5_len) + "s", md5_len, bytes(defs["MD5"], "utf-8")
        )

        # modbus serial
        config_bytes += struct.pack(
            "<?IB",
            defs["MODBUS_SERIAL"]["ENABLED"],
            int(defs["MODBUS_SERIAL"]["BAUD_RATE"]),
            int(defs["MODBUS_SERIAL"]["SLAVE_ID"]),
        )
        # TODO parse another fields of mb tcp
        config_bytes += struct.pack("<?", defs["MODBUS_TCP"]["ENABLED"])

        func_name_to_code = {
            "ST_FW_SEND": 102,
            "SEND_FW_PACKET": 103,
            "END_FW_SEND": 104,
        }

        is_error_occured = False

        send_client = ModbusSendClient(
            modbus_type="RTU", serial_port=port, baudrate=115200, slave_id=1
        )

        if send_client.connect():
            self.outputIntoCompileWindow(f"Connected to device from {port}\n")
        else:
            self.outputIntoCompileWindow(f"Failed to connect to device from {port}\n")
            return

        f = open(fw_path, "rb")
        data_byte = f.read(248)
        send_client.set_timeout(3)
        resp = send_client._send_modbus_request(
            func_name_to_code["ST_FW_SEND"], bytes()
        )
        if resp is None or resp[2 + 6] != 0:
            is_error_occured = True
            self.outputIntoCompileWindow(
                "An error occurred during transmission (failed to initiate sending)\n"
            )
        send_client.set_timeout(0.1)
        if not is_error_occured:
            while data_byte:
                resp = send_client._send_modbus_request(
                    func_name_to_code["SEND_FW_PACKET"], data_byte
                )
                if resp is None or resp[2 + 6] != 0:
                    self.outputIntoCompileWindow(
                        "An error occurred during transmission\n"
                    )
                    break
                data_byte = f.read(248)
        f.close()

        if not is_error_occured:
            resp = send_client._send_modbus_request(
                func_name_to_code["END_FW_SEND"], bytes()
            )
            if resp is not None:
                self.outputIntoCompileWindow("An error occurred during transmission\n")

        if not is_error_occured:
            self.outputIntoCompileWindow("The firmware was successfully loaded\n")
        else:
            self.outputIntoCompileWindow("The firmware wasn't loaded\n")

        send_client.disconnect()

    def _setupSrcFiles(self, defs, resource_name, build_path):
        
        gen_path = self.path_to_generated_files
        try:
            os.remove(os.path.join(gen_path, "app_conf.h"))
            os.remove(os.path.join(gen_path, f"{resource_name}.c"))
            os.remove(os.path.join(gen_path, f"{resource_name}.h"))
            os.remove(os.path.join(gen_path, "Config0.c"))
            os.remove(os.path.join(gen_path, "Config0.h"))
            os.remove(os.path.join(gen_path, "LOCATED_VARIABLES.h"))
            os.remove(os.path.join(gen_path, "io_vars.c"))
            os.remove(os.path.join(gen_path, "io_vars.h"))
            os.remove(os.path.join(gen_path, "POUS.h"))
            os.remove(os.path.join(gen_path, "POUS.c"))
        except FileNotFoundError:
            pass
        
        self.outputIntoCompileWindow("Prepearing files for building\n")
        
        if not os.path.exists(gen_path):
            os.makedirs(gen_path)
            
        with open(os.path.join(gen_path, "app_conf.h"), "w") as f:
            f.write(
                f"""#ifndef APP_CONF_H
#define APP_CONF_H

#define MD5 "{defs["MD5"]}"

#define MB_SERIAL_IFACE {defs["MODBUS_SERIAL"]["INTERFACE"]}
#define MB_SERIAL_EN {'1' if defs["MODBUS_SERIAL"]["ENABLED"] else '0'}
#define MB_SERIAL_BR {defs["MODBUS_SERIAL"]["BAUD_RATE"]}
#define MB_SERIAL_SLAVE_ID {defs["MODBUS_SERIAL"]["SLAVE_ID"]}

#define MB_TCP_EN {'1' if defs["MODBUS_TCP"]["ENABLED"] else '0'}
#define MB_TCP_MAC {defs["MODBUS_TCP"]["MAC"]}
#define MB_TCP_IP {defs["MODBUS_TCP"]["IP"]}
#define MB_TCP_DNS {defs["MODBUS_TCP"]["DNS"]}
#define MB_TCP_GATEWAY {defs["MODBUS_TCP"]["GATEWAY"]}
#define MB_TCP_SUBNET {defs["MODBUS_TCP"]["SUBNET"]}
#define MB_TCP_SSID {defs["MODBUS_TCP"]["SSID"]}
#define MB_TCP_PWD {defs["MODBUS_TCP"]["PWD"]}

#endif"""
            )

        res_file = open(os.path.join(build_path, f"{resource_name}.c"), "r")
        res_file_code = res_file.read()
        res_file.close()

        lines = res_file_code.splitlines()
        lines[4] = f'#include "{resource_name}.h"'
        res_file_code = ""
        for line in lines:
            if "POUS.c" not in line:
                res_file_code += line + "\n"

        with open(os.path.join(gen_path, f"{resource_name}.c"), "w") as f:
            f.write(res_file_code)

        with open(os.path.join(gen_path, f"{resource_name}.h"), "w") as f:
            f.write(
                f"""#ifndef {resource_name.upper()}_H
#define {resource_name.upper()}_H
            
void {resource_name.upper()}_init__(void);
            
void {resource_name.upper()}_run__(unsigned long tick);
            
#endif"""
            )

        config_file = open(os.path.join(build_path, "Config0.c"), "r")
        config_file_code = config_file.read()
        config_file.close()

        lines = config_file_code.splitlines()
        lines[4] = '#include "Config0.h"'
        config_file_code = ""
        for line in lines:
            config_file_code += line + "\n"

        with open(os.path.join(gen_path, "Config0.c"), "w") as f:
            f.write(config_file_code)

        with open(os.path.join(gen_path, "Config0.h"), "w") as f:
            f.write(
                """#ifndef CONFIG0_H
#define CONFIG0_H

void config_init__(void);
void config_run__(unsigned long tick);

#endif"""
            )

        located_vars_file = open(os.path.join(build_path, "LOCATED_VARIABLES.h"), "r")
        located_vars = located_vars_file.read()
        located_vars_lines = located_vars.splitlines()

        glue_vars = """#include "io_vars.h"

#define __LOCATED_VAR(type, name, ...) type __##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR
#define __LOCATED_VAR(type, name, ...) type* name = &__##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR

"""
        var_type_to_max_addr = {"IX": 0, "QX": 0, "IW": 0, "QW": 0}
        loc_vars_init = ""
        for located_var in located_vars_lines:
            # cleanup located var line
            if "__LOCATED_VAR(" in located_var:
                located_var = located_var.split("(")[1].split(")")[0]
                var_data = located_var.split(",")
                if len(var_data) < 5:
                    raise ExtractError(
                        "Error processing located var line: " + located_var
                    )
                else:
                    var_name = var_data[1]
                    var_type = var_name[2:4]
                    var_address = int(var_data[4])
                    var_subaddress = 0
                    if len(var_data) > 5:
                        var_subaddress = int(var_data[5])
                        var_total_addr = var_address * 8 + var_subaddress
                    else:
                        var_total_addr = var_address
                    if var_subaddress > 7:
                        raise ExtractError("Error: wrong location for var " + var_name)

                    if var_type_to_max_addr.get(var_type) is None:
                        raise ExtractError(
                            'Could not process location "'
                            + var_name
                            + '" from line: '
                            + located_var
                        )
                    else:
                        loc_vars_init += f"   vars_to_io_linker.{var_type}[{var_total_addr}] = {var_name};\n"
                        var_type_to_max_addr[var_type] = max(
                            var_type_to_max_addr[var_type], var_total_addr + 1
                        )

        glue_vars += f"""VarsToIOLinker vars_to_io_linker;

void io_vars_init()
{{
{loc_vars_init}
}}
        """

        with open(os.path.join(gen_path, "io_vars.c"), "w") as f:
            f.write(glue_vars)

        with open(os.path.join(gen_path, "io_vars.h"), "w") as f:
            f.write(
                f"""#ifndef IO_VARS_H
#define IO_VARS_H

#include "iec_std_lib.h"

typedef struct {{
    IEC_BOOL *IX[{var_type_to_max_addr["IX"]}];
    IEC_BOOL *QX[{var_type_to_max_addr["QX"]}];
    IEC_UINT *IW[{var_type_to_max_addr["IW"]}];
    IEC_UINT *QW[{var_type_to_max_addr["QW"]}];
}} VarsToIOLinker;

void io_vars_init();

#endif
"""
            )

        with open(os.path.join(gen_path, "LOCATED_VARIABLES.h"), "w") as f:
            f.write(located_vars)

        with open(os.path.join(build_path, "POUS.h"), "r") as f:
            pous_code_h = f.read()
        pous_code_h = pous_code_h.replace('#include "beremiz.h"', "")

        with open(os.path.join(gen_path, "POUS.h"), "w") as f:
            f.write(pous_code_h)

        with open(os.path.join(build_path, "POUS.c"), "r") as f:
            pous_code_c = f.read()
        pous_code_c = '#include "POUS.h"\n\n' + pous_code_c

        with open(os.path.join(gen_path, "POUS.c"), "w") as f:
            f.write(pous_code_c)


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
        self.timeout = 10

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
                    port=self.serial_port, baudrate=self.baudrate, timeout=1.5
                )
                time.sleep(2)  # make sure connection happens
            except Exception as e:
                # print(f"Serial port connection error: {str(e)}")
                print("Serial port connection error: {}".format(str(e)))
                return False

        return True

    def set_timeout(self, timeout: float):
        if self.modbus_type == "TCP":
            self.sock.settimeout(self.timeout)
        elif self.modbus_type == "RTU":
            self.serial.timeout = timeout

    def disconnect(self):
        if self.modbus_type == "TCP":
            if self.sock:
                self.sock.close()
                self.sock = None

        elif self.modbus_type == "RTU":
            if self.serial:
                self.serial.close()
                self.serial = None
