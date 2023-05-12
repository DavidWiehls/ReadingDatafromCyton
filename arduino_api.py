from pyfirmata import Arduino, SERVO, util
import time

port = 'COM4'
board=Arduino(port)

# Define a pin for every finger
pin_thumb = 9
pin_index = 8
pin_middle = 7
pin_ring = 6
pin_little = 5

# SERVO Motors initialitation 
board.digital[pin_thumb].mode = SERVO
board.digital[pin_index].mode = SERVO
board.digital[pin_middle].mode = SERVO
board.digital[pin_ring].mode = SERVO
board.digital[pin_little].mode = SERVO


def initial_position():
    board.digital[pin_thumb].write(150)
    board.digital[pin_index].write(150)
    board.digital[pin_middle].write(170)
    board.digital[pin_ring].write(170)
    board.digital[pin_little].write(0)

# Fist
def hand_position1():
    board.digital[pin_thumb].write(0)
    board.digital[pin_index].write(0)
    board.digital[pin_middle].write(0)
    board.digital[pin_ring].write(0)
    board.digital[pin_little].write(120)

# Rock and Roll!
def hand_position2():
    board.digital[pin_thumb].write(130)
    board.digital[pin_index].write(130)
    board.digital[pin_middle].write(0)
    board.digital[pin_ring].write(0)
    board.digital[pin_little].write(0)

# Peace
def hand_position3():
    board.digital[pin_thumb].write(0)
    board.digital[pin_index].write(130)
    board.digital[pin_middle].write(130)
    board.digital[pin_ring].write(0)
    board.digital[pin_little].write(0)

# Middle Finger
def hand_position4():
    board.digital[pin_thumb].write(0)
    board.digital[pin_index].write(0)
    board.digital[pin_middle].write(170)
    board.digital[pin_ring].write(0)
    board.digital[pin_little].write(150)

# Klenkes
def hand_position4():
    board.digital[pin_thumb].write(0)
    board.digital[pin_index].write(0)
    board.digital[pin_middle].write(0)
    board.digital[pin_ring].write(0)
    board.digital[pin_little].write(0)


#while True:
   
    #board.digital[pin_middle].write(0)
    #time.sleep(2)
    #board.digital[pin_middle].write(150)
    #time.sleep(2)
    #initial_position()
    #time.sleep(3)
    #hand_position2()
    #time.sleep(2)
    # hand_position3()
    # time.sleep(2)
    # hand_position4()
    # time.sleep(2)