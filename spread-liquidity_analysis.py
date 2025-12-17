import pandas as pd
from lob_engine import LimitOrderBookSimulator

LAMBDA_LIMIT_VALS = [x for x in range(1, 13)]
STEPS = int(1e5)
results = []

for lam in LAMBDA_LIMIT_VALS:
    lob = LimitOrderBookSimulator(lambda_market=4.0,lambda_limit=lam,lambda_cancel=3.0)
    history = lob.simulate(steps=STEPS)
    df = pd.DataFrame(history)

    avg_spread = df["spread"].dropna().mean()
    std_spread = df["spread"].std()

    results.append({
        "lambda_limit": lam,
        "avg_spread": avg_spread,
        "std_spread": std_spread
    })

results_df = pd.DataFrame(results)
results_df.to_csv(
"spread_vs_lambda_limit.csv",
index=False
)
print(results_df)

import matplotlib.pyplot as plt

df = results_df

plt.figure(figsize=(7, 4))
plt.plot(df["lambda_limit"], df["avg_spread"], marker="o")
plt.xlabel(r"$\lambda_{\text{limit}}$")
plt.ylabel("Average Spread")
plt.title("Spread vs Limit Order Arrival Rate")
plt.grid(True)
plt.tight_layout()
plt.show()

