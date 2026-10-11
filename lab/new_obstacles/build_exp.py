#!/usr/bin/env python3
"""LAB ONLY. Builds lab/new_obstacles/sim_exp.py from the production generators/physics_2d/sim_engine.py by applying
text patches that add three experimental CHALLENGE series (owner request 2026-10-11, "coba ketiganya"):

  pendulum  CARS VS THE GIANT WRECKING BALL   a steel ball swings across the road on a fixed rhythm
  domino    CARS VS GIANT FALLING DOMINOES     a wave of giant dominoes topples along the road
  pinball   CARS VS GIANT PINBALL BUMPERS      bumpers over a lava pit kick the car around (a note per bounce)

Nothing in production imports lab/. Production sim_engine.py is only READ. Re-run this script after the engine changes:
  python lab/new_obstacles/build_exp.py            (writes sim_exp.py next to it)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "generators", "physics_2d", "sim_engine.py")
DST = os.path.join(HERE, "sim_exp.py")
s = open(SRC, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert s.count(old) >= 1, f"anchor not found: {old[:70]!r}"
    s = s.replace(old, new, count)


# ------------------------------------------------------------------ 1. series definitions
sub('''"3D graphics", "shorts", "MegaWheel Arena"]),
}
''', '''"3D graphics", "shorts", "MegaWheel Arena"]),
    # ---- LAB series (lab/new_obstacles): same 3-level story, slow-mo and narration as the lava format
    "pendulum": dict(title="CARS VS THE WRECKING BALL!", obst="a giant swinging wrecking ball", max_fail=20.0,
                     max_win=26.0, win_pool="any", signature="scripted",
                     force_theme=dict(location="volcano", weather="clear"),
                     fail_lines={"smash": "Bonk! {n} got smashed by the giant wrecking ball!",
                                 "pit": "Oh no! {n} fell into the lava and is melting!"},
                     yt_title="Cars VS The Giant Wrecking Ball! Who Survives? 💥",
                     tags=["cars", "wrecking ball", "pendulum", "car crash", "crash test", "physics simulation",
                           "shorts", "MegaWheel Arena"]),
    "domino": dict(title="CARS VS GIANT DOMINOES!", obst="a wave of giant falling dominoes", max_fail=20.0,
                   max_win=26.0, win_pool="any", signature="scripted", speed_scale=1.7,
                   fail_lines={"chop": "Crunch! {n} got flattened by the falling dominoes!"},
                   yt_title="Cars VS Giant Falling Dominoes! Who Survives? 🁢",
                   tags=["cars", "dominoes", "domino chain reaction", "car crash", "crash test",
                         "physics simulation", "shorts", "MegaWheel Arena"]),
    "pinball": dict(title="CARS VS GIANT PINBALL!", obst="giant pinball bumpers over a lava pit", max_fail=20.0,
                    max_win=26.0, win_pool="any", signature="scripted",
                    force_theme=dict(location="volcano", weather="clear"),
                    fail_lines={"pit": "Boing! {n} bounced right into the lava!"},
                    yt_title="Cars VS Giant Pinball Bumpers! Who Survives? 🔴",
                    tags=["cars", "pinball", "bumpers", "lava", "car crash", "crash test", "physics simulation",
                          "shorts", "MegaWheel Arena"]),
}
''')

# ------------------------------------------------------------------ 2. hazard globals + reset + dispatch
sub("AXES = []           #", "PENDS = []          # dict(x, period, phase) swinging wrecking balls (lab series pendulum)\n"
    "DOMS = []           # dict(x0, n, delay, lead) domino fields; the wave starts when the car is `lead` m past x0\n"
    "BUMPERS = []        # dict(x, y) pinball bumpers over a pit (lab series pinball)\nAXES = []           #")
sub("PIT_SHAPES, AXES, OGRES\n    PUDDLES", "PIT_SHAPES, AXES, OGRES, PENDS, DOMS, BUMPERS\n    PUDDLES")
sub("    AXES, OGRES = [], []\n", "    AXES, OGRES, PENDS, DOMS, BUMPERS = [], [], [], [], []\n")
sub('"dungeon": make_dungeon_track}', '"dungeon": make_dungeon_track,\n     "pendulum": make_pendulum_track, "domino": make_domino_track, "pinball": make_pinball_track}')

# ------------------------------------------------------------------ 3. track builders + helpers
sub("def make_bumps_track(seed):", '''PEND_PIV, PEND_LEN, PEND_AMP, PEND_R, PEND_K, PEND_MARGIN = 8.6, 6.5, 1.3, 1.0, 3.5, 0.4     # pivot height, chain length, swing (rad), ball radius
DOM_W, DOM_H, DOM_GAP, DOM_FALL = 0.9, 5.2, 2.3, 0.55
BUMP_R = 1.1


def pend_state(p, t):
    """(head x, head y, head vx, swing angle) of one wrecking ball at time t."""
    w = 2 * math.pi / p["period"]
    sv = math.sin(w * (t + p["phase"]))
    if PEND_K > 0:                      # hangs high at both ends, whips fast through the bottom (a gate, not a lullaby)
        th = PEND_AMP * math.tanh(PEND_K * sv) / math.tanh(PEND_K)
        dth = PEND_AMP * PEND_K * (1 - math.tanh(PEND_K * sv) ** 2) / math.tanh(PEND_K) * w * math.cos(w * (t + p["phase"]))
    else:
        th = PEND_AMP * sv
        dth = PEND_AMP * w * math.cos(w * (t + p["phase"]))
    return (p["x"] + PEND_LEN * math.sin(th), PEND_PIV - PEND_LEN * math.cos(th), PEND_LEN * math.cos(th) * dth, th)


def dom_angle(d, k, t, tt):
    """Fall angle (rad, 0 = standing, pi/2 = lying toward +x) of slab k. tt = the time the car triggered the field."""
    if tt is None or t < tt:
        return 0.0
    u = min(1.0, max(0.0, (t - tt - k * d["delay"]) / DOM_FALL))
    return (math.pi / 2) * u * u


def dom_pts(d, k, t, tt):
    """(angle, [(x, y)] samples along the slab's centre line) for the crush test."""
    a = dom_angle(d, k, t, tt)
    px = d["x0"] + k * DOM_GAP + DOM_W / 2
    pts = []
    for sdist in np.linspace(0.2, DOM_H, 12):
        rx, ry = -DOM_W / 2, sdist
        pts.append((px + rx * math.cos(a) + ry * math.sin(a), -rx * math.sin(a) + ry * math.cos(a)))
    return a, pts


def _lab_pit(tb, r, w, d, ramp, spans, obst, danger):
    x0 = tb.x
    tb.to(ramp[0], ramp[1])
    RAMPS.append((x0, tb.x, ramp[1]))
    tb.drop(-d)
    px0 = tb.x
    tb.flat(w)
    tb.drop(0.0)
    PITS.append((px0, tb.x, d))
    spans.append((px0, tb.x))
    obst.append(((px0 + tb.x) / 2, "lava"))
    danger.append(px0 - ramp[0])
    return px0, tb.x


def _lab_finish(tb, tag, spans, obst, danger, params):
    global RAMP, TRACK, TRACK_PARAMS, TRACK_ID, FINISH_X, OBST_SPANS, OBSTACLES, DANGER_X, SIGNS
    tb.flat(12.0)
    FINISH_X = round(tb.x - 2.0, 1)
    tb.pts.append((FINISH_X + 80, 0))
    TRACK = tb.pts
    RAMP = RAMPS[0] if RAMPS else None
    TRACK_PARAMS = params
    TRACK_ID = tag + "_" + hashlib.md5(json.dumps(TRACK_PARAMS).encode()).hexdigest()[:8]
    OBST_SPANS, OBSTACLES, DANGER_X = spans, obst, danger
    SIGNS = [d - 3 for d in danger]


def make_pendulum_track(seed):
    """Wrecking-ball road: ball -> ball -> launch ramp + lava pit -> double ball -> ball."""
    global PIT_KIND
    r = np.random.default_rng(9500 + seed)
    PIT_KIND = "lava"
    tb = _TB(0.0)
    tb.flat(float(r.uniform(36, 41)))
    spans, obst, danger = [], [], []

    def ball(dx=0.0, phase=None):
        p = dict(x=round(tb.x + 3.5 + dx, 2), period=round(float(r.uniform(5.2, 6.4)), 2),
                 phase=round(float(r.uniform(0, 3.0)) if phase is None else phase, 2))
        PENDS.append(p)
        spans.append((p["x"] - 2.2, p["x"] + 2.2))
        obst.append((p["x"], "pendulum"))
        danger.append(p["x"] - 8.0)
        return p

    ball()
    tb.flat(float(r.uniform(13, 16)))
    _lab_pit(tb, r, round(float(r.uniform(6.5, 8.5)), 1), 4.5,
             (round(float(r.uniform(5, 6.5)), 1), round(float(r.uniform(1.2, 1.6)), 2)), spans, obst, danger)
    tb.flat(float(r.uniform(13, 16)))
    ball()
    tb.flat(18.0)
    _lab_finish(tb, "pendulum", spans, obst, danger, dict(pends=PENDS, pits=PITS, ramps=RAMPS))


def make_domino_track(seed):
    """Domino road: three fields of giant dominoes that topple in a wave toward +x (chasing the cars)."""
    r = np.random.default_rng(9600 + seed)
    tb = _TB(0.0)
    tb.flat(float(r.uniform(30, 34)))
    spans, obst, danger = [], [], []

    def field(n):
        d = dict(x0=round(tb.x + 1.0, 2), n=n, delay=round(float(r.uniform(0.05, 0.06)), 3),
                 lead=round(float(r.uniform(9.0, 10.5)), 1))
        DOMS.append(d)
        spans.append((d["x0"] + d["lead"] - 1.0, d["x0"] + n * DOM_GAP + DOM_H))
        obst.append((d["x0"] + d["lead"] + 6.0, "dominoes"))
        danger.append(d["x0"] + d["lead"] - 2.0)
        tb.flat(n * DOM_GAP + DOM_H + 4.0)

    field(9)
    tb.flat(float(r.uniform(7, 9)))
    field(10)
    tb.flat(float(r.uniform(7, 9)))
    field(9)
    tb.flat(14.0)
    _lab_finish(tb, "domino", spans, obst, danger, dict(doms=DOMS))


def make_pinball_track(seed):
    """Pinball road: three launch ramps over lava pits; bumpers floating over each pit kick the car around."""
    global PIT_KIND
    r = np.random.default_rng(9700 + seed)
    PIT_KIND = "lava"
    tb = _TB(0.0)
    tb.flat(float(r.uniform(30, 34)))
    spans, obst, danger = [], [], []
    for n, w in ((3, 12.0), (3, 13.0)):
        w = round(w + float(r.uniform(-0.8, 0.8)), 1)
        x0, x1 = _lab_pit(tb, r, w, 4.5, (round(float(r.uniform(5, 6.0)), 1), round(float(r.uniform(1.4, 1.7)), 2)),
                          spans, obst, danger)
        for i in range(n):
            BUMPERS.append(dict(x=round(x0 + w * (i + 1) / (n + 1) + float(r.uniform(-0.6, 0.6)), 2),
                                y=round([3.4, 5.0, 3.0, 4.6][i % 4] + float(r.uniform(-0.4, 0.4)), 2)))
        tb.flat(float(r.uniform(8, 10)))
    _lab_finish(tb, "pinball", spans, obst, danger, dict(bumpers=BUMPERS, pits=PITS, ramps=RAMPS))


def make_bumps_track(seed):''')

# ------------------------------------------------------------------ 4. physics
sub("    axe_hit, ogre_hit, crushed, smashed = set(), set(), None, None\n",
    "    axe_hit, ogre_hit, crushed, smashed = set(), set(), None, None\n    pend_hit, dom_hit, dom_trig, bump_last, bump_log = set(), set(), {}, {}, []\n")
sub("        # hydroplaning: each puddle once; snow: fishtail after a hard landing\n", '''        for pi2, pd in enumerate(PENDS):                    # LAB: the wrecking ball smashes whoever it meets
            if pi2 in pend_hit or event is not None:
                continue
            hx, hy, hvx, _th = pend_state(pd, t)
            if (abs(hvx) > 1.0 and abs(ch.position.x - hx) < PEND_R + PEND_MARGIN * bw
                    and hy - PEND_R < ch.position.y + car_top and hy + PEND_R > ch.position.y - bh / 2):
                pend_hit.add(pi2)
                m_tot = v["mass"]
                ch.apply_impulse_at_local_point((m_tot * hvx * 0.6, m_tot * 5.5), (0, bh * 0.3))
                smashed = smashed or t
                event = dict(type="smash", t=t)
                if broken is None:
                    debris = break_car(space, car, v, rng, v["break_dv"] * 2.0, i)
                    broken = dict(t=t, x=ch.position.x, y=ch.position.y)
        for di2, dm in enumerate(DOMS):                     # LAB: the car trips the wave; a falling tile flattens it
            if di2 not in dom_trig and ch.position.x >= dm["x0"] + dm["lead"]:
                dom_trig[di2] = t
            tt_ = dom_trig.get(di2)
            if tt_ is None or event is not None or di2 in dom_hit:
                continue
            lo_x, hi_x = ch.position.x - bw / 2 * 0.9, ch.position.x + bw / 2 * 0.9
            lo_y, hi_y = ch.position.y - bh / 2, ch.position.y + car_top
            for k in range(dm["n"]):
                a_, pts = dom_pts(dm, k, t, tt_)
                if 0.25 < a_ < 1.35 and any(lo_x - DOM_W / 2 < px_ < hi_x + DOM_W / 2 and lo_y - DOM_W / 2 < py_ < hi_y
                                            for px_, py_ in pts):
                    dom_hit.add(di2)
                    ch.velocity = (ch.velocity.x * 0.1, min(ch.velocity.y, 0.0) - 2.5)
                    ch.angular_velocity *= 0.3
                    for w_ in wheels:
                        w_.velocity = (w_.velocity.x * 0.1, w_.velocity.y)
                    crushed = crushed or t
                    event = dict(type="chop", t=t)
                    if broken is None:
                        debris = break_car(space, car, v, rng, v["break_dv"] * 2.0, i)
                        broken = dict(t=t, x=ch.position.x, y=ch.position.y)
                    break
        if event is None:                                   # LAB: pinball bumpers kick the car (forward-biased bounce)
            for bi2, bp in enumerate(BUMPERS):
                if t - bump_last.get(bi2, -9.0) < 0.6:
                    continue
                ddx, ddy = ch.position.x - bp["x"], ch.position.y - bp["y"]
                dist = math.hypot(ddx, ddy)
                if dist < BUMP_R + 0.62 * bw:
                    bump_last[bi2] = t
                    ux = ddx / max(dist, 1e-6) + float(rng.uniform(0.9, 2.0))      # forward bias, random per bounce
                    uy = ddy / max(dist, 1e-6) + float(rng.uniform(0.0, 0.5))
                    un = math.hypot(ux, uy)
                    sp_ = min(max(ch.velocity.length * 0.85, 7.0) + 1.0, 12.0)
                    ch.velocity = (ux / un * sp_, uy / un * sp_)
                    ch.angular_velocity = ch.angular_velocity * 0.1
                    bump_log.append((t, bi2, sp_))
        # hydroplaning: each puddle once; snow: fishtail after a hard landing
''')
sub("                crushed=crushed, smashed=smashed,\n", "                crushed=crushed, smashed=smashed, bumps=bump_log, dom_trig=dom_trig,\n")
sub('''    if sig == "dungeon":''', '''    if sig == "scripted":                                        # LAB series: a smash / crush, a bumper kick or a lava plunge
        return (L["event"]["type"] in ("chop", "smash") or len(L.get("bumps") or []) >= 2
                or (L.get("sunk") is not None and L.get("sunk_kind") == "lava"))
    if sig == "dungeon":''')

# ------------------------------------------------------------------ 5. drawing
sub("def crush_amount(L, st):", '''def draw_pendulums(ctx, st):
    """LAB: gantry beam, chain and a spiked steel wrecking ball (in front of the cars)."""
    for p in PENDS:
        hx, hy, _vx, th = pend_state(p, st)
        x = p["x"]
        ctx.move_to(x - 0.7, PEND_PIV)                                     # support up to the cavern ceiling
        ctx.line_to(x - 0.2, 16.0)
        ctx.move_to(x + 0.7, PEND_PIV)
        ctx.line_to(x + 0.2, 16.0)
        ctx.set_source_rgb(0.25, 0.25, 0.32)
        ctx.set_line_width(0.14)
        ctx.stroke()
        rrect(ctx, x - 1.5, PEND_PIV - 0.1, 3.0, 0.7, 0.15)
        ctx.set_source_rgb(0.3, 0.3, 0.38)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.07, 0.07, 0.14)
        ctx.set_line_width(0.06)
        ctx.stroke()
        n = int(PEND_LEN / 0.45)
        for k in range(1, n):                                              # chain links along the swing
            f = k / n
            lx, ly = x + (hx - x) * f, PEND_PIV + (hy - PEND_PIV) * f
            ctx.save()
            ctx.translate(lx, ly)
            ctx.rotate(th)
            ctx.scale(0.2 if k % 2 else 0.1, 0.3)
            ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgb(0.4, 0.38, 0.45)
            ctx.set_line_width(0.07)
            ctx.stroke()
        for kk in range(10):                                               # spikes
            a = th * 1.5 + kk * math.tau / 10
            ctx.move_to(hx + (PEND_R - 0.1) * math.cos(a - 0.17), hy + (PEND_R - 0.1) * math.sin(a - 0.17))
            ctx.line_to(hx + (PEND_R + 0.55) * math.cos(a), hy + (PEND_R + 0.55) * math.sin(a))
            ctx.line_to(hx + (PEND_R - 0.1) * math.cos(a + 0.17), hy + (PEND_R - 0.1) * math.sin(a + 0.17))
            ctx.close_path()
            ctx.set_source_rgb(0.62, 0.64, 0.7)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.07, 0.07, 0.14)
            ctx.set_line_width(0.05)
            ctx.stroke()
        ctx.arc(hx, hy, PEND_R, 0, math.tau)
        g = cairo.RadialGradient(hx - 0.35, hy + 0.35, 0.1, hx, hy, PEND_R)
        g.add_color_stop_rgb(0, 0.82, 0.85, 0.92)
        g.add_color_stop_rgb(0.5, 0.35, 0.37, 0.46)
        g.add_color_stop_rgb(1, 0.12, 0.12, 0.2)
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.07, 0.07, 0.14)
        ctx.set_line_width(0.08)
        ctx.stroke()
        ctx.arc(hx, hy, PEND_R * 0.55, th * 1.5, th * 1.5 + math.pi * 0.8)   # yellow warning band
        ctx.set_source_rgb(0.98, 0.8, 0.1)
        ctx.set_line_width(0.14)
        ctx.stroke()


