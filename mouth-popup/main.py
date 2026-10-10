"""Mouth pop-up (the talking mouth) — sheet-hyperobjects cartridge (Pliego).

One cut and six scored folds in a card: a slit crosses the gutter (the mouth, `mouth_width` long),
and each lip is a pair of triangles between two diagonal folds and a short length of gutter folded
the other way (the lip's ridge). Push the lips through to the inside and the mouth opens and shuts
as the card opens and closes.

Kinematics (Tier R, exact). Each lip meets the gutter at one vertex P: the gutter above P (valley),
the lip's ridge below it (mountain, collinear with the gutter) and the two diagonals to the slit's
ends (valleys). With θ the angle of a diagonal below the slit-parallel direction, the sectors are
(90° + θ, 90° + θ, 90° − θ, 90° − θ): a flat-foldable degree-4 vertex, and the lip moves on its
mode 1 branch (Foschi–Hull–Ku, `pliego.kinematics.degree4_mode1`): the ridge folds by −γ and both
diagonals by ρ with tan(γ/2) = sin θ · tan(ρ/2), γ the gutter angle. One degree of freedom; flat at
γ = 0, folded flat at γ = 180°. The slit makes the two lips independent, so each lip has its own θ.

The program is kinematic: fold the card shut, open it to 90° (the mouth opens) and "talk" (close
it a little and open it again). Every state and every midpoint is checked with
`pliego.kinematics.closure_residual` (fail loud).
"""

import math

import pliego
from pliego import kinematics


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))        # noqa: F821
page_height = float(PARAM(lambda: page_height, 150.0))      # noqa: F821
mouth_width = float(PARAM(lambda: mouth_width, 80.0))       # noqa: F821
upper_lip = float(PARAM(lambda: upper_lip, 22.0))           # noqa: F821
lower_lip = float(PARAM(lambda: lower_lip, 28.0))           # noqa: F821
mouth_position = float(PARAM(lambda: mouth_position, 0.5))  # noqa: F821
talk = float(PARAM(lambda: talk, 40.0))                     # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")               # noqa: F821

W = pliego.clamp(page_width, 90.0, 220.0)
H = pliego.clamp(page_height, 90.0, 260.0)
L = pliego.clamp(mouth_width, 20.0, 180.0) / 2.0        # the slit runs L into each page
du = pliego.clamp(upper_lip, 6.0, 80.0)
dl = pliego.clamp(lower_lip, 6.0, 80.0)
pos = pliego.clamp(mouth_position, 0.2, 0.8)
talk_deg = pliego.clamp(talk, 10.0, 60.0)
if stock not in ("cardstock-160", "cardstock-250", "kraft-120", "copy-80"):
    raise ValueError(f"mouth-popup: unsupported stock {stock!r}")

MARGIN = 6.0
TOL_MM = 1e-6


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


ym = H * pos
if L > W - MARGIN:
    raise ValueError(f"mouth-popup: a {2 * L:g} mm mouth needs pages wider than {L + MARGIN:g} mm")
if ym + du > H - MARGIN or ym - dl < MARGIN:
    raise ValueError("mouth-popup: the lips run off the card; move the mouth or shorten the lips")

P_UP, P_DN = (W, ym + du), (W, ym - dl)
E_L, E_R, MID = (W - L, ym), (W + L, ym), (W, ym)
th_u, th_l = math.atan2(du, L), math.atan2(dl, L)

card = pliego.Sheet("card", [(0, 0), (2 * W, 0), (2 * W, H), (0, H)], stock=stock,
                    grain_deg=90.0, label=L4("Card with a mouth", "Tarjeta con boca",
                                              "Carte avec une bouche", "Cartão com boca"))
card.cut([E_L, MID, E_R], name="mouth")
gut = L4("Gutter (the card's spine)", "Pliegue central (lomo de la tarjeta)",
         "Pliure centrale (dos de la carte)", "Dobra central (lombada do cartão)")
g_lo = card.valley((W, 0), P_DN, treatment="score", label=gut, name="gutter")
g_hi = card.valley(P_UP, (W, H), treatment="score", label=gut, name="gutter")
ridge = card.mountain(P_DN, P_UP, treatment="score", name="lip-ridge", label=L4(
    "Lip ridges (the gutter, folded the other way)",
    "Crestas de los labios (el pliegue central, doblado al revés)",
    "Arêtes des lèvres (la pliure, pliée dans l'autre sens)",
    "Cristas dos lábios (a dobra central, dobrada ao contrário)"))
d_up = [card.valley(P_UP, E, treatment="score", label=L4(
    "Upper lip: diagonal fold", "Labio superior: doblez diagonal",
    "Lèvre supérieure : pli diagonal", "Lábio superior: dobra diagonal")) for E in (E_L, E_R)]
d_dn = [card.valley(P_DN, E, treatment="score", label=L4(
    "Lower lip: diagonal fold", "Labio inferior: doblez diagonal",
    "Lèvre inférieure : pli diagonal", "Lábio inferior: dobra diagonal")) for E in (E_L, E_R)]
arr = card.build()
ROOT = pliego.P(MARGIN, MARGIN)


def diag(gamma, theta):
    """Mode 1 of the lip vertex: the diagonal fold for gutter angle γ (degrees)."""
    if gamma >= 180.0:
        return 180.0
    return math.degrees(2.0 * math.atan(math.tan(math.radians(gamma) / 2.0) / math.sin(theta)))


