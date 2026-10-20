"""Builds data/content.json: original quote of the day and humor strings.

Run:  python tools/build_content.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_src import HUMOR, QUOTES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ["earth", "water", "fire", "air"]
TONE_OVERRIDES = {163: "funny", 164: "wise"}  # finish the arc on a wise note; totals stay 82/82


def main():
    schedule = json.load(open(os.path.join(ROOT, "data", "schedule.json"), encoding="utf-8"))["days"]

    quotes, daily = [], []
    used = {(el, t): 0 for el in ORDER for t in ("wise", "funny")}
    for day in schedule:
        el, cyc, n = day["element"], day["cycle"], day["day"]
        idx = ORDER.index(el)
        tone = TONE_OVERRIDES.get(n, "wise" if (cyc + idx) % 2 == 1 else "funny")
        pool = QUOTES[el][tone]
        k = used[(el, tone)]
        assert k < len(pool), f"ran out of {el}/{tone} quotes on day {n}"
        used[(el, tone)] = k + 1
        who, text = pool[k]
        quotes.append(dict(id=len(quotes), character=who, text=text, tone=tone, element=el))
        daily.append(dict(day=n, quote=len(quotes) - 1))
    for (el, tone), k in used.items():
        assert k == len(QUOTES[el][tone]), f"{el}/{tone}: wrote {len(QUOTES[el][tone])} quotes but used {k}"
    tones = [q["tone"] for q in quotes]
    out = dict(quotes=quotes, daily=daily, humor=HUMOR,
               notes=dict(quotes="Original lines written in the voice of Avatar: The Last Airbender characters. Fan homage, not affiliated."))
    with open(os.path.join(ROOT, "data", "content.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"quotes={len(quotes)} wise={tones.count('wise')} funny={tones.count('funny')} days={len(daily)}")


if __name__ == "__main__":
    main()
