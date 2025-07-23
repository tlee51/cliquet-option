# cliquet-option

A Cliquet option (ratchet option) is an exotic option type that locks in periodic gains while resetting its strike price at intervals. At each reset date, the gain (if any) is locked in, and the option continues from the new strike. 

Key implementations:
- Option resets at several intervals (e.g. monthly or yearly)
- At each reset, the return for that interval is calculated
- The total payout is the sum of these returns, subject to local/global caps and floors

Potential additions:
- Adjust for discrete dividends
- Use antithetic variates or control variates for variance reduction

NOTE
Monte Carlo simulation gives an estimate, though not exact unless infinitely many paths are simulated. Computing the exact expected payoff of a Cliquet option is analytically complex, as it depends on the sum of the maximums of several dependent random variables (periodic returns). One approach to attaining deterministic behavior is by using the fact that the expected return of a lognormal process over a small time interval can be derived. We can compute the expected value at each reset analytically (approximate), then sum them. 
