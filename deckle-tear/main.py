"""Deckle tear — sheet-hyperobjects cartridge (Pliego).

Torn and deckle edges: a strip is torn off a sheet and lifts away. Three modes:

* `crease` — fold, crease, tear: the strip is folded over along a line, opened, folded back the
  other way and opened again; the hard double crease weakens the fibres along the line and the
  strip tears off almost straight. The line is a kiss cut (`F` + `halfcut`): it folds, and it is
  the line along which the piece separates (spec §5.8).
* `deckle` — a free tear: the edge wanders and frays at the scale of the paper's fibres. The
  outline is a procedural deckle (seeded value noise, four octaves) whose amplitude and wavelength
  come from the stock's fibre length and from the tear's direction against the grain. Optionally
  every edge of the sheet is deckled, like a sheet of handmade paper.
* `ruler` — a strip torn upward against a straightedge: the ruler holds one side, so the edge stays
  on the free side of the ruler line and wanders less than a free tear.

The torn outline is generated geometry, not fracture physics. The cut piece (`excess`) separates
along it and the program's `remove` step lifts it away (spec §5.8); real tearing (stress, fibre
pull-out) is the engine's wave-3 work. Every random-looking outline is a deterministic function of
the `seed`: same parameters, same bytes.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "deckle")                          # noqa: F821
width = float(PARAM(lambda: width, 148.0))                    # noqa: F821
height = float(PARAM(lambda: height, 105.0))                  # noqa: F821
strip = float(PARAM(lambda: strip, 32.0))                     # noqa: F821
stock = PARAM(lambda: stock, "kraft-120")                     # noqa: F821
grain = PARAM(lambda: grain, "along")                         # noqa: F821
roughness = float(PARAM(lambda: roughness, 1.0))              # noqa: F821
seed = int(round(float(PARAM(lambda: seed, 7))))              # noqa: F821
all_edges = bool(PARAM(lambda: all_edges, False))             # noqa: F821

if mode not in ("crease", "deckle", "ruler"):
    raise ValueError(f"deckle-tear: unknown mode {mode!r}")
if grain not in ("along", "across"):
    raise ValueError(f"deckle-tear: grain must be 'along' or 'across', got {grain!r}")

# Fibre length (mm) per stock: engineering estimates for the fibre furnish (hardwood/softwood
# office and card pulps ≈ 1–3 mm, sack kraft is long softwood fibre, kozo bast fibre is several
# times longer) — they set the scale of the torn fringe, they are not measurements.
FIBRE_MM = {"copy-80": 1.5, "cardstock-160": 1.8, "kraft-120": 3.0, "washi-kozo-30": 8.0}
ISOTROPIC = {"washi-kozo-30"}        # handmade: no machine direction
if stock not in FIBRE_MM:
    raise ValueError(f"deckle-tear: stock {stock!r} is not offered (choose {sorted(FIBRE_MM)})")

W = pliego.clamp(width, 60.0, 300.0)
H = pliego.clamp(height, 40.0, 300.0)
ROUGH = pliego.clamp(roughness, 0.25, 2.0)
SEED = int(pliego.clamp(seed, 1, 9999))
FIB = FIBRE_MM[stock]
# Tearing across the grain wanders more than tearing along it (paper splits most easily between
# fibres lying along the machine direction); an isotropic sheet sits in between.
G_FACTOR = 1.3 if stock in ISOTROPIC else (1.0 if grain == "along" else 1.6)
AMP = {"crease": 0.0, "deckle": 0.6, "ruler": 0.25}[mode] * FIB * G_FACTOR * ROUGH
WAVE = 2.5 * FIB                     # longest noise wavelength (mm)
STEP = min(0.5, WAVE / 10.0)          # outline sampling (mm)
EDGE_AMP = 0.45 * FIB * ROUGH        # inward fray of a deckled outline (handmade sheet)
S = pliego.clamp(strip, 12.0 + 2.0 * AMP, W / 2.0)
X0 = W - S                           # the tear line (or the ruler's edge)
MIN_FEATURE = 1.0
GRAIN_DEG = 90.0 if grain == "along" else 0.0   # the tear runs along v


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def _hash01(i, salt):
    """A deterministic integer hash → [0, 1) (no randomness: same input, same value)."""
    h = (i * 374761393 + salt * 668265263 + SEED * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296.0


def noise(t, salt):
    """Four octaves of smoothed value noise in [−1, 1] along a coordinate t (mm)."""
    total, norm = 0.0, 0.0
    for octave, gain in enumerate((1.0, 0.55, 0.35, 0.2)):
        lam = WAVE / (2 ** octave)
        x = t / lam
        i = math.floor(x)
        f = x - i
        f = f * f * (3.0 - 2.0 * f)
        a = _hash01(i, salt * 7 + octave)
        b = _hash01(i + 1, salt * 7 + octave)
        total += gain * (2.0 * (a + (b - a) * f) - 1.0)
        norm += gain
    return total / norm


def samples(length):
    n = max(2, int(math.ceil(length / STEP)))
    return [length * k / n for k in range(n + 1)]


def ends(v):
    """0 at both ends of the torn line, 1 a wavelength in: a tear starts square to the edge."""
    t = min(1.0, max(0.0, min(v, H - v) / WAVE))
    return t * t * (3.0 - 2.0 * t)


def tear_x(v):
    """x of the torn line at height v (the line runs from v = 0 to v = H)."""
    if mode == "deckle":
        return X0 + AMP * ends(v) * noise(v, 1)
    if mode == "ruler":   # held by the ruler on the left: the edge stays on the free side
        return X0 + AMP * ends(v) * 0.5 * (noise(v, 1) + 1.0)
    return X0


FRAYED = all_edges and mode == "deckle"
P_LEN = 2.0 * (W + H)
MEET = (X0, 2.0 * W + H - X0)          # perimeter positions where the tear meets the outline


def fray(s):
    """Inward fray of a deckled outline at perimeter position s (continuous round the corners),
    zero where the torn line meets the outline."""
    d = min(min(abs(s - m), P_LEN - abs(s - m)) for m in MEET)
    win = 0.0 if d < 1.0 else min(1.0, (d - 1.0) / WAVE)
    return EDGE_AMP * win * 0.5 * (noise(s, 11) + 1.0)


# The outline, counter-clockwise from (0, 0). The perimeter is walked edge by edge; a deckled
# outline moves every point inward by fray(s) (corners along their bisector), so it stays simple.
if FRAYED:
    corners = [(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)]
    dirs = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]     # edge k's direction (CCW)
    ring, s0 = [], 0.0
    for k in range(4):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % 4]
        length = math.hypot(bx - ax, by - ay)
        ts = samples(length)[:-1]
        meet = [m - s0 for m in MEET if s0 < m < s0 + length]
        gap = EDGE_AMP + STEP              # no samples this near a corner but the corner itself
        ts = sorted(set([t for t in ts if t == 0.0 or gap < t < length - gap] + meet))
        nx, ny = -dirs[k][1], dirs[k][0]                         # its inward normal
        for t in ts:
            d = fray(s0 + t)
            if t == 0.0:   # the corner: inward along both edges' normals
                px, py = -dirs[k - 1][1], dirs[k - 1][0]
                ring.append((ax + (nx + px) * d, ay + (ny + py) * d))
            else:
                ring.append((ax + (bx - ax) * t / length + nx * d,
                             ay + (by - ay) * t / length + ny * d))
        s0 += length
else:
    ring = [(0.0, 0.0), (X0, 0.0), (W, 0.0), (W, H), (X0, H), (0.0, H)]

face = {"copy-80": "#f7f7f2", "cardstock-160": "#f4efe6", "kraft-120": "#b98a5a",
        "washi-kozo-30": "#f3eee2"}[stock]
sheet = pliego.Sheet("sheet", ring, stock=stock, grain_deg=GRAIN_DEG, front=face, back=face,
                     label=L4("Sheet", "Hoja", "Feuille", "Folha"))
# The end points sit on the outline's vertices (unfrayed there).
line_pts = [(X0, 0.0)] + [(tear_x(v), v) for v in samples(H)[1:-1]] + [(X0, H)]
if mode == "crease":
    tear = sheet.halfcut([line_pts[0], line_pts[-1]], name="tear-line",
                         label=L4("Crease, then tear", "Marca y luego rasga",
                                  "Marquer, puis déchirer", "Vincar e depois rasgar"))
else:
    tear = sheet.cut(line_pts, name="tear-line",
                     label=L4("Torn edge", "Borde rasgado", "Bord déchiré", "Borda rasgada"))

# Papercut check: exactly two pieces, and no torn tongue narrower than the minimum feature.
if mode != "crease":
    rep = pliego.papercut.analyze(sheet, min_feature_mm=MIN_FEATURE)
    if rep.components != 2:
        raise ValueError(f"deckle-tear: the torn line must part the sheet in two, "
                         f"got {rep.components} pieces")
    thin = [i for i in rep.issues if i["kind"] == "bridge_too_thin"]
    if thin:
        raise ValueError(f"deckle-tear: {thin[0]['detail']}; lower the roughness")
    bridge = rep.min_bridge_mm
else:
    bridge = None

body = pliego.piece("body", sheet, at=(X0 / 2.0, H / 2.0), role="keep",
                    label=L4("Sheet", "Hoja", "Feuille", "Folha"))
strip_piece = pliego.piece("strip", sheet, at=((X0 + AMP + W) / 2.0, H / 2.0), role="excess",
                           label=L4("Torn-off strip", "Tira rasgada", "Bande déchirée",
                                    "Tira rasgada"),
                           pull=[0.45, 1.0, 0.0])

steps = []
if mode == "crease":
    steps += [
        pliego.Step("fold-over", L4("Fold the strip over along the line",
                                    "Dobla la tira hacia delante por la línea",
                                    "Rabattre la bande le long de la ligne",
                                    "Dobre a tira para a frente pela linha"),
                    [(tear, 180.0)], duration_ms=1400,
                    note=L4("Press the fold hard with a bone folder or a thumbnail.",
                            "Marca el doblez con fuerza, con una plegadera o con la uña.",
                            "Marquez fortement le pli à l'os à plier ou à l'ongle.",
                            "Vinque a dobra com força, com uma dobradeira ou com a unha.")),
        pliego.Step("open", L4("Open it", "Ábrela", "L'ouvrir", "Abra"), [(tear, 0.0)],
                    duration_ms=900),
        pliego.Step("fold-back", L4("Fold it back the other way",
                                    "Dóblala hacia atrás, al otro lado",
                                    "La replier dans l'autre sens",
                                    "Dobre para trás, para o outro lado"),
                    [(tear, -180.0)], duration_ms=1400,
                    note=L4("Folding both ways breaks the fibres along the line.",
                            "Doblar hacia los dos lados rompe las fibras a lo largo de la línea.",
                            "Plier dans les deux sens casse les fibres le long de la ligne.",
                            "Dobrar para os dois lados quebra as fibras ao longo da linha.")),
        pliego.Step("open-again", L4("Open it again", "Ábrela de nuevo", "La rouvrir",
                                     "Abra de novo"), [(tear, 0.0)], duration_ms=900),
    ]
tear_label = {
    "crease": L4("Tear the strip off along the crease", "Desprende la tira por el pliegue",
                 "Détacher la bande le long du pli", "Destaque a tira pelo vinco"),
    "deckle": L4("Tear the strip away", "Arranca la tira", "Arracher la bande",
                 "Arranque a tira"),
    "ruler": L4("Tear the strip upward against the ruler", "Rasga la tira hacia arriba contra la regla",
                "Déchirer la bande vers le haut contre la règle",
                "Rasgue a tira para cima contra a régua"),
}[mode]
tear_note = {
    "crease": L4("Start at one end and pull slowly, close to the line.",
                 "Empieza por un extremo y jala despacio, cerca de la línea.",
                 "Commencer par un bout et tirer lentement, près de la ligne.",
                 "Comece por uma ponta e puxe devagar, perto da linha."),
    "deckle": L4("Pull the two halves apart slowly; the fibres fray along the edge.",
                 "Separa las dos partes despacio; las fibras se deshilachan en el borde.",
                 "Écarter lentement les deux parties ; les fibres s'effilochent sur le bord.",
                 "Separe as duas partes devagar; as fibras desfiam na borda."),
    "ruler": L4("Hold the ruler down firmly and pull the strip up and toward you.",
                "Sujeta firme la regla y jala la tira hacia arriba y hacia ti.",
                "Maintenir fermement la règle et tirer la bande vers le haut et vers soi.",
                "Segure firme a régua e puxe a tira para cima e na sua direção."),
}[mode]
steps.append(pliego.Step("tear", tear_label, duration_ms=1800, note=tear_note, remove=["strip"]))

print(f"deckle-tear: mode={mode} sheet={W:g}x{H:g}mm stock={stock} fibre={FIB:g}mm "
      f"grain={'isotropic' if stock in ISOTROPIC else grain} amplitude={AMP:.2f}mm "
      f"wavelength={WAVE:.1f}mm strip={S:.1f}mm seed={SEED} "
      f"min_bridge={'none-near' if bridge is None else round(bridge, 2)}")

clock = {"crease": L4("Crease and tear", "Marcar y rasgar", "Marquer et déchirer", "Vincar e rasgar"),
         "deckle": L4("Tear", "Rasgar", "Déchirer", "Rasgar"),
         "ruler": L4("Tear against the ruler", "Rasgar contra la regla", "Déchirer contre la règle",
                     "Rasgar contra a régua")}[mode]
result = pliego.Assembly([sheet], controls=[pliego.sequence_control(label=clock)],
                         sequence=pliego.Sequence(steps, mode="physical"),
                         pieces=[body, strip_piece], title="Deckle tear")
