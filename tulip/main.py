"""Tulip — sheet-hyperobjects cartridge (Pliego).

The traditional flat tulip of first folding lessons, as a two-sheet assembly: a blossom and a stem
with a leaf, each folded from its own square, then put together.

- **Blossom** (a square held as a diamond): fold the top corner down to the bottom, making a
  triangle point down; fold each side corner up along a line from the top edge to just beside the
  bottom point, so that the corners rise above the top edge as two petals.
- **Stem and leaf** (a square held as a diamond): fold the two edges at the top corner onto the
  vertical diagonal (a kite), fold the new edges onto it again (narrowing), fold the stem in half
  along its axis, and fold the wide bottom of the front layers up and out as the leaf.

Every fold is a simple fold of a flat stack: `pliego.simplefold` computes, from the folded state,
the crease each fold leaves in every layer it crosses, with its mountain or valley sense, and
`pliego.Sequence.kinematic_path` (the kernel's motion solver) turns each fold into exact rigid
in-between states. After the folds, the `assemble` control slides the blossom down onto the stem
point (a `translate` mechanism the studio preview can drive). All geometry is computed here; the
tulip is traditional (no designer's diagram is used).
"""

import math

import pliego
from pliego import flatfold, kinematics, simplefold


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


blossom_size = float(PARAM(lambda: blossom_size, 150.0))  # noqa: F821
stem_size = float(PARAM(lambda: stem_size, 150.0))  # noqa: F821
petal = float(PARAM(lambda: petal, 0.7))  # noqa: F821
stock = PARAM(lambda: stock, "kami")  # noqa: F821
blossom_size = max(80.0, min(300.0, blossom_size))
stem_size = max(80.0, min(300.0, stem_size))
petal = max(0.62, min(0.8, petal))  # where the petal fold meets the top edge, × half-diagonal
CLOSURE_TOL_MM = 1e-4  # mm; layered folds stack grid-snapped vertices
STEM_FRONT, STEM_BACK = "#4f8a3c", "#e3ecd6"  # green paper, pale back


def fold_program(sheet_id, outline, folds, label, stock_, front=None, back=None):
    """Run simple folds on a flat outline; return the sheet with one crease mark per segment, the
    key poses and the folded state. `folds`: (step id, step label, crease label, line,
    direction, layers)."""
    fs = simplefold.FoldedState(outline)
    plan = []
    for sid, slabel, clabel, line, direction, layers in folds:
        n0 = len(fs.creases)
        fs.fold(line, direction, layers)
        plan.append((sid, slabel, clabel, fs.creases[n0:]))
    sheet = pliego.Sheet(sheet_id, outline, stock=stock_, label=label, front=front, back=back)
    keys = []
    for sid, slabel, clabel, segs in plan:
        if not segs:
            raise ValueError(f"fold '{sid}' crosses no layer")
        targets = []
        for a, b, asg in segs:
            mark = sheet.crease((a.x, a.y), (b.x, b.y),
                                "valley" if asg == "V" else "mountain", label=clabel)
            targets.append((mark, 180.0 if asg == "V" else -180.0))
        keys.append((sid, slabel, targets))
    return sheet, keys, fs


def rigid_steps(sheet, keys, durations, n=6):
    """Key poses → exact rigid steps with the kernel's motion solver (`kinematics.solve`): every
    other crease holds; chord continuation first, the linear drive when the chord's branch
    analysis does not settle (a simple fold of a flat stack moves its creases linearly)."""
    arr = sheet.build()
    var = [e for e, a in enumerate(arr.assignment) if a in ("M", "V", "U")]
    cur, steps, worst = {}, [], 0.0
    for sid, lab, tg in keys:
        targets = {e: a for m, a in tg for e in m.edges()}
        fixed = [e for e in var if e not in targets]
        try:
            path = kinematics.solve(sheet, cur, targets, fixed, n, along="chord")
        except kinematics.KinematicsError:
            path = kinematics.solve(sheet, cur, targets, fixed, n, along="drive")
        worst = max(worst, path.max_residual_rad)
        for k, state in enumerate(path, 1):
            moved = [(pliego.assembly.EdgeRef(sheet, e), targets[e] if k == n else state[e])
                     for e in path.edges if e in targets]
            steps.append(pliego.Step(f"{sid}-{k}", {g: f"{lab[g]} ({k}/{n})" for g in lab},
                                     moved, duration_ms=max(100, round(durations.get(sid, 1500)
                                                                         / n))))
        cur.update(targets)
    return steps, cur, worst


def solve(sheet, keys, root, durations):
    steps, final, worst = rigid_steps(sheet, keys, durations)
    arr = sheet.build()
    closure = kinematics.closure_residual(arr, final, pliego.P(*root))
    if closure > CLOSURE_TOL_MM:
        raise ValueError(f"{sheet.id}: folded state does not close ({closure:.3g} mm)")
    pose = kinematics.pose_arrangement(arr, final, pliego.P(*root))
    return steps, final, closure, worst, pose


GRID_SECTOR_DEG = 1e-4  # two sectors closer than this are equal up to the coordinate grid


