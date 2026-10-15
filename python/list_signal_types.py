"""The signal catalog: what you can detect, where to create it, and what it costs. Free.

    python list_signal_types.py
"""

from rodz import rodz

catalog = rodz("GET", "/api/v1/signal-types")
for t in catalog["signalTypes"]:
    price = t.get("pricingModel") or {}
    print(f"{t['signalTypeId']:<40} {price.get('baseCredits', '?'):>4} credits/{price.get('unit', 'lead')}")
    print(f"    POST {t['createEndpoint']}  -  {t['name']}")