def draw_roadband(ctx, x0, x1):
    """LAB (domino): the road seen from slightly above: a second lane behind the cars + a far curb."""
    ctx.rectangle(x0, 0.0, x1 - x0, 1.6)
    g = cairo.LinearGradient(0, 0, 0, 1.6)
    g.add_color_stop_rgb(0, 0.3, 0.3, 0.36)
    g.add_color_stop_rgb(1, 0.4, 0.4, 0.46)
    ctx.set_source(g)
    ctx.fill()
    ctx.rectangle(x0, 1.6, x1 - x0, 0.28)
    ctx.set_source_rgb(0.82, 0.8, 0.76)
    ctx.fill()
    ctx.rectangle(x0, 1.88, x1 - x0, 0.06)
    ctx.set_source_rgb(0.2, 0.2, 0.26)
    ctx.fill()
    x = math.floor(x0 / 2.4) * 2.4
    while x < x1:
        ctx.rectangle(x, 0.78, 1.2, 0.07)
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.fill()
        x += 2.4


def draw_dominoes(ctx, st, front):
    """LAB: giant ivory domino boxes (back face + top/side for a 3D look). Standing / lying ones are behind the cars,
    falling ones in front; a dust puff where each tile lands."""
    cur = globals().get("_CUR_L")
    trig = (cur[0].get("dom_trig") if cur and cur[0] else None) or {}
    ox, oy = 0.34, 0.36
    for di, d in enumerate(DOMS):
        tt = trig.get(di)
        for k in range(d["n"]):
            a = dom_angle(d, k, st, tt)
            late = bool(cur and cur[0] and cur[0].get("crushed") is not None and st >= cur[0]["crushed"])
            if ((0.2 < a < 1.45) or (late and a >= 1.45)) != front:      # after a crush the tiles lie ON the car
                continue
            ctx.save()
            ctx.translate(d["x0"] + k * DOM_GAP + DOM_W / 2, 0.0)
            ctx.rotate(-a)
            rrect(ctx, -DOM_W + ox, oy, DOM_W, DOM_H, 0.12)                 # back face (depth)
            ctx.set_source_rgb(0.62, 0.6, 0.55)
            ctx.fill()
            for poly_ in ([(-DOM_W, DOM_H), (-DOM_W + ox, DOM_H + oy), (ox, DOM_H + oy), (0, DOM_H)],
                          [(0, 0), (ox, oy), (ox, DOM_H + oy), (0, DOM_H)]):
                ctx.move_to(*poly_[0])
                for pt in poly_[1:]:
                    ctx.line_to(*pt)
                ctx.close_path()
                ctx.set_source_rgb(0.78, 0.76, 0.7)
                ctx.fill_preserve()
                ctx.set_source_rgb(0.1, 0.1, 0.16)
                ctx.set_line_width(0.05)
                ctx.stroke()
            rrect(ctx, -DOM_W, 0.0, DOM_W, DOM_H, 0.12)
            g = cairo.LinearGradient(-DOM_W, 0, 0, 0)
            g.add_color_stop_rgb(0, 0.99, 0.97, 0.91)
            g.add_color_stop_rgb(1, 0.84, 0.82, 0.76)
            ctx.set_source(g)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.1, 0.1, 0.16)
            ctx.set_line_width(0.07)
            ctx.stroke()
            ctx.move_to(-DOM_W + 0.1, DOM_H / 2)
            ctx.line_to(-0.1, DOM_H / 2)
            ctx.set_line_width(0.1)
            ctx.stroke()
            for cx_, cy_ in [(-DOM_W * 0.3, DOM_H * 0.88), (-DOM_W * 0.7, DOM_H * 0.78), (-DOM_W * 0.5, DOM_H * 0.68),
                             (-DOM_W * 0.3, DOM_H * 0.3), (-DOM_W * 0.7, DOM_H * 0.18)]:
                ctx.arc(cx_, cy_, 0.13, 0, math.tau)
                ctx.set_source_rgb(0.1, 0.1, 0.16)
                ctx.fill()
            ctx.restore()
            if tt is not None and front is False:
                age = (st - tt - k * d["delay"] - DOM_FALL) / 0.4         # dust where the tile hit the ground
                if 0 <= age < 1:
                    for sg in (-1, 1):
                        ctx.save()
                        ctx.translate(d["x0"] + k * DOM_GAP + DOM_H * 0.9 + sg * (0.5 + 1.6 * age), 0.35)
                        ctx.scale(0.8 + 1.0 * age, 0.45 + 0.5 * age)
                        ctx.arc(0, 0, 1.0, 0, math.tau)
                        ctx.restore()
                        ctx.set_source_rgba(0.82, 0.78, 0.7, 0.6 * (1 - age))
                        ctx.fill()


