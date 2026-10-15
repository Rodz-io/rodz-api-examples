"""Enrich a person or a company.

    python enrich.py contact https://www.linkedin.com/in/some-profile   # 0.25 credits (cached)
    python enrich.py email Marie Dupont doctolib.fr                     # find a professional email
    python enrich.py company doctolib.fr                                # size, industry, HQ...
"""

import json
import sys

from rodz import rodz

if len(sys.argv) < 3:
    sys.exit(__doc__)
kind = sys.argv[1]

if kind == "contact":
    # freshness=cached: 0.25 credits, profile at most 8 days old, ~1 s.
    # freshness=live (default): 0.5 credits, fetched at request time.
    result = rodz("GET", "/api/v1/enrichment/contact", params={"url": sys.argv[2], "freshness": "cached"})
    person = result["data"]["person"]
    print(f"{person['name']} - {person['headline']} - {person['location']}")
elif kind == "email":
    first, last, domain = sys.argv[2:5]
    result = rodz("GET", "/api/v1/enrichment/find-email", params={"firstName": first, "lastName": last, "domain": domain})
    print(json.dumps(result["data"], indent=2))
elif kind == "company":
    result = rodz("GET", "/api/v1/enrichment/firmographic", params={"domain": sys.argv[2]})
    f = result["data"]["company"]["firmographics"]
    print(f"{f['name']} - {f['companySize']} employees - {f['industries']} - {f['HQcity']}, {f['HQcountry']}")
else:
    sys.exit(__doc__)
