"""Masu box — sheet-hyperobjects cartridge (Pliego): the traditional masu box and its lid.
The square starts creased along its midlines (their crease memory is the document's rest angles);
it is blintzed, creased at each edge through every layer and its ends opened, all `pliego.
FoldProgram` operations on a layer-ordered flat state (layer order, Kawasaki and Maekawa checked).
Then in 3-D: the side walls rise (`hinges`), each end wall rises while its corners fold in (a
rigid step on the whole pattern, `kinematic`), and its flap folds over the wall onto the floor (a
flat fold inside the wall's plane with the tip turning at once). No glue.
"""

import math

import pliego
import pliego.foldpose  # noqa: F401 - creases_on / edges_on: the end walls' drive creases


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
size = C(float(P(lambda: size, 200.0)), 120.0, 400.0)  # noqa: F821
gap = C(float(P(lambda: gap, 1.5)), 0.5, 5.0)  # noqa: F821
stock = P(lambda: stock, "kami")  # noqa: F821
run_mode = P(lambda: mode, "box")  # noqa: F821
S0 = size + (4.0 * math.sqrt(2.0) * gap if run_mode == "lid" else 0.0)  # lid floor 2·gap wider
# every vertex sits on a multiple of S0/8: keep those on the kernel's 1e-6 mm grid (the lid's
# square, size + 4√2·gap, moves by at most 4 µm), so the snapped pattern closes exactly where the
# end walls start to rise
S0 = round(S0 / 0.008) * 0.008
h, Lh = S0 / 2.0, S0 / math.sqrt(2.0)  # Lh: half the diagonal = the blintzed square's side
q = Lh / 4.0  # the floor is the square |x|, |y| <= q; the walls are q high
# the stocks' crease yield (`crease_yield_deg`, materials/<stock>/stock.json): a crease folded flat
# and opened again springs back to about this — the precreased square's rest angles
YIELDS = {"kami": 35.0, "copy-80": 35.0, "cardstock-160": 35.0}
if stock not in YIELDS:
    raise ValueError(f"no crease yield recorded for stock {stock!r}")
