import multiprocessing
import os
import time
from wabot import WABot
from x2j import X2J

def start():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    x2j = X2J()
    #x2j.add_data()

    while True:
        
        wabot = WABot()
        wabot.login()

        start = time.time()
        while True:
            wabot.get_data()
            if time.time() - start > 7200:
                wabot.driver.quit()
                break
        '''except:
            try:
                del wabot
            except:
                pass
        '''

if __name__ == '__main__':
    start()