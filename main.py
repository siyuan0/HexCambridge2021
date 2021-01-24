from optibook.synchronous_client import Exchange
from utils import get_data, check_arbitrage, withdraw_orders, check_our_position, adjust_ask_price, adjust_bid_price, position_overload

import logging
import time
import random
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

instrument_id1 = 'PHILIPS_A'
instrument_id2 = 'PHILIPS_B'

e = Exchange()
a = e.connect()

# get_data

TIME_DELAY = 0.25

position_state = 0
prev_data = None
# for i in range(10):
while True:
    e_instance = e
    data, prev_data = get_data(e_instance, prev_data)
    if data is None:
        print("no market data exists")
        time.sleep(TIME_DELAY)
        continue
    
    
    arbitrage_status = check_arbitrage(data,0.3)
    
    if arbitrage_status == 0:
        withdraw_orders(e_instance)
        
    else:
        
        overload_state = position_overload(e_instance)
        
        position_state = check_our_position(e_instance, position_state)
        
        if arbitrage_status == -1:
            """
            We buy from M1, and sell to M2
            
            Check position state: sell, buy, or both?
            
            Position state: Both
                
                Set M1 bid price
                Set M2 ask price
            
            Position state: Sell
            
                Remove M1 bid price
                Set M2 ask price
                
            Position state: Buy
            
                Set M1 bid price
                Remove M2 ask price
            """
            if overload_state == 1:
                continue
            elif position_state == 0:
                adjust_bid_price(e_instance,instrument_id1)
                adjust_ask_price(e_instance,instrument_id2)
                
            elif position_state == -1:
                withdraw_orders(e_instance)
                adjust_ask_price(e_instance,instrument_id2)
                
            elif position_state == 1:
                withdraw_orders(e_instance)
                adjust_bid_price(e_instance,instrument_id1)
        
        
        elif arbitrage_status == 1:
            """
            We buy from M2, and sell to M1
            
            Check position state: sell, buy, or both?
            
            Position state: Both
                
                Set M1 ask price
                Set M2 bid price
            
            Position state: Sell
            
                Set M1 ask price
                Remove M2 bid price
                
            Position state: Buy
            
                Remove M1 ask price
                Set M2 bid price
                
            """
            if overload_state == -1:
                continue
            elif position_state == 0:
                adjust_bid_price(e_instance,instrument_id2)
                adjust_ask_price(e_instance,instrument_id1)
                
            elif position_state == -1:
                withdraw_orders(e_instance)
                adjust_ask_price(e_instance,instrument_id1)
                
            elif position_state == 1:
                withdraw_orders(e_instance)
                adjust_bid_price(e_instance,instrument_id2)
    
    time.sleep(TIME_DELAY)