"""Check every example in this repo against the live Rodz OpenAPI spec.

    python scripts/validate_against_spec.py            # fetches https://api.rodz.io/openapi.json
    python scripts/validate_against_spec.py spec.json  # or a local copy

It checks that:
  * each request body in signals/*.json only uses fields the create endpoint accepts,
    with the right types and allowed values;
  * every API path called by the curl, Python and JavaScript examples exists in the spec
    with that HTTP method;
  * every query parameter the examples send is declared on its endpoint.

No API key needed, nothing is created, no credits are spent.
"""

import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC_URL = "https://api.rodz.io/openapi.json"

# signals/<file>.json -> the endpoint that creates it
SIGNAL_BODIES = {
    "job-changes.json": "/api/v1/signals/job-changes",
    "fundraising.json": "/api/v1/signals/fundraising",
    "job-offers.json": "/api/v1/signals/job-offers",
    "competitor-connections.json": "/api/v1/signals/competitor-connections",
}


def load_spec():
    if len(sys.argv) > 1:
        return json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    with urllib.request.urlopen(SPEC_URL, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


class Checker:
    def __init__(self, spec):
        self.spec = spec
        self.schemas = spec.get("components", {}).get("schemas", {})
        self.errors = []

    def resolve(self, s):
        while isinstance(s, dict) and "$ref" in s:
            s = self.schemas[s["$ref"].split("/")[-1]]
        return s

    def _type_ok(self, value, t):
        return {
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
            "null": value is None,
        }.get(t, True)

    def problems(self, value, schema, where):
        """Return a list of problems (empty = valid)."""
        s = self.resolve(schema)
        if not isinstance(s, dict) or not s:
            return []
        for key in ("anyOf", "oneOf"):
            if key in s:
                options = [self.problems(value, o, where) for o in s[key]]
                if any(not p for p in options):
                    return []
                return min(options, key=len)
        if "allOf" in s:
            return [p for o in s["allOf"] for p in self.problems(value, o, where)]
        out = []
        t = s.get("type")
        if t and not self._type_ok(value, t):
            return [f"{where}: expected {t}, got {type(value).__name__}"]
        if "enum" in s and value not in s["enum"]:
            out.append(f"{where}: {value!r} is not one of {s['enum']}")
        if "pattern" in s and isinstance(value, str) and not re.search(s["pattern"], value):
            out.append(f"{where}: {value!r} does not match {s['pattern']}")
        if isinstance(value, list) and "items" in s:
            for i, v in enumerate(value):
                out += self.problems(v, s["items"], f"{where}[{i}]")
        if isinstance(value, dict) and "properties" in s:
            props = s["properties"]
            for req in s.get("required", []):
                if req not in value:
                    out.append(f"{where}: missing required field {req!r}")
            for k, v in value.items():
                if k not in props:
                    out.append(f"{where}: unknown field {k!r}")
                else:
                    out += self.problems(v, props[k], f"{where}.{k}")
                    out += self.documented_values(v, props[k], f"{where}.{k}")
        return out

    def documented_values(self, value, schema, where):
        """Many fields list their allowed values in the description ('Valid values: "a", "b"')."""
        desc = self.resolve(schema).get("description", "")
        m = re.search(r'(?:Valid values|Values|How recent):\s*((?:"[^"]+"(?:,\s*)?)+)', desc)
        if not m:
            return []
        allowed = set(re.findall(r'"([^"]+)"', m.group(1)))
        values = value if isinstance(value, list) else [value]
        return [f"{where}: {v!r} is not a documented value" for v in values if isinstance(v, str) and v not in allowed]

    def check_bodies(self):
        for fname, path in SIGNAL_BODIES.items():
            body = json.loads((ROOT / "signals" / fname).read_text(encoding="utf-8"))
            op = self.spec["paths"].get(path, {}).get("post")
            if not op:
                self.errors.append(f"{fname}: POST {path} not in the spec")
                continue
            schema = op["requestBody"]["content"]["application/json"]["schema"]
            probs = self.problems(body, schema, fname)
            self.errors += probs
            print(f"  {'OK ' if not probs else 'BAD'} signals/{fname} -> POST {path}")

    def check_calls(self):
        files = [p for d in ("curl", "python", "javascript") for p in (ROOT / d).glob("*") if p.is_file()]
        # matches `-X POST "$RODZ_BASE_URL/api/v1/..."`, `rodz("GET", "/api/v1/..."`, `rodz('GET', `/api/v1/...``
        call_re = re.compile(r"(GET|POST|PATCH|DELETE)[^\n/]{0,40}?(/api/v1/[A-Za-z0-9_\-/{}$]+)(\?[^\s\"'`]*)?")
        # query parameters passed as a dict: Python `params={...}`, JavaScript `query: {...}`
        dict_re = re.compile(r"^[^\n]{0,20}?(?:params=|query:\s*)\{(.*?)\}", re.S)
        seen = set()
        for f in files:
            text = f.read_text(encoding="utf-8")
            for m in call_re.finditer(text):
                method, path, query = m.group(1).lower(), m.group(2), m.group(3) or ""
                key = (f.relative_to(ROOT).as_posix(), method, path, query)
                if key in seen:
                    continue
                seen.add(key)
                spec_path = self.match_path(path)
                op = self.spec["paths"].get(spec_path, {}).get(method) if spec_path else None
                if not op:
                    self.errors.append(f"{key[0]}: {method.upper()} {path} not in the spec")
                    print(f"  BAD {key[0]}: {method.upper()} {path}")
                    continue
                declared = {p["name"] for p in op.get("parameters", []) if p.get("in") == "query"}
                names = re.findall(r"[?&]([A-Za-z_]+)=", query)
                d = dict_re.match(text[m.end() : m.end() + 400].lstrip("\"'`,) \n"))
                if d:
                    for part in d.group(1).split(","):  # `"name": value` or JS shorthand `name`
                        k = re.match(r"\s*[\"']?([A-Za-z_]+)", part)
                        if k:
                            names.append(k.group(1))
                    query = query or "?" + "&".join(f"{n}=" for n in names)
                if f.suffix == ".sh":  # curl -G --data-urlencode "name=value"
                    names += re.findall(r"--data-urlencode \"([A-Za-z_]+)=", text)
                for name in names:
                    if name not in declared:
                        self.errors.append(f"{key[0]}: query parameter {name!r} not declared on {path}")
                print(f"  OK  {key[0]}: {method.upper()} {path}{query}")

    def match_path(self, path):
        if path in self.spec["paths"]:
            return path
        parts = path.strip("/").split("/")
        for candidate in self.spec["paths"]:
            cparts = candidate.strip("/").split("/")
            if len(cparts) == len(parts) and all(
                c == p or (c.startswith("{") and (p.startswith("{") or p.startswith("$") or p.startswith(":")))
                for c, p in zip(cparts, parts)
            ):
                return candidate
        return None


def main():
    spec = load_spec()
    print(f"Spec: {spec['info']['title']} ({spec['info'].get('version', '?')[:12]})")
    c = Checker(spec)
    print("Request bodies:")
    c.check_bodies()
    print("Endpoints called by the examples:")
    c.check_calls()
    if c.errors:
        print("\nFAILED:")
        for e in c.errors:
            print("  -", e)
        sys.exit(1)
    print("\nAll examples match the spec.")


if __name__ == "__main__":
    main()
