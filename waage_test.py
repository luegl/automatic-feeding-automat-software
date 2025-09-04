import gpiozero

import time

import sys

from JoyIT_hx711py import HX711



# Force Python 3 ###########################################################



if sys.version_info[0] != 3:

    raise Exception("Python 3 is required.")



############################################################################





hx = HX711(5, 6)





def cleanAndExit():

    print("Cleaning...")

    # GPIO.cleanup()

    print("Bye!")

    sys.exit()





def setup():

    """

    code run once

    """

    hx.set_offset(8018181.6875)

    hx.set_scale(-916.85)





def loop():

    """

    code run continuosly

    """



    try:

        val = hx.get_grams()

        print(val)



        hx.power_down()

        time.sleep(.001)

        hx.power_up()



        time.sleep(1)

    except (KeyboardInterrupt, SystemExit):

        cleanAndExit()





##################################



if __name__ == "__main__":



    setup()

    while True:

        loop()