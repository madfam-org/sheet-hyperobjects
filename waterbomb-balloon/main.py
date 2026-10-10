"""Waterbomb balloon — sheet-hyperobjects cartridge (Pliego): the traditional water bomb.
The square starts creased (two diagonals valley, the midline mountain; their crease memory is the
document's rest angles), collapses into the waterbomb base as one degree-6 vertex
(`pliego.flatvertex.collapse`), then on each face the corners fold up, the side points in and the
two top points are tucked into the side pockets (`FoldProgram.tuck`). Every fold is a
`pliego.FoldProgram` operation on a layer-ordered flat state, checked for layer order, Kawasaki
and Maekawa. Inflating it is pressure on paper and waits for the physics engine.
"""

import math

import pliego
import pliego.flatvertex  # noqa: F401 - the base's vertex collapse


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


def present(b, world, fwd, up, lift=0.0):
    """Show the finished model with `up` → +Y and `fwd` → −Z, resting on the floor. `world`: the
    final world pose of every face of `b.state` (`fp.pose.world`); the studio roots the sheet at
    pattern face 0, and the flat sheet of the first frame stays above the floor too."""
    fm = pliego.flatmotion
    lat = (up[1] * fwd[2] - up[2] * fwd[1], up[2] * fwd[0] - up[0] * fwd[2],
           up[0] * fwd[1] - up[1] * fwd[0])
    rd = (((-lat[0], -lat[1], -lat[2]), tuple(up), (-fwd[0], -fwd[1], -fwd[2])), (0.0, 0.0, 0.0))
    st = b.state
    g = [fm.compose(rd, w) for w in world]
    f0 = g[b.face_map[0]]
    pts = [(f0, q) for q in st.outline] + [(g[f], q) for f in range(len(st.faces))
                                           for q in st.poly(f)]
    low = min(fm.apply(w, (q[0], 0.0, -q[1]))[1] for w, q in pts)
    r, t = f0
    b.sheet.placement = pliego.Placement((t[0], t[1] - low + lift, t[2]), quat(r))