def draw_bumpers(ctx, st):
    """LAB: pinball mushroom bumpers hanging over the pit; they flash when the car bounces off."""
    cur = globals().get("_CUR_L")
    log = (cur[0].get("bumps") if cur and cur[0] else None) or []
    for bi, bp in enumerate(BUMPERS):
        x, y = bp["x"], bp["y"]
        age = min([st - t_ for t_, i_, _s in log if i_ == bi and t_ <= st] or [9.0])
        ctx.move_to(x, 16.0)
        ctx.line_to(x, y + BUMP_R * 0.6)
        ctx.set_source_rgb(0.25, 0.25, 0.32)
        ctx.set_line_width(0.16)
        ctx.stroke()
        if age < 0.4:                                                      # flash ring
            ctx.arc(x, y, BUMP_R * (1.0 + 1.4 * age), 0, math.tau)
            ctx.set_source_rgba(1, 0.9, 0.2, 0.7 * (1 - age / 0.4))
            ctx.set_line_width(0.2)
            ctx.stroke()
        rad = BUMP_R * (1.0 + (0.18 if age < 0.12 else 0.0))
        ctx.arc(x, y, rad, 0, math.tau)
        g = cairo.RadialGradient(x - 0.3, y + 0.3, 0.1, x, y, rad)
        lit = age < 0.3
        g.add_color_stop_rgb(0, 1, 1, 0.7 if lit else 0.9)
        g.add_color_stop_rgb(0.5, 1, 0.8 if lit else 0.2, 0.1 if lit else 0.25)
        g.add_color_stop_rgb(1, 0.6, 0.05, 0.12)
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.07, 0.07, 0.14)
        ctx.set_line_width(0.08)
        ctx.stroke()
        ctx.arc(x, y, rad * 0.62, 0, math.tau)
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(0.1)
        ctx.stroke()


