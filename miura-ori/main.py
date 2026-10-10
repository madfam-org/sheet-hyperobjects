"""Miura-ori — sheet-hyperobjects cartridge (Pliego).

A rigid-foldable tessellation of congruent parallelogram panels with one degree of freedom.
The crease pattern and its closed-form angle law come from `pliego.tessellate.miura` (geometry
computed by the kernel, no third-party crease pattern copied). The fold program is kinematic:
two steps drive every crease to the exact rigid state at η = fold·γ/2 and η = fold·γ, so the
viewer can scrub between consistent states of the one-parameter family.

Angle law (kernel `pliego.tessellate`, with cx = cos γ / cos η, cz² = 1 − cx²):
    cos ρ_row = (cz² − cx²·sin²η) / sin²γ
    cos ρ_col = (cz²·cos 2η − cx²·sin²η) / sin²γ
Facet–plane angle θ (Schenk & Guest 2013): sin η = sin θ · sin γ.
In-plane Poisson ratio: ν = −cos²θ · tan²γ.
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


cells_x = int(clamp(PARAM(lambda: cells_x, 6), 2, 16))
cells_y = int(clamp(PARAM(lambda: cells_y, 6), 2, 16))
panel_a = clamp(PARAM(lambda: panel_a, 20.0), 8.0, 60.0)
panel_b = clamp(PARAM(lambda: panel_b, 20.0), 8.0, 60.0)
gamma = clamp(PARAM(lambda: gamma, 60.0), 30.0, 85.0)
fold = clamp(PARAM(lambda: fold, 0.75), 0.1, 1.0)
stock = str(PARAM(lambda: stock, "kami"))
if stock not in ("kami", "copy-80", "washi-kozo-30", "tant"):
    raise ValueError(f"stock {stock!r} is not one this cartridge offers")

tess = pliego.tessellate.miura(cells_x, cells_y, panel_a, panel_b, gamma, fold, stock,
                               sheet_id="miura-ori")


def facet_angle(eta_deg):
    """θ from η: sin η = sin θ · sin γ (θ = 0 flat, θ = 90° fully folded)."""
    s = math.sin(math.radians(eta_deg)) / math.sin(math.radians(gamma))
    return math.degrees(math.asin(max(-1.0, min(1.0, s))))


def poisson(theta_deg):
    """In-plane Poisson ratio ν = −cos²θ · tan²γ (Schenk & Guest 2013)."""
    return -math.cos(math.radians(theta_deg)) ** 2 * math.tan(math.radians(gamma)) ** 2


def signed(mark, magnitude):
    return magnitude if mark.assignment == "V" else -magnitude


def step(step_id, t, label):
    """A kinematic step to the exact rigid state at η = t·γ (the kernel's closed-form law)."""
    law = tess.law(t)
    eta = t * gamma
    theta = facet_angle(eta)
    nu = poisson(theta)
    targets = ([(m, signed(m, law["row"])) for m in tess.groups["rows"]]
               + [(m, signed(m, law["column"])) for m in tess.groups["columns"]])
    vals = (f"η = {eta:.1f}°, θ = {theta:.1f}°, ρ_row = {law['row']:.1f}°, "
            f"ρ_col = {law['column']:.1f}°, ν = {nu:.3f}")
    note = {"en": f"Rigid state: {vals}.", "es": f"Estado rígido: {vals}.",
            "fr": f"État rigide : {vals}.", "pt": f"Estado rígido: {vals}."}
    return pliego.Step(step_id, label, targets, duration_ms=2500, note=note)


steps = [
    step("fold-halfway", fold / 2, {"en": "Fold halfway: every crease moves together",
                                    "es": "Dobla a medias: todos los pliegues se mueven a la vez",
                                    "fr": "Plier à mi-course : tous les plis bougent ensemble",
                                    "pt": "Dobre até a metade: todas as dobras se movem juntas"}),
    step("fold", fold, {"en": "Keep folding to the final state",
                        "es": "Sigue doblando hasta el estado final",
                        "fr": "Continuer à plier jusqu'à l'état final",
                        "pt": "Continue dobrando até o estado final"}),
]

result = pliego.Assembly(
    [tess.sheet],
    controls=[pliego.sequence_control()],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    title="Miura-ori",
    targets=dict(tess.targets),
)