fp = pliego.FoldProgram([(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front="#f4efe6", back="#c1121f")
fp.rotate(45.0, (h, h))  # a diamond, centred on (h, h)


def o(x, y):
    """A point of the diamond's frame (centred on the origin) in the folded frame."""
    return (x + h, y + h)


corner = {}
for p in fp.state.outline:  # sheet corners by where they sit on the diamond: top, right, ...
    w = fp.state.to_folded(p)
    corner[(round((w[0] - h) / Lh), round((w[1] - h) / Lh))] = (p[0] + 0.02 * (h - p[0]),
                                                               p[1] + 0.02 * (h - p[1]))
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")


def crease(sid, label, a, b):
    """Fold and unfold through every layer."""
    fp.fold(sid, label, (o(*a), o(*b)), "valley", ms=900)
    fp.unfold_last(sid + "-open", UNFOLD, ms=600)


HALF = L4("Fold in half and unfold", "Dobla por la mitad y desdobla", "Pliez en deux et dépliez",
          "Dobre ao meio e desdobre")
crease("half-1", HALF, (-Lh, -Lh), (Lh, Lh))
crease("half-2", HALF, (Lh, -Lh), (-Lh, Lh))   # the program starts here, the square creased
BLINTZ = L4("Fold the four corners to the centre", "Dobla las cuatro esquinas hasta el centro",
            "Rabattez les quatre coins au centre", "Dobre os quatro cantos até ao centro")
for k, (a, b) in enumerate((((-Lh, 2 * q), (Lh, 2 * q)), ((2 * q, Lh), (2 * q, -Lh)),
                            ((Lh, -2 * q), (-Lh, -2 * q)), ((-2 * q, -Lh), (-2 * q, Lh)))):
    fp.fold("blintz" + (f"-{k + 1}" if k else ""), BLINTZ, (o(*a), o(*b)), "valley")
EDGE = L4("Fold the edge to the centre line and unfold",
          "Dobla el borde hasta la línea central y desdobla",
          "Rabattez le bord sur la ligne centrale et dépliez",
          "Dobre a aresta até à linha central e desdobre")
for sid, a, b in (("edge-top", (-Lh, q), (Lh, q)), ("edge-bottom", (Lh, -q), (-Lh, -q)),
                  ("edge-right", (q, Lh), (q, -Lh)), ("edge-left", (-q, -Lh), (-q, Lh))):
    crease(sid, EDGE, a, b)
OPEN = L4("Unfold the top and bottom corners", "Desdobla las esquinas de arriba y de abajo",
          "Dépliez les coins du haut et du bas", "Desdobre os cantos de cima e de baixo")
fp.fold("open-ends", OPEN, (o(Lh, 2 * q), o(-Lh, 2 * q)), "valley", ms=1200,
        sheet_points=[corner[(0, 1)]])
fp.fold("open-ends-2", OPEN, (o(-Lh, -2 * q), o(Lh, -2 * q)), "valley",
        sheet_points=[corner[(0, -1)]])
flat = fp.state

# ── 3-D: the side walls, then each end wall with its corners, then its flap ──
fp.hinges("walls", L4("Raise the two side walls", "Levanta las dos paredes laterales",
                      "Relevez les deux parois latérales", "Levante as duas paredes laterais"),
          [{"line": (o(q, -Lh), o(q, Lh)), "turn": 90.0, "at": o(1.6 * q, 0.0)},
           {"line": (o(-q, -Lh), o(-q, Lh)), "turn": 90.0, "at": o(-1.6 * q, 0.0)}], ms=1500)
END = L4("Raise the end wall: its corners fold in",
         "Levanta la pared del extremo: sus esquinas se doblan hacia dentro",
         "Relevez la paroi du bout : ses coins se replient vers l'intérieur",
         "Levante a parede da ponta: os cantos dobram-se para dentro")
FLAP = L4("Fold the flap over the wall and down onto the floor",
          "Dobla la solapa por encima de la pared y hasta el fondo",
          "Rabattez le rabat par-dessus la paroi jusqu'au fond",
          "Dobre a aba por cima da parede até ao fundo")
N, SPLIT = 5, {}
for sy in (1, -1):
    tag = "top" if sy > 0 else "bottom"
    free = []
    for sx in (1, -1):
        free += [(o(sx * q, sy * q), o(sx * 2 * q, sy * q)),
                 (o(sx * q, sy * q), o(sx * q, sy * 3 * q)),
                 (o(sx * q, sy * q), o(sx * 2 * q, sy * 2 * q))]
    drive = (o(-q, sy * q), o(q, sy * q))
    # leaving flat, each gusset folds in (the hint); then on to 90° in one rigid step, shown
    # as four steps of 18° (the drive turns evenly along the kernel's chord)
    fp.kinematic(f"end-{tag}-1", parts_of("end", END, N)[0][1], [(drive, 90.0 / N)],
                 free=[(f, "valley") if j % 3 == 1 else f for j, f in enumerate(free)],
                 fixed=(h, h), ms=450, substeps=1)
    SPLIT[f"end-{tag}"] = (parts_of(f"end-{tag}", END, N, 2),
                           pliego.foldpose.creases_on(fp.state, [drive]))
    fp.kinematic(f"end-{tag}", END, [(drive, 90.0)], free=free, fixed=(h, h), ms=450 * (N - 1),
                 substeps=N - 1)
    line = (o(-Lh, 2 * q), o(Lh, 2 * q)) if sy > 0 else (o(Lh, -2 * q), o(-Lh, -2 * q))
    fp.fold(f"flap-{tag}", FLAP, line, "valley", within=flat.preimage(o(0.0, sy * 1.5 * q)),
            sheet_points=[corner[(0, sy)]], ms=1500,
            hinge={"line": (o(-Lh, sy * 3 * q), o(Lh, sy * 3 * q)), "turn": -90.0,
                   "at": o(0.0, sy * 3.5 * q)})
    # read the flap's creases halfway too: a crease that goes from open to ±180° in one sample
    # takes its sign from the motion, not from round-off at the end
    fp.recs[-1].move.samples[:] = [0.5, 1.0]

built = fp.build("square", start_after="half-2-open", rest_memory=YIELDS[stock])
fm, st = pliego.flatmotion, fp.state
wld = [fm.compose(((fm.ID_RIGID[0]), (-h, 0.0, h)), w) for w in fp.pose.world]  # centre at 0
box = [fm.apply(wld[f], fm.w3(p)) for f in range(len(st.faces)) for p in st.poly(f)]
if max(max(abs(w[0]), abs(w[2]), abs(w[1] - q / 2.0) + q / 2.0) for w in box) > q + 1e-6:
    raise ValueError("the finished box has paper outside its walls")
present(built, wld, (0.0, 0.0, -1.0), (0.0, 1.0, 0.0))
for sid, (parts, segs) in SPLIT.items():
    SPLIT[sid] = (parts, pliego.foldpose.edges_on(built.arr, segs))
seq, worst, mid = diagram(built, fp.recs, {"blintz-2", "blintz-3", "blintz-4", "open-ends-2"},
                          split=SPLIT)
print(built.summary())
print(f"kinematics: mode={run_mode} side={S0:.1f}mm floor={2 * q:.1f}mm wall={q:.1f}mm "
      f"steps={len(seq.steps)} max_closure_mm={worst:.3e} max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, initial=built.initial("square"), targets={"folded": built.target(pose=True)},
    title="Masu box" if run_mode == "box" else "Masu box lid")
