"""Generates data/schedule.json (164 unique days) and data/exercises.json (only used exercises).

Run:  python tools/build_data.py
"""
import json
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from library import EX  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = date(2026, 10, 19), date(2027, 3, 31)

PHASES = [
    dict(id="foundation", name="Foundation", numeral="I", start="2026-10-19", end="2026-11-30",
         focus="Technique, volume & mobility", blurb="Build the roots: perfect positions, controlled tempo, lots of quality volume."),
    dict(id="strength", name="Strength", numeral="II", start="2026-12-01", end="2027-01-31",
         focus="Heavier loads", blurb="Raise the ceiling: heavier compound lifts, contrast pairs, crisp Olympic work."),
    dict(id="power", name="Power", numeral="III", start="2027-02-01", end="2027-02-28",
         focus="Explosive work & plyometrics", blurb="Turn strength into speed: Olympic lifts, jumps and throws with maximal intent."),
    dict(id="peak", name="Peak", numeral="IV", start="2027-03-01", end="2027-03-31",
         focus="Sport transfer, speed & sand-ready conditioning", blurb="Sharpen the blade: sand speed, approach and block jumps, low-volume strength."),
]

ELEMENTS = {
    "earth": dict(name="Earth", focus="Legs"),
    "water": dict(name="Water", focus="Back & Biceps"),
    "fire": dict(name="Fire", focus="Chest, Triceps & Shoulders"),
    "air": dict(name="Air", focus="Rest & Mobility"),
}
CYCLE = ["earth", "water", "fire", "air"]

FORMATS = {
    "earth": {"H": ("heavy-strength", "Heavy Strength"), "O": ("olympic-power", "Olympic & Power"),
              "P": ("plyo-speed", "Plyometric & Fast-Twitch"), "S": ("single-leg-sand", "Single-Leg & Sand"),
              "M": ("mobility-legs", "Mobility-Focused Legs")},
    "water": {"St": ("pull-strength", "Pulling Strength"), "A": ("athletic-pull", "Athletic & Volleyball Pulling"),
              "Hy": ("back-hypertrophy", "Back & Biceps Hypertrophy"), "Po": ("posture-shoulder", "Posture & Shoulder Health")},
    "fire": {"Hy": ("push-hypertrophy", "Push Hypertrophy"), "Ex": ("explosive-push", "Explosive Pushing"),
             "Oh": ("overhead-strength", "Overhead Strength"), "Rc": ("cuff-health", "Rotator Cuff & Shoulder Health")},
    "air": {"Mf": ("mobility-flow", "Mobility Flow"), "Y": ("yoga", "Yoga-Style Stretching"),
            "HT": ("hip-thoracic", "Hip & Thoracic Mobility"), "FR": ("foam-roll", "Foam Rolling & Recovery"),
            "AR": ("active-recovery", "Light Active Recovery")},
}

# Format order per element across the 41 cycles (Foundation | Strength | Power | Peak).
SEQ = {
    "earth": ("H S O M P H S O M P H | O H S P H M O H S P H O M H S P | O P S O M P O | S P H S P M P"),
    "water": ("Hy Po St A Hy Po St A Hy Po A | St Hy St Po A St Hy St Po A St Hy St Po A | St A Po A Hy A St | A Po St A Hy A Po A"),
    "fire": ("Hy Rc Oh Ex Hy Rc Oh Hy Ex Rc Hy | Oh Ex Hy Oh Rc Oh Ex Hy Oh Rc Oh Ex Hy Oh Rc | Ex Rc Oh Ex Hy Rc Ex | Oh Ex Rc Hy Ex Rc Ex Rc"),
    "air": " ".join(["Mf AR Y FR HT"] * 9).split()[:41],
}
SEQ = {el: (s.replace("|", " ").split() if isinstance(s, str) else s) for el, s in SEQ.items()}

TITLES = {
    ("earth", "H"): ["Rooted Like a Badgermole", "The Mountain Does Not Move", "Pillars of Ba Sing Se",
                     "King Bumi's Heavy Lifting", "The Earth King's Deadlift", "Dai Li Discipline",
                     "The Boulder's Big Day", "Raising the Stone Ceiling", "Bedrock Peak"],
    ("earth", "O"): ["Omashu Express: Clean Technique", "Seismic Sense: Snatch Technique", "Tectonic Power Cleans",
                     "Rock Avalanche Snatches", "Metalbending Breakthrough", "Earthquake Hips",
                     "Meteorite Snatches", "Lavabending Speed"],
    ("earth", "P"): ["Landing School on the Sand", "Elastic Foundations", "Strength Meets Spring",
                     "Sky Bison Takeoff", "Depth Charge", "Rock Catapult Plyos", "Hurricane Footwork",
                     "Read & React", "Spring Tune-Up", "The Final Trial"],
    ("earth", "S"): ["Badgermole Balance", "Kyoshi Stance", "Stone Pillars, One at a Time", "Earth Rumble Footwork",
                     "Omashu Delivery Lunges", "Spring-Loaded Stance", "Sand Legs, Sandbender", "Court-Ready Hips"],
    ("earth", "M"): ["Roots & Range", "Barefoot Earthbending", "Joint Armor", "Swamp-Root Mobility",
                     "Pressure Release", "Grounded Before Flight"],
    ("water", "St"): ["Pulling the Moon", "Northern Water Tribe Rows", "Glacier Strength", "Iceberg Pulls",
                      "The Tide Rises", "Pakku's Heavy Hand", "Frozen Waterfall Pulls", "Ocean Spirit Strength",
                      "Riptide Power Pulls", "Undertow", "Full Moon Pulls"],
    ("water", "A"): ["The Waterbender's Whip", "Octopus Form", "Wave & Return", "Ice Spear Throws",
                     "Water Whip Rotation", "Spirit Oasis Power", "Surfing the Swell", "Tidal Torque",
                     "Typhoon Throws", "Riptide Rotation", "Monsoon Arms", "Healing Waters Pull", "Ocean's Fury"],
    ("water", "Hy"): ["Unagi-Sized Lats", "Ice Palace Sculpting", "Sculpted by the Tide", "Glacial Pump",
                      "Southern Tribe Swell", "The Great Unagi", "Tidal Pump", "Polar Bear Dog Back"],
    ("water", "Po"): ["Stand Tall Like Gran Gran", "Spirit Oasis Posture", "Still Water, Strong Shoulders",
                      "Koi Fish Balance", "Ice Sculptor's Posture", "Push & Pull Like Tui and La",
                      "Calm Before the Swell", "Moon Spirit Alignment", "Reflections"],
    ("fire", "Hy"): ["Sun Warrior Sculpting", "Dragon Dance Pump", "Embers of Ember Island", "Fire Lily Pump",
                     "Kindling the Flame", "Royal Palace Pump", "Hot Springs Hypertrophy", "Burning Builder",
                     "Furnace Finish"],
    ("fire", "Ex"): ["Fire Fist Basics", "Spark & Snap", "Lightning Generation", "Fire Jab Combos",
                     "Dragon's Breath", "Agni Kai Explosives", "Comet Power", "Combustion Push",
                     "Blue Flame Speed", "Phoenix Rising", "Lightning Redirection"],
    ("fire", "Oh"): ["Fire Sage Foundations", "Eternal Flame Presses", "Volcano Press", "Sozin's Comet Strength",
                     "Caldera Press", "The Fire Lord's Throne", "Molten Overhead", "The Sun's Zenith",
                     "Inferno Push Press", "Crown of Flame"],
    ("fire", "Rc"): ["Iroh's Tea-Cup Shoulders", "The Hitting Arm's Armor", "Dragon Scale Cuffs", "Banked Embers",
                     "The Steady Flame", "Candle Flame Control", "Jasmine Tea Rotations",
                     "Firebender Breath & Balance", "Smoldering Stability", "Ginseng Shoulders", "Ready to Serve"],
    ("air", "Mf"): ["Leaf on the Wind", "Air Temple Morning", "Floating Like Appa", "Glider Flow",
                    "Wind Through the Temple", "Air Nomad Unwind", "Breeze Flow", "Sky Bison Stretch",
                    "Avatar State: Fully Realized"],
    ("air", "Y"): ["Chakra Flow I: Earth (Let Go of Fear)", "Chakra Flow II: Water (Release Guilt)",
                   "Chakra Flow III: Fire (Release Shame)", "Chakra Flow IV: Air (Let Go of Grief)",
                   "Chakra Flow V: Sound (Speak Truth)", "Chakra Flow VI: Light (See Clearly)",
                   "Chakra Flow VII: Thought (Release Attachment)", "Chakra Flow VIII: Full Circle"],
    ("air", "HT"): ["Unlocking the Hips of the Ancients", "Spinning Like an Air Scooter", "Temple Spire Spine",
                    "Monk Gyatso's Twist", "Cyclone Hips", "The Spiral Staircase", "Eye of the Storm",
                    "Windmill Hips"],
    ("air", "FR"): ["Rolling Like a Lemur", "Momo's Massage Day", "Iron Out the Kinks", "Hot Leaf Juice Recovery",
                    "Appa's Grooming Session", "Bread & Butter Recovery", "Smooth as a Glider",
                    "Pai Sho Tile Reset"],
    ("air", "AR"): ["A Walk With Uncle", "Swim With the Koi", "Footwork Practice at Dawn", "Spin Class on Appa",
                    "Barefoot Pilgrimage", "Penguin Sledding Recovery", "Light Feet, Light Heart",
                    "Air Nomad Wander"],
}

SUMMARY = {
    "H": "Heavy bilateral strength raises your force ceiling. Every approach jump and block is built on it.",
    "O": "Olympic lifts teach the hips to explode: the same triple extension that drives your approach jump.",
    "P": "Elastic plyometrics and sprints for quick ground contacts, higher touches and a faster first step.",
    "S": "Single-leg strength and lateral power protect knees and ankles and help you own the sand.",
    "M": "Joint-armor day: deep range under light load for hips, knees, ankles and tendons.",
    "St": "Heavy pulling builds the back that brakes every arm swing and protects the shoulder.",
    "A": "Rotational power and athletic pulling, the engine behind a fast, healthy arm swing.",
    "Hy_water": "Volume for muscle: wider lats and bigger arms, with rear-delt work to balance the shoulder.",
    "Po": "Posture and scapular control keep the hitting shoulder healthy all season.",
    "Hy_fire": "Muscle-building pressing volume with shoulder care built into every session.",
    "Ex": "Explosive pushing builds rate of force development for blocking, transitions and quick hands.",
    "Oh": "Overhead strength for a stable, powerful shoulder where volleyball lives: above your head.",
    "Rc": "Rotator cuff, scapula and T-spine work: armor for your hitting and serving arm.",
    "Mf": "A head-to-toe mobility flow to restore range and calm the nervous system.",
    "Y": "Yoga-style stretching and breathwork for supple tissue and a quiet mind.",
    "HT": "Hips and thoracic spine: rotation for your swing and range for your digs.",
    "FR": "Foam rolling and gentle stretching to flush the week out of your tissues.",
    "AR": "Easy movement that boosts blood flow without adding fatigue.",
}
PHASE_NOTE = {
    "foundation": "Foundation focus: own every position, control the tempo, stop 2-3 reps shy of failure.",
    "strength": "Strength focus: heavier loads, full rest, crisp reps. Quality over grinding.",
    "power": "Power focus: maximal intent on every rep. If speed drops, end the set.",
    "peak": "Peak focus: low volume, high quality. Leave the session feeling faster than you arrived.",
}


# ---------------------------------------------------------------- item helpers
def M(id, sets, reps, load=None, rest=None, note=None, tag=None, ramp=False):
    assert id in EX, f"unknown exercise {id}"
    d = dict(id=id, sets=sets, reps=reps, load=load, rest=rest)
    if note:
        d["note"] = note
    if tag:
        d["tag"] = tag
    if ramp:
        d["ramp"] = True
    return d


def D(id, dose, note=None):
    assert id in EX, f"unknown exercise {id}"
    d = dict(id=id, dose=dose)
    if note:
        d["note"] = note
    return d


def pair(a, b, letter, note=None):
    """Superset/contrast: a then b, rest after b."""
    a = dict(a)
    b = dict(b)
    a["tag"], b["tag"] = f"{letter}1", f"{letter}2"
    b["rest"] = b.get("rest") or a.get("rest")
    a["rest"] = f"→ {letter}2"
    if note:
        b["note"] = note if not b.get("note") else b["note"] + " " + note
    return [a, b]


def tri(items, letter):
    out = []
    for i, it in enumerate(items):
        it = dict(it)
        it["tag"] = f"{letter}{i + 1}"
        if i < len(items) - 1:
            it["rest"] = f"→ {letter}{i + 2}"
        out.append(it)
    return out


def tagged(items):
    """Assign A, B, C... tags to main items that don't have one yet (supersets keep theirs)."""
    letters = "ABCDEFGHIJ"
    out, li = [], 0
    i = 0
    while i < len(items):
        it = items[i]
        if isinstance(it, list):
            grp = []
            first_rest = it[0].get("rest")
            for j, sub in enumerate(it):
                sub = dict(sub)
                sub["tag"] = f"{letters[li]}{j + 1}"
                if j < len(it) - 1:
                    sub["rest"] = f"→ {letters[li]}{j + 2}"
                elif not sub.get("rest") and first_rest and not first_rest.startswith("→"):
                    sub["rest"] = first_rest
                grp.append(sub)
            out.extend(grp)
        else:
            it = dict(it)
            it["tag"] = letters[li]
            out.append(it)
        li += 1
        i += 1
    return out


