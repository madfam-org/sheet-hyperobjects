"""Paper popper (banger) — sheet-hyperobjects cartridge (Pliego): the traditional paper banger,
folded flat by simple folds. Every fold is a `pliego.FoldProgram` operation on a layer-ordered
flat state, checked for a consistent layer order and for Kawasaki and Maekawa at every vertex; the
crease pattern is the final state unfolded. The bang (the inner flap snapping out) is physics and
waits for the engine; the program ends in the folded, ready-to-snap state.
"""

import math

import pliego


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── presentation and the diagram's steps ─────────────────────────────────────
def quat(r):
    """Unit quaternion [x, y, z, w] of a rotation matrix (rows)."""
    tr = r[0][0] + r[1][1] + r[2][2]
    if tr > 0.0:
        s = math.sqrt(tr + 1.0) * 2.0
        return ((r[2][1] - r[1][2]) / s, (r[0][2] - r[2][0]) / s, (r[1][0] - r[0][1]) / s, s / 4)
    i = max(range(3), key=lambda k: r[k][k])
    j, k = (i + 1) % 3, (i + 2) % 3
    s = math.sqrt(max(1e-30, 1.0 + r[i][i] - r[j][j] - r[k][k])) * 2.0
    q = [0.0] * 4
    q[i], q[j], q[k] = s / 4, (r[j][i] + r[i][j]) / s, (r[k][i] + r[i][k]) / s
    q[3] = (r[k][j] - r[j][k]) / s
    return tuple(q)


def present(items, fwd, up, lift=0.0):
    """Show the finished model with `up` → +Y and `fwd` → −Z, resting on the floor. `items`:
    (built, world rigid of its folded frame or None); the studio roots each sheet at face 0."""
    fm = pliego.flatmotion
    lat = (up[1] * fwd[2] - up[2] * fwd[1], up[2] * fwd[0] - up[0] * fwd[2],
           up[0] * fwd[1] - up[1] * fwd[0])
    rd = (((-lat[0], -lat[1], -lat[2]), tuple(up), (-fwd[0], -fwd[1], -fwd[2])), (0.0, 0.0, 0.0))
    poses, low = [], math.inf
    for b, pre in items:
        base = fm.compose(rd, pre or fm.ID_RIGID)
        st = b.state
        f0 = fm.compose(base, pliego.flatstate.embed3(st.faces[b.face_map[0]].xf))
        poses.append(f0)
        pts = [(f0, q) for q in st.outline] + [
            (fm.compose(base, pliego.flatstate.embed3(st.faces[f].xf)), q)
            for f in range(len(st.faces)) for q in st.poly(f)]
        low = min([low] + [fm.apply(g, (q[0], 0.0, -q[1]))[1] for g, q in pts])
    for (b, _), (r, t) in zip(items, poses):
        b.sheet.placement = pliego.Placement((t[0], t[1] - low + lift, t[2]), quat(r))


def diagram(builts, joins, order=None):
    """The kinematic fold program: the operations in `joins` merged into the step before them, as
    the diagram shows them (one step, all their creases blended together), and the worst loop
    closure at every state and halfway between states (the preview's linear blend)."""
    steps = []
    for b in builts:
        for st in b.sequence.steps:
            if st.id in joins:
                pv = steps[-1][1]
                tg = {r.edge: (r, a) for r, a in pv.targets + st.targets}
                steps[-1] = (b, pliego.Step(pv.id, pv.label, sorted(
                    tg.values(), key=lambda x: x[0].edge), duration_ms=pv.duration_ms,
                    note=pv.note))
            else:
                steps.append((b, st))
    if order is not None:
        by = {st.id: (b, st) for b, st in steps}
        steps = [by[k] for k in order]
    worst = mid = 0.0
    for b in builts:
        cur, rt = dict(b.start_angles), pliego.P(*b.root())
        for bb, st in steps:
            if bb is b:
                nxt = {**cur, **{r.edge: a for r, a in st.targets}}
                half = {e: (cur[e] + nxt[e]) / 2.0 for e in cur}
                worst = max(worst, pliego.kinematics.closure_residual(b.arr, nxt, rt))
                mid = max(mid, pliego.kinematics.closure_residual(b.arr, half, rt))
                cur = nxt
    if worst > 1e-3:
        raise ValueError(f"inconsistent fold state: closure {worst:.3g} mm")
    seq = pliego.Sequence([st for _, st in steps], mode="kinematic")
    return seq, worst, mid


