"""Outside reverse fold — sheet-hyperobjects cartridge (Pliego).

A strip is folded in half along its spine; a reverse crease pair meets the spine at one vertex V.
The four creases at V form a flat-foldable degree-4 vertex with sector angles
(180° − β, β, β, 180° − β), β being the acute angle between the BODY's spine and the reverse
crease, so the flap's sectors are obtuse. Every fold state comes from the Foschi–Hull–Ku closed
forms in `pliego.kinematics`:

- mode 1 (k = 0 at this vertex): the spine folds, the reverse creases stay flat — folding in half;
- the flat-folded branch at spine = 180°: both layers turn together about the coincident reverse
  creases — the precrease;
- mode 2, driven negative: the reverse creases fold as mountains, the flap's spine flips to a
  mountain and the flap wraps around the outside of the body — the outside reverse fold (the
  positive drive of the same mode is the inside reverse fold of the other side).

The two modes meet only at the flat sheet, so the rigid program opens the strip before collapsing
along mode 2 (mode `rigid`, kinematic). Mode `hand` drives the same creases straight from the
folded strip and leaves the bending to the paper (physical).

All geometry is computed here; the move is traditional (no designer's diagram is used).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


length = float(PARAM(lambda: length, 200.0))
width = float(PARAM(lambda: width, 60.0))
angle = float(PARAM(lambda: angle, 45.0))
position = float(PARAM(lambda: position, 0.5))
stock = PARAM(lambda: stock, "kami")
run_mode = PARAM(lambda: mode, "rigid")  # noqa: F821 - injected by the runner

length = max(120.0, min(300.0, length))
width = max(30.0, min(120.0, width))
angle = max(25.0, min(65.0, angle))
position = max(0.35, min(0.75, position))
COLLAPSE_STEPS = 8
TOL_MM = 1e-5  # mm; vertex coordinates are grid-snapped by the arrangement


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── geometry ──────────────────────────────────────────────────────────────────

half = width / 2.0
vx = position * length
V = (vx, half)


def ray_to_boundary(origin, deg):
    """Where the ray from `origin` at `deg` leaves the rectangle [0, length] × [0, width]."""
    dx, dy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    hits = []
    if dx > 1e-12:
        hits.append((length - origin[0]) / dx)
    if dx < -1e-12:
        hits.append(-origin[0] / dx)
    if dy > 1e-12:
        hits.append((width - origin[1]) / dy)
    if dy < -1e-12:
        hits.append(-origin[1] / dy)
    t = min(h for h in hits if h > 0)
    return (origin[0] + t * dx, origin[1] + t * dy)


sheet = pliego.Sheet(
    "strip", pliego.rectangle(length, width), stock=stock,
    label=L4("Strip", "Tira", "Bande", "Tira"),
    front="#f4efe6", back="#c8553d",
)
# CCW around V, starting at the flap's spine: e1, e2, e3, e4 (sectors 180−β, β, β, 180−β)
flap_spine = sheet.mountain(V, (length, half), label=L4(
    "Flap spine", "Lomo de la solapa", "Dos du rabat", "Lombada da aba"))
reverse_up = sheet.mountain(V, ray_to_boundary(V, 180.0 - angle), label=L4(
    "Reverse crease (front layer)", "Pliegue invertido (capa delantera)",
    "Pli inversé (couche avant)", "Dobra invertida (camada da frente)"))
body_spine = sheet.valley((0.0, half), V, label=L4(
    "Body spine", "Lomo del cuerpo", "Dos du corps", "Lombada do corpo"))
reverse_down = sheet.mountain(V, ray_to_boundary(V, 180.0 + angle), label=L4(
    "Reverse crease (back layer)", "Pliegue invertido (capa trasera)",
    "Pli inversé (couche arrière)", "Dobra invertida (camada de trás)"))
CREASES = (flap_spine, reverse_up, body_spine, reverse_down)
arr = sheet.build()
EDGE = [m.edges()[0] for m in CREASES]
ROOT = pliego.P(vx / 2.0, half + 0.5)  # just above the spine, on the body's front layer


def mode2(drive):
    return kinematics.degree4_mode2(180.0 - angle, angle, drive)


def state(rho):
    return dict(zip(EDGE, rho))


def residuals(rho):
    """(closure residual, worst edge-length change) of one fold state, in mm."""
    ang = state(rho)
    closure = kinematics.closure_residual(arr, ang, ROOT)
    pose = kinematics.pose_arrangement(arr, ang, ROOT)
    worst = 0.0
    for a, b in arr.edges:
        flat = arr.vertices[a].distance(arr.vertices[b])
        worst = max(worst, abs(math.dist(pose[a], pose[b]) - flat))
    return closure, worst


def arc_samples(curve, n):
    """n states along curve(t), t ∈ (0, 1], evenly spaced in fold-angle arc length."""
    fine = [curve(i / 400.0) for i in range(401)]
    cum = [0.0]
    for i in range(400):
        cum.append(cum[-1] + math.dist(fine[i], fine[i + 1]))
    out, j = [], 0
    for k in range(1, n + 1):
        goal = cum[-1] * k / n
        while j < 400 and cum[j + 1] < goal:
            j += 1
        out.append(curve(min(1.0, (j + 1) / 400.0)) if k < n else curve(1.0))
    return out


# ── the fold program ─────────────────────────────────────────────────────────

FOLDED = (180.0, 0.0, 180.0, 0.0)
PRECREASED = (180.0, -180.0, 180.0, 180.0)
FLAT = (0.0, 0.0, 0.0, 0.0)
FINAL = mode2(-180.0)  # (−180, −180, 180, −180): body spine valley, the rest mountain

program = [
    ("fold-in-half", L4("Valley-fold the strip in half along its spine",
                        "Dobla la tira por la mitad en valle, a lo largo del lomo",
                        "Pliez la bande en deux en vallée, le long du dos",
                        "Dobre a tira ao meio em vale, ao longo da lombada"), FOLDED, 1500),
    ("precrease", L4("Fold the flap back behind through both layers",
                     "Dobla la solapa hacia atrás a través de las dos capas",
                     "Rabattez le rabat vers l'arrière à travers les deux couches",
                     "Dobre a aba para trás através das duas camadas"), PRECREASED, 1200),
    ("unfold-precrease", L4("Unfold the flap: the reverse crease is marked",
                            "Desdobla la solapa: el pliegue invertido queda marcado",
                            "Dépliez le rabat : le pli inversé est marqué",
                            "Desdobre a aba: a dobra invertida fica marcada"), FOLDED, 1000),
]
if run_mode == "hand":
    program.append(("reverse", L4(
        "Open the flap and wrap it around the outside of the body, then flatten",
        "Abre la solapa y envuélvela por fuera del cuerpo; luego aplana",
        "Ouvrez le rabat et enveloppez-le autour du corps, puis aplatissez",
        "Abra a aba e envolva-a por fora do corpo; depois achate"), FINAL, 2500))
else:
    program.append(("open-flat", L4(
        "Open the strip flat: the two rigid modes meet only here",
        "Abre la tira en plano: los dos modos rígidos solo se cruzan aquí",
        "Ouvrez la bande à plat : les deux modes rigides ne se croisent qu'ici",
        "Abra a tira no plano: os dois modos rígidos só se cruzam aqui"), FLAT, 1500))
    samples = arc_samples(lambda t: mode2(-180.0 * t), COLLAPSE_STEPS)
    for k, rho in enumerate(samples, 1):
        program.append((f"collapse-{k}", L4(
            f"Collapse along the creases, wrapping the flap outside ({k}/{COLLAPSE_STEPS})",
            f"Pliega a lo largo de las marcas, envolviendo la solapa por fuera "
            f"({k}/{COLLAPSE_STEPS})",
            f"Repliez le long des marques en enveloppant le rabat par l'extérieur "
            f"({k}/{COLLAPSE_STEPS})",
            f"Dobre ao longo dos vincos, envolvendo a aba por fora ({k}/{COLLAPSE_STEPS})"),
            rho, 400))

# consistency: every rigid step state must close (fail visible, never silent)
worst_closure = worst_edge = worst_mid = 0.0
prev = FLAT
for sid, _, rho, _ in program:
    c, e = residuals(rho)
    worst_closure, worst_edge = max(worst_closure, c), max(worst_edge, e)
    mid = tuple((a + b) / 2.0 for a, b in zip(prev, rho))
    worst_mid = max(worst_mid, residuals(mid)[0])
    prev = rho
if run_mode != "hand" and (worst_closure > TOL_MM or worst_edge > TOL_MM):
    raise ValueError(f"inconsistent rigid fold state: closure {worst_closure:.3g} mm, "
                     f"edge {worst_edge:.3g} mm")
print(f"kinematics: mode={run_mode} steps={len(program)} max_closure_mm={worst_closure:.3e} "
      f"max_edge_error_mm={worst_edge:.3e} max_linear_midpoint_closure_mm={worst_mid:.3e}")

steps = [pliego.Step(sid, label, [(m, a) for m, a in zip(CREASES, rho)], duration_ms=ms)
         for sid, label, rho, ms in program]

result = pliego.Assembly(
    [sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence(steps, mode="physical" if run_mode == "hand" else "kinematic"),
    targets={"reverse-folded": {"angles": dict(zip(CREASES, FINAL)), "root": (ROOT.x, ROOT.y)}},
    title="Outside reverse fold",
)
