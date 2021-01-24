import time
import random

instrument_id1 = 'PHILIPS_A'
instrument_id2 = 'PHILIPS_B'
VOLUME = 5
INCREMENT = 0.1

def get_data(e, prev, threshold=0.1):
    pb1 = e.get_last_price_book(instrument_id1)
    pb2 = e.get_last_price_book(instrument_id2)
    
    if len(pb1.bids) * \
        len(pb1.asks) * \
        len(pb2.bids) * \
        len(pb2.asks) == 0 and prev == None:
            # print(pb1.bids,
            #     pb1.asks,
            #     pb2.bids,
            #     pb2.asks)
            return None, None
    if len(pb1.bids) == 0: pb1.bids = prev[0].bids
    if len(pb1.asks) == 0: pb1.asks = prev[0].asks
    if len(pb2.bids) == 0: pb2.bids = prev[1].bids
    if len(pb2.asks) == 0: pb2.asks = prev[1].asks
        
    A_best_bid = pb1.bids[0].price
    A_best_ask = pb1.asks[0].price
    B_best_bid = pb2.bids[0].price
    B_best_ask = pb2.asks[0].price
    
    A_lower = A_best_bid*(1-threshold)
    A_upper = A_best_ask*(1+threshold)
    B_lower = B_best_bid*(1-threshold)
    B_upper = B_best_ask*(1+threshold)
    
    A_prices = []
    A_volume = []
    B_prices = []
    B_volume = []
    
    for n in range(len(pb1.bids)):
        pricebidA = pb1.bids[n].price
        if A_lower < pricebidA:
            volumebidA = pb1.bids[n].volume
            A_prices.append(pricebidA)
            A_volume.append(volumebidA)
        
    for n in range(len(pb1.asks)):
        priceaskA = pb1.asks[n].price
        if A_upper > priceaskA:
            volumeaskA = pb1.asks[n].volume
            A_prices.append(priceaskA)
            A_volume.append(volumeaskA)
            
    for n in range(len(pb2.bids)):
        pricebidB = pb2.bids[n].price
        if B_lower < pricebidB:
            volumebidB = pb2.bids[n].volume
            B_prices.append(pricebidB)
            B_volume.append(volumebidB)
        
    for n in range(len(pb2.asks)):
        priceaskB = pb2.asks[n].price
        if B_upper > priceaskB:
            volumeaskB = pb2.asks[n].volume
            B_prices.append(priceaskB)
            B_volume.append(volumeaskB)
    
    A_sum = 0
    B_sum = 0
    
    for n in range(len(A_prices)):
        A_sum += A_prices[n]*A_volume[n]
    
    for n in range(len(B_prices)):
        B_sum += B_prices[n]*B_volume[n]
        
    A_EV = A_sum/sum(A_volume)
    B_EV = B_sum/sum(B_volume)
    
    data = [[round(A_best_bid,2), round(A_best_ask,2), A_EV], [round(B_best_bid,2), round(B_best_ask,2), B_EV]]
    
    # print(data) #REMOVED AFTER TESTING
    
    return data, (pb1, pb2)
        
def check_arbitrage(data,threshold=0.30): 
    """
    CHECK ARBITRAGE CONDITION
    Takes in data from "get_data" function, and checks if an arbitrage exists.
    Returns -1, 0, or 1
    0 refers to no arbitrage.
    -1 refers to Philip A lower EV than Philip B
    1 refers to Philip A higher EV than Philip B
    """
    if data[0][2] + threshold < data[1][2]:
        y = -1
        
    elif data[0][2] > data[1][2] + threshold:
        y = 1
    elif data[0][0] > data[1][1] + 0.1: #added to test
        y = 1
    elif data[0][1] < data[1][0] + 0.1: #added to test
        y = -1
    else:
        y = 0
        
        
    return y
    
def withdraw_orders(e):
    """
    REMOVE ALL ORDERS
    """
    e.delete_orders(instrument_id1)
    e.delete_orders(instrument_id2)
    print("DELETED ORDERS")
    
    
def check_our_position(e, prev):
    """
    Takes in the positions we have.
    If we have 20 positions, we buy/sell only until we have 10 positions.
    0 - freely buy/sell
    1 - can only buy
    -1 - can only sell
    """
    SOFT_THRESHOLD = 20
    HARD_THRESHOLD = 40
    OFFSET = 0
    
    positions = e.get_positions()
    net_position = positions[instrument_id1] + positions[instrument_id2]
    if prev == -1 and net_position >= OFFSET + SOFT_THRESHOLD:
        #keep selling
        return -1
    elif prev == 1 and net_position <= OFFSET - SOFT_THRESHOLD:
        #keep buying
        return 1
    elif net_position >= OFFSET + HARD_THRESHOLD:
        #start selling
        return -1
    elif net_position <= OFFSET - HARD_THRESHOLD:
        #start buying
        return 1
    else:
        #status quo
        return 0

def position_overload(e):
    '''get positional inbalance
    0 - all is well
    -1 - move position towards A
    1 - move position towards B'''
    THRESHOLD = 20
    positions = e.get_positions()
    if abs(positions[instrument_id1] - positions[instrument_id2]) > THRESHOLD:
        if positions[instrument_id1] < positions[instrument_id2]: 
            return -1
        else:
            return 1
    else:
        return 0

def get_outstanding_orders(e, instrument_id, side):
    '''get bid/ask orders in the system'''
    order_id = None
    prev_price = None
    try:
        for key, item in e.get_outstanding_orders(instrument_id):
            if item.side == side:
                order_id = item.order_id
                prev_price = item.price
    except:
        pass
    return order_id, prev_price
    

def adjust_bid_price(e, instrument_id):
    """
    If arbitrage exists, check if we need to adjust bid price.
    If adjustment required, proceed to adjust bid price.
    """
    order_id, prev_price = get_outstanding_orders(e, instrument_id, side="bid")
    bidprice = e.get_last_price_book(instrument_id).bids[0].price + INCREMENT
    
    if order_id is None:
        result = e.insert_order(instrument_id, price=bidprice, volume=VOLUME, side='bid', order_type='limit')
        print("CREATED NEW BID")
    else:
        if prev_price < e.get_last_price_book(instrument_id).bids[0].price:
            result = e.delete_order(instrument_id, order_id=order_id)
            result = e.insert_order(instrument_id, price=bidprice, volume=VOLUME, side='bid', order_type='limit')
            print("BID PRICE ADJUSTED")
    
def adjust_ask_price(e, instrument_id):
    """
    If arbitrage exists, check if we need to adjust ask price.
    If adjustment required, proceed to adjust ask price.
    """
    order_id, prev_price = get_outstanding_orders(e, instrument_id, side="ask")
    askprice = e.get_last_price_book(instrument_id).asks[0].price - INCREMENT
    
    if order_id is None:
        result = e.insert_order(instrument_id, price=askprice, volume=VOLUME, side='ask', order_type='limit')
        print("CREATED NEW ASK")
    else:
        if prev_price > e.get_last_price_book(instrument_id).asks[0].price:
            result = e.delete_order(instrument_id, order_id=order_id)
            result = e.insert_order(instrument_id, price=askprice, volume=VOLUME, side='bid', order_type='limit')
            print("ASK PRICE ADJUSTED")

