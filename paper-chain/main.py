"""Paper chain — sheet-hyperobjects cartridge (Pliego).

Strips of paper looped and glued into rings, each threaded through the one before, so the rings
interlock into a chain. N links are N sheets.

Segmentation. Each ring is a curved band, modelled as a prism of `sides` narrow flat panels: `F`
lines across the strip (treatment `none`: plain paper, never scored). The closed ring is an exact
isometry of the strip: a regular polygon prism whose side is one panel wide, inscribed radius
a = w / (2 tan(π/n)). The strip's last panels are the glue overlap; in the closed ring they lie
exactly on its first panels (inside), where a `glue` join welds them.

The chain hangs straight down. Link k's centre is p·k below the first one and its plane turns 90°
from link to link (planes XY and YZ alternately), so each ring passes through its neighbours. Two
neighbours cross at right angles: the lower sides of one ring rise by δ = rise(W/2) at the edge
of the other's band, and the other's upper sides fall by δ at the edge of this band, so the pitch
is p = 2a − 2δ − g, with g = `gap` the clearance left between them. The script checks that the
rings interlock (p < 2a) and that link k clears link k + 2 (p > circumradius). Contact between
links, and the sag of a real chain, are the physics engine's job.

Modes.
- `make`: the links are flat strips placed where their rings will hang (each sheet's placement puts
  its first panel at the bottom of its ring); a kinematic program loops and closes them one by one,
  ending in the chain (`target:chain`). The studio preview plays it.
- `glued`: the finished chain for the physics engine: glue welds, the first link pinned at its top
  (a `pin` join driven by a `translate` mechanism, control `lift`), `initial` = the chain.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


SLUG = "paper-chain"
STOCKS = {"copy-80": 1.0, "kraft-120": 1.0, "cardstock-160": 1.5, "papel-de-china": 1.5,
          "foil-paper": 1.5}
PALETTES = {
    "rainbow": ["#e94f37", "#f2b134", "#3bb273", "#2e86ab", "#7768ae", "#e8336d"],
    "festive": ["#c8102e", "#1b7f3b", "#e8b923"],
    "kraft": ["#b98a5a", "#f4efe6"],
}

mode = str(PARAM(lambda: mode, "make"))                                    # noqa: F821
links = int(pliego.clamp(PARAM(lambda: links, 8), 2, 16))                 # noqa: F821
strip_length = pliego.clamp(PARAM(lambda: strip_length, 200.0), 100.0, 300.0)   # noqa: F821
strip_width = pliego.clamp(PARAM(lambda: strip_width, 25.0), 10.0, 50.0)        # noqa: F821
overlap = pliego.clamp(PARAM(lambda: overlap, 20.0), 10.0, 40.0)               # noqa: F821
sides = int(pliego.clamp(PARAM(lambda: sides, 18), 10, 32))               # noqa: F821
gap = pliego.clamp(PARAM(lambda: gap, 1.0), 0.5, 10.0)                    # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))                              # noqa: F821
palette = str(PARAM(lambda: palette, "rainbow"))                          # noqa: F821
if mode not in ("make", "glued"):
    raise ValueError(f"paper-chain: mode must be make or glued, got {mode!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-chain: stock must be one of {tuple(STOCKS)}, got {stock!r}")
if palette not in PALETTES:
    raise ValueError(f"paper-chain: palette must be one of {tuple(PALETTES)}, got {palette!r}")

C = strip_length - overlap          # ring circumference
n = sides + sides % 2               # even: every ring has a flat side at its top and bottom
w = C / n                           # panel width
m = max(1, round(overlap / w))      # overlap panels (the overlap is resized to whole panels)
ov = m * w
L_strip = C + ov
W = strip_width
a = w / (2.0 * math.tan(math.pi / n))           # inscribed radius
R = w / (2.0 * math.sin(math.pi / n))           # circumradius


def rise(x):
    """Height of the ring's lower boundary above its flat bottom side at offset x (|x| < R)."""
    best = 0.0
    for j in range(n):
        t = -math.pi / 2.0 + 2.0 * math.pi * j / n
        if math.sin(t) < -1e-9:
            best = max(best, (a - x * math.cos(t)) / math.sin(t) + a)
    return best


# Two neighbouring rings cross at right angles: this ring's lower sides, rising by rise(W/2) at
# the edge of the next ring's band, must pass under the next ring's upper sides, which fall by
# the same amount at the edge of this ring's band; `gap` is the clearance left between them.
p = 2.0 * a - 2.0 * rise(W / 2.0) - gap          # pitch between link centres
if not p < 2.0 * a - 1.0:
    raise ValueError("paper-chain: the rings would not interlock; lower the gap")
