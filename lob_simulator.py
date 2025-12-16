import numpy as np
from collections import defaultdict

#random seed for reproducibility
np.random.seed(42)

#tags for events
MARKET_BUY  = "market_buy "
MARKET_SELL = "market_sell"
LIMIT_BUY   = "limit_buy  "
LIMIT_SELL  = "limit_sell "
CANCEL_BID  = "cancel_bid "
CANCEL_ASK  = "cancel_ask "
CANCEL_NONE = "cancel_none"


class LimitOrderBookSimulator:
    def __init__(self,initial_price=100,tick_size=1,lambda_market = 4.0,lambda_limit = 7.0,lambda_cancel = 3.0,order_size = 1):
        self.initial_price = initial_price
        self.tick_size = tick_size
        self.lambda_market = lambda_market
        self.lambda_limit = lambda_limit
        self.lambda_cancel = lambda_cancel
        self.order_size = order_size
        
        self.bids = defaultdict(int)  # price level -> volume
        self.asks = defaultdict(int)  # price level -> volume
        
        self._initialize_book(initial_price)
    
    def _initialize_book(self,price,levels=5,volume=10):
        for i in range(1,levels+1):
            self.bids[price - i * self.tick_size] = volume
            self.asks[price + i * self.tick_size] = volume

    def best_bid(self):
        return max(self.bids.keys()) if self.bids else None
    def best_ask(self):
        return min(self.asks.keys()) if self.asks else None
    

    def mid_price(self):
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is not None and ask is not None:
            return (bid + ask) / 2
        return None
    
    def spread(self):
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is not None and ask is not None:
            return ask - bid
        return None
    
    def bid_depth(self):
        return self.bids[self.best_bid()]

    def relative_bid_depth(self):
        bd = self.bids[self.best_bid()]
        ad = self.asks[self.best_ask()]
        return bd / (bd + ad)

    def imbalance(self):
        bd = self.bids[self.best_bid()]
        ad = self.asks[self.best_ask()]
        return (bd - ad) / (bd + ad)

    def market_buy(self,size=None):
        size = size or self.order_size
        
        while size > 0 and self.asks:
            best_ask = self.best_ask()
            trade_vol = min(size,self.asks[best_ask])
            self.asks[best_ask] -= trade_vol
            size -= trade_vol
            if self.asks[best_ask] == 0:
                del self.asks[best_ask]
        

    def market_sell(self,size=None):
        size = size or self.order_size
        while size > 0 and self.bids:
            best_bid = self.best_bid()
            trade_vol = min(size,self.bids[best_bid])
            self.bids[best_bid] -= trade_vol
            size -= trade_vol
            if self.bids[best_bid] == 0:
                del self.bids[best_bid]

    def limit_buy(self):
        k = np.random.randint(1, 6)   # placement depth
        ref = self.best_bid() if self.best_bid() is not None else self.initial_price
        price = ref - k * self.tick_size
        self.bids[price] += self.order_size
    
    def limit_sell(self):
        k = np.random.randint(1, 6)   # placement depth
        ref = self.best_ask() if self.best_ask() is not None else self.initial_price
        price = ref + k * self.tick_size
        self.asks[price] += self.order_size

    def cancel_order(self):
        imb = self.imbalance()
        p = 0.5 + 0.5 * abs(imb)

        # Panic-biased cancellation
        if imb < 0 and self.bids and np.random.rand() < p:
            price = self.best_bid()
            self.bids[price] -= 1
            if self.bids[price] == 0:
                del self.bids[price]
            return CANCEL_BID

        elif imb > 0 and self.asks and np.random.rand() < p:
            price = self.best_ask()
            self.asks[price] -= 1
            if self.asks[price] == 0:
                del self.asks[price]
            return CANCEL_ASK

        # Neutral fallback
        elif self.bids and (not self.asks or np.random.rand() < 0.5):
            price = self.best_bid()
            self.bids[price] -= 1
            if self.bids[price] == 0:
                del self.bids[price]
            return CANCEL_BID

        elif self.asks:
            price = self.best_ask()
            self.asks[price] -= 1
            if self.asks[price] == 0:
                del self.asks[price]
            return CANCEL_ASK

        # Cancellation event occurred, but nothing to cancel
        return CANCEL_NONE


    def step(self):
        total_rate = self.lambda_market+self.lambda_limit+self.lambda_cancel
        prob_market = self.lambda_market / total_rate
        prob_limit = self.lambda_limit / total_rate
        rand = np.random.rand()
        if rand < prob_market:
            if np.random.rand() < 0.5:
                self.market_buy()
                return MARKET_BUY
            else:
                self.market_sell()
                return MARKET_SELL
        elif rand < prob_market + prob_limit:
            if np.random.rand() < 0.5:
                self.limit_buy()
                return LIMIT_BUY
            else:
                self.limit_sell()
                return LIMIT_SELL
        else:
            # Cancel order
            return self.cancel_order()
            
    
    def snapshot(self):
        return {
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "mid_price": self.mid_price(),
            "spread": self.spread(),
            "bid_depth": self.bid_depth(),
            "rel_bid_depth": self.relative_bid_depth(),
            "imbalance": self.imbalance()
        }

    def simulate(self,steps=100):
        history = []
        for i in range(steps):
            event = self.step()
            state = self.snapshot()
            state["event"] = event
            history.append(state)
        return history
    
def print_state(step, state):
    print(
        f"Step {step + 1:4d} | "
        f"Event: {state['event']} | "
        f"Bid: {state['best_bid']:>5} ({state['bid_depth']:>2}) | "
        f"Ask: {state['best_ask']:>5} | "
        f"Mid: {state['mid_price']:>6.2f} | "
        f"Spr: {state['spread']:>2} | "
        f"Imb: {state['imbalance']:>6.3f}"
    )

    
if __name__ == "__main__":
    lob = LimitOrderBookSimulator()
    history = lob.simulate(steps=50)
    for i, snapshot in enumerate(history):
        print_state(i, snapshot)
    


            
    

    





