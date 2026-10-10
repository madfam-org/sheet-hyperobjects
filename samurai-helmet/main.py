"""Samurai helmet (kabuto) — sheet-hyperobjects cartridge (Pliego): the traditional helmet,
folded flat from a square by simple folds with parametric horns. Every fold is a
`pliego.FoldProgram` operation on a layer-ordered flat state, checked for a consistent layer order
and for Kawasaki and Maekawa at every vertex; the crease pattern is the final state unfolded.
Opening it to wear bends the paper, which needs the physics engine.
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
P, C = pliego.param, pliego.clamp
size = C(float(P(lambda: size, 250.0)), 150.0, 600.0)  # noqa: F821
horn = C(float(P(lambda: horn, 67.5)), 55.0, 80.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
S0, h = size, size / 2.0
d = S0 / math.sqrt(2.0)

T_ = {
    "triangle": L4("Fold the top corner down to the bottom one: a triangle, point down",
                   "Dobla la esquina de arriba hasta la de abajo: un triángulo con la punta abajo",
                   "Rabattez le coin du haut sur celui du bas : un triangle, pointe en bas",
                   "Dobre o canto de cima até ao de baixo: um triângulo com a ponta para baixo"),
    "corners-down": L4("Fold the left and right corners down to the bottom point: a square",
                       "Dobla las esquinas izquierda y derecha hasta la punta de abajo: un cuadrado",
                       "Rabattez les coins gauche et droit sur la pointe du bas : un carré",
                       "Dobre os cantos esquerdo e direito até à ponta de baixo: um quadrado"),
    "flaps-up": L4("Fold the two front flaps up to the top point",
                   "Dobla las dos solapas de delante hacia arriba hasta la punta superior",
                   "Remontez les deux rabats avant jusqu'à la pointe du haut",
                   "Dobre as duas abas da frente para cima até à ponta de cima"),
    "horns": L4("Fold the two points outwards and up: the horns",
                "Dobla las dos puntas hacia fuera y hacia arriba: los cuernos",
                "Rabattez les deux pointes vers l'extérieur et vers le haut : les cornes",
                "Dobre as duas pontas para fora e para cima: os chifres"),
    "brim-1": L4("Fold the front bottom corner up, the front layer only",
                 "Dobla hacia arriba la esquina inferior de delante, solo la capa delantera",
                 "Remontez le coin inférieur avant, la couche de devant seulement",
                 "Dobre para cima o canto de baixo da frente, só a camada da frente"),
    "brim-2": L4("Fold it up again along the base of the horns: the brim",
                 "Vuelve a doblarla hacia arriba por la base de los cuernos: la visera",
                 "Remontez-le encore le long de la base des cornes : la visière",
                 "Dobre-a outra vez para cima pela base dos chifres: a pala"),
    "back": L4("Fold the back corner up behind the helmet",
               "Dobla la esquina de atrás hacia arriba, por detrás del casco",
               "Remontez le coin arrière derrière le casque",
               "Dobre o canto de trás para cima, por trás do capacete"),
}

# ── the fold program: the square turned to a diamond, centred on (h, h) ──────
fp = pliego.FoldProgram([(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front="#b5121b", back="#f4efe6")
fp.rotate(45.0, (h, h))


def o(x, y):
    """A point of the diamond's frame (centred on the origin) in the folded frame."""
    return (x + h, y + h)


corner = {}
for p in fp.state.outline:  # sheet corners by where they sit on the diamond (top, right, ...)
    w = fp.state.to_folded(p)
    corner[(round((w[0] - h) / d), round((w[1] - h) / d))] = (p[0] + 0.02 * (h - p[0]),
                                                             p[1] + 0.02 * (h - p[1]))
T, R, B, L = corner[(0, 1)], corner[(1, 0)], corner[(0, -1)], corner[(-1, 0)]
off = S0 / 125.0  # off the diagonal fold, and on the sheet at every size (2 mm at 250 mm)
R, L = (R[0] - off, R[1] - off), (L[0] - off, L[1] - off)
JOINS = {"corners-down-2", "flaps-up-2", "horns-2"}

fp.fold("triangle", T_["triangle"], (o(-d - 1.0, 0.0), o(d + 1.0, 0.0)), "valley")
fp.fold("corners-down", T_["corners-down"], (o(-0.1 * d, 0.1 * d), o(1.1 * d, -1.1 * d)), "valley")
fp.fold("corners-down-2", T_["corners-down"], (o(-1.1 * d, -1.1 * d), o(0.1 * d, 0.1 * d)),
        "valley")
for k, sd in enumerate((R, L)):
    fp.fold("flaps-up" + ("-2" if k else ""), T_["flaps-up"], (o(d, -d / 2.0), o(-d, -d / 2.0)),
            "valley", sheet_points=[sd])
c, s_ = math.cos(math.radians(horn)), math.sin(math.radians(horn))
fp.fold("horns", T_["horns"], (o(0.0, -d / 2.0), o(c * d, -d / 2.0 + s_ * d)), "valley",
        sheet_points=[R])
fp.fold("horns-2", T_["horns"], (o(-c * d, -d / 2.0 + s_ * d), o(0.0, -d / 2.0)), "valley",
        sheet_points=[L])
fp.fold("brim-1", T_["brim-1"], (o(d, -0.75 * d), o(-d, -0.75 * d)), "valley", sheet_points=[T])
tm = (h + 0.69 * (T[0] - h) + 1.0, h + 0.69 * (T[1] - h))  # the front layer just below the line
fp.fold("brim-2", T_["brim-2"], (o(d, -0.62 * d), o(-d, -0.62 * d)), "valley", sheet_points=[tm])
fp.fold("back", T_["back"], (o(d, -0.7 * d), o(-d, -0.7 * d)), "mountain", sheet_points=[B])

built = fp.build("square")
present([(built, (pliego.flatmotion.ID_RIGID[0], (-h, 0.0, h)))],
        (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))  # stand the flat helmet up
seq, worst, mid = diagram([built], JOINS)
print(built.summary())
print(f"kinematics: steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target()}, title="Samurai helmet")