if not p > R + 1e-9:
    raise ValueError(f"paper-chain: {W:g} mm strips are too wide for {C:g} mm rings to link "
                     "without touching their second neighbour; make the strips narrower or "
                     "longer")
CH = min(3.0, W / 4.0)              # chamfer of the overlap's corners

# ── one strip (all links share its geometry) ──
outline = [(0.0, 0.0), (L_strip - CH, 0.0), (L_strip, CH), (L_strip, W - CH),
           (L_strip - CH, W), (0.0, W)]


def make_strip(k):
    colour = PALETTES[palette][k % len(PALETTES[palette])]
    s = pliego.Sheet(f"link-{k + 1}", outline, stock=stock, grain_deg=0.0,
                     label=L4(f"Link {k + 1}", f"Eslabón {k + 1}", f"Maillon {k + 1}",
                              f"Elo {k + 1}"),
                     front=colour, back=colour)
    for j in range(1, n + m):
        s.crease((j * w, 0.0), (j * w, W), "flat", 0.0, treatment="crease",
                 name="overlap" if j == n else None)
    return s


# ── the closed ring in the strip's un-placed frame: polygon in the x–y plane, axis −z ──
def ring_local(uv):
    u, v = uv
    k = min(max(int(u / w + 1e-9), 0), n + m - 1)
    s = (u - k * w) / w
    a0 = -math.pi / 2.0 - math.pi / n
    c0 = (w / 2.0 + R * math.cos(a0 + 2.0 * math.pi * (k % n) / n),
          a + R * math.sin(a0 + 2.0 * math.pi * (k % n) / n))
    c1 = (w / 2.0 + R * math.cos(a0 + 2.0 * math.pi * ((k + 1) % n) / n),
          a + R * math.sin(a0 + 2.0 * math.pi * ((k + 1) % n) / n))
    return (c0[0] + s * (c1[0] - c0[0]), c0[1] + s * (c1[1] - c0[1]), -v)


CENTRE = (w / 2.0, a, -W / 2.0)       # ring centre in the un-placed frame
TOP = (links - 1) * p + a + 20.0      # the first link's centre height: the last clears the table
Q_EVEN = (0.0, 0.0, 0.0, 1.0)
Q_ODD = (0.0, math.sqrt(0.5), 0.0, math.sqrt(0.5))      # 90° about y: plane XY → plane YZ


def rot(q, v):
    x, y, z, s = q
    tx, ty, tz = 2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])
    return (v[0] + s * tx + (y * tz - z * ty), v[1] + s * ty + (z * tx - x * tz),
            v[2] + s * tz + (x * ty - y * tx))


def placement(k):
    q = Q_ODD if k % 2 else Q_EVEN
    rc = rot(q, CENTRE)
    return q, (-rc[0], TOP - k * p - rc[1], -rc[2])


strips = []
for k in range(links):
    s = make_strip(k)
    q, o = placement(k)
    s.placement = pliego.Placement(origin=o, rotation=q)
    strips.append(s)

cut_check = pliego.papercut.analyze(strips[0], min_feature_mm=STOCKS[stock])
if not cut_check.ok:
    raise ValueError(f"paper-chain: the strip fails the papercut check: {cut_check.issues}")

arr = strips[0].build()


def newell(pts):
    nv = [0.0, 0.0, 0.0]
    for i, pt in enumerate(pts):
        qt = pts[(i + 1) % len(pts)]
        nv[0] += (pt[1] - qt[1]) * (pt[2] + qt[2])
        nv[1] += (pt[2] - qt[2]) * (pt[0] + qt[0])
        nv[2] += (pt[0] - qt[0]) * (pt[1] + qt[1])
    s = math.sqrt(nv[0] ** 2 + nv[1] ** 2 + nv[2] ** 2)
    return (nv[0] / s, nv[1] / s, nv[2] / s)


def fold_angles(pose):
    """Signed fold angle (FOLD convention, deg) of every interior F/M/V edge of the strip."""
    pts = [pose((vx.x, vx.y)) for vx in arr.vertices]
    left = {}
    for fi, f in enumerate(arr.faces):
        for k in range(len(f)):
            left[(f[k], f[(k + 1) % len(f)])] = fi
    normals = [newell([pts[v] for v in f]) for f in arr.faces]
    out = {}
    for e, (ea, eb) in enumerate(arr.edges):
        if arr.assignment[e] in ("F", "M", "V") and (ea, eb) in left and (eb, ea) in left:
            d = tuple(pts[eb][i] - pts[ea][i] for i in range(3))
            out[e] = pliego.tessellate.signed_fold_angle(normals[left[(ea, eb)]],
                                                         normals[left[(eb, ea)]], d)
    return out


