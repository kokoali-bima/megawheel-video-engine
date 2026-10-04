"""VARIETY DIRECTOR — every new video gets a structure the audience has not seen recently (user 2026-10-04:
"buatkan engine / sistem baku agar pembuatan video sesuai standar, terutama variasinya, agar penonton ga bosan").

How it works
- Each format has a CATALOG of variation dimensions (layout template, obstacle shapes / sizes / contents, ...).
- The director reads the registry history (videos that are pending, approved or aired) and ranks every option by how
  often and how recently it was used in the same family; the least used comes first, the seed only breaks ties.
- A plan has a STRUCTURE SIGNATURE (what a viewer would notice, e.g. "ramp_first|box-L-lava,v-S-spikes,..."). A plan
  whose signature equals one of the last RECENT videos of the family is rejected. The signature is stored in the
  manifest + registry ("structure"), so the check works on shapes, not on random numbers.
- The plan is saved in the manifest (track_params["plan"]); re-rendering an approved episode reuses it exactly.

Used by sim_engine.make_potholes_track (CHALLENGE potholes / lava_potholes) and race25d.setup (hazard layout).
"""
import numpy as np

RECENT = 10                                          # no identical structure within the last N videos of a family

# ------------------------------------------------------------------ CHALLENGE: potholes family
FAMILY = {"potholes": "potholes", "lava_potholes": "potholes"}
# templates: items left to right. "P" = pit, "RP" = ramp + pit right after it; size class S / M / L;
# gaps (m) between items. The first obstacle starts at FIRST_X (after the intro narration).
TEMPLATES = {
    "classic":       dict(items=[("P", "S"), ("RP", "L"), ("P", "M")], gaps=[(11, 16), (13, 18)], first=(26, 31)),
    "ramp_first":    dict(items=[("RP", "L"), ("P", "M"), ("P", "S")], gaps=[(12, 16), (10, 14)], first=(26, 30)),
    "twin_early":    dict(items=[("P", "S"), ("P", "S"), ("RP", "L")], gaps=[(5, 7), (12, 16)], first=(26, 30)),
    "late_gauntlet": dict(items=[("P", "M"), ("RP", "L"), ("P", "S")], gaps=[(8, 11), (7, 10)], first=(34, 40)),
    "double_ramp":   dict(items=[("RP", "M"), ("RP", "L")], gaps=[(14, 18)], first=(27, 32)),
    "four_small":    dict(items=[("P", "S"), ("P", "S"), ("P", "M"), ("P", "S")], gaps=[(8, 11), (8, 11), (8, 11)],
                          first=(26, 30)),
}
SIZE = {"S": dict(w=(2.6, 3.6), d=(2.8, 3.6)), "M": dict(w=(3.8, 5.4), d=(3.0, 4.2)), "L": dict(w=(6.5, 9.0), d=(4.2, 5.5))}
# pit shapes (cross-section). The engine turns them into the road polyline, so physics and drawing follow the shape.
SHAPES = ["box", "narrow_deep", "wide_shallow", "v", "step", "crumble"]
SHAPE_MOD = {"narrow_deep": (0.75, 1.3), "wide_shallow": (1.35, 0.6)}       # (width x, depth x)
# what is inside a pit. Explosions in CHALLENGE are allowed only for lava and bombs (user 2026-10-04 asked for bombs).
FILLS = ["rubble", "water", "spikes", "bomb", "monster", "lava"]
FILL_MAX = {"bomb": 1, "monster": 1}                 # at most one per track: each is a moment, not wallpaper


def _family_history(active, family):
    """Most recent first: plans (dict) of videos in the family that recorded one."""
    out = []
    for e in reversed(active):
        if FAMILY.get(e.get("series")) == family:
            out.append(e)
    return out


def _rank(options, used_counts, recent_set, rng):
    """Least used first; options seen in the most recent videos pushed back; seed breaks ties."""
    tie = {o: float(rng.random()) for o in options}
    return sorted(options, key=lambda o: (o in recent_set, used_counts.get(o, 0), tie[o]))


def potholes_signature(plan):
    return plan["template"] + "|" + ",".join(f"{p['shape']}-{p['size']}-{p['fill']}" for p in plan["pits"])


def plan_potholes(series, active, seed, attempt=0):
    """Pick template, then a shape / fill per pit, favouring what the family has used least.
    attempt > 0 walks further down the ranking (when the engine rejected the first plan)."""
    rng = np.random.default_rng(70000 + seed * 13 + attempt)
    hist = _family_history(active, "potholes")
    plans = [e.get("plan") for e in hist if e.get("plan")]
    sigs = [e.get("structure") for e in hist[:RECENT] if e.get("structure")]
    t_count = {}
    for p in plans:
        t_count[p["template"]] = t_count.get(p["template"], 0) + 1
    if len(plans) < len(hist):                       # older videos had no plan: they were all "classic"
        t_count["classic"] = t_count.get("classic", 0) + (len(hist) - len(plans))
    recent_t = {p["template"] for p in plans[:2]} | ({"classic"} if not plans else set())
    s_count, f_count = {}, {}
    for p in plans:
        for q in p["pits"]:
            s_count[q["shape"]] = s_count.get(q["shape"], 0) + 1
            f_count[q["fill"]] = f_count.get(q["fill"], 0) + 1
    recent_s = {q["shape"] for p in plans[:1] for q in p["pits"]}
    recent_f = {q["fill"] for p in plans[:1] for q in p["pits"]}
    templates = _rank(list(TEMPLATES), t_count, recent_t, rng)
    for k in range(len(templates)):
        tname = templates[(k + attempt) % len(templates)]
        tpl = TEMPLATES[tname]
        shapes = _rank(SHAPES, s_count, recent_s, rng)
        if series == "lava_potholes":
            fills_rank = ["lava"]
        else:
            fills_rank = _rank([f for f in FILLS if f != "lava"], f_count, recent_f, rng)
        pits, used_f = [], {}
        for i, (kind, size) in enumerate(tpl["items"]):
            shape = shapes[i % len(shapes)]
            if kind == "RP" and shape in ("wide_shallow",):  # a ramp jump into a shallow tray reads as no obstacle
                shape = "box"
            fill = next((f for f in fills_rank[i % len(fills_rank):] + fills_rank
                         if used_f.get(f, 0) < FILL_MAX.get(f, 9)), "rubble")
            used_f[fill] = used_f.get(fill, 0) + 1
            pits.append(dict(kind=kind, size=size, shape=shape, fill=fill))
        plan = dict(template=tname, pits=pits, attempt=attempt)
        if potholes_signature(plan) not in sigs:
            return plan
    return plan


