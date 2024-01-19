# Hacker Fab Lab, Fall 2023
# B. Joel Gonzalez
# Sends G-code to gantry over USB

# from os import waitid
import time
import numpy as np
import serial.tools.list_ports
import sys

old_x = 0
old_y = 0
old_z = 0

TIME_PAUSE = 0
BAUD_RATE = 115200

gantry_port = None

def calcMoveTime(x, y, z):
    times = []
    amax = 100
    for new, orig, vmax in zip([x, y, z], [old_x, old_y, old_z], [16, 16, 16]):
        d = abs(new - orig) + 1e-6
        t = np.sqrt(4 * d / amax)
        if 2 * d / t > vmax:
            t = (d + vmax * vmax / amax) / vmax
        times.append(t)
    return max(times) + TIME_PAUSE

# homes the axes
def home_gantry():
    global old_x, old_y, old_z

    # set_stepper_motors("M502")
    # time.sleep(5)
    # print("Reset done!")

    start_time = time.time()

    set_stepper_motors("G92 X0 Y0 Z0", dont_wait_for_echo=True)
    send_gantry_command(x_pos=15, y_pos=15, z_pos=15, dont_wait_for_echo=True)
    print("Moved axes forward a bit before homing")

    command = "G28"
    set_stepper_motors(command, wait_for_ok=True)

    wait_time = 30
    time.sleep(max(0, wait_time - (time.time() - start_time))) # In case 'ok' was returned early, just wait min 30 seconds
    print("Homing done!")

    old_x = 0
    old_y = 0
    old_z = 0

# sets X/Y positions for gantry and Z position for end-effector
# arguments are optional
def send_gantry_command(x_pos = None, y_pos = None, z_pos = None, dont_wait_for_echo=False):
    global old_x, old_y, old_z

    command = "G1"

    new_x = x_pos if x_pos is not None else old_x
    new_y = y_pos if y_pos is not None else old_y
    new_z = z_pos if z_pos is not None else old_z
    
    if x_pos != None:
        command += " X" + str(x_pos)
    if y_pos != None:
        command += " Y" + str(y_pos)
    if z_pos != None:
        command += " Z" + str(z_pos)
        
    print(command)
    set_stepper_motors(command, dont_wait_for_echo=dont_wait_for_echo)

    waiting_time = calcMoveTime(new_x, new_y, new_z)
    print(f"Waiting for {waiting_time} seconds")
    time.sleep(waiting_time)

    old_x = new_x
    old_y = new_y
    old_z = new_z

# moves the gantry in an arc motion
# x_center and y_center are the current position of the XY gantry
# radius is 16mm for gate valves, 29mm for rotary valve
# alpha is the initial angle, omega is the target angle (radians for both)
# we move counterclockwise like a normal unit circle :)
def send_gantry_command_arc(x_init, y_init, alpha, omega, radius, upwards, direction=None):
    # G17 for XY plane, G18 for ZX plane
    if upwards:
        set_stepper_motors("G18")
    else:
        set_stepper_motors("G17")

    arc_direction = "" # G2 is clockwise, G3 is counter-clockwise
    target_angle = 0 # needs to be in radians, eventually

    print("angles: " + str(alpha) + " " + str(omega))

    if (alpha < omega):
        arc_direction = "G2 "
        target_angle = omega - alpha
    else:
        arc_direction = "G3 "
        target_angle = alpha - omega

    # manually set for rotary valve
    if direction != None:
        arc_direction = direction

    # find the center of the gate valve, accounting for our flipped x-axis
    x_center = x_init + radius * np.cos(alpha)
    y_center = y_init - radius * np.sin(alpha)
    
    print("center: " + str(x_center) + " " + str(y_center))

    # find target location, accounting for our flipped x-axis
    x_target = (x_center) - radius * np.cos(omega)
    y_target = (y_center) + radius * np.sin(omega)

    command = str(arc_direction) + "X" + str(x_target) + " Y" + str(y_target) + " R" + str(radius)

    print(command)
    set_stepper_motors(command)

    # account for arc travel time
    waiting_time = calcMoveTime(0, 0, radius * target_angle)
    print(f"Waiting for {waiting_time} seconds")
    time.sleep(waiting_time)

    return x_target, y_target

# send command to gantry
# you can just feed G-code commands to this function, if you want to test manual movement
def set_stepper_motors(stepper_commands, wait_for_ok=False, dont_wait_for_echo=False):
    stepper_commands += '\n'
    GANTRY_PORT.flush()
    GANTRY_PORT.write(stepper_commands.encode())
    if not dont_wait_for_echo:
        if wait_for_ok:
            gantry_echo = ""
            while("ok" not in gantry_echo):
                gantry_echo = str(gantry_port.readline())
                print(gantry_echo)
        else:
            # Just wait for the first thing we get back
            gantry_echo = str(gantry_port.readline())
            print(gantry_echo)

# assign gantry port
def assign_ports():
    global GANTRY_PORT
    ports = list(serial.tools.list_ports.comports())
    # go thru open ports
    for p in ports:
        print(p)

        windows_port = "CH340" in p.description
        linux_port = "USB Serial" in p.description
        if windows_port or linux_port: # ender 5 S1 board - may need to be more specific if we have multiple USB devices connected
            GANTRY_PORT = serial.Serial(p.device, BAUD_RATE)
            print("Gantry connected!")

if __name__ == '__main__':
    assign_ports()

    while 1:
        stepper_commands = input("Stepper Motor Commands:\n") # user input for testing/debugging
        if stepper_commands != '':
            set_stepper_motors(stepper_commands, dont_wait_for_echo=True)