angles = fold_angles(ring_local)
if min(angles.values()) <= 0.0:
    raise ValueError("paper-chain: the ring pose is not a valley roll (orientation error)")
verts = arr.vertices


def edge_u(e):
    ea, eb = arr.edges[e]
    return (verts[ea].x + verts[eb].x) / 2.0


band_e = [e for e in angles if edge_u(e) < C - w / 2.0]
lap_e = [e for e in angles if e not in band_e]

inset = 1.0
region = [(C + inset, inset), (L_strip - CH, inset), (L_strip - inset, CH),
          (L_strip - inset, W - CH), (L_strip - CH, W - inset), (C + inset, W - inset)]
glue_map = (1.0, 0.0, 0.0, 1.0, -C, 0.0)
for pt in region:
    gap_mm = math.dist(ring_local(pt), ring_local((pt[0] - C, pt[1])))
    if not strips[0].region_contains(pt) or gap_mm > 1e-6:
        raise ValueError(f"paper-chain: weld point {pt} misses its glue zone ({gap_mm} mm)")


def chain(sheet_id, uv):
    k = int(sheet_id.split("-")[1]) - 1
    q, o = placement(k)
    lp = rot(q, ring_local(uv))
    return (lp[0] + o[0], lp[1] + o[1], lp[2] + o[2])


params = {"links": links, "strip_length": strip_length, "strip_width": strip_width,
          "overlap": overlap, "sides": sides, "gap": gap, "stock": stock, "palette": palette}
print(f"paper-chain: links={links} ring_inscribed_radius={a:.2f}mm circumradius={R:.2f}mm "
      f"pitch={p:.2f}mm crossing_gap={gap:g}mm overlap_panels={m} chain_length={(links - 1) * p + 2 * a:.0f}mm")

if mode == "make":
    steps = []
    for k, s in enumerate(strips):
        first = k == 0
        label = (L4("Loop the first strip into a ring and glue the ends",
                    "Enrolla la primera tira en un aro y pega los extremos",
                    "Bouclez la première bande en anneau et collez les extrémités",
                    "Enrole a primeira tira num aro e cole as pontas") if first else
                 L4(f"Pass strip {k + 1} through link {k}, loop it and glue the ends",
                    f"Pasa la tira {k + 1} por el eslabón {k}, ciérrala en aro y pega los "
                    "extremos", f"Passez la bande {k + 1} dans le maillon {k}, bouclez-la et "
                    "collez les extrémités", f"Passe a tira {k + 1} pelo elo {k}, feche-a em aro "
                    "e cole as pontas"))
        targets = [(pliego.assembly.EdgeRef(s, e), angles[e]) for e in band_e + lap_e]
        steps.append(pliego.Step(f"link-{k + 1}", label, targets, duration_ms=1500))
    assembly = pliego.Assembly(
        strips, controls=[pliego.sequence_control(label=L4("Make the chain", "Hacer la cadena",
                                                           "Faire la chaîne",
                                                           "Fazer a corrente"))],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"chain": {s.id: {"angles": dict(angles)} for s in strips}},
        title="Paper chain")
else:
    joins = [pliego.glue(f"seam-{k + 1}", s, region, s, glue_map, "front")
             for k, s in enumerate(strips)]
    # the first link hangs from the point of its band at the top of its ring (mid-width)
    top_u = (n // 2 + 0.5) * w
    joins.append(pliego.pin("hang", (strips[0], (top_u, W / 2.0)), world=None,
                            mechanism="raise"))
    lift = pliego.control("lift", "distance", L4("Lift the chain", "Levantar la cadena",
                                                 "Soulever la chaîne", "Levantar a corrente"),
                          0.0, 0.0, 100.0, "mm")
    assembly = pliego.Assembly(
        strips, joins=joins, initial=chain, controls=[lift],
        mechanisms=[pliego.translate("raise", "lift", (0.0, 1.0, 0.0), 100.0)],
        targets={"chain": chain}, title="Paper chain")

doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The panel lines are plain paper (spec §4: F + `none`); the Sheet API authors F lines with a
# treatment, so they are marked untreated here: exporters must not score a curved strip.
tr = doc.data["pliego:edges_treatment"]
for e, asg in enumerate(doc.data["edges_assignment"]):
    if asg == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
