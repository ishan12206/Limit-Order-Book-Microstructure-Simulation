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
    def __init__(self,initial_price=100,tick_size=1,lambda_market = 4.0,lambda_limit = 1.0,lambda_cancel = 3.0,order_size = 1):
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
        if not self.bids:
            return None
        return max(p for p in self.bids if p is not None)

    def best_ask(self):
        if not self.asks:
            return None
        return min(p for p in self.asks if p is not None)

    

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
        if self.best_bid() is None:
            return 0
        return self.bids[self.best_bid()]

    def relative_bid_depth(self):
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return None
        bd = self.bids[bid]
        ad = self.asks[ask]
        if bd + ad == 0:
            return None
        return bd / (bd + ad)

    def imbalance(self):
        bid = self.best_bid()
        ask = self.best_ask()
        if bid is None or ask is None:
            return 0.0
        
        bd = self.bids[bid]
        ad = self.asks[ask]

        if bd+ad == 0:
            return 0.0
        
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
        ref = self.best_bid() if self.best_bid() is not None else self.initial_price
        spread = self.spread() if self.spread() is not None else 0
        p_inside = min(0.95, 0.3 + 0.1 * spread)
        if np.random.rand() < p_inside:  # 30%-95% at best bid
            price = ref
        else:
            k = np.random.randint(1, 6)
            price = ref - k * self.tick_size

        self.bids[price] += self.order_size


    def limit_sell(self):
        ref = self.best_ask() if self.best_ask() is not None else self.initial_price
        spread = self.spread() if self.spread() is not None else 0
        p_inside = min(0.95, 0.3 + 0.1 * spread)
        if np.random.rand() < p_inside:  # 30%-95% at best ask
            price = ref
        else:
            k = np.random.randint(1, 6)
            price = ref + k * self.tick_size

        self.asks[price] += self.order_size


    def cancel_order(self):
        imb = self.imbalance()
        panic_prob = 0.5 + 0.5 * abs(imb)

        # Panic-biased cancellation
        if imb > 0 and self.asks and np.random.rand() < panic_prob:
            price = self.best_ask()
            if price is not None:
                self.asks[price] -= 1
                if self.asks[price] <= 0:
                    del self.asks[price]
                return CANCEL_ASK

        if imb < 0 and self.bids and np.random.rand() < panic_prob:
            price = self.best_bid()
            if price is not None:
                self.bids[price] -= 1
                if self.bids[price] <= 0:
                    del self.bids[price]
                return CANCEL_BID

        # Neutral fallback
        if self.bids and (not self.asks or np.random.rand() < 0.5):
            price = self.best_bid()
            if price is not None:
                self.bids[price] -= 1
                if self.bids[price] <= 0:
                    del self.bids[price]
                return CANCEL_BID

        if self.asks:
            price = self.best_ask()
            if price is not None:
                self.asks[price] -= 1
                if self.asks[price] <= 0:
                    del self.asks[price]
                return CANCEL_ASK

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
    



            
    

    