def block(kind, where, items, title=None, note=None):
    titles = {"warmup": "Warm-up", "main": "Main Work", "finisher": "Finisher & Core", "cooldown": "Cool-down"}
    b = dict(kind=kind, title=title or titles[kind], where=where, items=items)
    if note:
        b["note"] = note
    return b


def rot(pool, i, n=1, step=None):
    step = step or n
    L = len(pool)
    return [pool[(i * step + j) % L] for j in range(n)]


# ---------------------------------------------------------------- shared pools
WU_MOB = [  # (id, dose)
    ("worlds-greatest-stretch", "5/side"), ("hip-circles", "8/side"), ("goblet-squat", "2 × 5, pry at the bottom"),
    ("monster-walk", "2 × 10 steps/side"), ("single-leg-glute-bridge", "2 × 8/side"), ("leg-swings", "10/direction"),
    ("90-90-switch", "8/side"), ("inchworm", "5"), ("ankle-circles", "10/direction"), ("cossack-squat", "5/side"),
    ("kneeling-hip-flexor", "30 s/side"), ("knee-circles", "10/direction"), ("standing-hip-circles", "8/direction"),
]
WU_CARDIO_GYM = [("row-easy", "4 min easy"), ("bike-easy", "4 min easy"), ("jump-rope", "3 min easy")]
CD_LEGS = [
    ("kneeling-hip-flexor", "60 s/side"), ("runners-stretch", "45 s/side"), ("pigeon-pose", "60 s/side"),
    ("figure-four", "45 s/side"), ("90-90-hamstring", "45 s/side"), ("calf-stretch", "45 s/side"),
    ("foam-roll-quads", "60 s/side"), ("foam-roll-calves", "60 s/side"), ("childs-pose", "60 s"),
    ("straddle", "60 s"), ("side-quad-stretch", "45 s/side"), ("soleus-stretch", "45 s/side"),
    ("groin-stretch", "60 s"), ("seated-forward-fold", "60 s"),
]
CD_SAND = [
    ("calf-stretch", "45 s/side"), ("runners-stretch", "45 s/side"), ("pigeon-pose", "60 s/side"),
    ("childs-pose", "60 s"), ("figure-four", "45 s/side"), ("low-lunge", "45 s/side"),
    ("seated-forward-fold", "60 s"), ("soleus-stretch", "45 s/side"), ("groin-stretch", "60 s"),
]
WU_UPPER = [
    ("band-pull-apart", "2 × 15"), ("scap-pull-up", "2 × 8"), ("cat-cow", "8"), ("kb-halo", "5/direction"),
    ("dowel-pass-through", "10"), ("arm-circles", "10/direction"), ("external-rotation-band", "2 × 12/side"),
    ("foam-roll-lats", "45 s/side"), ("thread-needle", "5/side"), ("wall-slide", "2 × 8"),
    ("foam-roll-upper-back", "60 s"), ("wrist-circles", "10/direction"), ("open-book", "6/side"),
]
CD_UPPER = [
    ("lat-stretch-wall", "45 s/side"), ("childs-pose", "60 s"), ("upper-back-stretch", "45 s"),
    ("pec-stretch", "45 s"), ("forearm-stretch", "45 s"), ("foam-roll-upper-back", "90 s"),
    ("cross-body-stretch", "30 s/side"), ("sleeper-stretch", "45 s/side"), ("triceps-stretch", "30 s/side"),
    ("thread-needle", "6/side"), ("foam-roll-lats", "60 s/side"), ("neck-stretch", "30 s/side"),
]
WU_SAND = [("carioca", "2 × 20 m"), ("fast-skips", "2 × 20 m"), ("lateral-shuffle", "2 × 10 m/side"),
           ("worlds-greatest-stretch", "4/side"), ("ankle-circles", "10/direction"), ("leg-swings", "10/direction"),
           ("inchworm", "5"), ("hip-circles", "6/side")]


def pick_pairs(pool, i, n, exclude=()):
    """Rotate through a (id, dose) pool and return n D() items, skipping excluded ids."""
    out, j, seen = [], 0, set(exclude)
    L = len(pool)
    start = i * n + i // max(1, L // n)  # drift the window each lap so windows don't repeat
    while len(out) < n and j < L * 2:
        id_, dose = pool[(start + j) % L]
        j += 1
        if id_ in seen:
            continue
        seen.add(id_)
        out.append(D(id_, dose))
    return out


def gym_leg_warmup(c, primer=None, extra=None, exclude=()):
    items = [D(*WU_CARDIO_GYM[c.cycle % 3])]
    items += pick_pairs(WU_MOB, c.cycle, 3, exclude)
    if extra:
        items += extra
    if primer:
        items.append(primer)
    return block("warmup", "Gym", items)


def sand_warmup(c, n=3, extra=None, exclude=()):
    items = [D("sand-jog", "4 min easy")]
    items += pick_pairs(WU_SAND, c.cycle, n, exclude)
    if extra:
        items += extra
    return block("warmup", "Sand", items)


def leg_cooldown(c, where="Gym", n=3, exclude=()):
    pool = CD_SAND if where == "Sand" else CD_LEGS
    items = pick_pairs(pool, c.cycle, n, exclude) + [D("box-breathing", "2 min")]
    return block("cooldown", where, items)


def upper_warmup(c, n=3, exclude=(), cardio=True):
    items = [D(*WU_CARDIO_GYM[(c.cycle + 1) % 2])] if cardio else []
    items += pick_pairs(WU_UPPER, c.cycle + (7 if c.element == "fire" else 0), n, exclude)
    return block("warmup", "Gym", items)


def upper_cooldown(c, n=3, exclude=()):
    items = pick_pairs(CD_UPPER, c.cycle + (5 if c.element == "fire" else 0), n, exclude)
    items.append(D("box-breathing", "2 min"))
    return block("cooldown", "Gym", items)


CORE_PAIRS = [
    (M("copenhagen-plank", 3, "20 s/side", "Bodyweight"), M("hanging-leg-raise", 3, "10", "Bodyweight", "60 s")),
    (M("pallof-press", 3, "10/side", "RPE 7"), M("side-plank", 3, "30 s/side", "Bodyweight", "45 s")),
    (M("ab-roller", 3, "10", "Bodyweight"), M("copenhagen-plank", 3, "25 s/side", "Bodyweight", "45 s")),
    (M("dead-bug", 3, "8/side", "Bodyweight"), M("suitcase-deadlift", 3, "8/side", "RPE 7", "60 s")),
    (M("hanging-leg-raise", 3, "12", "Bodyweight"), M("side-plank", 3, "40 s/side", "Bodyweight", "45 s")),
    (M("copenhagen-plank", 3, "30 s/side", "Bodyweight"), M("ab-roller", 3, "8", "Bodyweight", "60 s")),
    (M("pallof-rotation", 3, "8/side", "RPE 7"), M("hanging-leg-raise", 3, "10", "Bodyweight", "60 s")),
    (M("cable-crunch", 3, "12", "RPE 8"), M("copenhagen-plank", 3, "30 s/side", "Bodyweight", "45 s")),
    (M("woodchop", 3, "10/side", "RPE 7"), M("dead-bug", 3, "10/side", "Bodyweight", "45 s")),
]


def core_finisher(c, where="Gym", idx=None, title=None):
    a, b = CORE_PAIRS[(c.cycle if idx is None else idx) % len(CORE_PAIRS)]
    return block("finisher", where, pair(a, b, "F"), title=title)


# ---------------------------------------------------------------- EARTH builders
def legs_H(c):
    T = [  # primary, sets, reps, load, rest, note, contrast(id, reps, load)
        ("back-squat", 4, "6", "67% 1RM", "2–3 min", "Tempo 3-1-1: three seconds down, one-second pause in the hole.", None),
        ("trap-bar-deadlift", 4, "6", "70% 1RM", "2–3 min", "Every rep from a dead stop. Reset the brace each time.", None),
        ("front-squat", 4, "5", "72% 1RM", "2–3 min", "One-second pause at the bottom.", None),
        ("back-squat", 5, "5", "78% 1RM", "3 min", None, ("box-jump", "3", "Max intent")),
        ("deadlift", 5, "3", "82% 1RM", "3 min", None, ("broad-jump", "2", "Max intent")),
        ("front-squat", 5, "3", "82% 1RM", "3 min", None, ("cmj", "3", "Max intent")),
        ("back-squat", 5, "3", "86% 1RM", "3–4 min", None, ("box-jump", "2", "Max height")),
        ("trap-bar-deadlift", 5, "2", "88% 1RM", "3–4 min", None, ("broad-jump", "2", "Max distance")),
        ("back-squat", 3, "2", "85% 1RM", "3 min", "Fast concentric. Stop the set if bar speed drops.", ("cmj", "3", "Max intent")),
    ]
    B = [("romanian-deadlift", 3, "8", "RPE 7", "2 min"), ("hack-squat", 3, "10", "RPE 7", "2 min"),
         ("hip-thrust", 3, "10", "RPE 7", "90 s"), ("good-morning", 4, "6", "RPE 7", "2 min"),
         ("front-squat", 3, "5", "70% 1RM", "2 min"), ("romanian-deadlift", 4, "6", "RPE 8", "2 min"),
         ("hip-thrust", 4, "6", "RPE 8", "2 min"), ("box-squat", 3, "3", "65% 1RM, fast", "2 min"),
         ("romanian-deadlift", 3, "5", "RPE 7", "2 min")]
    C = [("bulgarian-split-squat", 3, "8/side", "RPE 7", "90 s"), ("reverse-lunge", 3, "8/side", "RPE 7", "90 s"),
         ("step-up-knee-drive", 3, "6/side", "RPE 7", "75 s"), ("deficit-reverse-lunge", 3, "6/side", "RPE 8", "90 s"),
         ("bulgarian-split-squat", 3, "6/side", "RPE 8", "2 min"), ("crossover-lunge", 3, "8/side", "RPE 7", "75 s"),
         ("barbell-bulgarian", 3, "5/side", "RPE 8", "2 min"), ("step-up", 3, "5/side", "RPE 8", "90 s"),
         ("bulgarian-split-squat", 2, "5/side", "RPE 7", "90 s")]
    HAM = [("nordic-curl", "4"), ("lying-leg-curl", "10"), ("glute-ham-raise", "6"), ("ball-leg-curl", "10"),
           ("nordic-curl", "5"), ("seated-leg-curl", "10"), ("glute-ham-raise", "8"), ("nordic-curl", "5"),
           ("lying-leg-curl", "8")]
    CALF = [("standing-calf-raise", "12"), ("seated-calf-raise", "15"), ("tibialis-raise", "15"),
            ("db-calf-raise", "12"), ("standing-calf-raise", "10"), ("tibialis-raise", "20"),
            ("seated-calf-raise", "12"), ("db-calf-raise", "10"), ("tibialis-raise", "15")]
    k = c.k
    p = T[k]
    A = M(p[0], p[1], p[2], p[3], p[4], p[5], ramp=True)
    main = []
    if p[6]:
        main.append(pair(A, M(p[6][0], p[1], p[6][1], p[6][2], p[4]), "A",
                         note="Contrast: jump within 30 s of racking A1."))
    else:
        main.append(A)
    main.append(M(*B[k]))
    main.append(M(*C[k]))
    h, hr = HAM[k]
    cf, cr = CALF[k]
    main.append(pair(M(h, 3, hr, "Bodyweight" if h == "nordic-curl" else "RPE 8"),
                     M(cf, 3, cr, "RPE 8", "75 s"), "D"))
    primer = None if p[6] else D("box-jump", "3 × 3", "Low box. Practice soft, quiet landings.")
    return [gym_leg_warmup(c, primer),
            block("main", "Gym", tagged(main)),
            core_finisher(c),
            leg_cooldown(c)]


