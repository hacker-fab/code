import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())

BAUD_RATE = 115200
TOF_PORT = None

for p in ports:
    print(p)

    if "Arduino" in p.description: # arduino nano board
        TOF_PORT = serial.Serial(p.device, BAUD_RATE)
        print("ToF sensor connected!")

while 1:
    # input("Press enter to get reading")
    tof_reading = str(TOF_PORT.readline())
    if "Invalid" not in tof_reading:
        parsed_tof_reading = tof_reading.strip() # need to strip the newline/return chars
        print(int(parsed_tof_reading))
