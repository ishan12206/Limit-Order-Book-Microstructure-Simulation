import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from lob_engine import LimitOrderBookSimulator
LOW_SPREAD = 5
HIGH_SPREAD = 15

STEPS = 2000
RUNS = 300

LAMBDA_MARKET = 4.0
LAMBDA_CANCEL = 3.0

def extract_spreads(history):
    return np.array([h["spread"] for h in history if h["spread"] is not None])

def compute_recovery_times(spreads, high=HIGH_SPREAD, low=LOW_SPREAD):
    recovery_times = []
    n = len(spreads)
    i = 0
    while i < n:
        if spreads[i] > high:
            j = i + 1
            while j < n and spreads[j] > low:
                j += 1
            recovery_times.append(j - i)
            i = j
        else:
            i += 1
    return recovery_times


def run_recovery_time_experiment():
    lambda_limit_vals = range(1, 13)
    results = []

    for lam in lambda_limit_vals:
        all_recovery_times = []
        for _ in range(RUNS):
            lob = LimitOrderBookSimulator(
                lambda_market=LAMBDA_MARKET,
                lambda_limit=lam,
                lambda_cancel=LAMBDA_CANCEL,
            )
            history = lob.simulate(steps=STEPS)
            spreads = extract_spreads(history)
            recovery_times = compute_recovery_times(spreads)
            all_recovery_times.extend(recovery_times)

        if all_recovery_times:
            avg_recovery = np.mean(all_recovery_times)
            std_recovery = np.std(all_recovery_times)
        else:
            avg_recovery = np.nan
            std_recovery = np.nan

        results.append({
            "lambda_limit": lam,
            "avg_recovery_time": avg_recovery,
            "std_recovery_time": std_recovery
        })

    results_df = pd.DataFrame(results)
    print(results_df)

    # Plotting
    plt.figure(figsize=(7, 4))
    plt.plot(results_df["lambda_limit"], results_df["avg_recovery_time"], marker="o")
    plt.xlabel(r"$\lambda_{\text{limit}}$")
    plt.ylabel("Average Recovery Time")
    plt.title("Recovery Time vs Limit Order Arrival Rate")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_recovery_time_experiment()