def legs_O(c):
    k = c.k
    T = [  # A olympic, B, C strength, D posterior, (contrast?)
        dict(A=("hang-clean", 5, "3", "60–65% clean", "2 min", "Technique first: bar close, fast elbows."),
             B=("muscle-snatch", 4, "3", "Light: empty bar to 40%", "90 s"),
             C=("front-squat", 4, "5", "70% 1RM", "2–3 min"), D=("kb-swing", 3, "10/side", "RPE 7", "75 s")),
        dict(A=("hang-snatch", 5, "3", "60% snatch", "2 min", "Patience at the hip, then a fast turnover."),
             B=("snatch-grip-deadlift", 3, "5", "RPE 7", "2 min"),
             C=("back-squat", 4, "5", "72% 1RM", "2–3 min"), D=("hip-thrust", 3, "8", "RPE 7", "90 s")),
        dict(A=("power-clean", 6, "2", "75% 1RM", "2 min"), B=("trap-bar-jump", 4, "3", "30% trap-bar 1RM", "90 s"),
             C=("front-squat", 4, "4", "80% 1RM", "3 min"), D=("romanian-deadlift", 3, "6", "RPE 8", "2 min")),
        dict(A=("power-snatch", 6, "2", "72% 1RM", "2 min"), B=("clean-pull", 4, "3", "95% of best clean", "2 min"),
             C=("back-squat", 4, "4", "80% 1RM", "3 min"), D=("glute-ham-raise", 3, "6", "Bodyweight+", "90 s")),
        dict(A=("hang-clean", 5, "2", "80% clean", "2–3 min"), B=("jump-squat", 4, "3", "25% back squat", "90 s"),
             C=("trap-bar-deadlift", 4, "3", "85% 1RM", "3 min"), D=("kb-swing", 3, "8/side", "Heavy", "75 s")),
        dict(A=("power-clean", 6, "2", "82% 1RM", "2–3 min"),
             C=("front-squat", 3, "3", "85% 1RM", "3 min"), B=("trap-bar-jump", 3, "3", "30% trap-bar 1RM", None),
             D=("nordic-curl", 3, "4", "Bodyweight", "90 s"), contrast=True),
        dict(A=("hang-snatch", 6, "2", "75% snatch", "2 min"),
             C=("back-squat", 3, "3", "85% 1RM", "3 min"), B=("kneeling-jump-squat", 3, "3", "Bodyweight or empty bar", None),
             D=("hip-thrust", 3, "5", "Explosive, RPE 8", "2 min"), contrast=True),
        dict(A=("power-clean-blocks", 5, "2", "85% power clean", "2–3 min"),
             C=("trap-bar-deadlift", 3, "2", "87% 1RM", "3 min"), B=("jump-squat", 3, "2", "30% back squat", None),
             D=("single-leg-rdl", 3, "5/side", "RPE 7", "75 s"), contrast=True),
    ]
    FIN = [
        (M("scoop-throw", 4, "3", "Medicine ball 4–6 kg"), M("copenhagen-plank", 3, "20 s/side", "Bodyweight", "60 s")),
        (M("backward-throw", 4, "3", "Medicine ball 4–6 kg"), M("hanging-leg-raise", 3, "10", "Bodyweight", "60 s")),
        (M("tibialis-raise", 3, "15", "Bodyweight"), M("ab-roller", 3, "10", "Bodyweight", "60 s")),
        (M("scoop-throw", 4, "3", "Medicine ball 4–6 kg"), M("side-plank", 3, "30 s/side", "Bodyweight", "60 s")),
        (M("db-calf-raise", 3, "12", "RPE 8"), M("pallof-press", 3, "10/side", "RPE 7", "60 s")),
        (M("backward-throw", 4, "2", "Max distance"), M("copenhagen-plank", 3, "30 s/side", "Bodyweight", "60 s")),
        (M("seated-calf-raise", 3, "15", "RPE 8"), M("dead-bug", 3, "8/side", "Bodyweight", "60 s")),
        (M("scoop-throw", 4, "2", "Max height"), M("hanging-leg-raise", 3, "12", "Bodyweight", "60 s")),
    ]
    t = T[k]
    A = M(*t["A"][:5], note=t["A"][5] if len(t["A"]) > 5 else None, ramp=True)
    main = [A]
    if t.get("contrast"):
        main.append(pair(M(*t["C"]), M(*t["B"]), "B", note="French-contrast style: jump within 30 s of the heavy set."))
    else:
        main.append(M(*t["B"]))
        main.append(M(*t["C"]))
    main.append(M(*t["D"]))
    a, b = FIN[k]
    wu_extra = [D("overhead-squat", "2 × 5", "Empty bar. Groove the bottom position.")]
    return [gym_leg_warmup(c, extra=wu_extra),
            block("main", "Gym", tagged(main)),
            block("finisher", "Gym", pair(a, b, "F"), title="Power Finisher & Core"),
            leg_cooldown(c)]


def legs_P(c):
    k = c.k
    S = "Sand"
    if k == 0:
        main = [M("pogo-hops", 3, "20", "Low amplitude", "60 s", "Count contacts; stay springy."),
                M("broad-jump", 4, "3", "80% effort", "90 s", "Stick each landing. Last rep: one max-effort baseline; note the distance."),
                M("lateral-bound", 3, "4/side", "Controlled", "90 s", "Stick each landing one second."),
                M("approach-jump", 4, "3", "80% effort", "90 s", "Rhythm over height. Last rep: one max touch as your baseline; note it."),
                M("lateral-shuffle", 4, "10 m/side", "Fast feet", "45 s"),
                M("sand-sprint", 8, "15 m", "90%", "Walk back")]
        return [sand_warmup(c), block("main", S, tagged(main)),
                block("finisher", S, pair(M("side-plank", 3, "30 s/side", "Bodyweight"),
                                          M("bear-crawl", 3, "10 m", "Steady", "60 s"), "F")),
                leg_cooldown(c, S)]
    if k == 1:
        gym = [M("box-jump", 5, "3", "Max intent", "90 s", "Step down every rep."),
               M("hurdle-hops", 4, "4", "Quick contacts", "90 s"),
               M("single-leg-push-off", 3, "5/side", "Explosive", "75 s")]
        sand = [M("sand-sprint", 6, "20 m", "90%", "Walk back"),
                M("lateral-shuffle", 4, "10 m/side", "Fast feet", "60 s")]
        return [gym_leg_warmup(c), block("main", "Gym", tagged(gym), title="Gym: Jumps"),
                block("main", S, [dict(x, tag=t) for x, t in zip(sand, ["D", "E"])], title="Sand: Speed"),
                block("finisher", "Gym", pair(M("pallof-press", 3, "10/side", "RPE 7"),
                                              M("tibialis-raise", 3, "15", "Bodyweight", "60 s"), "F")),
                leg_cooldown(c, S)]
    if k == 2:
        gym = [pair(M("trap-bar-deadlift", 4, "3", "85% 1RM", "3 min", ramp=True),
                    M("box-jump", 4, "2", "Max height"), "A", note="Contrast: jump within 30 s."),
               M("hurdle-hops", 4, "5", "Quick contacts", "90 s"),
               M("split-jump", 3, "4/side", "Max height", "75 s")]
        sand = [M("sand-sprint", 8, "20 m", "95%", "Walk back"), M("lateral-bound", 3, "5/side", "Max distance", "90 s")]
        return [gym_leg_warmup(c), block("main", "Gym", tagged(gym), title="Gym: Strength & Spring"),
                block("main", S, [dict(sand[0], tag="D"), dict(sand[1], tag="E")], title="Sand: Speed & Bounds"),
                core_finisher(c, "Gym", idx=0),
                leg_cooldown(c, S)]
    if k == 3:
        main = [M("approach-jump", 6, "2", "Max intent", "90 s", "Full rest. Every rep is a max touch."),
                M("tuck-jump", 4, "5", "Rebound fast", "90 s"),
                M("diagonal-bound", 4, "4/side", "Distance and height", "90 s"),
                M("side-hop-sprint", 5, "6 hops + 10 m", "Max intent", "75 s"),
                M("sand-sprint", 6, "25 m", "95%", "Walk back")]
        return [sand_warmup(c), block("main", S, tagged(main)),
                block("finisher", S, pair(M("dead-bug", 3, "10/side", "Bodyweight"),
                                          M("side-plank", 3, "40 s/side", "Bodyweight", "45 s"), "F")),
                leg_cooldown(c, S)]
    if k == 4:
        gym = [M("depth-jump", 4, "3", "18–24 in box", "2 min", "Step off, touch, rebound up to the second box."),
               M("seated-box-jump", 4, "3", "Max intent", "90 s"),
               M("single-leg-lateral-hop", 3, "6/side", "Stiff ankle", "60 s"),
               M("sled-push", 5, "15 m", "Heavy, fast", "90 s")]
        sand = [M("lateral-shuffle", 5, "10 m/side", "Fast feet", "60 s"),
                M("block-jump", 3, "5", "Quick rebounds", "75 s")]
        return [gym_leg_warmup(c), block("main", "Gym", tagged(gym), title="Gym: Reactive Strength"),
                block("main", S, [dict(sand[0], tag="E"), dict(sand[1], tag="F")], title="Sand: Court Movement"),
                block("finisher", "Gym", pair(M("copenhagen-plank", 3, "25 s/side", "Bodyweight"),
                                              M("hanging-leg-raise", 3, "10", "Bodyweight", "60 s"), "G")),
                leg_cooldown(c, S)]
    if k == 5:
        gym = [M("depth-jump", 5, "3", "24–30 in box", "2 min", "Shortest possible ground contact."),
               pair(M("jump-squat", 4, "3", "25% back squat", ramp=True),
                    M("box-jump", 4, "2", "Max height", "2 min"), "B"),
               M("single-leg-hop", 3, "4/side", "Distance", "75 s")]
        sand = [M("approach-jump", 5, "3", "Max intent", "90 s"), M("sand-sprint", 6, "20 m", "Max", "Walk back")]
        return [gym_leg_warmup(c), block("main", "Gym", tagged(gym), title="Gym: Rock Catapults"),
                block("main", S, [dict(sand[0], tag="D"), dict(sand[1], tag="E")], title="Sand: Transfer"),
                core_finisher(c, "Gym", idx=5),
                leg_cooldown(c, S)]
    if k == 6:
        main = [M("approach-jump", 6, "3", "Max intent", "90 s"),
                M("block-jump", 4, "5", "Quick rebounds", "75 s"),
                M("lateral-bound", 4, "4/side", "Max distance", "90 s"),
                M("broad-jump", 4, "3", "Continuous", "90 s", "Three consecutive jumps, minimal ground time."),
                M("sand-sprint", 8, "15 m", "Max", "Walk back")]
        return [sand_warmup(c), block("main", S, tagged(main)),
                block("finisher", S, pair(M("bear-crawl", 3, "15 m", "Steady"),
                                          M("side-plank", 3, "30 s/side", "Bodyweight", "45 s"), "F")),
                leg_cooldown(c, S)]
    if k == 7:
        main = [M("side-hop-sprint", 6, "6 hops + 10 m", "React", "75 s"),
                M("approach-jump", 5, "3", "Max intent", "90 s"),
                M("block-jump", 4, "4", "Then shuffle 3 m", "60 s", "Block, shuffle three meters, block again."),
                M("backpedal-sprint", 6, "5 m + 10 m", "React", "60 s"),
                M("lateral-shuffle", 4, "10 m/side", "Fast feet", "45 s")]
        return [sand_warmup(c), block("main", S, tagged(main)),
                block("finisher", S, pair(M("sand-sprint", 4, "30 m", "90%", "60 s"),
                                          M("dead-bug", 3, "8/side", "Bodyweight", "45 s"), "F"),
                      title="Sand Conditioning & Core"),
                leg_cooldown(c, S)]
    if k == 8:
        gym = [M("depth-jump", 3, "3", "24 in box", "2 min"),
               M("trap-bar-jump", 3, "3", "30% trap-bar 1RM", "90 s", ramp=True),
               M("single-leg-hop", 3, "4/side", "Distance", "75 s")]
        sand = [M("approach-jump", 4, "3", "Max intent", "90 s"),
                M("sand-sprint", 6, "20 m", "Max", "20 s", "Repeat-sprint ability: short rest on purpose.")]
        return [gym_leg_warmup(c), block("main", "Gym", tagged(gym), title="Gym: Spring Tune-Up"),
                block("main", S, [dict(sand[0], tag="D"), dict(sand[1], tag="E")], title="Sand: Game Speed"),
                core_finisher(c, "Gym", idx=7),
                leg_cooldown(c, S)]
    # k == 9: The Final Trial
    main = [M("broad-jump", 3, "1", "Test: best of 3", "90 s", "Record it in the notes and compare with your Day 17 baseline."),
            M("approach-jump", 5, "1", "Test: max touch", "2 min", "Mark your best touch and compare it with your Day 17 baseline."),
            M("sand-sprint", 3, "10 m", "Test: timed", "2 min", "Have a friend time you, or film it."),
            M("lateral-broad-jump", 3, "1/side", "Test: best each side", "90 s", "Compare left vs right; aim for symmetry."),
            M("block-jump", 3, "3", "Max height", "90 s")]
    gauntlet = tri([M("lateral-shuffle", 5, "10 m/side", "Fast feet"),
                    M("sand-sprint", 5, "10 m", "Max"),
                    M("block-jump", 5, "3", "Max height", "90 s")], "F")
    return [sand_warmup(c, n=4), block("main", S, tagged(main), title="Benchmark Tests"),
            block("finisher", S, gauntlet, title="The Avatar State Gauntlet",
                  note="Five rounds, no rest inside a round. Leave it all on the sand."),
            leg_cooldown(c, S, n=4)]