def flat_line(sheet):
    """Maekawa, Kawasaki and big-little-big on the folded pattern (every crease is folded flat in
    the final state); fail loud on an error. Big-little-big applies to a *strictly* smallest
    sector: where a fold crosses a folded edge, the two small sectors are equal in exact geometry
    and differ only by grid snapping (about 10⁻⁵°), which is reported, not failed."""
    reports, issues = flatfold.check(sheet.build())
    by_v = {r.vertex: r for r in reports}
    errors, snapped = [], 0
    for i in issues:
        if i["level"] != "error":
            continue
        r = by_v.get(i.get("vertex"))
        if i["kind"] == "big_little_big" and r is not None:
            sec = r.sectors_deg
            k = min(range(len(sec)), key=lambda j: sec[j])
            gap = min(sec[k - 1], sec[(k + 1) % len(sec)]) - sec[k]
            if gap < GRID_SECTOR_DEG:
                snapped += 1
                continue
        errors.append(i["detail"])
    if errors:
        raise ValueError(f"{sheet.id}: not flat-foldable: " + "; ".join(errors))
    return (f"{sheet.id}: vertices={len(reports)} "
            f"max_degree={max([r.degree for r in reports] or [0])} blb_equal_sectors={snapped}")


def world_of(arr, pose, pt):
    i = min(range(len(arr.vertices)), key=lambda j: arr.vertices[j].distance(pliego.P(*pt)))
    return pose[i]


# ── the blossom: a diamond of half-diagonal d ────────────────────────────────
d = blossom_size / math.sqrt(2.0)
B_TOP, B_LEFT, B_BOT, B_RIGHT = (0.0, d), (-d, 0.0), (0.0, -d), (d, 0.0)
FOOT = 0.1 * d  # the petal folds end this far beside the bottom point
blossom_folds = [
    ("blossom-in-half", L4(
        "Blossom: fold the top corner down to the bottom corner",
        "Flor: dobla la esquina de arriba hasta la de abajo",
        "Fleur : rabattez le coin du haut sur le coin du bas",
        "Flor: dobre o canto de cima até ao de baixo"),
     L4("Blossom, diagonal", "Flor, diagonal", "Fleur, diagonale", "Flor, diagonal"),
     (B_LEFT, B_RIGHT), "valley", "all"),
    ("blossom-left-petal", L4(
        "Fold the left corner up so it rises above the top edge: a petal",
        "Dobla la esquina izquierda hacia arriba para que sobresalga del borde: un pétalo",
        "Relevez le coin gauche pour qu'il dépasse le bord du haut : un pétale",
        "Dobre o canto esquerdo para cima para que passe da borda de cima: uma pétala"),
     L4("Blossom, left petal", "Flor, pétalo izquierdo", "Fleur, pétale gauche",
        "Flor, pétala esquerda"),
     ((-FOOT, -d + FOOT), (-petal * d, 0.0)), "valley", "all"),
    ("blossom-right-petal", L4(
        "Fold the right corner up the same way", "Dobla igual la esquina derecha",
        "Relevez de même le coin droit", "Dobre da mesma forma o canto direito"),
     L4("Blossom, right petal", "Flor, pétalo derecho", "Fleur, pétale droit",
        "Flor, pétala direita"),
     ((petal * d, 0.0), (FOOT, -d + FOOT)), "valley", "all"),
]
blossom, blossom_keys, _ = fold_program(
    "blossom", [B_TOP, B_LEFT, B_BOT, B_RIGHT], blossom_folds,
    L4("Blossom", "Flor", "Fleur", "Flor"), stock)

# ── the stem and leaf: a diamond of half-diagonal e, point P at the top ──────
e = stem_size / math.sqrt(2.0)
S_TOP, S_LEFT, S_BOT, S_RIGHT = (0.0, e), (-e, 0.0), (0.0, -e), (e, 0.0)


def ray(deg, length):
    return (S_TOP[0] + length * math.cos(math.radians(deg)),
            S_TOP[1] + length * math.sin(math.radians(deg)))


