import numpy as np

def simulate_cliquet_option_price(
    S0, r, sigma, T, n_resets, n_paths, global_cap=None
):
    """
    Price a Cliquet option using Monte Carlo simulation.

    Parameters:
    - S0: initial stock price
    - r: risk-free rate
    - sigma: volatility
    - T: total maturity in years
    - n_resets: number of reset periods
    - n_paths: number of Monte Carlo simulations
    - global_cap: maximum payout (e.g., 0.5 = 50%)

    Returns:
    - estimated option price
    """

    dt = T / n_resets
    total_returns = []

    for _ in range(n_paths):
        S = S0
        payoff = 0.0

        for _ in range(n_resets):
            # Simulate return over one reset period
            z = np.random.normal()
            S_new = S * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

            local_return = max((S_new - S) / S, 0.0)  # local payoff (no floor, no cap)
            payoff += local_return
            S = S_new

        if global_cap is not None:
            payoff = min(payoff, global_cap)

        total_returns.append(payoff)

    discounted_payoff = np.exp(-r * T) * np.mean(total_returns)
    return discounted_payoff


# Example usage
if __name__ == "__main__":
    price = simulate_cliquet_option_price(
        S0=100,        # initial price
        r=0.03,        # risk-free rate
        sigma=0.2,     # volatility
        T=1.0,         # maturity (1 year)
        n_resets=12,   # monthly resets
        n_paths=10000, # number of simulations
        global_cap=0.5 # max payout is 50%
    )

    print(f"Estimated Cliquet Option Price: {price:.4f}")
