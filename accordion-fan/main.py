"""Accordion fan — sheet-hyperobjects cartridge (Pliego).

Two fans built on one geometry: a radial pleat. Every crease runs along a ray from one point O
(off the paper), alternately valley and mountain, with equal panel angles δ. Two modes:

- `hand-fan`: a rectangle whose pleats converge to a point below its base, so they gather at the
  base and spread at the top. One sheet; the program pleats it flat to closed and then spreads it.
- `folding-fan`: the paper leaf of a ribbed folding fan, an annular sector pleated radially,
  plus its ribs: separate sheets of card glued to the leaf and riveted together at O (pivot
  joins). The program closes the fan and opens it again.

**The rigid motion (closed form).** Number the rays r₀ … r_N from one edge of the fan. In a
symmetric state the even rays (valleys) stay in one plane, turned 2ψ apart, and the odd rays
(mountains) rise out of it by β, half-way between their neighbours in azimuth. Each panel keeps
its flat angle δ when

    cos δ = cos β · cos ψ

so ψ = δ is the flat sheet and ψ → 0 the closed stack. No crease ends inside the paper (O is off
the sheet), so there are no vertex loops to close and every such state is an exact rigid state;
the script still reads the fold angles off the 3-D model as signed dihedrals and checks loop
closure, the assignment and the panel angles. Hand fans with parallel pleats (the classroom
craft) can only be gathered by bending the paper; converging the pleats makes the fan rigid.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


run_mode = PARAM(lambda: mode, "hand-fan")  # noqa: F821 - injected by the runner
pleats = 2 * int(clamp(PARAM(lambda: pleats, 16), 8, 32) // 2)
spread = clamp(PARAM(lambda: spread, 0.85), 0.3, 0.95)
width = clamp(PARAM(lambda: width, 297.0), 150.0, 420.0)
height = clamp(PARAM(lambda: height, 105.0), 60.0, 210.0)
gather = clamp(PARAM(lambda: gather, 0.15), 0.08, 1.0)
radius = clamp(PARAM(lambda: radius, 220.0), 120.0, 350.0)
leaf_depth = clamp(PARAM(lambda: leaf_depth, 0.45), 0.25, 0.65)
fan_angle = clamp(PARAM(lambda: fan_angle, 150.0), 90.0, 180.0)
stock = str(PARAM(lambda: stock, "washi-kozo-30"))
if run_mode not in ("hand-fan", "folding-fan"):
    raise ValueError(f"mode {run_mode!r} must be 'hand-fan' or 'folding-fan'")
if stock not in ("washi-kozo-30", "kami", "copy-80", "kraft-120"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")
N = pleats
RIB_STOCK, RIB_WIDTH, RIB_HUB, RIB_GAP = "cardstock-300", 6.0, 6.0, 0.22
EdgeRef = pliego.assembly.EdgeRef


def polar(o, r, deg):
    return (o[0] + r * math.cos(math.radians(deg)), o[1] + r * math.sin(math.radians(deg)))


# ── the leaf ─────────────────────────────────────────────────────────────────

if run_mode == "hand-fan":
    # Rays from HUB = (width/2, −gather·height), equally spaced in angle between the rays to the
    # two top corners; the bottom corners outside those rays are trimmed (a trapezoid).
    HUB = (width / 2.0, -gather * height)
    th_start = math.degrees(math.atan2(height - HUB[1], width - HUB[0]))  # top-right corner
    th_end = math.degrees(math.atan2(height - HUB[1], -HUB[0]))  # top-left corner
    delta = (th_end - th_start) / N
    foot = width / 2.0 * gather / (1.0 + gather)                      # half the base width
    leaf = pliego.Sheet("leaf", [(width / 2.0 - foot, 0.0), (width / 2.0 + foot, 0.0),
                                 (width, height), (0.0, height)],
                        stock=stock, grain_deg=90.0,
                        label=L4("Fan sheet", "Hoja del abanico", "Feuille de l'éventail",
                                 "Folha do leque"))

    def crease_ends(deg):
        c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        return ((HUB[0] - c * HUB[1] / s, 0.0),
                (HUB[0] + c * (height - HUB[1]) / s, height))
else:
    th_start = 90.0 - fan_angle / 2.0
    th_end = 90.0 + fan_angle / 2.0
    delta = fan_angle / N
    r_in = radius * leaf_depth
    HUB = (0.0, 0.0)
    arc = [polar(HUB, radius, th_start + k * delta / 4.0) for k in range(4 * N + 1)]
    arc += [polar(HUB, r_in, th_start + k * delta / 4.0) for k in range(4 * N, -1, -1)]
    lo_x, lo_y = min(p[0] for p in arc), min(p[1] for p in arc)
    HUB = (HUB[0] - lo_x, HUB[1] - lo_y)
    arc = [(x - lo_x, y - lo_y) for x, y in arc]
    leaf = pliego.Sheet("leaf", arc, stock=stock, grain_deg=90.0,
                        label=L4("Fan leaf", "País del abanico", "Feuille de l'éventail",
                                 "Folha do leque"))

    def crease_ends(deg):
        return (polar(HUB, r_in, deg), polar(HUB, radius, deg))

marks = []
for k in range(1, N):
    a, b = crease_ends(th_start + k * delta)
    marks.append(leaf.crease(a, b, "valley" if k % 2 == 0 else "mountain"))
arr = leaf.build()


# ── the radial pleat in 3-D ──────────────────────────────────────────────────

def rays(psi, ysign):
    """World directions of r₀ … r_N (front of the flat sheet = +Y, sheet (u, v) ↦ (u, 0, −v))."""
    cb = math.cos(math.radians(delta)) / math.cos(math.radians(psi))
    beta = math.acos(max(-1.0, min(1.0, cb)))
    out = []
    for k in range(N + 1):
        az = math.radians(th_start + k * psi)
        if k % 2 == 0:
            out.append((math.cos(az), 0.0, -math.sin(az)))
        else:
            out.append((math.cos(beta) * math.cos(az), ysign * math.sin(beta),
                        -math.cos(beta) * math.sin(az)))
    return out


def leaf_point(R, u, v):
    """3-D position of the leaf point (u, v): inside the panel of its polar angle about HUB."""
    r = math.hypot(u - HUB[0], v - HUB[1])
    if r < 1e-9:
        return (0.0, 0.0, 0.0)
    phi = math.degrees(math.atan2(v - HUB[1], u - HUB[0]))
    j = min(N - 1, max(0, math.floor((phi - th_start) / delta)))
    al = math.radians(phi - th_start - j * delta)
    sd = math.sin(math.radians(delta))
    w1, w2 = math.sin(math.radians(delta) - al) / sd, math.sin(al) / sd
    return tuple(r * (w1 * R[j][i] + w2 * R[j + 1][i]) for i in range(3))


def newell(pts):
    nx = ny = nz = 0.0
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / m, ny / m, nz / m)


def fold_angles(world):
    verts = arr.vertices
    half = {}
    for fi, f in enumerate(arr.faces):
        for i in range(len(f)):
            half[(f[i], f[(i + 1) % len(f)])] = fi
    normals = []
    for f in arr.faces:
        flat = newell([(verts[v].x, 0.0, -verts[v].y) for v in f])
        nrm = newell([world[v] for v in f])
        normals.append(nrm if flat[1] > 0 else (-nrm[0], -nrm[1], -nrm[2]))
    out = {}
    for e, (a, b) in enumerate(arr.edges):
        if arr.assignment[e] in ("M", "V"):
            d = tuple(world[b][i] - world[a][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[half[(a, b)]],
                                                         normals[half[(b, a)]], d)
    return out


YSIGN = None
worst = 0.0


def state(psi):
    """Exact rigid state at half-step ψ: {edge: deg}, checked."""
    global YSIGN, worst
    for ys in ((YSIGN,) if YSIGN else (1.0, -1.0)):
        R = rays(psi, ys)
        world = [leaf_point(R, p.x, p.y) for p in arr.vertices]
        ang = fold_angles(world)
        if all((ang[e] > 0) == (arr.assignment[e] == "V") for e in ang):
            YSIGN = ys
            break
    else:
        raise ValueError("accordion-fan: the pleat disagrees with the assignment")
    for j in range(N):
        cos_panel = sum(R[j][i] * R[j + 1][i] for i in range(3))
        if abs(math.degrees(math.acos(max(-1.0, min(1.0, cos_panel)))) - delta) > 1e-7:
            raise ValueError(f"accordion-fan: panel {j} lost its flat angle")
    worst = max(worst, pliego.kinematics.closure_residual(arr, ang))
    return ang, R


psi_open, psi_closed = spread * delta, 0.04 * delta


def schedule(start, end, count):
    return [start + (end - start) * i / count for i in range(1, count + 1)]


def steps_for(psis, sid, label, note_fn):
    out = []
    for i, psi in enumerate(psis, 1):
        ang, _ = state(psi)
        out.append(pliego.Step(f"{sid}-{i}", {k: f"{v} ({i}/{len(psis)})" for k, v in
                                               label.items()},
                               [(EdgeRef(leaf, e), a) for e, a in sorted(ang.items())],
                               duration_ms=700, note=note_fn(psi)))
    return out


def note(psi):
    open_deg = N * psi
    return L4(f"Rigid state: the fan spans {open_deg:.0f}°.",
              f"Estado rígido: el abanico abarca {open_deg:.0f}°.",
              f"État rigide : l'éventail couvre {open_deg:.0f}°.",
              f"Estado rígido: o leque abrange {open_deg:.0f}°.")


CLOSE = L4("Fold every pleat together: the fan closes",
           "Dobla todos los pliegues a la vez: el abanico se cierra",
           "Plier tous les plis ensemble : l'éventail se referme",
           "Dobre todas as pregas juntas: o leque fecha-se")
OPEN = L4("Spread the top while the base stays gathered",
          "Abre la parte de arriba mientras la base se mantiene recogida",
          "Ouvrir le haut pendant que la base reste resserrée",
          "Abra a parte de cima enquanto a base fica recolhida")
LABEL = L4("Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras")

if run_mode == "hand-fan":
    steps = (steps_for(schedule(delta, psi_closed, 4), "close", CLOSE, note)
             + steps_for(schedule(psi_closed, psi_open, 3), "spread", OPEN, note))
    print(f"kinematics: hand fan pleats={N} delta={delta:.3f}° flat_span={N * delta:.1f}° "
          f"spread_span={N * psi_open:.1f}° interior_vertices=0 max_closure_mm={worst:.1e} "
          "(every state rigid)")
    result = pliego.Assembly([leaf], controls=[pliego.sequence_control(label=LABEL)],
                             sequence=pliego.Sequence(steps, mode="kinematic"),
                             title="Hand fan")
else:
    open_angles, R_open = state(psi_open)
    # Ribs: one card strip under each valley ray (and under both edges of the leaf), glued to the
    # panel beside it and riveted at HUB. The initial frame is the open fan.
    ribs, joins, rib_pose = [], [], {}
    rib_len = RIB_HUB + radius - 2.0
    for i, k in enumerate(range(0, N + 1, 2)):
        side = 1 if k < N else -1                       # panel on the counter-clockwise side
        c = 0.5 if side > 0 else RIB_WIDTH - 0.5        # rib-local v of the ray
        rib = pliego.Sheet(f"rib-{i}", pliego.rectangle(rib_len, RIB_WIDTH), stock=RIB_STOCK,
                           grain_deg=0.0, label=L4(f"Rib {i + 1}", f"Varilla {i + 1}",
                                                   f"Brin {i + 1}", f"Vareta {i + 1}"))
        ribs.append(rib)
        th = math.radians(th_start + k * delta)
        cs, sn = math.cos(th), math.sin(th)
        # rib-local (u, v) ↦ leaf-local HUB + Rot(θ_k)·(u − hub, v − c)
        tx = HUB[0] - cs * RIB_HUB + sn * c
        ty = HUB[1] - sn * RIB_HUB - cs * c
        lo, hi = (c + 0.3, RIB_WIDTH - 0.2) if side > 0 else (0.2, c - 0.3)
        u0, u1 = RIB_HUB + r_in + 2.0, RIB_HUB + radius - 4.0
        joins.append(pliego.glue(f"glue-rib-{i}", rib, [(u0, lo), (u1, lo), (u1, hi), (u0, hi)],
                                 leaf, (cs, -sn, sn, cs, tx, ty), side="back"))
        if i:
            joins.append(pliego.pivot(f"rivet-{i}", (rib, (RIB_HUB, c)),
                                      (ribs[0], (RIB_HUB, 0.5))))
        # world pose: along R_k, across the glued panel, just under it
        j = k if side > 0 else k - 1
        a, b = R_open[j], R_open[j + 1]
        axis = R_open[k]
        other = b if side > 0 else a
        t = [other[q] - sum(other[s] * axis[s] for s in range(3)) * axis[q] for q in range(3)]
        tn = math.sqrt(sum(x * x for x in t))
        t = [x / tn * side for x in t]          # rib-local +v direction (towards the panel if +1)
        nrm = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
        nn = math.sqrt(sum(x * x for x in nrm)) * (1 if nrm[1] > 0 else -1)
        nrm = [x / nn for x in nrm]
        rib_pose[rib.id] = (axis, t, nrm, c)

    def initial(sid, uv):
        if sid == "leaf":
            return leaf_point(R_open, uv[0], uv[1])
        axis, t, nrm, c = rib_pose[sid]
        return tuple((uv[0] - RIB_HUB) * axis[q] + (uv[1] - c) * t[q] - RIB_GAP * nrm[q]
                     for q in range(3))

    steps = (steps_for(schedule(psi_open, psi_closed, 4), "close", CLOSE, note)
             + steps_for(schedule(psi_closed, psi_open, 4), "open",
                         L4("Open the fan again", "Vuelve a abrir el abanico",
                            "Rouvrir l'éventail", "Abra o leque de novo"), note))
    print(f"kinematics: folding fan pleats={N} ribs={len(ribs)} delta={delta:.3f}° "
          f"open_span={N * psi_open:.1f}° interior_vertices=0 max_closure_mm={worst:.1e} "
          "(leaf states rigid; ribs follow through glue and rivet in the physics engine)")
    result = pliego.Assembly([leaf] + ribs, joins=joins,
                             controls=[pliego.sequence_control(label=LABEL)],
                             sequence=pliego.Sequence(steps, mode="kinematic"),
                             initial=initial, title="Folding fan")
