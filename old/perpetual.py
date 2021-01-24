from optibook.synchronous_client import Exchange

import logging
import time
logger = logging.getLogger('client')
logger.setLevel('ERROR')

print("Setup was successful.")

instrument_id1 = 'PHILIPS_A'
instrument_id2 = 'PHILIPS_B'

e = Exchange()
a = e.connect()

# Returns all current positions
# positions = e.get_positions()
# for p in positions:
#     print(p, positions[p])
#     print("-----------------------------")
#     # print(e.get_outstanding_orders(p))
#     # print("-----------------------------")
#     print(e.get_last_price_book(p).asks)
#     print(e.get_last_price_book(p).bids)

while True:
    if  len(e.get_last_price_book(instrument_id1).bids)  == 0 or \
        len(e.get_last_price_book(instrument_id1).asks)  == 0 or \
        len(e.get_last_price_book(instrument_id2).bids)  == 0 or \
        len(e.get_last_price_book(instrument_id2).asks)  == 0:
            time.sleep(0.25)
    else:
        A_best_bid = e.get_last_price_book(instrument_id1).bids[0].price
        A_best_ask = e.get_last_price_book(instrument_id1).asks[0].price
        B_best_bid = e.get_last_price_book(instrument_id2).bids[0].price
        B_best_ask = e.get_last_price_book(instrument_id2).asks[0].price
        
        # print(A_best_bid, A_best_ask, B_best_bid, B_best_ask)
        
        if A_best_bid > B_best_ask:
            A_best_bid_vol = e.get_last_price_book(instrument_id1).bids[0].volume
            B_best_ask_vol = e.get_last_price_book(instrument_id2).asks[0].volume
            
            volume = min(A_best_bid_vol, B_best_ask_vol)
            
            result = e.insert_order(instrument_id1, price = A_best_bid, volume=volume, side='bid', order_type='limit')
            result = e.insert_order(instrument_id2, price = B_best_ask, volume=volume, side='ask', order_type='limit')
            print(f"Order Id: {result}")
            
        if B_best_bid > A_best_ask:
            A_best_ask_vol = e.get_last_price_book(instrument_id1).asks[0].volume
            B_best_bid_vol = e.get_last_price_book(instrument_id2).bids[0].volume
            
            volume = min(A_best_ask_vol, B_best_bid_vol)
            
            result = e.insert_order(instrument_id2, price = B_best_bid, volume=volume, side='bid', order_type='limit')
            result = e.insert_order(instrument_id1, price = A_best_ask, volume=volume, side='ask', order_type='limit')
            print(f"Order Id: {result}")
        
        time.sleep(0.25)
        
        if len(e.get_outstanding_orders(instrument_id1)) != 0:
            e.delete_orders(instrument_id1)
        if len(e.get_outstanding_orders(instrument_id2)) != 0:
            e.delete_orders(instrument_id2)