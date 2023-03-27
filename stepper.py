#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

in1 = 6
in2 = 13
in3 = 19
in4 = 26

#fastest without stall:
step_sleep = 0.00075
step_sleep = .0015

step_count = 4096 # 5.625*(1/64) per step, 4096 steps is 360°

direction = True # True for clockwise, False for counter-clockwise

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]
# setting up
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )

# initializing
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )


motor_pins = [in1,in2,in3,in4]
motor_step_counter = 0 ;

def do_steps(num_steps):
    global motor_step_counter
    increment = 1
    if (num_steps < 0):
        increment = -1
    while (num_steps != 0):
        motor_step_counter = (motor_step_counter + increment) % 8
        for pin in range(0,len(motor_pins)):
            GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
        num_steps = num_steps - increment
        time.sleep(step_sleep)

def cleanup():
    GPIO.output( in1, GPIO.LOW )
    GPIO.output( in2, GPIO.LOW )
    GPIO.output( in3, GPIO.LOW )
    GPIO.output( in4, GPIO.LOW )
    GPIO.cleanup()

if __name__ == '__main__':
    # the meat
    try:
        i = 0
        while True:   
            i = i +1
            if (i%5000 == 0):
                print("STEP: " + str(step_sleep))
                direction = not direction
            for pin in range(0, len(motor_pins)):
                GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
            if direction==True:
                motor_step_counter = (motor_step_counter - 1) % 8
            elif direction==False:
                motor_step_counter = (motor_step_counter + 1) % 8
            time.sleep( step_sleep )

    except KeyboardInterrupt:
        cleanup()