LONG = 3.0 * e
stem_folds = [
    ("kite-left", L4(
        "Stem: fold the upper left edge onto the vertical diagonal",
        "Tallo: lleva el borde superior izquierdo a la diagonal vertical",
        "Tige : rabattez le bord supérieur gauche sur la diagonale verticale",
        "Caule: leve a aresta superior esquerda até à diagonal vertical"),
     L4("Stem, kite fold (left)", "Tallo, pliegue de cometa (izquierdo)",
        "Tige, pli cerf-volant (gauche)", "Caule, dobra de pipa (esquerda)"),
     (ray(247.5, LONG), S_TOP), "valley", "all"),
    ("kite-right", L4(
        "Fold the upper right edge onto it: a kite",
        "Lleva el borde superior derecho a la misma línea: una cometa",
        "Rabattez le bord supérieur droit dessus : un cerf-volant",
        "Leve a aresta superior direita até à mesma linha: uma pipa"),
     L4("Stem, kite fold (right)", "Tallo, pliegue de cometa (derecho)",
        "Tige, pli cerf-volant (droit)", "Caule, dobra de pipa (direita)"),
     (S_TOP, ray(292.5, LONG)), "valley", "all"),
    ("narrow-left", L4(
        "Fold the new left edge onto the diagonal again, to narrow the stem",
        "Vuelve a llevar el nuevo borde izquierdo a la diagonal, para afinar el tallo",
        "Rabattez de nouveau le nouveau bord gauche sur la diagonale, pour affiner la tige",
        "Leve de novo a nova aresta esquerda até à diagonal, para afinar o caule"),
     L4("Stem, narrowing fold (left)", "Tallo, pliegue para afinar (izquierdo)",
        "Tige, pli d'affinage (gauche)", "Caule, dobra de afinar (esquerda)"),
     (ray(258.75, LONG), S_TOP), "valley", "all"),
    ("narrow-right", L4(
        "Narrow the right side the same way", "Afina igual el lado derecho",
        "Affinez de même le côté droit", "Afine da mesma forma o lado direito"),
     L4("Stem, narrowing fold (right)", "Tallo, pliegue para afinar (derecho)",
        "Tige, pli d'affinage (droit)", "Caule, dobra de afinar (direita)"),
     (S_TOP, ray(281.25, LONG)), "valley", "all"),
    ("stem-in-half", L4(
        "Fold the stem in half along its axis", "Dobla el tallo a la mitad por su eje",
        "Pliez la tige en deux selon son axe", "Dobre o caule ao meio pelo eixo"),
     L4("Stem, axis", "Tallo, eje", "Tige, axe", "Caule, eixo"),
     (S_TOP, S_BOT), "valley", "all"),
    ("leaf", L4(
        "Fold the wide bottom up and out at a slant: the leaf",
        "Dobla la parte ancha de abajo hacia arriba y afuera, en diagonal: la hoja",
        "Relevez en biais le bas large vers l'extérieur : la feuille",
        "Dobre a parte larga de baixo para cima e para fora, na diagonal: a folha"),
     L4("Leaf fold", "Pliegue de la hoja", "Pli de la feuille", "Dobra da folha"),
     ((0.0, -0.45 * e), (-0.45 * e, -e)), "valley", "all"),
]
stem, stem_keys, _ = fold_program(
    "stem", [S_TOP, S_LEFT, S_BOT, S_RIGHT], stem_folds,
    L4("Stem and leaf", "Tallo y hoja", "Tige et feuille", "Caule e folha"), stock,
    front=STEM_FRONT, back=STEM_BACK)

DUR = {"blossom-in-half": 1500, "stem-in-half": 1500, "leaf": 1800}
STEM_ROOT = (-0.04 * e, 0.3 * e)      # a sliver of the base layer beside the axis, near the top
BLOSSOM_ROOT = (0.0, -0.6 * d)        # the blossom's body below the top edge
stem_steps, stem_final, stem_closure, stem_res, stem_pose = solve(stem, stem_keys, STEM_ROOT, DUR)
stem_arr = stem.build()
bl_steps, bl_final, bl_closure, bl_res, bl_pose = solve(blossom, blossom_keys, BLOSSOM_ROOT, DUR)
bl_arr = blossom.build()

# ── placement and assembly ───────────────────────────────────────────────────
GAP = 20.0
blossom.placement = pliego.Placement(origin=(e + d + GAP, 0.0, 0.0))
tip = world_of(stem_arr, stem_pose, S_TOP)              # the stem's point (stem at the origin)
bottom = world_of(bl_arr, bl_pose, B_BOT)               # the blossom's bottom point, local
INSERT = 0.25 * d                                       # how far the stem goes into the blossom
goal = (tip[0], tip[1] + 0.5, tip[2] + INSERT)          # world: down the stem is +z
start = (bottom[0] + e + d + GAP, bottom[1], bottom[2])
move = tuple(g - s_ for g, s_ in zip(goal, start))
travel = math.sqrt(sum(c * c for c in move))
print(f"flatfold: {flat_line(stem)} {flat_line(blossom)} maekawa=ok kawasaki=ok "
      "big_little_big=ok")
print(f"kinematics: stem_steps={len(stem_steps)} blossom_steps={len(bl_steps)} "
      f"max_residual_rad={max(stem_res, bl_res):.2e} "
      f"stem_closure_mm={stem_closure:.2e} blossom_closure_mm={bl_closure:.2e} "
      f"assemble_travel_mm={travel:.1f}")

sequence = pliego.Sequence(stem_steps + bl_steps, mode="kinematic")
result = pliego.Assembly(
    [stem, blossom],
    mechanisms=[pliego.translate("assemble-slide", "assemble",
                                 [c / travel for c in move], travel, sheets_moving=[blossom])],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras")),
        pliego.control("assemble", "distance", L4(
            "Put the blossom on the stem", "Pon la flor en el tallo", "Posez la fleur sur la tige",
            "Ponha a flor no caule"), 0.0, 0.0, round(travel, 3), "mm")],
    sequence=sequence,
    targets={"folded": {"stem": {"angles": stem_final, "root": STEM_ROOT},
                        "blossom": {"angles": bl_final, "root": BLOSSOM_ROOT}}},
    title="Tulip",
)
