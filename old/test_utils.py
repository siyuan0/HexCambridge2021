import time

instrument_id1 = 'PHILIPS_A'
instrument_id2 = 'PHILIPS_B'



def get_data(e,threshold=0.1):
    
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
        
        A_lower = A_best_bid*(1-threshold)
        A_upper = A_best_ask*(1+threshold)
        B_lower = B_best_bid*(1-threshold)
        B_upper = B_best_ask*(1+threshold)
        
        A_prices = []
        A_volume = []
        B_prices = []
        B_volume = []
        
        for n in range(len(e.get_last_price_book(instrument_id1).bids)):
            pricebidA = e.get_last_price_book(instrument_id1).bids[n].price
            if A_lower < pricebidA:
                volumebidA = e.get_last_price_book(instrument_id1).bids[n].volume
                A_prices.append(pricebidA)
                A_volume.append(volumebidA)
            
        for n in range(len(e.get_last_price_book(instrument_id1).asks)):
            priceaskA = e.get_last_price_book(instrument_id1).asks[n].price
            if A_upper > priceaskA:
                volumeaskA = e.get_last_price_book(instrument_id1).asks[n].volume
                A_prices.append(priceaskA)
                A_volume.append(volumeaskA)
                
        for n in range(len(e.get_last_price_book(instrument_id2).bids)):
            pricebidB = e.get_last_price_book(instrument_id2).bids[n].price
            if B_lower < pricebidB:
                volumebidB = e.get_last_price_book(instrument_id2).bids[n].volume
                B_prices.append(pricebidB)
                B_volume.append(volumebidB)
            
        for n in range(len(e.get_last_price_book(instrument_id2).asks)):
            priceaskB = e.get_last_price_book(instrument_id2).asks[n].price
            if B_upper > priceaskB:
                volumeaskB = e.get_last_price_book(instrument_id2).asks[n].volume
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
        
        data = [[A_best_bid, A_best_ask, A_EV], [B_best_bid, B_best_ask, B_EV]]
        
        print(data) #REMOVED AFTER TESTING
        
        return data
        
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
        
    else:
        y = 0
        
    print(y) #REMOVE AFTER TESTING
        
    return y
    
def withdraw_orders(e):
    """
    REMOVE ALL ORDERS
    """
    # e.delete_orders(instrument_id1)
    # e.delete_orders(instrument_id2)
    print("DELETED ORDERS")
    
    
def check_our_position(e, prev):
    """
    Takes in the positions we have.
    If we have 20 positions, we buy/sell only until we have 10 positions.
    """
    SOFT_THRESHOLD = 10
    HARD_THRESHOLD = 20
    
    positions = e.get_positions()
    net_position = positions[instrument_id1] + positions[instrument_id2]
    if prev == -1 and net_position >= SOFT_THRESHOLD:
        #keep selling
        print("Net position: ", prev, "strategy: -1")  
        return -1
    elif prev == 1 and net_position <= -SOFT_THRESHOLD:
        #keep buying
        print("Net position: ", prev, "strategy: 1")  
        return 1
    elif net_position >= HARD_THRESHOLD:
        #start selling
        print("Net position: ", prev, "strategy: -1")  
        return -1
    elif net_position <= -HARD_THRESHOLD:
        #start buying
        print("Net position: ", prev, "strategy: 1")  
        return 1
    else:
        #status quo
        print("Net position: ", prev, "strategy: 0")  
        return 0
        