"""Ninja star (shuriken) — sheet-hyperobjects cartridge (Pliego): the traditional two-unit star.
Two half-square units, mirror images, are folded by simple folds; unit B is turned over, crossed
under unit A, and each unit's halves are folded across the other to lock them together. Every
fold is a `pliego.FoldProgram` operation on a layer-ordered flat state of its unit, checked for a
consistent layer order and for Kawasaki and Maekawa at every vertex; each crease pattern is the
unit's final state unfolded.
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
size = C(float(P(lambda: size, 150.0)), 100.0, 300.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
u = size / 4.0  # each unit is half a square: 4u by 2u
RECT = [(0.0, 0.0), (4.0 * u, 0.0), (4.0 * u, 2.0 * u), (0.0, 2.0 * u)]
ctr = (2.0 * u, u / 2.0)  # the unit's centre once folded
fm = pliego.flatmotion
# unit B: turned over, a quarter turn, its centre on unit A's, one paper thickness below
flip = fm.rot_line((ctr[0], 0.0, -ctr[1]), (1.0, 0.0, 0.0), math.pi)
quarter = fm.rot_line((ctr[0], 0.0, -ctr[1]), (0.0, 1.0, 0.0), math.pi / 2.0)
tB = fm.compose((fm.ID_RIGID[0], (0.0, -0.4, 0.0)), fm.compose(quarter, flip))
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")


def labels(n):
    return {
        "crease": L4(f"Unit {n}: fold in half crosswise", f"Pieza {n}: dobla por la mitad a lo ancho",
                     f"Module {n} : pliez en deux dans la largeur",
                     f"Peça {n}: dobre ao meio na largura"),
        "half": L4(f"Unit {n}: fold in half lengthwise", f"Pieza {n}: dobla por la mitad a lo largo",
                   f"Module {n} : pliez en deux dans la longueur",
                   f"Peça {n}: dobre ao meio no comprimento"),
        "corners": L4(
            f"Unit {n}: fold opposite corners in, one up and one down",
            f"Pieza {n}: dobla esquinas opuestas, una hacia arriba y otra hacia abajo",
            f"Module {n} : rabattez deux coins opposés, l'un vers le haut, l'autre vers le bas",
            f"Peça {n}: dobre cantos opostos, um para cima e outro para baixo"),
        "arms": L4(
            f"Fold unit {n}'s two halves across the other unit, one each way, and tuck them in",
            f"Dobla las dos mitades de la pieza {n} sobre la otra pieza, una hacia cada lado, y "
            "mételas",
            f"Rabattez les deux moitiés du module {n} sur l'autre module, une de chaque côté, et "
            "rentrez-les",
            f"Dobre as duas metades da peça {n} sobre a outra peça, uma para cada lado, e "
            "encaixe-as"),
    }


def unit(name, mirror, front):
    """One unit, folded in its own sheet frame (unit B is unit A's mirror image)."""
    fp = pliego.FoldProgram(RECT, stock=stock, label=L4(f"Unit {name}", f"Pieza {name}",
                                                        f"Module {name}", f"Peça {name}"),
                            front=front, back="#e9c46a")
    t, n = labels(name), name.lower()

    def F(sid, p0, p1, seeds=None, ms=1500):
        if mirror:
            p0, p1 = (4.0 * u - p1[0], p1[1]), (4.0 * u - p0[0], p0[1])
            seeds = None if seeds is None else [(4.0 * u - q[0], q[1]) for q in seeds]
        fp.fold(f"{n}-{sid}", t[sid.split("-")[0]], (p0, p1), "valley", ms=ms,
                sheet_points=seeds)
    F("crease", (2.0 * u, -1.0), (2.0 * u, 2.0 * u + 1.0), ms=900)
    fp.unfold_last(f"{n}-unfold", UNFOLD, ms=700)
    F("half", (-1.0, u), (4.0 * u + 1.0, u))
    F("corners", (u + 1.0, -1.0), (-1.0, u + 1.0))
    F("corners-2", (3.0 * u - 1.0, u + 1.0), (4.0 * u + 1.0, -1.0))
    F("arms", (u - 1.0, -1.0), (2.0 * u + 1.0, u + 1.0), [(0.3 * u, 0.9 * u)])
    F("arms-2", (3.0 * u + 1.0, u + 1.0), (2.0 * u - 1.0, -1.0), [(3.7 * u, 0.1 * u)])
    return fp.build(f"unit-{n}")


bA = unit("A", False, "#264653")
bB = unit("B", True, "#e76f51")
present([(bA, None), (bB, tB)], (0.0, 0.0, -1.0), (0.0, 1.0, 0.0))
ORDER = ["a-crease", "a-unfold", "a-half", "a-corners", "b-crease", "b-unfold", "b-half",
         "b-corners", "b-arms", "a-arms"]
seq, worst, mid = diagram([bA, bB], {"a-corners-2", "b-corners-2", "a-arms-2", "b-arms-2"},
                          ORDER)
print(bA.summary())
print(bB.summary())
print(f"kinematics: steps={len(seq.steps)} max_closure_mm={worst:.3e}")
result = pliego.Assembly(
    [bA.sheet, bB.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": {"unit-a": bA.target(), "unit-b": bB.target()}},
    title="Ninja star")
