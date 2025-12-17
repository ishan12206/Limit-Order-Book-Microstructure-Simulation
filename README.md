# Limit Order Book Microstructure Simulator  
**Quantitative Market Microstructure Project**

---

## Project Motivation

This project implements a **stochastic limit order book (LOB) simulator** to study how liquidity provision, order cancellation, and market order flow jointly determine **market stability, tail risk, and resilience**.

Rather than focusing on price prediction, the simulator is designed to:
- isolate **mechanistic microstructure effects**
- analyze **nonlinear liquidity regimes**
- quantify **liquidity stress and recovery dynamics**

The project emphasizes **interpretability, controlled experimentation, and regime analysis**, consistent with quantitative research workflows.

---

## Model Description

### Event-Driven Order Book

The simulator models a single-instrument LOB with three stochastic event types:

- **Limit Orders**
  - Buy and sell limit orders arrive at random depths relative to the current best bid/ask  
  - Placement depth is discrete and configurable  
  - Orders contribute volume at multiple price levels  

- **Market Orders**
  - Market buys consume best ask liquidity  
  - Market sells consume best bid liquidity  

- **Order Cancellations**
  - Inside orders may be canceled  
  - Cancellation probability increases with order book imbalance (state-dependent panic)

At each step, an event is sampled based on user-specified intensities:

$$\
(\lambda_{\text{market}},\ \lambda_{\text{limit}},\ \lambda_{\text{cancel}})
\$$

---

### State Variables Tracked

At every step, the simulator records:

- best bid and best ask  
- mid-price  
- bid–ask spread  
- volume at the best bid  
- order book imbalance  

These variables are sufficient to characterize **liquidity conditions and stress propagation**.

---

## Experiments and Results

### 1. Spread vs Limit Order Intensity

**Objective**  
Measure how increased liquidity provision affects typical trading costs.

**Result**  
Average spreads decrease with higher limit order intensity, but averages alone are misleading due to rare liquidity vacuums.

This motivates tail-based analysis.

---

### 2. Tail Risk of Liquidity Vacuums

**Objective**  
Quantify the probability of extreme liquidity breakdowns.

**Method**  
For each limit order intensity  $\lambda_{\text{limit}} \$, estimate:

- $\ P(\text{spread} > 5) \$  
- $\ P(\text{spread} > 10) \$  
- $\ P(\text{spread} > 20) \$ 

**Result**  
Tail risk exhibits a **non-monotonic dependence** on liquidity provision:
- Moderate limit flow increases instability due to churn and cancellations  
- High limit flow suppresses tail risk by rapidly refilling the inside  

This reveals a **critical liquidity regime** where markets are most fragile.

---

### 3. Liquidity Recovery Time (Market Resilience)

**Objective**  
Measure how quickly the market recovers after a liquidity shock.

**Definitions**
- **Shock:** spread > 15 
- **Recovery:** spread ≤ 5  
- **Recovery time:** number of steps between shock and recovery  

**Result**  
Recovery times peak sharply at intermediate limit order intensities, indicating **critical slowing down**:
- Liquidity replenishment and withdrawal compete  
- The book remains in stressed states for extended periods  

At high limit order intensity, shocks are rare and recovery is rapid, indicating a resilient regime.

---

## Key Takeaways

- Liquidity provision has **nonlinear effects** on market stability  
- Intermediate liquidity can be more destabilizing than low liquidity  
- Tail probabilities and recovery times outperform averages as risk metrics  
- High limit order flow stabilizes markets by overwhelming panic-driven cancellation  

These findings are consistent with empirical market microstructure theory.

---


