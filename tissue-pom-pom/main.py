"""Tissue pom-pom (pompón de papel de china) — sheet-hyperobjects cartridge (Pliego).

A stack of tissue sheets pleated together like a fan, tied at the centre, its ends trimmed round
or pointed, then its layers pulled apart into a ball.

The stack. `sheets` identical sheets of papel de china, one sheet each in the document, lie on top
of each other one caliper apart (non-identity placements, so the document carries an `initial`
frame: the flat stack). Each sheet carries `pleats` − 1 pleat lines across its length (parallel
to its short side), alternately valley and mountain (treatment `crease`: the hand creases them),
and one `F` line along its middle, square to the pleats: where the tie gathers the stick. That
line is plain paper (treatment `none`).

The ends. The pleated stick is trimmed through every layer at once, so every panel gets the same
end: a semicircular lobe (`round`) or a point (`pointed`). The sheet outline is cut to that shape
from the start — the result is the same as trimming the folded stick, and it keeps each sheet one
connected piece for the studio preview. The trimmed outline is checked with
`pliego.papercut.analyze` against papel de china's minimum feature (1.5 mm).

The program (mode `make`, `kinematic`). The pleats are parallel and never cross, so pleating the
stack is an exact rigid motion: half closed (±90°), then closed up to ±178° — not 180°, since the
stack has thickness and the creases spring back a little (and the studio draws closed folds 0.5°
open anyway). It ends in the pleated stick, also written as the frame `target:pleated`.

The fanning is not a rigid motion. A pleated sheet whose panels stay flat can only take shapes that
are cylinders over a zigzag; it cannot fan out from a point. Real fanning bends and crushes the
tissue at the tie, which only a physics engine models. The frame `target:spread` is the closest
exact state: every pleat flat-folded (180°) and every sheet folded at the tie so that its two
halves lift by its own angle, the 2·`sheets` halves spaced evenly round the tie — the layers pulled
apart, before each half fans sideways into a half-disc and the halves fill a sphere.

Mode `hung`: the finished pom-pom for the physics engine. The spread state is its `initial` frame,
the tie is one `pin` join per sheet along its tie line (the thread holds that line where it is and
the pom-pom hangs from it), and a `wind` control moves it. No fold program: the rest is physics.
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


SLUG = "tissue-pom-pom"
STOCK = "papel-de-china"
MIN_FEATURE = 1.5            # mm, papel de china (materials/papel-de-china/stock.json)
CALIPER = 0.04               # mm, papel de china (estimated caliper of the stock card)
CLOSED = 178.0               # deg, how far the pleats close in the program
ROUND_SEGMENTS = 4           # segments per round lobe
APEX_TRIM = 1.0              # mm trimmed at the tip of each lobe (the stick's ends are cut clean)
PALETTES = {
    "pink": ["#e8336d"], "orange": ["#f28c28"], "yellow": ["#f6c445"], "turquoise": ["#1fa5a5"],
    "purple": ["#7a3e9d"], "tricolour": ["#006847", "#f4f4f0", "#ce1126"],
    "fiesta": ["#e8336d", "#f28c28", "#f6c445", "#1fa5a5", "#7a3e9d"],
}

mode = str(PARAM(lambda: mode, "make"))                                    # noqa: F821
n_sheets = int(pliego.clamp(PARAM(lambda: sheets, 6), 3, 10))             # noqa: F821
sheet_length = pliego.clamp(PARAM(lambda: sheet_length, 360.0), 150.0, 700.0)   # noqa: F821
sheet_width = pliego.clamp(PARAM(lambda: sheet_width, 250.0), 100.0, 500.0)     # noqa: F821
pleat = pliego.clamp(PARAM(lambda: pleat, 30.0), 15.0, 60.0)               # noqa: F821
ends = str(PARAM(lambda: ends, "round"))                                   # noqa: F821
colours = str(PARAM(lambda: colours, "pink"))                              # noqa: F821
wind = pliego.clamp(PARAM(lambda: wind, 1.0), 0.0, 8.0)                    # noqa: F821
if mode not in ("make", "hung"):
    raise ValueError(f"tissue-pom-pom: mode must be make or hung, got {mode!r}")
if ends not in ("round", "pointed"):
    raise ValueError(f"tissue-pom-pom: ends must be round or pointed, got {ends!r}")
if colours not in PALETTES:
    raise ValueError(f"tissue-pom-pom: colours must be one of {tuple(PALETTES)}, got {colours!r}")

n = max(4, round(sheet_length / pleat))     # panels per sheet
p = sheet_length / n                        # pleat width
Lx, Hy = sheet_length, sheet_width
depth = APEX_TRIM + (0.5 * p if ends == "round" else 0.9 * p)   # how far the trim reaches in
if Hy < 4.0 * depth:
    raise ValueError(f"tissue-pom-pom: a {Hy:g} mm sheet is too short for {p:.1f} mm pleats "
                     f"with {ends} ends")
mid = Hy / 2.0
HANG = mid + 50.0                           # height of the tie in the spread state (it hangs)


def end_profile(y_edge, sign):
    """The trimmed end along one long side: one lobe or point per panel, left to right.
    `sign` = −1 for the top edge (the trim reaches down), +1 for the bottom."""
    pts = [(0.0, y_edge + sign * depth)]
    for j in range(n):
        x0 = j * p
        if ends == "round":
            for i in range(1, ROUND_SEGMENTS):
                th = math.pi * i / ROUND_SEGMENTS
                pts.append((x0 + 0.5 * p * (1.0 - math.cos(th)),
                            y_edge + sign * (depth - (depth - APEX_TRIM) * math.sin(th))))
        else:
            pts.append((x0 + 0.5 * p, y_edge + sign * APEX_TRIM))
        pts.append((x0 + p, y_edge + sign * depth))
    return pts


bottom = end_profile(0.0, 1.0)
top = end_profile(Hy, -1.0)
outline = bottom + list(reversed(top))      # counter-clockwise
y_low, y_high = depth, Hy - depth           # where the pleat lines meet the trimmed ends


def make_sheet(k):
    col = PALETTES[colours][k % len(PALETTES[colours])]
    sh = pliego.Sheet(
        f"sheet-{k + 1}", outline, stock=STOCK, grain_deg=90.0,
        label=L4(f"Tissue sheet {k + 1}", f"Hoja de papel de china {k + 1}",
                 f"Feuille de papier de soie {k + 1}", f"Folha de papel de seda {k + 1}"),
        front=col, back=col,
        placement=pliego.Placement(origin=(0.0, k * CALIPER, 0.0)) if k else None)
    for j in range(1, n):
        sh.crease((j * p, y_low), (j * p, y_high), "valley" if j % 2 else "mountain", 180.0,
                  treatment="crease")
    sh.crease((0.0, mid), (Lx, mid), "flat", 0.0, treatment="crease", name="tie-line")
    return sh


sheets = [make_sheet(k) for k in range(n_sheets)]
cut_check = pliego.papercut.analyze(sheets[0], min_feature_mm=MIN_FEATURE)
if not cut_check.ok:
    raise ValueError(f"tissue-pom-pom: the trimmed sheet fails the papercut check: "
                     f"{cut_check.issues}")

arr = sheets[0].build()
verts = arr.vertices


def edge_kind(e):
    a, b = arr.edges[e]
    if arr.assignment[e] in ("M", "V"):
        return "pleat"
    if arr.assignment[e] == "F" and abs(verts[a].y - mid) < 1e-6 and abs(verts[b].y - mid) < 1e-6:
        return "tie"
    return "other"


pleat_e = [e for e in range(len(arr.edges)) if edge_kind(e) == "pleat"]
tie_e = [e for e in range(len(arr.edges)) if edge_kind(e) == "tie"]
if len(tie_e) != n:
    raise ValueError(f"tissue-pom-pom: expected {n} tie segments, found {len(tie_e)}")


def pleat_sign(e):
    a, _ = arr.edges[e]
    j = round(verts[a].x / p)
    return 1.0 if j % 2 else -1.0             # valley on odd lines, mountain on even


# ── the spread layers (target:spread): pleats flat-folded, each sheet folded at the tie ──
def lift_deg(k):
    """Both halves of sheet k (bottom → top) lift by this angle: the 2N halves sit evenly
    spaced, 180°/N apart, round the tie."""
    return -90.0 + (k + 0.5) * 180.0 / n_sheets


def spread(sheet_id, uv):
    k = int(sheet_id.split("-")[1]) - 1
    x, y = uv
    j = min(max(int(x / p), 0), n - 1)
    xf = (x - j * p) if j % 2 == 0 else (p - (x - j * p))    # the accordion folded flat
    yc = y - mid
    g = math.radians(lift_deg(k))
    return (xf, HANG + abs(yc) * math.sin(g), -yc * math.cos(g))


def isometric(pose, sheet_id):
    worst = 0.0
    for a, b in arr.edges:
        d0 = math.dist((verts[a].x, verts[a].y), (verts[b].x, verts[b].y))
        d1 = math.dist(pose(sheet_id, (verts[a].x, verts[a].y)),
                       pose(sheet_id, (verts[b].x, verts[b].y)))
        worst = max(worst, abs(d1 - d0))
    return worst


for sh in sheets:
    gap = isometric(spread, sh.id)      # vertices sit on the kernel's 1e-6 mm grid
    if gap > 1e-5:
        raise ValueError(f"tissue-pom-pom: the spread pose stretches {sh.id} by {gap} mm")

pleated = {e: pleat_sign(e) * CLOSED for e in pleat_e}
half = {e: pleat_sign(e) * 90.0 for e in pleat_e}

# the pleated stick: its footprint (from the kernel's face-tree pose)
stick = pliego.kinematics.pose_arrangement(arr, pleated)
xs = [q[0] for q in stick]
ys = [q[1] for q in stick]
render_vertices = n_sheets * sum(len(f) for f in arr.faces)
params = {"sheets": n_sheets, "sheet_length": Lx, "sheet_width": Hy, "pleat": pleat,
          "ends": ends, "colours": colours}
info = {"panels": n, "pleat_mm": round(p, 3), "trim_depth_mm": round(depth, 3),
        "stick_mm": [round(max(xs) - min(xs), 2), round(Hy, 1), round(max(ys) - min(ys), 2)],
        "ball_diameter_mm": round(Hy - 2.0 * APEX_TRIM, 1),
        "lifts_deg": [round(lift_deg(k), 2) for k in range(n_sheets)],
        "min_bridge_mm": cut_check.min_bridge_mm, "render_vertices": render_vertices}
print(f"tissue-pom-pom: {info}")


def targets(angles):
    return [(pliego.assembly.EdgeRef(sh, e), a) for sh in sheets for e, a in angles.items()]


ENDS = {"round": L4("round", "redondas", "arrondies", "redondas"),
        "pointed": L4("pointed", "en pico", "en pointe", "em bico")}[ends]
steps = [
    pliego.Step("pleat", L4("Pleat the whole stack like a fan, one pleat up, one pleat down",
                            "Dobla toda la pila en acordeón, un pliegue arriba y otro abajo",
                            "Pliez toute la pile en accordéon, un pli vers le haut, un vers le "
                            "bas", "Dobre a pilha toda em sanfona, uma dobra para cima e outra "
                            "para baixo"),
                targets(half), duration_ms=3000,
                note=L4(f"The ends of every panel are already cut {ENDS['en']}; in practice you "
                        "trim the folded stick, through every layer at once.",
                        f"Las puntas de cada panel ya están cortadas {ENDS['es']}; en la práctica "
                        "se recorta la tira ya doblada, todas las capas a la vez.",
                        f"Les extrémités de chaque panneau sont déjà coupées {ENDS['fr']} ; en "
                        "pratique, on taille le bâton plié, toutes les couches d'un coup.",
                        f"As pontas de cada painel já estão cortadas {ENDS['pt']}; na prática, "
                        "apara-se o bastão dobrado, todas as camadas de uma vez.")),
    pliego.Step("close-up", L4("Press the pleats closed into a narrow stick",
                               "Aprieta los pliegues hasta formar una tira angosta",
                               "Serrez les plis en un bâton étroit",
                               "Aperte as dobras até formar um bastão estreito"),
                targets(pleated), duration_ms=2500,
                note=L4("Tie the middle tightly with thread or wire; then pull the layers apart, "
                        "half up and half down (the frame target:spread), and fluff each one.",
                        "Amarra el centro bien apretado con hilo o alambre; luego separa las "
                        "capas, la mitad hacia arriba y la otra hacia abajo (el marco "
                        "target:spread), y esponja cada una.",
                        "Nouez le milieu bien serré avec du fil ou du fil de fer ; puis séparez "
                        "les couches, la moitié vers le haut et l'autre vers le bas (le cadre "
                        "target:spread), et faites gonfler chacune.",
                        "Amarre o meio bem apertado com linha ou arame; depois separe as camadas, "
                        "metade para cima e metade para baixo (o quadro target:spread), e afofe "
                        "cada uma.")),
]

if mode == "make":
    assembly = pliego.Assembly(
        sheets, controls=[pliego.sequence_control(label=L4("Pleat the stack", "Plisar la pila",
                                                           "Plisser la pile",
                                                           "Plissar a pilha"))],
        sequence=pliego.Sequence(steps, mode="kinematic"),
        targets={"pleated": {"angles": dict(pleated)}, "spread": spread},
        title="Tissue pom-pom")
else:
    # The finished pom-pom for the physics engine: the spread layers as the initial frame, the
    # tie as one `pin` per sheet holding its tie line where it is (the thread wound round the
    # centre, from which the pom-pom hangs), and the wind. The fluffing is left to the engine.
    params["wind"] = wind
    joins = [pliego.assembly.pin(f"tie-{k + 1}", along=(sh, [(0.0, mid), (Lx, mid)]))
             for k, sh in enumerate(sheets)]
    assembly = pliego.Assembly(
        sheets, joins=joins, initial=spread,
        controls=[pliego.control("wind", "wind", L4("Wind", "Viento", "Vent", "Vento"), wind,
                                 0.0, 8.0, "m/s")],
        targets={"spread": spread}, title="Tissue pom-pom")
doc = assembly.build(cartridge=SLUG, mode=mode, params=params)
# The tie line is plain paper (spec §4: F + `none`): it is where the thread gathers the stick, not
# a crease; the Sheet API authors F lines with a treatment, so it is marked untreated here.
tr = doc.data["pliego:edges_treatment"]
for e, a in enumerate(doc.data["edges_assignment"]):
    if a == "F" and tr[e] == "crease":
        tr[e] = "none"
result = doc.stamp()
