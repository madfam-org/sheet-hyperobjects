"""Screenfold codex — sheet-hyperobjects cartridge (Pliego).

The book form of Mesoamerica: a long strip of bark paper (amate) folded back and forth like a
screen into leaves, its surface coated white on both sides for painting. This cartridge builds
the structure only — a blank strip on the `amate` stock card with gesso-white leaves — and never
reproduces the imagery of any historical codex.

Geometry: `leaves` equal leaves, `leaf_width` × `height`, separated by creases that alternate
valley and mountain. All folds are parallel, so the folds never meet and the kinematic program,
linear in the angles, is exact:

1. fold the strip closed into a stack of leaves (valley +180°, mountain −180°, shut a hair short
   so the leaves stay in order);
2. open it into a standing screen, neighbouring leaves `display_angle` apart, as screenfolds are
   shown, reading a run of pages at once.

The strip stands upright (its v axis is world up). `surface = gesso` gives both faces the white
of the ground layer; `bare` shows the amate stock's own colour.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


leaves = round(float(PARAM(lambda: leaves, 10)))              # noqa: F821
leaf_width = float(PARAM(lambda: leaf_width, 100.0))          # noqa: F821
height = float(PARAM(lambda: height, 200.0))                  # noqa: F821
surface = PARAM(lambda: surface, "gesso")                     # noqa: F821
display_angle = float(PARAM(lambda: display_angle, 90.0))     # noqa: F821

if surface not in ("gesso", "bare"):
    raise ValueError(f"screenfold-codex: surface must be gesso or bare, got {surface!r}")
if not 4 <= leaves <= 48:
    raise ValueError(f"screenfold-codex: leaves must be an integer in [4, 48], got {leaves}")

n = leaves
w = pliego.clamp(leaf_width, 40.0, 200.0)
h = pliego.clamp(height, 60.0, 400.0)
gamma = pliego.clamp(display_angle, 20.0, 170.0)     # angle between neighbouring leaves, shown
GESSO = "#f2eee3"                                    # the white ground (front and back)
SHUT = 179.0                                         # closed: each fold a degree short of flat
UPRIGHT = (0.7071067811865476, 0.0, 0.0, 0.7071067811865476)   # +90° about X: v → world up


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


faces = {"front": GESSO, "back": GESSO} if surface == "gesso" else {}
strip = pliego.Sheet(
    "screenfold", [(0, 0), (n * w, 0), (n * w, h), (0, h)], stock="amate", grain_deg=0.0,
    placement=pliego.Placement(rotation=UPRIGHT),
    label=L4("Screenfold strip", "Tira del códice biombo", "Bande du codex en paravent",
             "Tira do códice em biombo"), **faces)
strip.label_edge("end-first", (0, 0), (0, h))
strip.label_edge("end-last", (n * w, 0), (n * w, h))
folds = []
for k in range(1, n):
    kind = "valley" if k % 2 else "mountain"
    folds.append(strip.crease((k * w, 0), (k * w, h), kind, 180.0, name="leaf-fold"))

arr = strip.build()
if len(arr.faces) != n:
    raise ValueError("screenfold-codex: the strip did not divide into its leaves")


def state(mag):
    out = {}
    for m in folds:
        for e in m.edges():
            out[e] = mag if m.assignment == "V" else -mag
    return out


for mag in (SHUT, 180.0 - gamma):
    if pliego.kinematics.closure_residual(arr, state(mag)) > 1e-6:
        raise ValueError("screenfold-codex: a key state is not rigid")

steps = [
    pliego.Step("close", L4("Fold the strip closed, leaf by leaf, like a screen",
                            "Pliega la tira hoja por hoja, como un biombo",
                            "Repliez la bande feuillet par feuillet, comme un paravent",
                            "Dobre a tira folha por folha, como um biombo"),
                [(m, SHUT if m.assignment == "V" else -SHUT) for m in folds],
                duration_ms=3500,
                note=L4(f"{n} leaves, {2 * n} pages: both faces carry a white ground. The strip "
                        f"is {n * w / 10:g} cm long unfolded.",
                        f"{n} hojas, {2 * n} páginas: las dos caras llevan una base blanca. "
                        f"Desplegada, la tira mide {n * w / 10:g} cm.",
                        f"{n} feuillets, {2 * n} pages : les deux faces portent un fond blanc. "
                        f"Dépliée, la bande mesure {n * w / 10:g} cm.",
                        f"{n} folhas, {2 * n} páginas: as duas faces levam uma base branca. "
                        f"Aberta, a tira mede {n * w / 10:g} cm.")),
    pliego.Step("display", L4(f"Stand it open as a screen, leaves {gamma:g}° apart",
                              f"Ábrelo de pie como biombo, con las hojas a {gamma:g}°",
                              f"Dressez-le ouvert en paravent, feuillets à {gamma:g}°",
                              f"Abra-o de pé como biombo, com as folhas a {gamma:g}°"),
                [(m, (180.0 - gamma) * (1 if m.assignment == "V" else -1)) for m in folds],
                duration_ms=3000),
]

print(f"screenfold: leaves={n} pages={2 * n} leaf={w:g}x{h:g}mm strip={n * w:g}mm "
      f"surface={surface} display={gamma:g}deg")

result = pliego.Assembly(
    [strip],
    controls=[pliego.sequence_control(label=L4("Fold and display", "Plegar y exhibir",
                                               "Plier et présenter", "Dobrar e expor"))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    title="Screenfold codex",
)
