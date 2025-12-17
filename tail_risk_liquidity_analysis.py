import numpy as np
import matplotlib.pyplot as plt

from lob_engine import LimitOrderBookSimulator


def compute_tail_probability(history, threshold):
    spreads = np.array(
        [h["spread"] for h in history if h["spread"] is not None]
    )
    return np.mean(spreads > threshold)


def monte_carlo_tail_prob(
    lambda_limit,
    threshold,
    runs=100,
    steps=500,
    lambda_market=4.0,
    lambda_cancel=3.0,
):
    probs = []

    for _ in range(runs):
        lob = LimitOrderBookSimulator(
            lambda_market=lambda_market,
            lambda_limit=lambda_limit,
            lambda_cancel=lambda_cancel,
        )
        history = lob.simulate(steps)
        probs.append(compute_tail_probability(history, threshold))

    return np.mean(probs), np.std(probs)


def run_tail_risk_experiment():
    lambda_vals = range(1, 13)
    thresholds = [5, 10, 20]

    results = {k: [] for k in thresholds}

    for k in thresholds:
        for lam in lambda_vals:
            mean_p, _ = monte_carlo_tail_prob(lam, k)
            results[k].append(mean_p)

    # Plot
    plt.figure(figsize=(7, 4))
    for k in thresholds:
        plt.plot(
            lambda_vals,
            results[k],
            marker="o",
            label=f"P(spread > {k})",
        )

    plt.xlabel(r"$\lambda_{\mathrm{limit}}$")
    plt.ylabel("Tail Probability")
    plt.title("Tail Risk of Spread vs Limit Order Intensity")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_tail_risk_experiment()

