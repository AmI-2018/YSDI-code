import zWaveModule as mod
import time

if __name__=="__main__":

    print("Trying to turn on plug:")
   # mod.turnOnPlug('coffeeMachine')
    print("should be on")
    print()
   # time.sleep(1)
    print("Trying to turn off plug:")
   # mod.turnOffPlug('coffeeMachine')
    print("should be off")
    print()
   # time.sleep(1)

    print("Trying to get lux:")
    x=mod.checkLux()
    print("light is: "+str(x))
    print()

    print("Trying to get lux:")
    x = mod.checkLux()
    print("light is: " + str(x))
    print()