def crush_amount(L, st):''')
sub("    draw_ogres(ctx, st)\n    draw_shadow(ctx, L, s)", "    if DOMS:\n        draw_roadband(ctx, camx - half, camx + half)\n    draw_ogres(ctx, st)\n    draw_dominoes(ctx, st, False)\n    draw_bumpers(ctx, st)\n    draw_shadow(ctx, L, s)")
sub("    draw_axes(ctx, st)\n    draw_ogre_clubs(ctx, st)", "    draw_axes(ctx, st)\n    draw_pendulums(ctx, st)\n    draw_dominoes(ctx, st, True)\n    draw_ogre_clubs(ctx, st)")

# ------------------------------------------------------------------ 6. audio
sub('''        sunk_lava = L.get("sunk") is not None and L.get("sunk_kind") == "lava"
        met = L.get("content")''', '''        for pi3, pd in enumerate(PENDS):                         # LAB: whoosh every time the ball passes the bottom
            nn = -2
            while True:
                t_w = nn * pd["period"] / 2 - pd["phase"]
                nn += 1
                if t_w < 0.1:
                    continue
                if t_w > L["live_end"]:
                    break
                gain = float(np.clip(1.1 - abs(float(interp(rec["cx"], t_w)) - pd["x"]) / 16, 0.1, 1.0))
                place(sfx, synth_whoosh(), st0 + out_time(L, t_w - 0.2), 0.9 * gain)
        for di3, tt3 in sorted((L.get("dom_trig") or {}).items()):   # LAB: dominoes: rumble + a clack per tile
            dm = DOMS[di3]
            place(sfx, synth_eruption(seed=47 + di3), st0 + out_time(L, tt3), 0.45)
            for k in range(dm["n"]):
                t_l = tt3 + k * dm["delay"] + DOM_FALL
                if 0.1 < t_l <= L["live_end"]:
                    gain = float(np.clip(1.1 - abs(float(interp(rec["cx"], t_l)) - (dm["x0"] + k * DOM_GAP)) / 18, 0.15, 1.0))
                    place(sfx, synth_impact(0.45 + 0.02 * k, seed=500 + k), st0 + out_time(L, t_l), 0.6 * gain)
        notes_ = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66]
        for kb, (t_b, bi_, sp_b) in enumerate(L.get("bumps") or []):   # LAB: pinball: a bright note + thunk per bounce
            ob = st0 + out_time(L, t_b)
            place(sfx, tone(notes_[kb % len(notes_)], 0.35, "tri", decay=0.14), ob, 0.8)
            place(sfx, synth_impact(0.35, seed=600 + kb), ob, 0.6)
        sunk_lava = L.get("sunk") is not None and L.get("sunk_kind") == "lava"
        met = L.get("content")''')


sub("""def shake_offset(L, st):
    dx = dy = 0.0
""", """def shake_offset(L, st):
    dx = dy = 0.0
    if DOMS and L.get("dom_trig"):                                    # LAB: the road shakes while tiles fall near the car
        cxr = float(car_state(L, st)["cx"])
        for di_, tt_ in L["dom_trig"].items():
            d_ = DOMS[di_]
            near = sum(1 for k_ in range(d_["n"]) if 0 < st - tt_ - k_ * d_["delay"] < DOM_FALL + 0.2
                       and abs(d_["x0"] + k_ * DOM_GAP - cxr) < 16)
            if near and st < L["event"]["t"] + 1.0:
                dx += 3.2 * min(near, 4) * math.sin(st * 97)
                dy += 3.2 * min(near, 4) * math.cos(st * 83)
""")
sub("""    if any(0 < dx - front < 6.5 for dx in DANGER_X):
        return "scared\"""", """    if any(0 < dx - front < 6.5 for dx in DANGER_X) or (DOMS and L.get("dom_trig") and st > min(L["dom_trig"].values())
                                                       and st < L["event"]["t"]):
        return "scared\"""")


# ------------------------------------------------------------------ 7. speed class order (owner 2026-10-11)
# "mosok Grizzly atau Rocky lebih cepat dari si biru (Nitro) di jalan lurus?" Each level is simulated alone and its
# speed is drawn from the character's own range; the ranges overlap (monster 9-20 vs F1 8-20), so a monster could
# start faster than the F1 car in the next level. Rule (cast/CAST.md: Nitro "pembalap paling cepat", Zippy "super
# cepat", Titan "lambat"): a faster class never starts slower than a slower class in the same video.
sub("def pick_combo(rng, timed):", """SPEED_RANK = {"f1": 0, "sports": 1, "police": 2, "taxi": 2, "monster": 3, "monster2": 3, "firetruck": 4,
              "icecream": 4, "bus": 5, "bigrig": 6}                      # smaller = faster class
VEHICLES["f1"]["speeds"] = (11, 22)                                      # a race car never crawls at the start
VEHICLES["sports"]["speeds"] = (9.5, 18)


def speed_order_ok(Ls, tol=0.3):
    for a in Ls:
        for b in Ls:
            if SPEED_RANK[a["vk"]] < SPEED_RANK[b["vk"]] and a["speed"] < b["speed"] - tol:
                return False
    return True


def pick_combo(rng, timed):""")
sub("""        Ls = [timed[li][ci] for li, ci in enumerate(combo)]
        total = sum(L["dur"] for L in Ls)""", """        Ls = [timed[li][ci] for li, ci in enumerate(combo)]
        if not speed_order_ok(Ls):
            continue
        total = sum(L["dur"] for L in Ls)""")
open(DST, "w", encoding="utf-8").write(s)
print("wrote", DST, len(s.splitlines()), "lines")