def legs_S(c):
    k = c.k
    S = "Sand"
    T = [
        dict(gym=[M("bulgarian-split-squat", 4, "8/side", "RPE 7", "90 s", ramp=True),
                  M("lateral-split-squat", 3, "6/side", "RPE 7", "75 s"),
                  M("single-leg-rdl", 3, "8/side", "RPE 7", "75 s"),
                  [M("copenhagen-plank", 3, "20 s/side", "Bodyweight"), M("tibialis-raise", 3, "15", "Bodyweight", "60 s")]],
             sand=[M("walking-lunge", 3, "20 m", "Bodyweight", "60 s"), M("lateral-shuffle", 4, "10 m/side", "Fast feet", "45 s")]),
        dict(gym=[M("step-up", 4, "8/side", "RPE 7", "90 s", ramp=True),
                  M("cossack-squat", 3, "5/side", "Bodyweight or light KB", "60 s"),
                  M("single-leg-glute-bridge", 3, "10/side", "Bodyweight", "45 s"),
                  [M("cable-hip-adduction", 3, "12/side", "RPE 7"), M("db-calf-raise", 3, "12", "RPE 8", "60 s")]],
             sand=[M("lateral-bound", 3, "5/side", "Stick 1 s", "75 s"), M("bear-crawl", 3, "15 m", "Steady", "60 s")]),
        dict(gym=[M("barbell-bulgarian", 4, "5/side", "RPE 8", "2 min", ramp=True),
                  M("crossover-lunge", 3, "8/side", "RPE 7", "75 s"),
                  M("single-leg-rdl", 3, "6/side", "RPE 8", "75 s"),
                  [M("copenhagen-plank", 3, "30 s/side", "Bodyweight"), M("seated-calf-raise", 3, "15", "RPE 8", "60 s")]],
             sand=[M("lateral-shuffle", 5, "10 m/side", "Fast feet", "45 s"), M("sand-sprint", 5, "15 m", "95%", "Walk back")]),
        dict(gym=[M("deficit-reverse-lunge", 4, "6/side", "RPE 8", "2 min", ramp=True),
                  M("lateral-split-squat", 3, "6/side", "RPE 8, barbell", "90 s"),
                  M("single-leg-box-squat", 3, "5/side", "Bodyweight or light DB", "60 s"),
                  [M("cable-hip-adduction", 3, "10/side", "RPE 8"), M("tibialis-raise", 3, "20", "Bodyweight", "60 s")]],
             sand=[M("lateral-bound", 4, "4/side", "Max distance", "90 s"), M("walking-lunge", 3, "20 m", "Bodyweight", "60 s")]),
        dict(gym=[M("bulgarian-split-squat", 4, "6/side", "RPE 8", "2 min", ramp=True),
                  M("lunge-pass-through", 3, "6/side", "RPE 7", "75 s"),
                  M("single-leg-rdl", 3, "8/side", "RPE 8", "75 s"),
                  [M("copenhagen-plank", 3, "30 s/side", "Bodyweight"), M("db-calf-raise", 3, "15", "3 s lowering", "60 s")]],
             sand=[M("lateral-shuffle", 6, "10 m/side", "Fast feet", "45 s"), M("backpedal-sprint", 5, "5 m + 10 m", "React", "60 s")]),
        dict(gym=[[M("bulgarian-split-squat", 3, "5/side", "RPE 8", "2 min", ramp=True),
                   M("single-leg-push-off", 3, "4/side", "Explosive")],
                  M("lateral-split-squat", 3, "5/side", "RPE 8", "90 s"),
                  M("single-leg-rdl", 3, "6/side", "RPE 8", "75 s")],
             sand=[M("lateral-bound", 4, "4/side", "Max distance", "90 s"), M("lateral-shuffle", 5, "10 m/side", "Fast feet", "45 s")],
             fin=(M("copenhagen-plank", 3, "30 s/side", "Bodyweight"), M("tibialis-raise", 3, "15", "Bodyweight", "60 s"))),
        dict(gym=None,
             sand=[M("walking-lunge", 3, "20 m", "Deep and slow", "60 s"), M("cossack-squat", 3, "6/side", "Bodyweight", "60 s"),
                   M("lateral-bound", 4, "4/side", "Max distance", "90 s"), M("lateral-shuffle", 6, "10 m/side", "Fast feet", "45 s"),
                   M("single-leg-lateral-hop", 3, "6/side", "Stiff ankle", "60 s"), M("bear-crawl", 3, "15 m", "Steady", "60 s")],
             fin=(M("side-plank", 3, "40 s/side", "Bodyweight"), M("dead-bug", 3, "10/side", "Bodyweight", "45 s"))),
        dict(gym=[M("step-up-knee-drive", 3, "6/side", "Explosive", "90 s", ramp=True),
                  M("crossover-lunge", 3, "6/side", "RPE 7", "75 s"),
                  M("single-leg-rdl", 3, "6/side", "RPE 7", "75 s"),
                  [M("copenhagen-plank", 3, "30 s/side", "Bodyweight"), M("tibialis-raise", 3, "15", "Bodyweight", "60 s")]],
             sand=[pair(M("lateral-shuffle", 5, "10 m/side", "Fast feet"), M("block-jump", 5, "3", "Max height", "60 s"), "X"),
                   M("sand-sprint", 5, "20 m", "95%", "Walk back")]),
    ]
    t = T[k]
    blocks = []
    if t["gym"]:
        gym_items = tagged(t["gym"])
        n_gym = len(t["gym"])
        blocks.append(gym_leg_warmup(c))
        blocks.append(block("main", "Gym", gym_items, title="Gym: Single-Leg Strength"))
        letters = "ABCDEFGH"
        sand_items = []
        li = n_gym
        for s in t["sand"]:
            if isinstance(s, list):
                for j, sub in enumerate(s):
                    sub = dict(sub)
                    sub["tag"] = f"{letters[li]}{j + 1}"
                    if j == 0:
                        sub["rest"] = f"→ {letters[li]}2"
                    sand_items.append(sub)
            else:
                sand_items.append(dict(s, tag=letters[li]))
            li += 1
        blocks.append(block("main", S, sand_items, title="Sand: Lateral & Court Work"))
    else:
        blocks.append(sand_warmup(c, n=4))
        blocks.append(block("main", S, tagged(t["sand"]), title="Sand: Single-Leg & Lateral"))
    if t.get("fin"):
        a, b = t["fin"]
        blocks.append(block("finisher", S if not t["gym"] else "Gym", pair(a, b, "F")))
    blocks.append(leg_cooldown(c, S))
    return blocks


