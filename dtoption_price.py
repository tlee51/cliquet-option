import numpy as np
from scipy.stats import norm

def cliquet_deterministic_value(S0, r, sigma, T, n_resets, global_cap=None):
    dt = T / n_resets
    mu = (r - 0.5 * sigma**2) * dt
    std = sigma * np.sqrt(dt)

    # Expected value of max(exp(X) - 1, 0), X ~ N(mu, std^2)
    d1 = -mu / std
    expected_return_per_period = norm.cdf(-d1) * (np.exp(mu + 0.5 * std**2) - 1)

    total_return = expected_return_per_period * n_resets

    if global_cap is not None:
        total_return = min(total_return, global_cap)

    discounted_return = np.exp(-r * T) * total_return
    return discounted_return


# Example usage
if __name__ == "__main__":
    value = cliquet_deterministic_value(
        S0=100,
        r=0.03,
        sigma=0.2,
        T=1.0,
        n_resets=12,
        global_cap=0.5
    )

    print(f"Deterministic Cliquet Option Price: {value:.4f}")
