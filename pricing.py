import numpy as np

def simulate_cliquet_option_price(
    S0, r, sigma, T, n_resets, n_paths,
    local_floor=0.0, local_cap=None,
    global_floor=0.0, global_cap=None
):
    """
    Price a Cliquet option using Monte Carlo simulation with local and global caps/floors.

    Parameters:
    - S0: initial stock price
    - r: risk-free rate (annualized)
    - sigma: volatility (annualized)
    - T: total maturity in years
    - n_resets: number of reset periods
    - n_paths: number of Monte Carlo simulations
    - local_floor: minimum payoff per reset period (absolute $)
    - local_cap: maximum payoff per reset period (absolute $)
    - global_floor: minimum total payoff (absolute $)
    - global_cap: maximum total payoff (absolute $)

    Returns:
    - estimated option price
    """

    dt = T / n_resets
    total_payoffs = []

    for _ in range(n_paths):
        S = S0
        payoff = 0.0  # in dollars

        for _ in range(n_resets):
            # Simulate price movement over one reset period
            z = np.random.normal()
            S_new = S * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)

            # Absolute gain for this reset
            local_gain = max(S_new - S, 0.0)

            # Apply local floor and cap
            if local_cap is not None:
                local_gain = min(local_gain, local_cap)
            local_gain = max(local_gain, local_floor)

            payoff += local_gain
            S = S_new  # reset the strike for the next period

        # Apply global floor and cap
        if global_cap is not None:
            payoff = min(payoff, global_cap)
        payoff = max(payoff, global_floor)

        total_payoffs.append(payoff)

    discounted_payoff = np.exp(-r * T) * np.mean(total_payoffs)
    return discounted_payoff


# Example usage
if __name__ == "__main__":
    price = simulate_cliquet_option_price(
        S0=100,        # initial price
        r=0.03,        # risk-free rate
        sigma=0.2,     # volatility
        T=1.0,         # maturity (1 year)
        n_resets=12,   # monthly resets
        n_paths=100000, # number of simulations
        local_floor=0.0,   # no negative payoff
        local_cap=5.0,     # max $5 per reset
        global_floor=0.0,  # no negative payoff
        global_cap=30.0    # max total $30 payoff
    )

    print(f"Estimated Cliquet Option Price: {price:.4f}")
