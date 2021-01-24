from optibook.synchronous_client import Exchange
from utils import *

import logging
import time
import random
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")


e = Exchange()
a = e.connect()

prev_data = None
moving_ave = 0
moving_sum = []

MAX_HISTORY = 50 #number of historical prices referenced for moving_ave
THRESHOLD = 0.2 #deviation from moving_ave threshold before entering the market
TIME_DELAY = 0.25 #frequency of cycle
VOLUME = 3 #volume per trade
MAX_POSITION = 20 #max absolute position allowed on either instrument

while True:
    time.sleep(TIME_DELAY)
    
    data, prev_data = get_data(e, prev_data)
    moving_sum.append((data[0][2] + data[1][2])/2)
    if len(moving_sum) >  MAX_HISTORY: moving_sum.pop(0)
    moving_ave = sum(moving_sum)/len(moving_sum)
    print(moving_ave)
    
    positions = e.get_positions()
    
    if data[0][0] > moving_ave + THRESHOLD and positions["PHILIPS_A"] > -MAX_POSITION:
        #PHILIPS_A is buying at above moving_ave + THRESHOLD
        #time to sell
        result = e.insert_order("PHILIPS_A", price=data[0][0], volume=VOLUME, side='ask', order_type='ioc')
        print("created order to sell PHILIPS_A")
    elif data[0][1] < moving_ave - THRESHOLD and positions["PHILIPS_A"] < MAX_POSITION: 
        #PHILIPS_A is selling at below moving_ave - THRESHOLD
        #time to buy
        result = e.insert_order("PHILIPS_A", price=data[0][1], volume=VOLUME, side='bid', order_type='ioc')
        print("created order to buy PHILIPS_A")
    elif data[1][0] > moving_ave + THRESHOLD and positions["PHILIPS_B"] > -MAX_POSITION: 
        #PHILIPS_B is buying at above moving_ave + THRESHOLD
        #time to sell
        result = e.insert_order("PHILIPS_B", price=data[1][0], volume=VOLUME, side='ask', order_type='ioc')
        print("created order to sell PHILIPS_B")
    elif data[1][1] < moving_ave - THRESHOLD and positions["PHILIPS_B"] < MAX_POSITION: 
        #PHILIPS_B is selling at below moving_ave - THRESHOLD
        #time to buy
        result = e.insert_order("PHILIPS_B", price=data[1][1], volume=VOLUME, side='bid', order_type='ioc')
        print("created order to buy PHILIPS_B")
    else:
        print("no orders made")
    