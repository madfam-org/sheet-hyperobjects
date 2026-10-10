"""Stack-cut panel — sheet-hyperobjects cartridge (Pliego).

One cut through N stacked sheets. Papel picado workshops cut tissue paper in stacks, many sheets
at a time (the papel-picado-banner article cites the sources and credits the tradition of San
Salvador Huixcolotla, Puebla). Here a stack of N tissue panels is cut once, flat, so every panel
carries exactly the same openings; the panels come off the stack in a run of colours, and the
uncut strip at the top of each one folds over the string.

The motifs are ORIGINAL geometric designs generated here (no artisan's design is copied):
`rosette` — a ring of petals round a disc inside a ring of diamonds, with small flowers in the
corners; `lattice` — a field of diamonds in rows, with a sun of rays in the middle. Each panel
has a solid frame and a zigzag bottom edge. The openings are cut flat (no fold), so they are
drawn whole and mirror-symmetric by construction. `pliego.papercut.analyze` checks one panel (they
are identical): one connected piece, every bridge at least tissue's minimum feature (1.5 mm).

The panels are separate sheets laid 0.03 mm apart in the stack (no joins: a cut stack is loose).
The fold program folds every panel's string strip over, as each is hung (physical; the studio
preview plays it). The cut itself is not simulated: v1 documents describe the sheets after cutting.
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


STOCK, MF, GAP = "papel-de-china", 1.5, 0.03
COLOURS = ["#e8336d", "#f28c28", "#f6d32d", "#33a852", "#2a7de1", "#8e44ad"]
NAMES = [("pink", "rosa", "rose", "rosa"), ("orange", "naranja", "orange", "laranja"),
         ("yellow", "amarillo", "jaune", "amarelo"), ("green", "verde", "vert", "verde"),
         ("blue", "azul", "bleu", "azul"), ("purple", "morado", "violet", "roxo")]

sheets = int(clamp(PARAM(lambda: sheets, 6), 2, 12))
motif = str(PARAM(lambda: motif, "rosette"))
width = clamp(PARAM(lambda: width, 180.0), 120.0, 260.0)
height = clamp(PARAM(lambda: height, 240.0), 160.0, 340.0)
hem = clamp(PARAM(lambda: hem, 20.0), 12.0, 40.0)
if motif not in ("rosette", "lattice"):
    raise ValueError(f"motif {motif!r} must be rosette or lattice")

W, H = width, height
frame = 0.06 * min(W, H) + 3.0
tooth = 0.05 * H
x0, x1 = frame, W - frame
y0, y1 = tooth + frame, H - hem - frame
CX, CY = W / 2.0, (y0 + y1) / 2.0
PW, PH = x1 - x0, y1 - y0
if min(PW, PH) < 60.0:
    raise ValueError("the panel leaves less than 60 mm for the motif: enlarge it or lower the hem")


def ring_of(n, r, make):
    return [make(2 * math.pi * k / n, (CX + r * math.cos(2 * math.pi * k / n),
                                       CY + r * math.sin(2 * math.pi * k / n))) for k in range(n)]


def petal(at, length, wide, deg):
    return [(p.x, p.y) for p in pliego.papercut.petal(at, length, wide, deg, segments=6)]


def diamond(c, wdt, hgt, deg=0.0):
    a = math.radians(deg)
    pts = [(0.0, -hgt / 2), (wdt / 2, 0.0), (0.0, hgt / 2), (-wdt / 2, 0.0)]
    return [(c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))
            for x, y in pts]


def disc(c, r, n=12):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


holes = []
if motif == "rosette":
    r = 0.28 * min(PW, PH)
    r_in = 0.24 * r
    holes += [petal((CX + r_in * math.cos(math.radians(30 * k)),
                     CY + r_in * math.sin(math.radians(30 * k))),
                    r - r_in, 0.3 * (r - r_in), 30.0 * k) for k in range(12)]
    holes.append(disc((CX, CY), 0.5 * r_in))
    ring = r + max(0.12 * r, 4.0)
    holes += [diamond((CX + ring * math.cos(math.radians(15 + 30 * k)),
                       CY + ring * math.sin(math.radians(15 + 30 * k))),
                      max(0.07 * r, 3.0), max(0.16 * r, 6.0), 15 + 30 * k - 90) for k in range(12)]
    q = 0.17 * min(PW, PH)
    for sx in (-1, 1):
        for sy in (-1, 1):
            fx, fy = CX + sx * (PW / 2 - q), CY + sy * (PH / 2 - q)
            holes += [petal((fx + 0.12 * q * math.cos(math.radians(90 * k + 45)),
                             fy + 0.12 * q * math.sin(math.radians(90 * k + 45))),
                            0.6 * q, 0.34 * q, 90 * k + 45) for k in range(4)]
else:
    r = 0.2 * min(PW, PH)
    holes.append(disc((CX, CY), 0.4 * r))
    for k in range(16):
        a, h = math.radians(22.5 * k), math.radians(5.0)
        base, tip = 0.55 * r, (1.15 if k % 2 == 0 else 0.9) * r
        holes.append([(CX + base * math.cos(a - h), CY + base * math.sin(a - h)),
                      (CX + tip * math.cos(a), CY + tip * math.sin(a)),
                      (CX + base * math.cos(a + h), CY + base * math.sin(a + h))])
    step = 0.13 * min(PW, PH)
    nx, ny = int((PW / 2) // step), int((PH / 2) // step)
    for i in range(-nx, nx + 1):
        for j in range(-ny, ny + 1):
            x, y = CX + i * step + (step / 2 if j % 2 else 0.0), CY + j * step
            if math.hypot(x - CX, y - CY) < 1.15 * r + 0.35 * step + 2 * MF:
                continue
            if abs(x - CX) > PW / 2 - 0.4 * step or abs(y - CY) > PH / 2 - 0.4 * step:
                continue
            holes.append(diamond((x, y), 0.42 * step, 0.62 * step))

# outline: the rectangle with a zigzag bottom edge (teeth pointing down)
teeth = max(4, round(W / 22.0))
outline = [(0.0, tooth)] + [(W * k / (2 * teeth), 0.0 if k % 2 else tooth)
                            for k in range(1, 2 * teeth)] + [(W, tooth), (W, H), (0.0, H)]

panels = []
for k in range(sheets):
    colour = COLOURS[k % len(COLOURS)]
    n = NAMES[k % len(NAMES)]
    sheet = pliego.Sheet(
        f"panel-{k + 1}", outline, stock=STOCK, grain_deg=90.0, front=colour, back=colour,
        label=L4(f"Panel {k + 1} ({n[0]})", f"Banderita {k + 1} ({n[1]})",
                 f"Fanion {k + 1} ({n[2]})", f"Bandeirinha {k + 1} ({n[3]})"),
        placement=pliego.Placement(origin=(0.0, k * GAP, 0.0)))
    for h in holes:
        sheet.hole(h)
    sheet.crease((0.0, H - hem), (W, H - hem), "valley", 180.0,
                 label=L4("String strip", "Franja del cordel", "Bande de la ficelle",
                          "Faixa do cordel"))
    panels.append(sheet)

report = pliego.papercut.analyze(panels[0], min_feature_mm=MF)
if not report.ok:
    raise ValueError("stack-cut-panel papercut check failed: "
                     + "; ".join(i["detail"] for i in report.issues if i["level"] == "error"))

strips = [m for s in panels for m in s.marks if m.assignment == "V"]
steps = [
    pliego.Step("cut", L4("Cut the whole stack at once, flat: every panel gets the same openings",
                          "Corta toda la pila de una vez, en plano: cada banderita queda con los "
                          "mismos huecos",
                          "Découper toute la pile d'un coup, à plat : chaque fanion reçoit les "
                          "mêmes jours",
                          "Corte a pilha inteira de uma vez, estendida: cada bandeirinha fica com "
                          "os mesmos vazados"),
                [(m, 0.0) for m in strips], duration_ms=1500),
    pliego.Step("fold-strips", L4("Fold each panel's string strip over, to hang it",
                                  "Dobla la franja del cordel de cada banderita para colgarla",
                                  "Rabattre la bande de la ficelle de chaque fanion pour le pendre",
                                  "Dobre a faixa do cordel de cada bandeirinha para pendurá-la"),
                [(m, None) for m in strips], duration_ms=2500),
]
result = pliego.Assembly(
    panels,
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Stack-cut panel",
    meta={"min_feature_mm": MF},
)
print(f"stack-cut-panel: sheets={sheets} motif={motif} openings={len(holes)} "
      f"min_bridge={report.min_bridge_mm}")
