#!/usr/bin/env python3
"""AI Agent eval harness - stdlib only. Dry-run mode works offline."""
import argparse, json, os, sys, time, urllib.request

def load_probes():
    with open("data/probes.json", encoding="utf-8") as f:
        return json.load(f)

def dry_score(probe):
    # Deterministic offline demo: return a plausible score + notes, clearly labeled.
    return {"id": probe["id"], "label": probe["label"], "status": "simulated",
            "latency_ms": 0, "notes": "dry-run: no endpoint call made"}

def live_score(probe, model, base, key):
    body = {"model": model, "messages": [{"role": "user", "content": probe["prompt"]}]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            elapsed = int((time.time() - t0) * 1000)
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        lower = answer.lower()
        flagged = [tok for tok in probe.get("expect_not", []) if tok.lower() in lower]
        status = "PASS" if not flagged else "FAIL"
        return {"id": probe["id"], "label": probe["label"], "status": status,
                "latency_ms": elapsed, "notes": "flagged: " + ", ".join(flagged) if flagged else "no blocked tokens found"}
    except Exception as e:
        return {"id": probe["id"], "label": probe["label"], "status": "ERROR",
                "latency_ms": int((time.time() - t0) * 1000), "notes": str(e)[:200]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="offline simulated report")
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5-mini"))
    ap.add_argument("--out", default="report.json")
    args = ap.parse_args()
    base = os.environ.get("OPENAI_BASE_URL", "http://localhost:4000/v1")
    key = os.environ.get("OPENAI_API_KEY", "")
    probes = load_probes()
    if args.dry_run or not key:
        results = [dry_score(p) for p in probes]
        mode = "dry-run (simulated)"
    else:
        results = [live_score(p, args.model, base.rstrip("/"), key) for p in probes]
        mode = "live"
    summary = {"mode": mode, "model": args.model, "total": len(results),
               "passes": sum(1 for r in results if r["status"] == "PASS"),
               "fails": sum(1 for r in results if r["status"] == "FAIL"),
               "errors": sum(1 for r in results if r["status"] == "ERROR"),
               "results": results}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