def build_potholes(plan, seed, end_x=92.0):
    """Concrete geometry from a plan: list of pits dict(x0, x1, d, shape, fill, kind) + ramps (x0, x1, h).
    Sizes jitter with the seed; FINISH_X stays 100 m: gaps are squeezed (never below 4 m) so all ends by end_x."""
    r = np.random.default_rng(1000 + seed)
    tpl = TEMPLATES[plan["template"]]
    x0 = float(r.uniform(*tpl["first"]))
    parts = []
    for q in plan["pits"]:
        sz = SIZE[q["size"]]
        wk, dk = SHAPE_MOD.get(q["shape"], (1.0, 1.0))
        w = float(r.uniform(*sz["w"])) * wk
        d = max(1.6, float(r.uniform(*sz["d"])) * dk)
        ramp = (float(r.uniform(5.0, 7.0)), float(r.uniform(1.1, 1.7))) if q["kind"] == "RP" else None
        parts.append((q, w, d, ramp))
    gaps = [float(r.uniform(*g)) for g in tpl["gaps"]]
    fixed = sum(w + (rp[0] if rp else 0.0) for _, w, _, rp in parts)
    room = end_x - x0 - fixed
    if sum(gaps) > room:
        k = max(0.0, room - 4.0 * len(gaps)) / max(1e-6, sum(g - 4.0 for g in gaps))
        gaps = [4.0 + (g - 4.0) * min(1.0, k) for g in gaps]
    pits, ramps, x = [], [], x0
    for i, (q, w, d, rp) in enumerate(parts):
        if rp:
            ramps.append((round(x, 1), round(x + rp[0], 1), round(rp[1], 1)))
            x += rp[0]
        pits.append(dict(x0=round(x, 1), x1=round(x + w, 1), d=round(d, 1), shape=q["shape"], fill=q["fill"],
                         kind=q["kind"]))
        x += w
        if i < len(gaps):
            x += gaps[i]
    return pits, ramps


def pit_profile(x0, x1, d, shape):
    """Road polyline points inside a pit, from the near rim (x0, 0) to the far rim (x1, 0), exclusive of the rims."""
    w = x1 - x0
    if shape == "v":                                 # sloped walls, narrow floor
        a, b = x0 + 0.3 * w, x1 - 0.3 * w
        return [(round(a, 2), -d), (round(b, 2), -d)]
    if shape == "step":                              # a ledge halfway down on the entry side
        m = x0 + 0.4 * w
        return [(x0, -round(0.45 * d, 2)), (round(m, 2), -round(0.45 * d, 2)), (round(m, 2), -d), (x1, -d)]
    if shape == "crumble":                           # broken rims slope in before the drop
        return [(round(x0 + 0.5, 2), -0.6), (round(x0 + 0.5, 2), -d), (round(x1 - 0.5, 2), -d),
                (round(x1 - 0.5, 2), -0.6)]
    return [(x0, -d), (x1, -d)]                      # box / narrow_deep / wide_shallow


# ------------------------------------------------------------------ RACE: hazard layout
RACE_LAYOUTS = {                                     # hazard x as fractions of the hazard zone; finish gap after
    "spread":     [0.0, 0.5, 1.0],
    "early_pair": [0.0, 0.18, 1.0],
    "late_pair":  [0.0, 0.82, 1.0],
    "gauntlet":   [0.25, 0.5, 0.75],
    "stagger":    [0.0, 0.35, 0.8],
}


def plan_race(active, seed):
    rng = np.random.default_rng(80000 + seed)
    hist = [e for e in reversed(active) if e.get("series") == "race25d"]
    used = {}
    for e in hist:
        lay = (e.get("plan") or {}).get("layout", "spread")
        used[lay] = used.get(lay, 0) + 1
    recent = {(e.get("plan") or {}).get("layout", "spread") for e in hist[:2]}
    lay = _rank(list(RACE_LAYOUTS), used, recent, rng)[0]
    zone = float(rng.uniform(160, 230))              # length of the hazard zone (m)
    return dict(layout=lay, zone=round(zone, 1), start=round(float(rng.uniform(95, 120)), 1),
                finish_gap=round(float(rng.uniform(85, 115)), 1))


def race_signature(plan, hazards):
    return plan["layout"] + "|" + ",".join(sorted(hazards))