def state(gamma):
    out = {g_lo: gamma, g_hi: gamma, ridge: -gamma}
    for m in d_up:
        out[m] = diag(gamma, th_u)
    for m in d_dn:
        out[m] = diag(gamma, th_l)
    return out


def edges_of(st):
    return {e: a for m, a in st.items() for e in m.edges()}


# cross-check the closed form against the kernel's degree-4 mode 1 (sectors 90+θ, 90+θ)
for th in (th_u, th_l):
    a1 = 90.0 + math.degrees(th)
    ref = kinematics.degree4_mode1(a1, a1, diag(60.0, th))
    if abs(abs(ref[1]) - 60.0) > 1e-9:
        raise ValueError(f"mouth-popup: closed form disagrees with degree4_mode1 ({ref})")

def arc_samples(g0, g1, n):
    """n gutter angles from g0 (excluded) to g1, evenly spaced along the path in fold-angle
    space, so the preview's linear blend between states stays close to the rigid motion."""
    def vec(g):
        return (g, diag(g, th_u), diag(g, th_l))
    fine = [vec(g0 + (g1 - g0) * i / 400.0) for i in range(401)]
    cum = [0.0]
    for i in range(400):
        cum.append(cum[-1] + math.dist(fine[i], fine[i + 1]))
    out, j = [], 0
    for k in range(1, n + 1):
        goal = cum[-1] * k / n
        while j < 400 and cum[j + 1] < goal:
            j += 1
        out.append(g1 if k == n else g0 + (g1 - g0) * (j + 1) / 400.0)
    return out


# ── the program: shut, open to 90°, talk ─────────────────────────────────────

phases = [
    ("shut", L4("Fold the card shut: the lips fold inside", "Cierra la tarjeta: los labios se "
                "doblan hacia dentro", "Fermez la carte : les lèvres se replient dedans",
                "Feche o cartão: os lábios se dobram para dentro"), 0.0, 180.0, 16),
    ("open", L4("Open it to 90°: the mouth opens", "Ábrela a 90°: la boca se abre",
                "Ouvrez-la à 90° : la bouche s'ouvre", "Abra-o a 90°: a boca se abre"),
     180.0, 90.0, 10),
    ("talk", L4("Close it a little: the mouth shuts", "Ciérrala un poco: la boca se cierra",
                "Refermez-la un peu : la bouche se ferme", "Feche-o um pouco: a boca se fecha"),
     90.0, 90.0 + talk_deg, 4),
    ("talk-again", L4("Open it again: the mouth speaks", "Ábrela otra vez: la boca habla",
                      "Rouvrez-la : la bouche parle", "Abra-o de novo: a boca fala"),
     90.0 + talk_deg, 90.0, 4),
]
steps = []
worst = worst_mid = 0.0
prev = edges_of(state(0.0))
for sid, label, g0, g1, n in phases:
    for k, g in enumerate(arc_samples(g0, g1, n), 1):
        st = state(g)
        cur = edges_of(st)
        mid = {e: (prev[e] + cur[e]) / 2.0 for e in cur}
        worst = max(worst, kinematics.closure_residual(arr, cur, ROOT))
        worst_mid = max(worst_mid, kinematics.closure_residual(arr, mid, ROOT))
        steps.append(pliego.Step(f"{sid}-{k}", {lang: f"{t} ({k}/{n})" for lang, t in
                                               label.items()},
                                 [(m, a) for m, a in st.items()], duration_ms=350))
        prev = cur
if worst > 1e-6:
    raise ValueError(f"mouth-popup: inconsistent rigid state (closure residual {worst:.3g} mm)")


def extent(gamma):
    tr = kinematics.face_transforms(arr, edges_of(state(gamma)), kinematics.root_face(arr, ROOT))
    pts = []
    for fi, f in enumerate(arr.faces):
        rot, off = tr[fi]
        for v in f:
            p = (arr.vertices[v].x, 0.0, -arr.vertices[v].y)
            pts.append([sum(rot[i][j] * p[j] for j in range(3)) + off[i] for i in range(3)])
    return ([min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)])


lo3, hi3 = extent(180.0)
if lo3[0] < -TOL_MM or hi3[0] > W + TOL_MM or lo3[2] < -H - TOL_MM or hi3[2] > TOL_MM \
        or max(abs(lo3[1]), abs(hi3[1])) > 1e-6:
    raise ValueError(f"mouth-popup: the shut card is not flat or the lips stick out "
                     f"({lo3}, {hi3})")
dof = kinematics.dof(arr, edges_of(state(60.0)))
print(f"kinematics: lips=2 dof={dof} program_steps={len(steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={worst_mid:.3e} "
      f"upper_theta={math.degrees(th_u):.2f} lower_theta={math.degrees(th_l):.2f}")

result = pliego.Assembly(
    [card],
    controls=[pliego.sequence_control(
        label=L4("Open, close and talk", "Abrir, cerrar y hablar", "Ouvrir, fermer et parler",
                 "Abrir, fechar e falar"), default=float(len(steps)))],
    sequence=pliego.Sequence(steps, mode="kinematic"),
    title="Mouth pop-up",
)