# ── parameters ───────────────────────────────────────────────────────────────
P = pliego.param
paper = P(lambda: paper, "a4")  # noqa: F821
stock = P(lambda: stock, "copy-80")  # noqa: F821
SIZES = {"a4": (297.0, 210.0), "letter": (279.4, 215.9), "a3": (420.0, 297.0)}
if paper not in SIZES:
    raise ValueError(f"unknown paper {paper!r}")
W, H = SIZES[paper]  # landscape: the long side runs along x
m, c = H / 2.0, W / 2.0
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")
T = {
    "fold-long": L4("Fold the sheet in half the long way", "Dobla la hoja por la mitad a lo largo",
                    "Pliez la feuille en deux dans la longueur",
                    "Dobre a folha ao meio no comprimento"),
    "corners": L4("Fold all four corners to the centre line",
                  "Dobla las cuatro esquinas hasta la línea central",
                  "Rabattez les quatre coins sur la ligne centrale",
                  "Dobre os quatro cantos até à linha central"),
    "fold-half": L4("Fold in half along the centre line, corners inside",
                    "Dobla por la mitad sobre la línea central, con las esquinas por dentro",
                    "Pliez en deux sur la ligne centrale, coins à l'intérieur",
                    "Dobre ao meio pela linha central, com os cantos por dentro"),
    "fold-short": L4("Fold in half the short way", "Dobla por la mitad a lo ancho",
                     "Pliez en deux dans la largeur", "Dobre ao meio na largura"),
    "ends-down": L4(
        "Fold both ends down along lines from the top centre: they point down",
        "Dobla los dos extremos hacia abajo por líneas que salen del centro de arriba: quedan "
        "apuntando hacia abajo",
        "Rabattez les deux extrémités le long de lignes partant du milieu du haut : elles "
        "pointent vers le bas",
        "Dobre as duas pontas para baixo por linhas que saem do centro de cima: ficam a apontar "
        "para baixo"),
    "fold-back": L4("Fold in half backwards: hold the two points and snap it down",
                    "Dobla por la mitad hacia atrás: sujeta las dos puntas y sacúdelo hacia abajo",
                    "Pliez en deux vers l'arrière : tenez les deux pointes et donnez un coup sec "
                    "vers le bas",
                    "Dobre ao meio para trás: segure as duas pontas e sacuda-o para baixo"),
}

# ── the fold program ─────────────────────────────────────────────────────────
fp = pliego.FoldProgram([(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)], stock=stock,
                        label=L4("Sheet", "Hoja", "Feuille", "Folha"),
                        front="#f4efe6", back="#6a4c93")
fp.fold("fold-long", T["fold-long"], ((-1.0, m), (W + 1.0, m)), "valley", ms=1100)
fp.unfold_last("unfold-long", UNFOLD, ms=800)
for k, line in enumerate((((m, 0.0), (0.0, m)), ((0.0, m), (m, H)), ((W, m), (W - m, 0.0)),
                          ((W - m, H), (W, m)))):
    fp.fold("corners" + (f"-{k + 1}" if k else ""), T["corners"], line, "valley")
fp.fold("fold-half", T["fold-half"], ((-1.0, m), (W + 1.0, m)), "valley")
fp.fold("fold-short", T["fold-short"], ((c, -1.0), (c, H + 1.0)), "valley", ms=1100)
fp.unfold_last("unfold-short", UNFOLD, ms=800)
fp.fold("ends-down", T["ends-down"], ((c - m, 0.0), (c, m)), "valley")
fp.fold("ends-down-2", T["ends-down"], ((c, m), (c + m, 0.0)), "valley")
fp.fold("fold-back", T["fold-back"], ((c, -W), (c, H + 1.0)), "mountain")

built = fp.build("sheet")
present([(built, None)], (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))  # stand it up, the points down
seq, worst, mid = diagram([built], {"corners-2", "corners-3", "corners-4", "ends-down-2"})
print(built.summary())
print(f"kinematics: paper={paper} steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target()}, title="Paper popper")