def diagram(b, recs, joins=(), split=None):
    """The kinematic fold program: each operation one step (the samples the build adds for the
    preview's blend merged back, so step ids stay the operations'), an operation in `split`
    ({id: (parts, edges)}, parts [(step id, label)]) shown as one step per part — even shares of
    its samples (edges None) or of the turn of the drive edge `edges[0]` — the operations in
    `joins` merged into the step before them, and the worst loop closure at every state and
    halfway between states (the preview's linear blend)."""
    meta, src, steps, i = {r.sid: r for r in recs}, b.sequence.steps, [], 0
    run = dict(b.start_angles)
    for row in b.report["rows"]:
        sid, n = row["id"], row["samples"]
        names = {sid} if n == 1 else {f"{sid}-{k}" for k in range(1, n + 1)}
        grp = []
        while i < len(src) and src[i].id in names:
            grp.append(src[i])
            i += 1
        rec, (parts, edges), out = meta[sid], (split or {}).get(sid, ([], None)), {}
        e, k = (edges or [None])[0], max(1, len(parts))
        a0 = run.get(e, 0.0)
        a1 = next((a for st in reversed(grp) for r, a in st.targets if r.edge == e), a0)
        for st in grp:
            run.update({r.edge: a for r, a in st.targets})
            g = int(st.id.rsplit("-", 1)[1]) if n > 1 else 1
            g = max(1, math.ceil((run[e] - a0) / (a1 - a0) * k - 1e-6)) if e is not None \
                else -(-g * k // n)
            out.setdefault(min(g, k), {}).update({r.edge: (r, a) for r, a in st.targets})
        for g, tg in sorted(out.items()):
            tgs = sorted(tg.values(), key=lambda x: x[0].edge)
            if parts:
                steps.append(pliego.Step(parts[g - 1][0], parts[g - 1][1], tgs,
                                         duration_ms=rec.ms // k,
                                         note=rec.note if g == 1 else None))
            elif sid in joins:
                pv = steps.pop()
                tgs = sorted({**{r.edge: (r, a) for r, a in pv.targets}, **tg}.values(),
                             key=lambda x: x[0].edge)
                steps.append(pliego.Step(pv.id, pv.label, tgs, duration_ms=pv.duration_ms,
                                         note=pv.note))
            else:
                steps.append(pliego.Step(sid, rec.label, tgs, duration_ms=rec.ms, note=rec.note))
    if i != len(src):
        raise ValueError(f"diagram: step {src[i].id} matches no operation")
    worst = mid = 0.0
    cur, rt = dict(b.start_angles), pliego.P(*b.root())
    for st in steps:
        nxt = {**cur, **{r.edge: a for r, a in st.targets}}
        half = {e: (cur[e] + nxt[e]) / 2.0 for e in cur}
        worst = max(worst, pliego.kinematics.closure_residual(b.arr, nxt, rt))
        mid = max(mid, pliego.kinematics.closure_residual(b.arr, half, rt))
        cur = nxt
    if worst > 1e-3:
        raise ValueError(f"inconsistent fold state: closure {worst:.3g} mm")
    return pliego.Sequence(steps, mode="kinematic"), worst, mid


def parts_of(sid, label, n, first=1):
    """Step ids and labels <sid>-k, "label (k/n)", for k = first … n."""
    return [(f"{sid}-{k}", {g: f"{v} ({k}/{n})" for g, v in label.items()})
            for k in range(first, n + 1)]


# ── parameters ───────────────────────────────────────────────────────────────
P, C = pliego.param, pliego.clamp
size = C(float(P(lambda: size, 150.0)), 100.0, 300.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
S0, h = size, size / 2.0
q, Q, e = S0 / 4.0, 3.0 * S0 / 4.0, 3.0 * S0 / 8.0
O = (h, h)
# a crease folded flat and opened again springs back to about the stock's yield angle: the
# precreased square's rest angles (crease memory, `pliego:edges_restAngle`); the values are the
# stocks' `crease_yield_deg` (materials/<stock>/stock.json, derived block)
YIELDS = {"kami": 35.0, "copy-80": 35.0}
if stock not in YIELDS:
    raise ValueError(f"no crease yield recorded for stock {stock!r}")
YIELD = YIELDS[stock]
fp = pliego.FoldProgram([(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front="#3a86ff", back="#f4efe6")
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")

# ── 1. the waterbomb base: two diagonals, one midline, one rigid degree-6 vertex ──
# (the precreases shape the starting sheet; the program starts at the collapse)
fp.fold("diagonal-1", L4("Valley-fold along a diagonal", "Dobla en valle por una diagonal",
                         "Pliez en vallée selon une diagonale", "Dobre em vale por uma diagonal"),
        ((0.0, S0), (S0, 0.0)), "valley", ms=1100)
fp.unfold_last("diagonal-1-open", UNFOLD, ms=700)
fp.fold("diagonal-2", L4("Valley-fold along the other diagonal",
                         "Dobla en valle por la otra diagonal",
                         "Pliez en vallée selon l'autre diagonale",
                         "Dobre em vale pela outra diagonal"),
        ((0.0, 0.0), (S0, S0)), "valley", at=(1.0, S0 - 6.0), ms=1100)
fp.unfold_last("diagonal-2-open", UNFOLD, ms=700)
fp.fold("midline", L4("Mountain-fold in half, top behind",
                      "Dobla en monte por la mitad, la parte de arriba hacia atrás",
                      "Pliez en deux en montagne, le haut vers l'arrière",
                      "Dobre em montanha ao meio, a parte de cima para trás"),
        ((-1.0, h), (S0 + 1.0, h)), "mountain", ms=1100)
fp.unfold_last("midline-open", UNFOLD, ms=700)
N = 6
base = pliego.flatvertex.collapse(fp.state, O, {0: "mountain", 180: "mountain", 45: "valley",
                                                135: "valley", 225: "valley", 315: "valley"})
base.samples[:] = [k / (4 * N) for k in range(1, 4 * N + 1)]  # shown as six key states
COLLAPSE = L4("Collapse into the waterbomb base: sides in, top down",
              "Colapsa en la base de bomba de agua: lados hacia dentro, arriba hacia abajo",
              "Affaissez en base de la bombe à eau : côtés dedans, haut en bas",
              "Colapse na base da bomba de água: lados para dentro, cima para baixo")
fp.add("collapse", COLLAPSE, base, ms=450 * N)


# ── 2. each face: corners up, sides in, top points tucked into the pockets ────
def face(kind, side):
    """The front face (valley folds, the top layers) or the back one (mountain folds, the bottom
    layers, as seen from the front)."""
    lay = "top" if kind == "valley" else "bottom"
    corners = L4(f"{side.capitalize()}: fold the bottom corners up to the top point",
                 f"{'Delante' if side == 'front' else 'Detrás'}: dobla las esquinas de abajo "
                 "hasta la punta de arriba",
                 f"{'Devant' if side == 'front' else 'Derrière'} : rabattez les coins du bas "
                 "jusqu'à la pointe du haut",
                 f"{'Frente' if side == 'front' else 'Trás'}: dobre os cantos de baixo até à "
                 "ponta de cima")
    fp.fold(f"{side}-corners", corners, ((h, 0.0), (q, q)), kind, at=(3.0, 1.5), layers=1)
    fp.fold(f"{side}-corners-2", corners, ((Q, q), (h, 0.0)), kind, at=(S0 - 3.0, 1.5),
            layers=1)
    sl, sr = fp.state.preimage((q + 2.0, q), lay), fp.state.preimage((Q - 2.0, q), lay)
    sides = L4("Fold the side points in to the centre line",
               "Dobla las puntas laterales hasta la línea central",
               "Rabattez les pointes latérales sur la ligne centrale",
               "Dobre as pontas laterais até à linha central")
    fp.fold(f"{side}-sides", sides, ((e, -1.0), (e, S0)), kind, sheet_points=[sl])
    fp.fold(f"{side}-sides-2", sides, ((S0 - e, S0), (S0 - e, -1.0)), kind, sheet_points=[sr])
    tips = [fp.state.preimage((h - 1.0, h - 4.0), lay), fp.state.preimage((h + 1.0, h - 4.0), lay)]
    tuck = L4("Fold the two top points down and tuck them into the side pockets",
              "Dobla hacia abajo las dos puntas de arriba y mételas en los bolsillos laterales",
              "Rabattez les deux pointes du haut et glissez-les dans les poches latérales",
              "Dobre para baixo as duas pontas de cima e meta-as nos bolsos laterais")
    for k, (tip, px) in enumerate(((tips[0], h - 6.0), (tips[1], h + 6.0))):
        fp.tuck(f"{side}-tuck" + ("-2" if k else ""), tuck, ((-1.0, e), (S0 + 1.0, e)), kind,
                sheet_points=[tip], pocket=((px, e - 4.0), 1), ms=1500)


face("valley", "front")
face("mountain", "back")
JOINS = {f"{s}-{x}-2" for s in ("front", "back") for x in ("corners", "sides", "tuck")}

built = fp.build("square", start_after="midline-open", rest_memory=YIELD)
st, fm = fp.state, pliego.flatmotion
wld = [pliego.flatstate.embed3(f.xf) for f in st.faces]


def at3(p):
    return fm.apply(wld[st.face_at(p)], fm.w3(p))


top, low = at3((h, h - 4.0)), at3((h, 2.0))
fwd = tuple(top[k] - low[k] for k in range(3))
fwd = tuple(x / math.sqrt(sum(y * y for y in fwd)) for x in fwd)
r = wld[st.face_at((h, 2.0))][0]
present(built, wld, fwd, (r[0][1], r[1][1], r[2][1]))
seq, worst, mid = diagram(built, fp.recs, JOINS,
                          split={"collapse": (parts_of("collapse", COLLAPSE, N), None)})
print(built.summary())
print(f"kinematics: steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e} pocket_crossings="
      f"{sum(r.get('pocket_crossings', 0) for r in built.report['rows'])}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, initial=built.initial("square"),
    targets={"folded": built.target()}, title="Waterbomb balloon")
