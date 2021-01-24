
from optibook.synchronous_client import Exchange

import logging
import time
# from utils import check_our_position, get_data
e = Exchange()
a = e.connect()
# for i in range(100):
pb1 = e.get_last_price_book("PHILIPS_A")
pb2 = e.get_last_price_book("PHILIPS_B")

print(pb1.bids,
    pb1.asks,
    pb2.bids,
    pb2.asks)
    # time.sleep(0.1)
