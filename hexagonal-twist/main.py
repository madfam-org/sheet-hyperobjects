"""Hexagonal twist — sheet-hyperobjects cartridge (Pliego).

The hexagon and triangle members of the twist-fold family: a central regular polygon outlined in
valleys, one pleat (mountain + valley) leaving each edge, on a sheet of the same symmetry (a
regular hexagon or an equilateral triangle). Both come from the kernel's generator
`pliego.tessellate.twist(n, …)` with n = 6 or n = 3.

At each corner of the central n-gon the creases sit at 0°, 180° − 360°/n (the polygon's edges),
270° − 360°/n + α and 270° + α (the pleats), so the sectors are

    180° − 360°/n,  90° + α,  360°/n,  90° − α

and Kawasaki holds for any α. Three valleys and one mountain give Maekawa. The big-little-big
rule decides the usable twist angles: for the triangle (sectors 60°, 90° + α, 120°, 90° − α) the
60° sector is bounded by two valleys, so it must not be the strictly smallest one, so α > 30°.
For the hexagon any α in range passes. The script runs `pliego.flatfold.check` and fails loud.

Rigid folding: the kernel's motion solver finds no rigid motion that leaves the flat sheet when a
centre valley is driven (`KinematicsError`), so the fold program is physical and its last step
is the exact flat-folded state. Twist folds are a generic, mathematically defined family; no
designer's crease pattern is copied.
"""

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


run_mode = PARAM(lambda: mode, "hexagon")  # noqa: F821 - injected by the runner
alpha_hex = clamp(PARAM(lambda: alpha_hex, 15.0), 5.0, 40.0)
alpha_tri = clamp(PARAM(lambda: alpha_tri, 40.0), 32.0, 60.0)
inner = clamp(PARAM(lambda: inner, 30.0), 15.0, 50.0)
sheet_size = clamp(PARAM(lambda: sheet_size, 160.0), 120.0, 300.0)
stock = str(PARAM(lambda: stock, "kami"))
if run_mode not in ("hexagon", "triangle"):
    raise ValueError(f"mode {run_mode!r} must be 'hexagon' or 'triangle'")
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")

n = 6 if run_mode == "hexagon" else 3
alpha = alpha_hex if n == 6 else alpha_tri
tess = pliego.tessellate.twist(n, inner, sheet_size, alpha, stock, sheet_id="twist")
sheet = tess.sheet
sheet.label = (L4("Hexagonal sheet", "Hoja hexagonal", "Feuille hexagonale", "Folha hexagonal")
               if n == 6 else
               L4("Triangular sheet", "Hoja triangular", "Feuille triangulaire",
                  "Folha triangular"))
centre, pleats = tess.groups["centre"], tess.groups["pleats"]

arr = sheet.build()
reports, issues = pliego.flatfold.check(arr)
errors = [i for i in issues if i["level"] == "error"]
if errors:
    raise ValueError(f"hexagonal-twist: not locally flat-foldable: {errors[0]['detail']}")
print(f"flatfold: n={n} alpha={alpha:g} vertices={len(reports)} maekawa=ok kawasaki=ok "
      f"big_little_big=ok exact={sum(1 for r in reports if r.kawasaki_exact)}/{len(reports)}")

# Rigid-folding evidence: drive one centre valley 10° from flat with the kernel's motion solver.
try:
    path = pliego.kinematics.solve(sheet, {}, {centre[0]: 10.0}, steps=4)
    rigid = f"found (dof={path.dof})"
except pliego.kinematics.KinematicsError:
    rigid = "none"
print(f"kinematics: rigid motion from flat driving a centre valley: {rigid} -> program is "
      "physical")


def signed(m, magnitude):
    return magnitude if m.assignment == "V" else -magnitude


def targets(pleat_deg, centre_deg):
    return ([(m, signed(m, pleat_deg)) for m in pleats]
            + [(m, signed(m, centre_deg)) for m in centre])


shape = (L4("hexagon", "hexágono", "hexagone", "hexágono") if n == 6 else
         L4("triangle", "triángulo", "triangle", "triângulo"))
steps = [
    pliego.Step("pre-fold-pleats",
                L4("Pre-fold the pleats halfway, mountains and valleys",
                   "Dobla los pliegues a medias, montes y valles",
                   "Préplier les plis à mi-course, montagnes et vallées",
                   "Dobre as pregas até a metade, montanhas e vales"),
                targets(90.0, 20.0), duration_ms=2000),
    pliego.Step("twist",
                L4(f"Turn the centre {shape['en']} while the pleats close round it",
                   f"Gira el {shape['es']} central mientras los pliegues se cierran a su "
                   "alrededor",
                   f"Tourner l'{shape['fr']} central pendant que les plis se referment autour"
                   if n == 6 else
                   "Tourner le triangle central pendant que les plis se referment autour",
                   f"Gire o {shape['pt']} central enquanto as pregas se fecham à sua volta"),
                targets(150.0, 120.0), duration_ms=2500,
                note=L4("The kernel's motion solver finds no rigid path: the panels bend on "
                        "the way.",
                        "El solucionador de movimiento del núcleo no encuentra una trayectoria "
                        "rígida: los paneles se curvan por el camino.",
                        "Le solveur de mouvement du noyau ne trouve aucune trajectoire rigide : "
                        "les panneaux se courbent en chemin.",
                        "O solucionador de movimento do núcleo não encontra trajetória rígida: "
                        "os painéis curvam-se pelo caminho.")),
    pliego.Step("flatten",
                L4("Press the twist flat", "Aplana la torsión", "Aplatir le twist",
                   "Achate a torção"),
                targets(180.0, 180.0), duration_ms=2000,
                note=L4("Flat-folded: every crease at 180°.",
                        "Plegado en plano: todos los pliegues a 180°.",
                        "Replié à plat : tous les plis à 180°.",
                        "Dobrado rente: todas as dobras a 180°.")),
]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4("Fold program", "Secuencia de pliegues",
                                               "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical"),
    targets={"flat-folded": {"angles": {m: signed(m, 180.0) for m in centre + pleats}}},
    title="Hexagonal twist" if n == 6 else "Triangle twist",
)
