
import RPi.GPIO as GPIO
import time
import threading
        
# self.LED1 = 13 #physical 33 # pin11
# self.LED2 = 19 #physical 35
# self.LED3 = 26 #physical 37
# self.LED4= 16 #physical 36
# self.LED5 = 20 #physical 38
# self.LED6= 21 #physical 40


        
class ControlLED:
    def __init__(self):
#         GPIO.setwarnings(False)
#         GPIO.setmode(GPIO.BCM) # We are accessing GPIOs according to their physical location
        chan_list = [13,19,26,16,20,21]
        GPIO.setup(chan_list, GPIO.OUT) # We have set our LED pin mode to output
        GPIO.output(chan_list, GPIO.LOW) # When it will start then LED will be OFF

        self.dictLED =  {1:13,2:19,3:26,4:16,5:20,6:21}

    def GPIO_clean(self):
        GPIO.cleanup()
        
    def turnONled(self,led):
#         print(led)
        led = self.dictLED.get(led) #busca en dictLED el key que sea led y devuelve el valor (si led==1, devuelve 13)
#         print(led)
        valON = 0.8
        valCycle= 2
        valRepeat = 15
    #         if valRepeat==0:
    #             valRepeat=86400
    #         print(valON,valCycle,valRepeat)
        OFFtime=valCycle - valON
        for i in range(valRepeat):
            GPIO.output(led,True)
#             print("enciende" + str(led))
            time.sleep(valON)
            GPIO.output(led,False)
#             print("apaga" + str(led))
            time.sleep(OFFtime)
        print("FIN LED {}".format(led))
          
  
