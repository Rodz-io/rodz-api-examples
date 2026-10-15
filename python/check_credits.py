"""How many credits are left on the account. Free.

    python check_credits.py
"""

from rodz import rodz

balance = rodz("GET", "/api/v1/account/credits")
print(f"{balance['credits']} credits left ({balance.get('companyName') or 'your account'})")

# Where the credits went over the last 7 days, by endpoint.
usage = rodz("GET", "/api/v1/account/credits/usage", params={"interval": "day"})
print(f"Last 7 days: {usage['totalCredits']} credits over {usage['totalCalls']} calls")
for row in usage["byEndpoint"]:
    print(f"  {row['endpoint']:<40} {row['credits']:>10} credits  {row['calls']:>6} calls")
