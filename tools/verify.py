"""Sanity checks for the generated data. Run: python tools/verify.py"""
import json
import os
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load = lambda p: json.load(open(os.path.join(ROOT, "data", p), encoding="utf-8"))
sched, exs, content, credits = load("schedule.json"), load("exercises.json"), load("content.json"), load("image-credits.json")
days, ex = sched["days"], {e["id"]: e for e in exs["exercises"]}
errors = []
check = lambda ok, msg: ok or errors.append(msg)

check(len(days) == 164, f"expected 164 days, got {len(days)}")
start = date(2026, 10, 19)
order = ["earth", "water", "fire", "air"]
for i, d in enumerate(days):
    check(d["date"] == (start + timedelta(days=i)).isoformat(), f"day {i + 1} date {d['date']}")
    check(d["element"] == order[i % 4], f"day {i + 1} out of 4-day order")
    check(d["location"] in ("Gym", "Sand", "Gym + Sand"), f"day {i + 1} location {d['location']}")
    check(60 <= d["minutes"] <= 90, f"day {i + 1} minutes {d['minutes']}")
    for b in d["blocks"]:
        for it in b["items"]:
            check(it["id"] in ex, f"day {i + 1}: unknown exercise {it['id']}")
            check(bool(it.get("cue")), f"day {i + 1}: {it['id']} missing cue")
check(days[0]["date"] == "2026-10-19" and days[-1]["date"] == "2027-03-31", "date range")
for el in order:
    fmts = [d["format"] for d in days if d["element"] == el]
    check(all(a != b for a, b in zip(fmts, fmts[1:])), f"{el}: same format on back-to-back cycles")
for e in ex.values():
    for k in ("image", "imageAlt", "thumb"):
        if e.get(k):
            check(os.path.exists(os.path.join(ROOT, e[k])), f"missing file {e[k]}")
cids = {c["id"] for c in credits["images"]}
check(cids == set(ex), "image-credits.json does not match the exercise library")
check(len(content["daily"]) == 164, "daily count")
tones = [q["tone"] for q in content["quotes"]]
check(tones.count("wise") == 82 and tones.count("funny") == 82, "quote tone split")
if errors:
    print("FAILED:\n  " + "\n  ".join(errors[:40]))
    raise SystemExit(1)
print(f"OK: 164 days {days[0]['date']} → {days[-1]['date']}, 4-day order, labels, 60–90 min, "
      f"{len(ex)} exercises all present with images, credits complete, 164 daily quotes 82/82.")
