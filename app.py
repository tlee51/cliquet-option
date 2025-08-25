# app.py
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from flask import Flask, jsonify, request, abort
# from pricing import simulate_cliquet_option_price
from Pricer.pricing import simulate_cliquet_option_price
import secrets
import string


app = Flask(__name__)

# ---- Domain model ----------------------------------------------------------

@dataclass
class Trade:
    trade_id: str
    ticker: str
    S0: float                 # stored "current" price (you can override per request)
    sigma: float              # stored vol (you can override per request)
    r: float                  # risk-free rate
    T: float                  # maturity in years
    n_resets: int             # number of reset periods
    n_paths: int = 50_000     # MC paths (override if you like)
    local_floor: float = 0.0
    local_cap: Optional[float] = None
    global_floor: float = 0.0
    global_cap: Optional[float] = None

    def price(self, S0_override: Optional[float] = None,
                    sigma_override: Optional[float] = None) -> float:
        S0_use = S0_override if S0_override is not None else self.S0
        sigma_use = sigma_override if sigma_override is not None else self.sigma

        return simulate_cliquet_option_price(
            S0=S0_use,
            r=self.r,
            sigma=sigma_use,
            T=self.T,
            n_resets=self.n_resets,
            n_paths=self.n_paths,
            local_floor=self.local_floor,
            local_cap=self.local_cap,
            global_floor=self.global_floor,
            global_cap=self.global_cap
        )

# ---- In-memory "store" -----------------------------------------------------

def generate_trade_id(length=12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# trade_id = generate_trade_id()
# TRADES: Dict[str, Trade] = {
#     "T1": Trade(
#         trade_id=generate_trade_id(),
#         ticker="XYZ",
#         S0=100.0,
#         sigma=0.2,
#         r=0.03,
#         T=1.0,
#         n_resets=12,
#         n_paths=100_000,
#         local_floor=0.0,
#         local_cap=5.0,
#         global_floor=0.0,
#         global_cap=30.0
#     )
# }

trade_id = generate_trade_id()
TRADES = {
    trade_id: Trade(
        trade_id=trade_id,
        ticker="XYZ",
        S0=100.0,
        sigma=0.2,
        r=0.03,
        T=1.0,
        n_resets=12,
        n_paths=100_000
    )
}


# ---- Helpers ---------------------------------------------------------------

def parse_float(q: Dict[str, Any], key: str) -> Optional[float]:
    val = q.get(key)
    if val is None:
        return None
    try:
        return float(val)
    except ValueError:
        abort(400, f"Query parameter '{key}' must be a float")

def _get_float(argname, required=True):
    v = request.args.get(argname)
    if v is None:
        if required:
            abort(400, f"Missing required query param '{argname}'")
        return None
    try:
        return float(v)
    except ValueError:
        abort(400, f"Query param '{argname}' must be a number")



# ---- Routes ----------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", time=datetime.now(timezone.utc).isoformat())

@app.route("/trades", methods=["GET"])
def list_trades():
    return jsonify([asdict(t) for t in TRADES.values()])

@app.route("/trades/<trade_id>/price", methods=["GET"])
def price_trade(trade_id: str):
    trade = TRADES.get(trade_id)
    if trade is None:
        abort(404, f"Trade '{trade_id}' not found")

    # Allow overrides through query params (because Current Price & Volatility change often)
    S0_override = parse_float(request.args, "S0")
    sigma_override = parse_float(request.args, "sigma")

    px = trade.price(S0_override=S0_override, sigma_override=sigma_override)
    return jsonify({
        "trade_id": trade_id,
        "ticker": trade.ticker,
        "estimated_price": px,
        "inputs_used": {
            "S0": S0_override if S0_override is not None else trade.S0,
            "sigma": sigma_override if sigma_override is not None else trade.sigma,
            "r": trade.r,
            "T": trade.T,
            "n_resets": trade.n_resets,
            "n_paths": trade.n_paths,
            "local_floor": trade.local_floor,
            "local_cap": trade.local_cap,
            "global_floor": trade.global_floor,
            "global_cap": trade.global_cap
        },
        "as_of": datetime.now(timezone.utc).isoformat()
    })

@app.route("/price", methods=["GET"])
def ad_hoc_price():
    """
    Direct pricing endpoint; everything passed as query params.
    Example:
    /price?S0=100&r=0.03&sigma=0.2&T=1&n_resets=12&n_paths=50000&global_cap=30&local_cap=5
    """
    required = ["S0", "r", "sigma", "T", "n_resets"]
    missing = [k for k in required if k not in request.args]
    if missing:
        abort(400, f"Missing required query params: {', '.join(missing)}")

    S0 = float(request.args["S0"])
    r = float(request.args["r"])
    sigma = float(request.args["sigma"])
    T = float(request.args["T"])
    n_resets = int(request.args["n_resets"])

    n_paths = int(request.args.get("n_paths", 50_000))

    local_floor = parse_float(request.args, "local_floor") or 0.0
    local_cap = parse_float(request.args, "local_cap")
    global_floor = parse_float(request.args, "global_floor") or 0.0
    global_cap = parse_float(request.args, "global_cap")

    px = simulate_cliquet_option_price(
        S0=S0, r=r, sigma=sigma, T=T, n_resets=n_resets, n_paths=n_paths,
        local_floor=local_floor, local_cap=local_cap,
        global_floor=global_floor, global_cap=global_cap
    )

    return jsonify({
        "estimated_price": px,
        "inputs_used": {
            "S0": S0, "r": r, "sigma": sigma, "T": T,
            "n_resets": n_resets, "n_paths": n_paths,
            "local_floor": local_floor, "local_cap": local_cap,
            "global_floor": global_floor, "global_cap": global_cap
        },
        "as_of": datetime.now(timezone.utc).isoformat()
    })

@app.route("/tradeprice", methods=["GET"])
def price_trade_minimal():
    """
    Minimal pricing endpoint:
    /tradeprice?trade_id=T1&S0=100&sigma=0.2&r=0.03&T=1
    Uses trade's stored n_resets/n_paths if available; no local/global caps.
    Returns: { "trade_id": "...", "price": 19.59 }
    """
    trade_id = request.args.get("trade_id")
    if not trade_id:
        abort(400, "Missing required query param 'trade_id'")

    S0 = _get_float("S0")
    sigma = _get_float("sigma")
    r = _get_float("r")
    T = _get_float("T")

    # pull n_resets/n_paths from stored trade if present; otherwise defaults
    trade = TRADES.get(trade_id)
    n_resets = trade.n_resets if trade else 12
    n_paths  = trade.n_paths  if trade else 50_000

    px = simulate_cliquet_option_price(
        S0=S0, r=r, sigma=sigma, T=T,
        n_resets=n_resets, n_paths=n_paths,
        local_floor=0.0, local_cap=None,
        global_floor=0.0, global_cap=None
    )

    return jsonify({
        "trade_id": trade_id,
        "price": round(px, 2)  # two decimals
    })

# ---- Entrypoint ------------------------------------------------------------

if __name__ == "__main__":
    # For dev only. For prod, run with gunicorn/uwsgi.
    app.run(host="0.0.0.0", port=8000, debug=True)
