import time
import sys
import MPU
import Adafruit_BBIO.PWM as PWM
sys.path.insert(1, './src')
import IMU_calc
import calc_functions
import PID_Controller 
import PID as PIDlib 
# Werte für 1 BAR Großer Arm
#a = -.00000204    
#b = 0.0006
#c = -0.0675
#d = 3.9591
#e = -19.343

#Werte für 2 Bar Großer Arm
a = -1.773E-7
b = 7.232E-5
c = -0.012
d = 1.1541
e = -0.0469

#Were für 3 Bar Großer Arm
#a = -8.526E-8
#b = 4.14E-5
#c = -0.0079
#d = 0.7641
#e = 1.0103

#Werte für 1 Bar kleiner Arm
#a = -3.124E-7
#b = 9.904E-5
#c = -0.015
#d = 1.7829
#e = -5.9829

#Werte für 2 Bar kleiner Arm
# a = -7.594E-7
# b = 0.0002
# c = -0.0235
# d = 1.4376
# e = -7.7863

#Werte für 3 Bar kleiner Arm
# a = -2.245E-7
# b = 7.556E-5
# c = -0.0096
# d = 0.7632
# e = -3.1327

PID = PIDlib.PidController([0.1, 16.667, 0.0], 0.01, 30)


myPWM = "P8_13"
PWM.start(myPWM, 0)
IMU_static = MPU.MPU_9150(0, 0)
IMU_dynamic = MPU.MPU_9150(0, 1)


for i in range(0, 10):

    ref_angle = calc_functions.reference_angle()
    first_time = time.monotonic()
    while time.monotonic() < (first_time + 1):
        vec_dynamic = IMU_dynamic.get_acceleration()
        vec_static = IMU_static.get_acceleration()
        current_angle = IMU_calc.calc_angle(vec_dynamic, vec_static)
        print(time.monotonic(), current_angle, ref_angle)
        
    DC = a * (ref_angle ** 4) + b * (ref_angle ** 3) + c * (ref_angle ** 2) + d * ref_angle + e

    try:
        while True:
            try:
                vec_dynamic = IMU_dynamic.get_acceleration()
                vec_static = IMU_static.get_acceleration()
                current_angle = IMU_calc.calc_angle(vec_dynamic, vec_static)
                output = PID.output(ref_angle, current_angle)
                print(time.monotonic(), current_angle, ref_angle)
#                print(current_angle)
                new_DC = DC + output
                if new_DC > 99.99:
                    new_DC = 99.99
                elif new_DC < .01:
                    new_DC = .01
#                print('output:\t\t', output, '\n')
                PWM.set_duty_cycle(myPWM, new_DC)
                time.sleep(.01)

            except OSError:
                pass

    except KeyboardInterrupt:
        pass


PWM.stop(myPWM)
PWM.cleanup()
