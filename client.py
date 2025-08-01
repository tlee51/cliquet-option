# client.py
import requests

def main():
    print("== Cliquet Option Pricing ==")

    # Prompt user for key inputs
    S0 = float(input("Enter current price (S0): "))
    sigma = float(input("Enter volatility (sigma): "))

    # Hardcoded params (optional: prompt for more)
    r = 0.03
    T = 1.0
    n_resets = 12
    local_cap = 5.0
    global_cap = 30.0

    # Construct request to localhost API
    params = {
        "S0": S0,
        "r": r,
        "sigma": sigma,
        "T": T,
        "n_resets": n_resets,
        "local_cap": local_cap,
        "global_cap": global_cap
    }

    try:
        res = requests.get("http://127.0.0.1:8000/price", params=params)
        res.raise_for_status()
        data = res.json()

        print("\n== Option Price ==")
        print(f"Estimated Price: ${data['estimated_price']:.4f}")
        print("Inputs Used:")
        for k, v in data["inputs_used"].items():
            print(f"  {k}: {v}")

    except requests.exceptions.RequestException as e:
        print(f"Error contacting pricing API: {e}")

if __name__ == "__main__":
    main()
