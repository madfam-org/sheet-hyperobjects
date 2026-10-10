"""Paper hat — sheet-hyperobjects cartridge (Pliego): the traditional newspaper hat and its
pirate's-bicorne variant, folded flat from a rectangle by simple folds. Every fold is a
`pliego.FoldProgram` operation on a layer-ordered flat state, checked for a consistent layer order
and for Kawasaki and Maekawa at every vertex; the crease pattern is the final state unfolded.
Wearing the hat rounds the paper, which needs the physics engine.
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
design = P(lambda: design, "newspaper")  # noqa: F821
paper = P(lambda: paper, "broadsheet")  # noqa: F821
stock = P(lambda: stock, "copy-80")  # noqa: F821
SIZES = {"a4": (210.0, 297.0), "a3": (297.0, 420.0), "tabloid": (280.0, 430.0),
         "broadsheet": (380.0, 580.0)}
if design not in ("newspaper", "pirate") or paper not in SIZES:
    raise ValueError(f"unknown design/paper {design!r} {paper!r}")
W, H = SIZES[paper]  # portrait
hc, w2 = H / 2.0, W / 2.0
b = hc - w2  # height of the brim strip under the triangle

T = {
    "fold-down": L4("Fold the sheet in half, top edge down to the bottom edge",
                    "Dobla la hoja por la mitad, el borde de arriba hasta el de abajo",
                    "Pliez la feuille en deux, le bord du haut sur celui du bas",
                    "Dobre a folha ao meio, a aresta de cima até à de baixo"),
    "crease": L4("Fold in half sideways", "Dobla por la mitad de lado a lado",
                 "Pliez en deux d'un côté à l'autre", "Dobre ao meio de um lado ao outro"),
    "unfold": L4("Unfold: the centre line is marked", "Desdobla: queda marcada la línea central",
                 "Dépliez : la ligne centrale est marquée",
                 "Desdobre: a linha central fica marcada"),
    "corners": L4("Fold the two top corners down to the centre line",
                  "Dobla las dos esquinas de arriba hasta la línea central",
                  "Rabattez les deux coins du haut sur la ligne centrale",
                  "Dobre os dois cantos de cima até à linha central"),
    "brim-front": L4("Fold the front strip up twice: the brim",
                     "Dobla dos veces hacia arriba la tira de delante: el ala",
                     "Remontez deux fois la bande de devant : le bord",
                     "Dobre duas vezes para cima a tira da frente: a aba"),
    "brim-back": L4("Turn over and fold the other strip up twice",
                    "Da la vuelta y dobla dos veces hacia arriba la otra tira",
                    "Retournez et remontez deux fois l'autre bande",
                    "Vire e dobre duas vezes para cima a outra tira"),
    "ends-front": L4("Fold the brim's ends behind, around the sides",
                     "Dobla los extremos del ala hacia atrás, alrededor de los costados",
                     "Rabattez les extrémités du bord derrière, autour des côtés",
                     "Dobre as pontas da aba para trás, à volta dos lados"),
    "ends-back": L4("Fold this brim's ends round to the front: a pirate's bicorne",
                    "Dobla los extremos de esta ala hacia delante: un bicornio de pirata",
                    "Rabattez les extrémités de ce bord vers l'avant : un bicorne de pirate",
                    "Dobre as pontas desta aba para a frente: um bicórnio de pirata"),
}

# ── the fold program ─────────────────────────────────────────────────────────
fp = pliego.FoldProgram([(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)], stock=stock,
                        label=L4("Sheet", "Hoja", "Feuille", "Folha"),
                        front="#f4efe6", back="#22223b")
fp.fold("fold-down", T["fold-down"], ((-1.0, hc), (W + 1.0, hc)), "valley")
fp.fold("crease", T["crease"], ((w2, -1.0), (w2, hc + 1.0)), "valley", ms=900)
fp.unfold_last("unfold", T["unfold"], ms=700)
fp.fold("corners", T["corners"], ((-10.0, b - 10.0), (w2 + 10.0, hc + 10.0)), "valley")
fp.fold("corners-2", T["corners"], ((w2 - 10.0, hc + 10.0), (W + 10.0, b - 10.0)), "valley")
JOINS = {"corners-2", "brim-front-2", "brim-back-2", "ends-front-2", "ends-back-2"}
for kind, seed, side in (("valley", (w2 + 7.0, H - 2.0), "front"),
                         ("mountain", (w2 + 7.0, 2.0), "back")):
    fp.fold(f"brim-{side}", T[f"brim-{side}"], ((W + 1.0, b / 2.0), (-1.0, b / 2.0)), kind,
            sheet_points=[seed])
    fp.fold(f"brim-{side}-2", T[f"brim-{side}"], ((W + 1.0, b), (-1.0, b)), kind,
            sheet_points=[seed])
    if design == "pirate":  # the brim's ends stick out past the crown: fold them round the sides,
        # before the other brim goes up, which then covers them (front ends behind, back to front)
        end = (1.0, H - 0.75 * b) if side == "front" else (1.0, 0.75 * b)
        wrap = "mountain" if side == "front" else "valley"
        fp.fold(f"ends-{side}", T[f"ends-{side}"], ((-10.0, b - 10.0), (w2, hc)), wrap,
                sheet_points=[end])
        fp.fold(f"ends-{side}-2", T[f"ends-{side}"], ((w2, hc), (W + 10.0, b - 10.0)), wrap,
                sheet_points=[(W - end[0], end[1])])

built = fp.build("sheet")
present([(built, None)], (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))  # stand the flat hat up
seq, worst, mid = diagram([built], JOINS)
print(built.summary())
print(f"kinematics: design={design} paper={paper} steps={len(seq.steps)} "
      f"max_closure_mm={worst:.3e} max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target()}, title="Paper hat")
