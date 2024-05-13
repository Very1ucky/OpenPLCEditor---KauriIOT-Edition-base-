from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient("COM10", baudrate=115200)
client.connect()
rr = client.read_coils(0, 3, 1)
print(rr.bits)