def legs_M(c):
    k = c.k
    where = "Gym" if k % 2 == 0 else "Sand"
    MOB = [("90-90-switch", "3 × 6/side"), ("pigeon-pose", "90 s/side"), ("kneeling-hip-flexor", "60 s/side"),
           ("straddle", "90 s"), ("groin-stretch", "90 s"), ("low-lunge", "60 s/side"), ("figure-four", "60 s/side"),
           ("worlds-greatest-stretch", "2 × 5/side"), ("soleus-stretch", "60 s/side"), ("happy-baby", "90 s"),
           ("prone-scorpion", "2 × 8/side"), ("seated-forward-fold", "90 s")]
    if where == "Gym":
        T = [
            [M("goblet-squat", 4, "8", "Tempo 4-2-1", "75 s", "Four seconds down, two-second pause, smooth up."),
             M("cossack-squat", 3, "6/side", "Light KB", "60 s"),
             M("single-leg-rdl", 3, "8/side", "Slow, RPE 6", "60 s"),
             M("nordic-curl", 3, "3", "Slowest possible lowering", "90 s"),
             [M("tibialis-raise", 3, "20", "Bodyweight"), M("db-calf-raise", 3, "12", "3 s lowering", "60 s")],
             M("backward-sled-drag", 4, "20 m", "Moderate", "60 s"),
             M("spanish-squat", 4, "30 s", "Isometric", "60 s")],
            [M("goblet-squat", 3, "10", "Pause 3 s at the bottom", "75 s"),
             M("leg-extension", 4, "10", "2 s hold at the top", "60 s", "Tendon-friendly: smooth, no jerking."),
             M("spanish-squat", 4, "40 s", "Isometric", "60 s"),
             M("ball-leg-curl", 3, "10", "Slow lowering", "60 s"),
             [M("copenhagen-plank", 3, "25 s/side", "Bodyweight"), M("seated-calf-raise", 3, "15", "3 s lowering", "60 s")],
             M("backward-sled-drag", 4, "25 m", "Moderate", "60 s")],
            [M("goblet-squat", 3, "8", "Tempo 3-3-1", "75 s"),
             M("lateral-split-squat", 3, "6/side", "Bodyweight", "60 s"),
             M("single-leg-box-squat", 3, "6/side", "Slow", "60 s"),
             M("nordic-curl", 2, "4", "Slow lowering", "90 s"),
             [M("tibialis-raise", 3, "20", "Bodyweight"), M("standing-calf-raise", 3, "12", "Slow", "60 s")],
             M("spanish-squat", 3, "45 s", "Isometric", "60 s"),
             [M("copenhagen-plank", 3, "20 s/side", "Bodyweight"), M("backward-sled-drag", 3, "20 m", "Light", "60 s")]],
        ][k // 2]
        warm = block("warmup", "Gym", [D("foam-roll-quads", "60 s/side"), D("foam-roll-adductors", "45 s/side"),
                                       D("hip-circles", "8/side"), D("ankle-circles", "10/direction")])
    else:
        T = [
            [M("walking-lunge", 3, "20 m", "Deep and slow", "60 s"),
             M("lateral-split-squat", 3, "8/side", "Bodyweight", "60 s"),
             M("cossack-squat", 3, "6/side", "Bodyweight", "60 s"),
             M("single-leg-glute-bridge", 3, "12/side", "Bodyweight", "45 s"),
             M("bear-crawl", 3, "15 m", "Slow and controlled", "60 s"),
             M("pogo-hops", 3, "15", "Light and springy", "60 s")],
            [M("cossack-squat", 3, "8/side", "Bodyweight", "60 s"),
             M("walking-lunge", 3, "25 m", "Pause each rep", "60 s"),
             M("single-leg-rdl", 3, "8/side", "Bodyweight, eyes closed for 2 reps", "45 s"),
             M("lateral-split-squat", 3, "6/side", "Bodyweight", "60 s"),
             M("pogo-hops", 3, "20", "Barefoot", "60 s")],
            [M("walking-lunge", 2, "20 m", "Easy", "60 s"),
             M("cossack-squat", 3, "5/side", "Bodyweight", "60 s"),
             M("single-leg-glute-bridge", 3, "10/side", "Bodyweight", "45 s"),
             M("bear-crawl", 2, "15 m", "Easy", "60 s"),
             M("pogo-hops", 2, "15", "Light", "60 s"),
             M("lateral-shuffle", 3, "10 m/side", "Easy rhythm", "45 s"),
             M("single-leg-rdl", 2, "8/side", "Bodyweight, slow", "45 s")],
        ][k // 2]
        warm = sand_warmup(c, n=2)
    mob = pick_pairs(MOB, c.k * 2 + 1, 4)
    blocks = [warm, block("main", where, tagged(T), title="Strength Through Range")]
    if where == "Sand":
        blocks.append(block("main", "Sand", [D("barefoot-sand-walk", "10 min easy")], title="Barefoot Reset"))
    blocks.append(block("cooldown", where, mob + [D("box-breathing", "3 min")], title="Deep Mobility"))
    return blocks


# ---------------------------------------------------------------- WATER builders
def back_St(c):
    k = c.k
    A = [("weighted-pull-up", 4, "6", "RPE 7, light belt"), ("chin-up", 4, "6", "RPE 7, +5–10%"),
         ("weighted-pull-up", 5, "5", "RPE 8"), ("neutral-pull-up", 5, "4", "RPE 8, weighted"),
         ("weighted-pull-up", 5, "3", "RPE 8.5"), ("chin-up", 5, "4", "RPE 8, weighted"),
         ("weighted-pull-up", 6, "2", "RPE 9"), ("neutral-pull-up", 5, "3", "RPE 8.5, weighted"),
         ("weighted-pull-up", 4, "3", "RPE 8, explosive up"), ("chin-up", 4, "3", "RPE 8, explosive up"),
         ("weighted-pull-up", 3, "3", "RPE 8")]
    B = [("barbell-row", 4, "8", "RPE 7"), ("t-bar-row", 4, "8", "RPE 7"), ("barbell-row", 5, "5", "RPE 8"),
         ("reverse-grip-row", 4, "6", "RPE 8"), ("rack-pull", 4, "4", "RPE 8"), ("t-bar-row", 4, "6", "RPE 8"),
         ("barbell-row", 5, "4", "RPE 8.5"), ("seal-row", 4, "6", "RPE 8"), ("reverse-grip-row", 4, "5", "RPE 8"),
         ("rack-pull", 3, "3", "RPE 8, fast lockout"), ("seal-row", 3, "5", "RPE 8")]
    C = [("db-row", "10/side"), ("meadows-row", "8/side"), ("single-arm-cable-row", "10/side"), ("db-row", "8/side"),
         ("meadows-row", "6/side"), ("renegade-row", "6/side"), ("db-row", "6/side"), ("single-arm-cable-row", "8/side"),
         ("meadows-row", "6/side"), ("db-row", "8/side"), ("single-arm-cable-row", "8/side")]
    SCAP = [("face-pull", "15"), ("band-pull-apart", "20"), ("reverse-fly", "12"), ("face-pull", "15"),
            ("incline-reverse-fly-er", "10"), ("band-pull-apart", "20"), ("face-pull", "12"), ("reverse-fly", "12"),
            ("face-pull", "15"), ("band-pull-apart", "20"), ("face-pull", "15")]
    BI = [("barbell-curl", 3, "8"), ("ez-curl", 3, "8"), ("drag-curl", 3, "8"), ("barbell-curl", 4, "6"),
          ("ez-curl", 4, "6"), ("drag-curl", 3, "6"), ("barbell-curl", 4, "5"), ("ez-curl", 3, "6"),
          ("barbell-curl", 3, "6"), ("drag-curl", 3, "8"), ("ez-curl", 3, "8")]
    FIN = [("farmers-walk", 3, "30 m", "Heavy"), ("hammer-curl", 3, "10", "RPE 8"), ("single-arm-hang", 3, "30 s/side", "Bodyweight"),
           ("reverse-curl", 3, "10", "RPE 8"), ("farmers-walk", 4, "30 m", "Heavy"), ("zottman-curl", 3, "10", "RPE 7"),
           ("suitcase-deadlift", 3, "8/side", "RPE 8"), ("wrist-roller", 3, "1 up + down", "Moderate"),
           ("farmers-walk", 3, "40 m", "Heavy"), ("hammer-curl", 3, "8", "RPE 8"), ("single-arm-hang", 3, "25 s/side", "Bodyweight")]
    a = A[k]
    main = [M(a[0], a[1], a[2], a[3], "2–3 min" if k >= 2 else "2 min", ramp=True),
            M(*B[k], "2 min"),
            pair(M(C[k][0], 3, C[k][1], "RPE 8"), M(SCAP[k][0], 3, SCAP[k][1], "Light, perfect form", "75 s"), "C"),
            M(BI[k][0], BI[k][1], BI[k][2], "RPE 8", "90 s")]
    f = FIN[k]
    fin = block("finisher", "Gym", [dict(M(f[0], f[1], f[2], f[3], "60 s"), tag="F")], title="Grip & Carry Finisher")
    return [upper_warmup(c, exclude=(SCAP[k][0],)), block("main", "Gym", tagged(main)), fin, upper_cooldown(c)]


def back_A(c):
    k = c.k
    THROW = [("overhead-throw", 4, "5"), ("one-arm-slam", 4, "5/side"), ("scoop-throw", 4, "4"), ("rotational-pass", 4, "6/side"),
             ("supine-one-arm-throw", 3, "8/side"), ("backward-throw", 4, "4"), ("med-ball-slam", 4, "6"),
             ("overhead-throw", 5, "4"), ("one-arm-slam", 5, "4/side"), ("rotational-pass", 5, "5/side"),
             ("scoop-throw", 5, "3"), ("supine-one-arm-throw", 4, "6/side"), ("overhead-throw", 5, "3")]
    PULL = [("pull-up", 5, "4", "Explosive up, 3 s down"), ("inverted-row", 4, "8", "Fast pull"), ("kb-snatch", 4, "5/side", "RPE 7"),
            ("pull-up", 5, "3", "Max speed up"), ("ring-row", 4, "10", "Fast pull, slow lower"), ("high-row", 4, "10", "RPE 7"),
            ("pull-up", 6, "3", "Max speed up"), ("inverted-row", 4, "10", "Feet elevated"), ("kb-snatch", 5, "4/side", "RPE 8"),
            ("pull-up", 5, "3", "Max speed up"), ("ring-row", 3, "12", "Fast pull"), ("pull-up", 4, "4", "Explosive up"),
            ("inverted-row", 3, "10", "Fast pull")]
    ROT = [("woodchop", "10/side"), ("landmine-rotation", "8/side"), ("pallof-rotation", "8/side"), ("cable-lift", "10/side"),
           ("russian-twist", "12/side"), ("woodchop", "8/side"), ("landmine-rotation", "6/side"), ("pallof-press", "10/side"),
           ("cable-lift", "8/side"), ("landmine-rotation", "8/side"), ("woodchop", "8/side"), ("pallof-rotation", "8/side"),
           ("russian-twist", "10/side")]
    ROW = [("single-arm-cable-row", "10/side"), ("renegade-row", "6/side"), ("db-row", "10/side"), ("meadows-row", "8/side"),
           ("single-arm-cable-row", "8/side"), ("renegade-row", "8/side"), ("db-row", "8/side"), ("meadows-row", "8/side"),
           ("single-arm-cable-row", "10/side"), ("renegade-row", "6/side"), ("db-row", "10/side"),
           ("single-arm-cable-row", "8/side"), ("meadows-row", "8/side")]
    SCAP = [("face-pull", "15"), ("scap-pull-up", "8"), ("scaption", "12"), ("band-pull-apart", "20"),
            ("incline-reverse-fly-er", "10"), ("face-pull", "15"), ("scap-pull-up", "10"), ("scaption", "10"),
            ("face-pull", "12"), ("band-pull-apart", "20"), ("incline-reverse-fly-er", "10"), ("face-pull", "15"),
            ("scaption", "12")]
    ARM = [("hammer-curl", "10"), ("zottman-curl", "10"), ("cross-body-hammer", "10/side"), ("rope-hammer-curl", "12"),
           ("zottman-curl", "8"), ("hammer-curl", "12"), ("cross-body-hammer", "8/side"), ("rope-hammer-curl", "10"),
           ("hammer-curl", "10"), ("zottman-curl", "10"), ("cross-body-hammer", "10/side"), ("rope-hammer-curl", "12"),
           ("zottman-curl", "8")]
    FIN = [("battle-ropes", 6, "20 s", "Hard", "40 s"), ("sledgehammer", 4, "10/side", "Powerful", "60 s"),
           ("med-ball-slam", 3, "10", "Fast", "45 s"), ("battle-ropes", 8, "15 s", "Hard", "30 s"),
           ("bear-crawl", 4, "15 m", "Steady", "45 s"), ("sledgehammer", 5, "8/side", "Powerful", "60 s"),
           ("battle-ropes", 6, "20 s", "Hard", "40 s"), ("med-ball-slam", 4, "8", "Fast", "45 s"),
           ("bear-crawl", 4, "20 m", "Steady", "45 s"), ("battle-ropes", 8, "20 s", "Hard", "40 s"),
           ("sledgehammer", 4, "10/side", "Powerful", "60 s"), ("med-ball-slam", 4, "10", "Fast", "45 s"),
           ("battle-ropes", 5, "30 s", "Hard", "45 s")]
    sand = (k % 2 == 0)
    t = THROW[k]
    throws = block("main", "Sand" if sand else "Gym",
                   [M(t[0], t[1], t[2], "Medicine ball 3–6 kg", "60 s", "Maximal intent; rest until you're fresh.", tag="A")],
                   title="Sand: Power Throws" if sand else "Power Throws")
    p = PULL[k]
    main = [M(p[0], p[1], p[2], p[3], "2 min"),
            pair(M(ROT[k][0], 3, ROT[k][1], "RPE 7"), M(ROW[k][0], 3, ROW[k][1], "RPE 8", "75 s"), "C"),
            pair(M(SCAP[k][0], 3, SCAP[k][1], "Light, perfect form"), M(ARM[k][0], 3, ARM[k][1], "RPE 8", "60 s"), "D")]
    main_t = []
    letters = "BCD"
    for i, it in enumerate(main):
        if isinstance(it, list):
            for j, sub in enumerate(it):
                sub = dict(sub)
                sub["tag"] = f"{letters[i]}{j + 1}"
                if j == 0:
                    sub["rest"] = f"→ {letters[i]}2"
                main_t.append(sub)
        else:
            main_t.append(dict(it, tag=letters[i]))
    f = FIN[k]
    fin_where = "Sand" if (sand and f[0] in ("med-ball-slam", "bear-crawl")) else "Gym"
    fin = block("finisher", fin_where, [dict(M(*f), tag="E")], title="Conditioning Finisher")
    if sand:
        warm = sand_warmup(c, n=2, extra=[D("arm-circles", "10/direction"), D("band-pull-apart", "2 × 15")])
    else:
        warm = upper_warmup(c, exclude=(SCAP[k][0],))
    return [warm, throws, block("main", "Gym", main_t, title="Gym: Athletic Pulling"), fin, upper_cooldown(c)]


def back_Hy(c):
    k = c.k
    A = [("lat-pulldown", 4, "10"), ("close-grip-pulldown", 4, "10"), ("v-bar-pulldown", 4, "10"), ("underhand-pulldown", 4, "8"),
         ("lat-pulldown", 4, "8"), ("neutral-pull-up", 4, "8"), ("close-grip-pulldown", 4, "8"), ("lat-pulldown", 3, "10")]
    B = [("seated-cable-row", 4, "10"), ("chest-supported-t-bar", 4, "10"), ("incline-db-row", 4, "12"), ("seated-cable-row", 4, "8"),
         ("chest-supported-t-bar", 4, "8"), ("t-bar-row", 4, "8"), ("seated-cable-row", 3, "10"), ("incline-db-row", 3, "10")]
    C = [("straight-arm-pulldown", "12"), ("single-arm-pulldown", "10/side"), ("straight-arm-pulldown", "15"),
         ("single-arm-pulldown", "10/side"), ("straight-arm-pulldown", "12"), ("single-arm-pulldown", "8/side"),
         ("straight-arm-pulldown", "12"), ("single-arm-pulldown", "10/side")]
    RD = [("reverse-machine-fly", "15"), ("cable-rear-delt-fly", "15"), ("reverse-fly", "12"), ("reverse-machine-fly", "12"),
          ("cable-rear-delt-fly", "12"), ("reverse-fly", "15"), ("reverse-machine-fly", "15"), ("cable-rear-delt-fly", "15")]
    B1 = [("incline-curl", "10"), ("preacher-curl", "10"), ("spider-curl", "12"), ("cable-curl", "12"),
          ("incline-curl", "8"), ("preacher-curl", "8"), ("spider-curl", "10"), ("cable-curl", "10")]
    B2 = [("hammer-curl", "12"), ("concentration-curl", "10/side"), ("high-cable-curl", "12"), ("cross-body-hammer", "10/side"),
          ("rope-hammer-curl", "12"), ("concentration-curl", "12/side"), ("high-cable-curl", "15"), ("hammer-curl", "10")]
    FIN = [(("back-extension", "12"), ("wrist-curl", "15")), (("shrug", "12"), ("back-extension", "15")),
           (("back-extension", "15"), ("reverse-curl", "12")), (("wrist-curl", "15"), ("back-extension", "12")),
           (("back-extension", "12"), ("shrug", "12")), (("shrug", "10"), ("back-extension", "15")),
           (("reverse-curl", "12"), ("back-extension", "12")), (("back-extension", "15"), ("wrist-curl", "15"))]
    main = [M(*A[k], "RPE 8", "90 s", ramp=False),
            M(*B[k], "RPE 8", "90 s"),
            pair(M(C[k][0], 3, C[k][1], "RPE 8"), M(RD[k][0], 3, RD[k][1], "RPE 8", "60 s"), "C"),
            pair(M(B1[k][0], 3, B1[k][1], "RPE 8"), M(B2[k][0], 3, B2[k][1], "RPE 8", "60 s"), "D")]
    f1, f2 = FIN[k]
    fin = block("finisher", "Gym", pair(M(f1[0], 3, f1[1], "RPE 7"),
                                        M(f2[0], 3, f2[1], "RPE 7", "45 s",
                                          "Last set: drop the weight and go to near-failure." if k % 2 else None), "E"),
                title="Pump Finisher")
    return [upper_warmup(c, n=4, exclude=(RD[k][0],)), block("main", "Gym", tagged(main)), fin, upper_cooldown(c)]


def back_Po(c):
    k = c.k
    ROW = [("incline-db-row", 3, "12", "2 s squeeze at the top"), ("ring-row", 3, "12", "Slow lowering"),
           ("chest-supported-t-bar", 3, "10", "Pause at the chest"), ("seal-row", 3, "10", "Pause on the bench"),
           ("incline-db-row", 3, "10", "2 s squeeze"), ("high-row", 3, "12", "Elbows high"),
           ("ring-row", 3, "15", "Slow lowering"), ("seal-row", 3, "8", "Pause on the bench"),
           ("incline-db-row", 3, "12", "2 s squeeze")]
    B = [("face-pull", "15"), ("incline-reverse-fly-er", "10"), ("cuban-press", "10"), ("face-pull", "15"),
         ("incline-reverse-fly-er", "12"), ("cuban-press", "8"), ("face-pull", "12"), ("incline-reverse-fly-er", "10"),
         ("face-pull", "15")]
    SC = [("scap-pull-up", "8"), ("serratus-raise", "12"), ("scaption", "12"), ("scap-pull-up", "10"),
          ("serratus-raise", "15"), ("scaption", "10"), ("scap-pull-up", "10"), ("serratus-raise", "12"),
          ("scaption", "12")]
    ER = [("external-rotation-db", "12/side"), ("external-rotation-cable", "12/side"), ("external-rotation-band", "15/side"),
          ("external-rotation-db", "10/side"), ("external-rotation-cable", "10/side"), ("external-rotation-band", "15/side"),
          ("external-rotation-db", "12/side"), ("external-rotation-cable", "12/side"), ("external-rotation-band", "15/side")]
    POST = [("back-extension", "12"), ("superman", "30 s"), ("reverse-hyper", "12"), ("back-extension", "15"),
            ("superman", "30 s"), ("reverse-hyper", "10"), ("back-extension", "12"), ("superman", "40 s"),
            ("back-extension", "15")]
    BI = [("zottman-curl", "10"), ("hammer-curl", "12"), ("incline-curl", "12"), ("zottman-curl", "12"),
          ("hammer-curl", "10"), ("incline-curl", "10"), ("zottman-curl", "10"), ("cross-body-hammer", "10/side"),
          ("hammer-curl", "12")]
    CARRY = [("farmers-walk", 3, "30 m"), ("single-arm-hang", 3, "30 s/side"), ("turkish-get-up", 3, "2/side"),
             ("farmers-walk", 3, "40 m"), ("single-arm-hang", 3, "30 s/side"), ("suitcase-deadlift", 3, "8/side"),
             ("turkish-get-up", 3, "2/side"), ("farmers-walk", 3, "30 m"), ("single-arm-hang", 3, "30 s/side")]
    r = ROW[k]
    main = [M(r[0], r[1], r[2], "RPE 7", "75 s", r[3]),
            pair(M(B[k][0], 3, B[k][1], "Light"), M(SC[k][0], 3, SC[k][1], "Controlled", "60 s"), "B"),
            pair(M(ER[k][0], 3, ER[k][1], "Light"), M("internal-rotation-band", 2, "15/side", "Light", "45 s"), "C"),
            pair(M(POST[k][0], 3, POST[k][1], "Bodyweight to light"), M(BI[k][0], 3, BI[k][1], "RPE 7", "60 s"), "D")]
    cr = CARRY[k]
    CORE_PO = [("dead-bug", "8/side"), ("bird-dog", "8/side"), ("plank", "45 s"), ("side-plank", "30 s/side"),
               ("dead-bug", "10/side"), ("bird-dog", "10/side"), ("plank", "60 s"), ("side-plank", "40 s/side"),
               ("dead-bug", "8/side")]
    fin = block("finisher", "Gym", pair(M(cr[0], cr[1], cr[2], "Moderate"),
                                        M(CORE_PO[k][0], 3, CORE_PO[k][1], "Bodyweight", "60 s"), "E"),
                title="Carry & Stability")
    mob = block("cooldown", "Gym",
                pick_pairs([("foam-roll-upper-back", "90 s"), ("thread-needle", "6/side"), ("sleeper-stretch", "45 s/side"),
                            ("lat-stretch-wall", "45 s/side"), ("childs-pose", "60 s"), ("pec-stretch", "45 s"),
                            ("dowel-pass-through", "2 × 10"), ("open-book", "8/side"), ("cross-body-stretch", "30 s/side"),
                            ("upper-back-stretch", "45 s")], k, 4) + [D("box-breathing", "2 min")],
                title="Shoulder Mobility Cool-down")
    return [upper_warmup(c, exclude=(B[k][0], SC[k][0])), block("main", "Gym", tagged(main)), fin, mob]


# ---------------------------------------------------------------- FIRE builders
def prehab_item(k, pool):
    id_, reps = pool[k % len(pool)]
    return M(id_, 3, reps, "Light, perfect form", "45 s")


def push_Hy(c):
    k = c.k
    A = [("incline-db-press", 4, "10", "RPE 7"), ("bench-press", 4, "8", "70% 1RM"), ("db-bench", 4, "10", "RPE 7"),
         ("incline-bench", 4, "8", "68% 1RM"), ("incline-db-press", 4, "8", "RPE 8"), ("bench-press", 4, "6", "75% 1RM"),
         ("neutral-incline-db", 4, "8", "RPE 8"), ("db-bench", 4, "8", "RPE 8"), ("incline-db-press", 3, "8", "RPE 8")]
    B = [("chest-dip", "10"), ("cable-crossover", "12"), ("low-cable-fly", "12"), ("db-fly", "12"), ("pec-deck", "12"),
         ("incline-cable-fly", "12"), ("chest-dip", "8"), ("cable-crossover", "12"), ("low-cable-fly", "12")]
    C = [("db-shoulder-press", "10"), ("arnold-press", "10"), ("single-arm-landmine", "10/side"), ("standing-db-press", "8"),
         ("db-shoulder-press", "8"), ("arnold-press", "8"), ("single-arm-landmine", "8/side"), ("db-shoulder-press", "10"),
         ("arnold-press", "10")]
    LAT = [("lateral-raise", "12"), ("cable-lateral-raise", "12/side"), ("lean-away-lateral", "12/side"), ("lateral-raise", "15"),
           ("cable-lateral-raise", "15/side"), ("lean-away-lateral", "10/side"), ("lateral-raise", "12"),
           ("cable-lateral-raise", "12/side"), ("lean-away-lateral", "12/side")]
    T1 = [("rope-pushdown", "12"), ("skull-crusher", "10"), ("overhead-cable-ext", "12"), ("db-overhead-ext", "10"),
          ("rope-pushdown", "10"), ("skull-crusher", "8"), ("overhead-cable-ext", "10"), ("db-overhead-ext", "12"),
          ("rope-pushdown", "12")]
    T2 = [("kickback", "12"), ("single-arm-cable-ext", "12/side"), ("bench-dip", "15"), ("bar-pushdown", "12"),
          ("close-push-up", "15"), ("tate-press", "12"), ("kickback", "12"), ("single-arm-cable-ext", "10/side"),
          ("bar-pushdown", "15")]
    PRE = [("face-pull", "15"), ("external-rotation-cable", "12/side"), ("face-pull", "15"), ("band-pull-apart", "20"),
           ("external-rotation-cable", "10/side"), ("face-pull", "15"), ("external-rotation-band", "15/side"),
           ("face-pull", "12"), ("band-pull-apart", "20")]
    FIN = [("push-up", 2, "15"), ("feet-elevated-push-up", 2, "12"), ("svend-press", 2, "15"), ("push-up", 2, "20"),
           ("feet-elevated-push-up", 2, "15"), ("svend-press", 2, "12"), ("push-up", 2, "15"),
           ("feet-elevated-push-up", 2, "12"), ("svend-press", 2, "15")]
    a = A[k]
    main = [M(a[0], a[1], a[2], a[3], "2 min", ramp=a[0] in ("bench-press", "incline-bench")),
            M(B[k][0], 3, B[k][1], "RPE 8", "90 s"),
            pair(M(C[k][0], 3, C[k][1], "RPE 8"), M(LAT[k][0], 3, LAT[k][1], "RPE 8", "75 s"), "C"),
            pair(M(T1[k][0], 3, T1[k][1], "RPE 8"), M(T2[k][0], 3, T2[k][1], "RPE 8", "60 s"), "D"),
            prehab_item(k, PRE)]
    f = FIN[k]
    fin = block("finisher", "Gym", [dict(M(f[0], f[1], f[2], "Bodyweight", "60 s", "Stop one rep before form breaks."), tag="F")],
                title="Pump Finisher")
    return [upper_warmup(c, exclude=(PRE[k][0],)), block("main", "Gym", tagged(main)), fin, upper_cooldown(c)]


def push_Ex(c):
    k = c.k
    A = [("push-press", 5, "5", "65% 1RM", "Smooth dip-drive timing."), ("power-jerk", 5, "3", "Technique: 50–60%", None),
         ("push-press", 5, "3", "75% 1RM", None), ("power-jerk", 5, "3", "75% 1RM", None), ("split-jerk", 5, "2", "75% 1RM", None),
         ("push-press", 6, "2", "82% 1RM", None), ("split-jerk", 6, "2", "80% 1RM", None), ("power-jerk", 5, "2", "82% 1RM", None),
         ("push-press", 4, "3", "75% 1RM, max speed", None), ("split-jerk", 4, "2", "75% 1RM, crisp", None),
         ("landmine-push-press", 4, "5", "Explosive", None)]
    CON = [(("bench-press", 4, "5", "72% 1RM"), ("plyo-push-up", "5")), (("bench-press", 4, "4", "75% 1RM"), ("chest-pass", "5")),
           (("bench-press", 4, "3", "82% 1RM"), ("drop-push-up", "4")), (("incline-bench", 4, "3", "80% 1RM"), ("chest-pass", "5")),
           (("bench-press", 4, "2", "87% 1RM"), ("plyo-push-up", "4")), (("bench-press", 4, "3", "85% 1RM"), ("drop-push-up", "4")),
           (("band-bench", 6, "3", "55% 1RM + bands"), ("supine-chest-throw", "6")),
           (("bench-press", 5, "2", "88% 1RM"), ("kb-plyo-push-up", "3/side")),
           (("band-bench", 6, "3", "50% 1RM + bands"), ("plyo-push-up", "5")), (("bench-press", 3, "2", "85% 1RM"), ("chest-pass", "4")),
           (("band-bench", 5, "3", "50% 1RM + bands"), ("kneeling-chest-push", "4"))]
    C = [("kneeling-chest-push", 4, "4"), ("single-arm-landmine", 4, "5/side"), ("chest-push-sprint", 5, "1 + 10 m sprint"),
         ("kb-push-press", 4, "4/side"), ("kneeling-chest-push", 5, "3"), ("landmine-push-press", 4, "4"),
         ("chest-push-sprint", 6, "1 + 10 m sprint"), ("kb-push-press", 4, "3/side"), ("chest-push-sprint", 5, "1 + 10 m sprint"),
         ("kneeling-chest-push", 4, "4"), ("kb-push-press", 3, "5/side")]
    TRI = [("close-grip-bench", "8"), ("jm-press", "8"), ("chest-dip", "6"), ("close-grip-bench", "5"), ("jm-press", "6"),
           ("chest-dip", "5"), ("close-grip-bench", "4"), ("jm-press", "5"), ("chest-dip", "6"), ("close-grip-bench", "5"),
           ("jm-press", "8")]
    CUFF = [("external-rotation-cable", "12/side"), ("face-pull", "15"), ("external-rotation-band", "15/side"), ("face-pull", "15"),
            ("external-rotation-cable", "10/side"), ("face-pull", "12"), ("external-rotation-band", "15/side"), ("face-pull", "15"),
            ("external-rotation-cable", "12/side"), ("face-pull", "15"), ("external-rotation-band", "15/side")]
    FIN = [("battle-ropes", 6, "20 s"), ("med-ball-slam", 4, "8"), ("battle-ropes", 8, "15 s"), ("plyo-push-up", 3, "6"),
           ("battle-ropes", 6, "20 s"), ("med-ball-slam", 4, "6"), ("battle-ropes", 5, "30 s"), ("plyo-push-up", 3, "5"),
           ("battle-ropes", 6, "20 s"), ("med-ball-slam", 3, "8"), ("battle-ropes", 6, "20 s")]
    a = A[k]
    con = CON[k]
    main = [M(a[0], a[1], a[2], a[3], "2–3 min", a[4], ramp=True),
            pair(M(*con[0], ramp=False), M(con[1][0], con[0][1], con[1][1], "Max intent", "2–3 min"), "B",
                 note="Contrast: explode within 30 s of racking B1.")]
    cc = C[k]
    sand_c = cc[0] == "chest-push-sprint"
    tri_item = M(TRI[k][0], 3, TRI[k][1], "RPE 8", "2 min")
    cuff = M(CUFF[k][0], 3, CUFF[k][1], "Light, perfect form", "45 s")
    blocks = [upper_warmup(c, exclude=(CUFF[k][0],))]
    if sand_c:
        blocks.append(block("main", "Gym", tagged(main + [tri_item, cuff]), title="Gym: Explosive Pressing"))
        blocks.append(block("main", "Sand", [dict(M(cc[0], cc[1], cc[2], "Medicine ball 4–6 kg", "90 s"), tag="E")],
                            title="Sand: Push to Sprint"))
    else:
        mid = M(cc[0], cc[1], cc[2], "Max intent" if "kb" not in cc[0] and "landmine" not in cc[0] else "Explosive, RPE 7", "90 s")
        blocks.append(block("main", "Gym", tagged(main + [mid, tri_item, cuff])))
    f = FIN[k]
    blocks.append(block("finisher", "Gym", [dict(M(f[0], f[1], f[2], "Hard", "40 s"), tag="F")], title="Fire Finisher"))
    blocks.append(upper_cooldown(c))
    return blocks


def push_Oh(c):
    k = c.k
    A = [("ohp", 4, "6", "70% 1RM"), ("standing-db-press", 4, "8", "RPE 7"), ("ohp", 5, "5", "77% 1RM"),
         ("push-press", 5, "3", "82% 1RM"), ("seated-ohp", 5, "4", "80% 1RM"), ("ohp", 5, "3", "85% 1RM"),
         ("push-press", 5, "2", "87% 1RM"), ("ohp", 4, "3", "87% 1RM"), ("push-press", 4, "3", "80% 1RM, explosive"),
         ("ohp", 3, "3", "82% 1RM")]
    B = [("incline-bench", 4, "6", "70% 1RM"), ("bench-press", 4, "6", "72% 1RM"), ("bench-press", 4, "5", "78% 1RM"),
         ("incline-bench", 4, "5", "75% 1RM"), ("close-grip-bench", 4, "5", "75% 1RM"), ("bench-press", 5, "3", "85% 1RM"),
         ("floor-press", 4, "4", "80% 1RM"), ("pin-press", 4, "3", "85% 1RM"), ("bench-press", 3, "3", "82% 1RM"),
         ("incline-bench", 3, "4", "78% 1RM")]
    C = [("chest-dip", "8"), ("db-floor-press", "10"), ("chest-dip", "6"), ("incline-db-press", "8"), ("chest-dip", "5"),
         ("db-floor-press", "8"), ("chest-dip", "6"), ("incline-db-press", "6"), ("db-floor-press", "8"), ("chest-dip", "6")]
    D_ = [("lateral-raise", "12"), ("cuban-press", "10"), ("lean-away-lateral", "10/side"), ("lateral-raise", "15"),
          ("cuban-press", "8"), ("cable-lateral-raise", "12/side"), ("lateral-raise", "12"), ("lean-away-lateral", "12/side"),
          ("cuban-press", "10"), ("lateral-raise", "12")]
    E = [("db-overhead-ext", "10"), ("jm-press", "8"), ("tate-press", "10"), ("skull-crusher", "8"), ("db-overhead-ext", "8"),
         ("jm-press", "6"), ("overhead-cable-ext", "10"), ("tate-press", "8"), ("skull-crusher", "8"), ("db-overhead-ext", "10")]
    PRE = [("face-pull", "15"), ("band-pull-apart", "20")]
    FIN = [("turkish-get-up", 3, "2/side"), ("kb-windmill", 3, "5/side"), ("bottoms-up-clean", 3, "5/side"),
           ("turkish-get-up", 3, "1/side"), ("kb-windmill", 3, "6/side"), ("bottoms-up-clean", 3, "6/side"),
           ("turkish-get-up", 3, "2/side"), ("kb-windmill", 3, "5/side"), ("bottoms-up-clean", 3, "5/side"),
           ("turkish-get-up", 2, "2/side")]
    a = A[k]
    main = [M(a[0], a[1], a[2], a[3], "2–3 min", ramp=True),
            M(*B[k], "2–3 min", ramp=False),
            M(C[k][0], 3, C[k][1], "RPE 8", "2 min"),
            pair(M(D_[k][0], 3, D_[k][1], "RPE 8"), M(E[k][0], 3, E[k][1], "RPE 8", "75 s"), "D"),
            prehab_item(k, PRE)]
    f = FIN[k]
    fin = block("finisher", "Gym", [dict(M(f[0], f[1], f[2], "Moderate KB", "60 s", "Slow and perfect; eyes on the bell."), tag="F")],
                title="Shoulder Stability Finisher")
    return [upper_warmup(c, exclude=(PRE[k % 2][0],)), block("main", "Gym", tagged(main)), fin, upper_cooldown(c)]


def push_Rc(c):
    k = c.k
    A = [("single-arm-landmine", 4, "10/side", "RPE 7"), ("neutral-db-bench", 4, "10", "RPE 7"), ("db-floor-press", 4, "10", "RPE 7"),
         ("push-up", 4, "12", "Tempo 3-1-1"), ("single-arm-landmine", 4, "8/side", "RPE 8"), ("neutral-db-bench", 4, "8", "RPE 8"),
         ("db-floor-press", 4, "8", "RPE 8"), ("push-up", 4, "15", "Tempo 3-1-1"), ("single-arm-landmine", 3, "10/side", "RPE 7"),
         ("neutral-db-bench", 3, "10", "RPE 7"), ("db-floor-press", 3, "10", "RPE 7")]
    ER = [("external-rotation-db", "12/side"), ("external-rotation-cable", "12/side"), ("external-rotation-band", "15/side")]
    THIRD = [("cuban-press", "10"), ("scaption", "12"), ("incline-reverse-fly-er", "10"), ("cuban-press", "8")]
    SER = [("serratus-raise", "12"), ("wall-slide", "10"), ("serratus-raise", "15"), ("wall-slide", "12")]
    TRI = [("rope-pushdown", "15"), ("overhead-cable-ext", "12"), ("single-arm-cable-ext", "12/side"), ("rope-pushdown", "12"),
           ("overhead-cable-ext", "15")]
    STAB = [("turkish-get-up", "2/side"), ("kb-halo", "6/direction"), ("bottoms-up-clean", "6/side"), ("kb-windmill", "5/side")]
    RD = [("rear-delt-raise", "15"), ("face-pull", "15"), ("reverse-fly", "12")]
    a = A[k]
    main = [M(a[0], a[1], a[2], a[3], "90 s"),
            tri([M(ER[k % 3][0], 3, ER[k % 3][1], "Light"), M("internal-rotation-band", 3, "15/side", "Light"),
                 M(THIRD[k % 4][0], 3, THIRD[k % 4][1], "Featherweight", "60 s")], "B"),
            pair(M(SER[k % 4][0], 3, SER[k % 4][1], "Controlled"), M(TRI[k % 5][0], 3, TRI[k % 5][1], "RPE 7", "60 s"), "C"),
            pair(M(STAB[k % 4][0], 3, STAB[k % 4][1], "Moderate KB"), M(RD[k % 3][0], 3, RD[k % 3][1], "Light", "60 s"), "D")]
    flat = []
    letters = "ABCD"
    for i, it in enumerate(main):
        if isinstance(it, list):
            for j, sub in enumerate(it):
                sub = dict(sub)
                sub["tag"] = f"{letters[i]}{j + 1}"
                flat.append(sub)
        else:
            flat.append(dict(it, tag=letters[i]))
    mob = block("cooldown", "Gym",
                pick_pairs([("sleeper-stretch", "45 s/side"), ("cross-body-stretch", "30 s/side"), ("pec-stretch", "45 s"),
                            ("dowel-pass-through", "2 × 10"), ("thread-needle", "6/side"), ("foam-roll-upper-back", "90 s"),
                            ("triceps-stretch", "30 s/side"), ("open-book", "8/side"), ("lat-stretch-wall", "45 s/side")], k, 5)
                + [D("box-breathing", "3 min")], title="T-Spine & Shoulder Mobility")
    warm = block("warmup", "Gym", [D("row-easy", "4 min easy"), D("foam-roll-lats", "45 s/side")]
                 + pick_pairs([("arm-circles", "10/direction"), ("kb-halo", "5/direction"), ("band-pull-apart", "2 × 15"),
                               ("scap-pull-up", "2 × 8"), ("cat-cow", "8"), ("wrist-circles", "10/direction")], k, 3))
    return [warm, block("main", "Gym", flat, title="Cuff, Scap & Press"), mob]


# ---------------------------------------------------------------- AIR builders
def rest_Mf(c):
    k = c.k
    where = "Sand" if k % 2 == 0 else "Gym"
    arrive = [D("barefoot-sand-walk", "8 min easy") if where == "Sand" else D("bike-easy", "8 min easy"),
              D("box-breathing", "2 min")]
    CARS = [("neck-stretch", "30 s/side"), ("arm-circles", "2 × 10/direction"), ("wrist-circles", "10/direction"),
            ("standing-hip-circles", "2 × 8/direction"), ("knee-circles", "8/direction"), ("ankle-circles", "10/direction"),
            ("leg-swings", "2 × 10/direction"), ("kb-halo", "2 × 5/direction")]
    FLOW = [("cat-cow", "2 × 8"), ("worlds-greatest-stretch", "2 × 5/side"), ("inchworm", "2 × 5"), ("cossack-squat", "2 × 6/side"),
            ("90-90-switch", "2 × 8/side"), ("downward-dog", "3 × 30 s"), ("cobra", "3 × 20 s"), ("low-lunge", "2 × 45 s/side"),
            ("thread-needle", "2 × 6/side"), ("prone-scorpion", "2 × 8/side"), ("hip-circles", "2 × 8/side"),
            ("open-book", "2 × 8/side"), ("pelvic-tilt-bridge", "2 × 8")]
    CORE = [("bird-dog", "2 × 8/side"), ("dead-bug", "2 × 8/side"), ("side-plank", "2 × 30 s/side"), ("plank", "2 × 45 s")]
    DOWN = [("childs-pose", "2 min"), ("legs-up-wall", "4 min"), ("knee-across", "60 s/side"), ("happy-baby", "90 s"),
            ("figure-four", "60 s/side"), ("seated-forward-fold", "2 min")]
    cars = pick_pairs(CARS, k, 6)
    flow = pick_pairs(FLOW, k, 8)
    core = pick_pairs(CORE, k, 2)
    down = pick_pairs(DOWN, k, 3) + [D("box-breathing", "5 min")]
    if c.day == 164:
        flow = pick_pairs(FLOW, 0, 10)
        down = [D("childs-pose", "2 min"), D("legs-up-wall", "5 min"),
                D("box-breathing", "6 min", "Reflect on 164 days. You did that.")]
    return [block("warmup", where, arrive, title="Arrive"),
            block("main", where, cars, title="Joint-by-Joint Circles"),
            block("main", where, flow, title="The Flow", note="Move slowly from one drill to the next; breathe through each."),
            block("main", where, core, title="Quiet Core"),
            block("cooldown", where, down, title="Down-Regulate")]


def rest_Y(c):
    k = c.k
    where = "Sand" if k % 2 == 0 else "Gym"
    STAND = [("warrior-two", "2 × 45 s/side"), ("triangle-pose", "2 × 45 s/side"), ("low-lunge", "60 s/side"),
             ("runners-stretch", "60 s/side"), ("worlds-greatest-stretch", "2 × 5/side")]
    FLOOR = [("pigeon-pose", "2 min/side"), ("seated-forward-fold", "2 min"), ("knee-across", "90 s/side"),
             ("happy-baby", "2 min"), ("groin-stretch", "2 min"), ("straddle", "2 min"), ("figure-four", "90 s/side"),
             ("seated-twist", "60 s/side"), ("90-90-switch", "2 × 6/side")]
    BAL = [("bird-dog", "2 × 8/side"), ("side-plank", "2 × 30 s/side"), ("dead-bug", "2 × 8/side"), ("plank", "2 × 45 s")]
    centering = [D("box-breathing", "4 min"), D("cat-cow", "10 slow"), D("childs-pose", "90 s")]
    sun = [D("downward-dog", "5 breaths × 4"), D("low-lunge", "5 breaths/side × 4"), D("cobra", "5 breaths × 4"),
           D("childs-pose", "5 breaths × 4")]
    if k % 2:
        sun = [D("downward-dog", "6 breaths × 4"), D("cobra", "6 breaths × 4"), D("worlds-greatest-stretch", "3/side × 3"),
               D("childs-pose", "6 breaths × 4")]
    stand = pick_pairs(STAND, k, 3)
    bal = pick_pairs(BAL, k, 2)
    floor = pick_pairs(FLOOR, k, 6)
    rest = [D("legs-up-wall", "5 min"), D("box-breathing", "5 min")]
    return [block("warmup", where, centering, title="Centering"),
            block("main", where, sun, title="Sun Flow", note="Link each pose to your breath. Four rounds."),
            block("main", where, stand, title="Standing Series"),
            block("main", where, bal, title="Balance & Core"),
            block("main", where, floor, title="Floor Series"),
            block("cooldown", where, rest, title="Stillness")]


def rest_HT(c):
    k = c.k
    where = "Gym" if k % 3 else "Sand"
    warm = ([D("bike-easy", "6 min easy"), D("foam-roll-upper-back", "2 min"), D("foam-roll-glutes", "60 s/side")]
            if where == "Gym" else [D("barefoot-sand-walk", "8 min easy"), D("leg-swings", "10/direction")]) + [D("cat-cow", "10")]
    HIPS = [("90-90-switch", "3 × 8/side"), ("hip-circles", "2 × 8/side"), ("kneeling-hip-flexor", "2 × 60 s/side"),
            ("pigeon-pose", "2 min/side"), ("groin-stretch", "2 min"), ("cossack-squat", "3 × 6/side"), ("figure-four", "90 s/side"),
            ("low-lunge", "2 × 45 s/side"), ("straddle", "2 min"), ("happy-baby", "2 min")]
    TSP = [("open-book", "2 × 8/side"), ("thread-needle", "2 × 6/side"), ("dowel-pass-through", "3 × 10"),
           ("lat-stretch-wall", "2 × 45 s/side"), ("prone-scorpion", "2 × 8/side"), ("seated-twist", "60 s/side"),
           ("worlds-greatest-stretch", "2 × 5/side"), ("childs-pose", "2 min")]
    LOADED = [("goblet-squat", "3 × 30 s hold", "Hold the bottom and pry the knees out."),
              ("kb-halo", "2 × 6/direction", None), ("cossack-squat", "2 × 5/side", "Light kettlebell as counterweight."),
              ("turkish-get-up", "2 × 1/side", "Light bell; slow and smooth."), ("single-leg-rdl", "2 × 6/side", "Light, slow.")]
    hips = pick_pairs(HIPS, k, 6)
    tsp = pick_pairs(TSP, k, 5)
    loaded = []
    seen = {i["id"] for i in hips + tsp}
    for j in range(len(LOADED)):
        id_, dose, note = LOADED[(k + j) % len(LOADED)]
        if id_ in seen:
            continue
        loaded.append(D(id_, dose, note))
        if len(loaded) == 3:
            break
    settle = [D("knee-across", "60 s/side") if any(i["id"] == "childs-pose" for i in tsp) else D("childs-pose", "2 min"),
              D("box-breathing", "4 min")]
    return [block("warmup", where, warm, title="Warm the Tissues"),
            block("main", where, hips, title="Hip Series"),
            block("main", where, tsp, title="Thoracic Series"),
            block("main", where, loaded, title="Loaded Mobility", note="Light weights that teach strength at end range."),
            block("cooldown", where, settle, title="Settle")]


def rest_FR(c):
    k = c.k
    ROLL = [("foam-roll-quads", "90 s/side"), ("foam-roll-hamstrings", "90 s/side"), ("foam-roll-calves", "90 s/side"),
            ("foam-roll-it-band", "60 s/side"), ("foam-roll-glutes", "90 s/side"), ("foam-roll-adductors", "60 s/side"),
            ("foam-roll-lats", "60 s/side"), ("foam-roll-upper-back", "2 min"), ("foam-roll-shins", "60 s/side"),
            ("foam-roll-peroneals", "60 s/side"), ("foot-smr", "90 s/side"), ("forearm-smr", "60 s/side")]
    STR = [("calf-stretch", "45 s/side"), ("90-90-hamstring", "60 s/side"), ("side-quad-stretch", "60 s/side"),
           ("pec-stretch", "60 s"), ("childs-pose", "2 min"), ("figure-four", "60 s/side"), ("soleus-stretch", "45 s/side"),
           ("forearm-stretch", "60 s"), ("cross-body-stretch", "45 s/side"), ("lat-stretch-wall", "45 s/side")]
    FLUSH = [D("bike-easy", "10 min easy"), D("incline-walk", "10 min easy"), D("row-easy", "8 min easy")]
    roll = pick_pairs(ROLL, k, 9)
    st = pick_pairs(STR, k, 6)
    return [block("warmup", "Gym", [D("incline-walk", "8 min easy")], title="Easy Start"),
            block("main", "Gym", roll, title="Rolling Circuit", note="Slow passes; pause 20 s on anything tender."),
            block("main", "Gym", st, title="Gentle Stretching"),
            block("main", "Gym", [FLUSH[k % 3]], title="Easy Flush"),
            block("cooldown", "Gym", [D("legs-up-wall", "4 min"), D("box-breathing", "4 min")], title="Breathe")]


def rest_AR(c):
    k = c.k
    MODE = [
        ("Sand", [D("barefoot-sand-walk", "35 min easy")]),
        ("Gym", [D("easy-swim", "35 min easy", "Mix in backstroke every few laps.")]),
        ("Sand", [D("sand-footwork", "15 min easy"), D("barefoot-sand-walk", "20 min easy")]),
        ("Gym", [D("bike-easy", "35 min, Zone 1")]),
        ("Sand", [D("barefoot-sand-walk", "40 min easy")]),
        ("Gym", [D("easy-swim", "35 min easy", "Kick sets on a board are welcome.")]),
        ("Sand", [D("sand-footwork", "20 min easy"), D("barefoot-sand-walk", "15 min easy")]),
        ("Gym", [D("incline-walk", "35 min easy")]),
    ]
    where, cardio = MODE[k % len(MODE)]
    MOB = [("worlds-greatest-stretch", "2 × 5/side"), ("90-90-switch", "2 × 8/side"), ("cat-cow", "10"),
           ("thread-needle", "6/side"), ("pigeon-pose", "60 s/side"), ("downward-dog", "3 × 30 s"),
           ("calf-stretch", "45 s/side"), ("hip-circles", "8/side"), ("open-book", "8/side"),
           ("kneeling-hip-flexor", "60 s/side"), ("childs-pose", "90 s")]
    mob = pick_pairs(MOB, k, 8)
    return [block("warmup", where, [D("ankle-circles", "10/direction"), D("leg-swings", "10/direction")], title="Wake Up"),
            block("main", where, cardio, title="Easy Movement", note="Conversational pace the whole time."),
            block("main", where, mob, title="Mobility Snack"),
            block("cooldown", where, [D("box-breathing", "5 min")], title="Breathe")]


BUILDERS = {
    ("earth", "H"): legs_H, ("earth", "O"): legs_O, ("earth", "P"): legs_P, ("earth", "S"): legs_S, ("earth", "M"): legs_M,
    ("water", "St"): back_St, ("water", "A"): back_A, ("water", "Hy"): back_Hy, ("water", "Po"): back_Po,
    ("fire", "Hy"): push_Hy, ("fire", "Ex"): push_Ex, ("fire", "Oh"): push_Oh, ("fire", "Rc"): push_Rc,
    ("air", "Mf"): rest_Mf, ("air", "Y"): rest_Y, ("air", "HT"): rest_HT, ("air", "FR"): rest_FR, ("air", "AR"): rest_AR,
}


# ---------------------------------------------------------------- duration estimate
def _num(s):
    m = re.match(r"\s*(\d+(?:\.\d+)?)(?:\s*[–-]\s*(\d+(?:\.\d+)?))?", s)
    if not m:
        return None
    lo = float(m.group(1))
    hi = float(m.group(2) or lo)
    return lo, hi


def rest_secs(r):
    if not r:
        return 0
    if r.startswith("→"):
        return 20
    if r.lower().startswith("walk back"):
        return 40
    n = _num(r)
    if not n:
        return 60
    v = (n[0] + n[1]) / 2
    return v * 60 if "min" in r else v


def work_secs(reps):
    side = 2 if re.search(r"/(side|direction)", reps) else 1
    if "hops +" in reps or "+ 10 m" in reps or "m +" in reps:
        return 12
    if "up + down" in reps:
        return 60
    n = _num(reps)
    if not n:
        return 30
    v = n[1]
    rest = reps[re.match(r"\s*[\d.]+(?:\s*[–-]\s*[\d.]+)?", reps).end():].strip()
    if rest.startswith("min"):
        return v * 60
    if rest.startswith("s") and not rest.startswith("st"):
        return v * side
    if rest.startswith("m ") or rest == "m" or rest.startswith("m/"):
        return (v * 0.6 + 5) * side
    if rest.startswith("breath"):
        return v * 6 * side
    return (v * 3.5 + 8) * side


def dose_secs(dose):
    m = re.match(r"\s*(\d+)\s*×\s*(.+)", dose)  # "2 × 8/side", "3 × 30 s"
    if m:
        sets = int(m.group(1))
        return sets * work_secs(m.group(2)) + (sets - 1) * 20
    m2 = re.match(r"(.+?)\s*×\s*(\d+)\s*$", dose)  # "5 breaths × 3"
    if m2:
        return int(m2.group(2)) * work_secs(m2.group(1))
    return work_secs(dose)


def est_item(it):
    if it.get("sets"):
        s = it["sets"]
        w = work_secs(it["reps"])
        r = rest_secs(it.get("rest"))
        if (it.get("rest") or "").startswith("→"):
            t = s * (w + r)
        else:
            t = s * w + (s - 1) * r + 45
        if it.get("ramp"):
            t += 300
        return t
    return dose_secs(it["dose"]) + 15


def est_day(blocks):
    total = 0
    for b in blocks:
        bt = sum(est_item(i) for i in b["items"])
        b["minutes"] = max(2, round(bt / 60))
        total += bt + 60
    return round(total / 60)


PLYO_IDS = {e["id"] for e in EX.values() if e["category"] in ("Plyometric",)} | {"approach-jump", "block-jump", "pogo-hops",
                                                                                     "trap-bar-jump", "jump-squat", "kneeling-jump-squat"}


def contacts(blocks):
    n = 0
    for b in blocks:
        for it in b["items"]:
            if it["id"] in PLYO_IDS and it.get("sets"):
                reps = it["reps"]
                m = re.match(r"(\d+)", reps)
                if not m:
                    continue
                v = int(m.group(1))
                if "hops" in reps:
                    pass
                elif re.search(r"\d+\s*m\b", reps):
                    continue
                mult = 2 if "/side" in reps else 1
                n += it["sets"] * v * mult
    return n


# ---------------------------------------------------------------- main
class Ctx:
    pass


def phase_of(d):
    for p in PHASES:
        if date.fromisoformat(p["start"]) <= d <= date.fromisoformat(p["end"]):
            return p["id"]
    raise ValueError(d)


def build():
    n_days = (END - START).days + 1
    assert n_days == 164, n_days
    for el, seq in SEQ.items():
        assert len(seq) == 41, (el, len(seq))
        for a, b in zip(seq, seq[1:]):
            assert a != b, f"{el}: back-to-back format {a}"
    occ = {}
    occ_phase = {}
    days = []
    for i in range(n_days):
        d = START + timedelta(days=i)
        cyc = i // 4 + 1
        el = CYCLE[i % 4]
        fmt = SEQ[el][cyc - 1]
        ph = phase_of(d)
        key = (el, fmt)
        c = Ctx()
        c.day, c.date, c.cycle, c.element, c.fmt, c.phase = i + 1, d, cyc, el, fmt, ph
        c.k = occ.get(key, 0)
        c.kp = occ_phase.get((el, fmt, ph), 0)
        occ[key] = c.k + 1
        occ_phase[(el, fmt, ph)] = c.kp + 1
        blocks = BUILDERS[key](c)
        wheres = {b["where"] for b in blocks if b["kind"] in ("main", "finisher")}
        loc = "Gym + Sand" if len(wheres) > 1 else wheres.pop()
        fid, fname = FORMATS[el][fmt]
        title = TITLES[key][c.k]
        summ = SUMMARY.get(f"{fmt}_{el}", SUMMARY.get(fmt))
        day = dict(day=i + 1, date=d.isoformat(), cycle=cyc, cycleDay=i % 4 + 1, element=el,
                   focus=ELEMENTS[el]["focus"], phase=ph, format=fid, formatName=fname, title=title,
                   location=loc, summary=summ, phaseNote=PHASE_NOTE[ph], blocks=blocks)
        days.append(day)
    # attach cues (rotate through each exercise's cue list) and estimates
    used = {}
    for day in days:
        for b in day["blocks"]:
            for it in b["items"]:
                n = used.get(it["id"], 0)
                cues = EX[it["id"]]["cues"]
                it["cue"] = cues[n % len(cues)]
                used[it["id"]] = n + 1
        day["minutes"] = est_day(day["blocks"])
        cn = contacts(day["blocks"])
        if cn:
            day["contacts"] = cn
        for b in day["blocks"]:
            for it in b["items"]:
                if it.get("sets") is None:
                    it.pop("sets", None)
                    it.pop("reps", None)
                    it.pop("load", None)
                    it.pop("rest", None)
                if it.get("load") is None:
                    it.pop("load", None)
                if it.get("rest") is None:
                    it.pop("rest", None)
        # log flags: every item with sets in main/finisher blocks is loggable
        for b in day["blocks"]:
            for it in b["items"]:
                if it.get("sets") and b["kind"] in ("main", "finisher"):
                    it["log"] = True
    return days, used


def image_info(ex, sources):
    """Decide image paths for an exercise (files produced by build_images.py)."""
    eid = ex["id"]
    if ex["fedb"]:
        return dict(image=f"images/{eid}.webp", imageAlt=f"images/{eid}-2.webp", thumb=f"images/thumbs/{eid}.webp",
                    imageType="photo")
    if eid in sources:
        return dict(image=f"images/{eid}.webp", thumb=f"images/thumbs/{eid}.webp", imageType="photo")
    return dict(image=f"images/placeholders/{eid}.svg", thumb=f"images/placeholders/{eid}.svg", imageType="placeholder")


def main():
    days, used = build()
    # uniqueness checks
    sigs = {}
    for d in days:
        sig = json.dumps([[(i["id"], i.get("sets"), i.get("reps"), i.get("dose"), i.get("load")) for i in b["items"]]
                          for b in d["blocks"]])
        assert sig not in sigs, f"day {d['day']} duplicates day {sigs[sig]}"
        sigs[sig] = d["day"]
    titles = [d["title"] for d in days]
    assert len(set(titles)) == len(titles), "duplicate titles"
    src_path = os.path.join(ROOT, "tools", "image_sources.json")
    sources = json.load(open(src_path, encoding="utf-8")) if os.path.exists(src_path) else {}
    exercises = []
    for eid in sorted(used):
        ex = EX[eid]
        out = dict(id=eid, name=ex["name"], element=ex["element"], category=ex["category"], equipment=ex["equipment"],
                   cues=ex["cues"])
        if ex["desc"]:
            out["desc"] = ex["desc"]
        out.update(image_info(ex, sources))
        out["source"] = ("fedb:" + ex["fedb"]) if ex["fedb"] else (
            "external" if eid in sources else "placeholder")
        exercises.append(out)
    program = dict(name="The White Lotus Training Arc", tagline="Mastering All Elements",
                   start=START.isoformat(), end=END.isoformat(), totalDays=len(days),
                   cycle=[dict(element=e, **ELEMENTS[e]) for e in CYCLE], phases=PHASES, version=1)
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "schedule.json"), "w", encoding="utf-8") as f:
        json.dump(dict(program=program, days=days), f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(ROOT, "data", "exercises.json"), "w", encoding="utf-8") as f:
        json.dump(dict(exercises=exercises), f, ensure_ascii=False, indent=1)
    # report
    mins = [d["minutes"] for d in days]
    print(f"days={len(days)} exercises={len(exercises)} minutes min={min(mins)} max={max(mins)}")
    bad = [(d["day"], d["element"], d["format"], d["minutes"]) for d in days if not 60 <= d["minutes"] <= 90]
    for b in bad:
        print("  OUT OF RANGE", b)
    if "--verbose" in sys.argv:
        for d in days:
            print(d["day"], d["date"], d["element"], d["format"], d["location"], d["minutes"], d.get("contacts", ""), d["title"])


if __name__ == "__main__":
    main()
