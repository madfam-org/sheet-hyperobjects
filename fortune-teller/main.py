"""Fortune teller (comecocos, salt cellar) — sheet-hyperobjects cartridge (Pliego).
Two blintzes and four creases through every layer, each a `pliego.FoldProgram` operation on a
layer-ordered flat state (layer order, Kawasaki and Maekawa checked after every fold); then the
toy's degree-8 vertex in 3-D (`FoldProgram.vertex_pose`): shaped, opened one way, closed, opened
the other way, every state an exact rigid pose of the vertex's eight sectors.
"""

import math

import pliego
import pliego.flatvertex  # noqa: F401 - the vertex's star (sectors and rays)
import pliego.motion  # noqa: F401 - vertex_folds


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
size = C(float(P(lambda: size, 200.0)), 120.0, 300.0)  # noqa: F821
mouth = C(float(P(lambda: mouth, 24.0)), 8.0, 34.0)  # noqa: F821
rest = P(lambda: rest, "open-ns")  # noqa: F821
stock = P(lambda: stock, "copy-80")  # noqa: F821
if rest not in ("closed", "open-ns", "open-ew"):
    raise ValueError(f"unknown rest pose {rest!r}")
s, h = size, size / 2.0
q, Q = s / 4.0, 3.0 * s / 4.0
O = (h, h)

fp = pliego.FoldProgram([(0.0, 0.0), (s, 0.0), (s, s), (0.0, s)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front="#e4572e", back="#f3e9d2")

# ── 1. two blintzes: four corners to the centre, then the four new corners behind ──
BLINTZ = L4("Fold the four corners to the centre", "Dobla las cuatro esquinas hasta el centro",
            "Rabattez les quatre coins au centre", "Dobre os quatro cantos até ao centro")
AGAIN = L4("Turn over and fold the four new corners to the centre",
           "Da la vuelta y dobla las cuatro esquinas nuevas hasta el centro",
           "Retournez et rabattez les quatre nouveaux coins au centre",
           "Vire a folha e dobre os quatro cantos novos até ao centro")
JOINS = set()
for k, (p0, p1) in enumerate((((h, 0.0), (0.0, h)), ((s, h), (h, 0.0)), ((h, s), (s, h)),
                              ((0.0, h), (h, s)))):
    sid = "blintz" if k == 0 else f"blintz-{k + 1}"
    fp.fold(sid, BLINTZ, (p0, p1), "valley")
    JOINS |= {sid} if k else set()
for k, (p0, p1) in enumerate((((Q, q), (q, q)), ((Q, Q), (Q, q)), ((q, Q), (Q, Q)),
                              ((q, q), (q, Q)))):
    sid = "blintz-again" if k == 0 else f"blintz-again-{k + 1}"
    fp.fold(sid, AGAIN, (p0, p1), "mountain")  # the back's corners, seen from the front
    JOINS |= {sid} if k else set()

# ── 2. crease both midlines and both diagonals through every layer ────────────
LINES = (
    ((h, -1.0), (h, s + 1.0), "mid-ns",
     L4("Fold in half and unfold", "Dobla por la mitad y desdobla", "Pliez en deux et dépliez",
        "Dobre ao meio e desdobre")),
    ((s + 1.0, h), (-1.0, h), "mid-ew",
     L4("Fold in half the other way and unfold", "Dobla por la mitad en el otro sentido y desdobla",
        "Pliez en deux dans l'autre sens et dépliez", "Dobre ao meio no outro sentido e desdobre")),
    ((s, 0.0), (0.0, s), "diag-1",
     L4("Fold along a diagonal and unfold", "Dobla por una diagonal y desdobla",
        "Pliez selon une diagonale et dépliez", "Dobre por uma diagonal e desdobre")),
    ((0.0, 0.0), (s, s), "diag-2",
     L4("Fold along the other diagonal and unfold", "Dobla por la otra diagonal y desdobla",
        "Pliez selon l'autre diagonale et dépliez", "Dobre pela outra diagonal e desdobre")),
)
for p0, p1, sid, lab in LINES:
    fp.fold(sid, lab, (p0, p1), "valley", ms=1100)
    fp.unfold_last(sid + "-open", ms=700)

# ── 3. the toy: one rigid degree-8 vertex at the centre, eight 45° sectors ────
X, N, U = (1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, -1.0, 0.0)  # east, north, up (the points)


def ray(az, polar):
    a, p = math.radians(az), math.radians(polar)
    return tuple(math.sin(p) * (math.cos(a) * X[i] + math.sin(a) * N[i]) + math.cos(p) * U[i]
                 for i in range(3))


def shaping(alpha):
    """Fourfold-symmetric rays: diagonals at polar alpha from the up axis, midlines at beta."""
    A, B, c45 = math.sqrt(0.5) * math.sin(math.radians(alpha)), math.cos(math.radians(alpha)), \
        math.sqrt(0.5)
    beta = math.degrees(math.atan2(A, B) + math.acos(min(1.0, c45 / math.hypot(A, B))))
    return {45 * k: ray(45.0 * k, alpha if k % 2 else beta) for k in range(8)}


def opened(tau, axis):
    """The mouth open by tau along 'ns' (north and south jaws apart) or 'ew'."""
    t, c45 = math.radians(tau), math.sqrt(0.5)
    be, bn = math.degrees(math.acos(c45 / math.cos(t))), tau + 45.0
    r = {0: ray(0.0, be), 90: ray(90.0, bn), 180: ray(180.0, be), 270: ray(270.0, bn)}
    for az in (45, 135, 225, 315):
        north = 1.0 if az < 180 else -1.0
        r[az] = tuple(math.cos(t) * U[i] + north * math.sin(t) * N[i] for i in range(3))
    if axis == "ns":
        return r
    return {az: (v[2], v[1], -v[0]) for az, v in  # +90° about up
            ((az, r[(az - 90) % 360]) for az in range(0, 360, 45))}


star = pliego.flatvertex.star(fp.state, O)
ORDER = [round(math.degrees(math.atan2(d[1], d[0]))) % 360 for d in star.dirs]
prev = [None, None]


def angles_of(rays):
    """Fold angles of the vertex's rays (valley > 0) for those ray directions, continuous with
    the previous pose."""
    out = pliego.motion.vertex_folds([rays[az] for az in ORDER], prev[0])
    prev[:] = [out, rays]
    return dict(zip(ORDER, out, strict=True))


def upright(world, rays):
    """The vertex poses keep one sector still; turn the model so its rays point where `rays`
    asks (the up axis through the points vertical, as the toy is held)."""
    fm = pliego.flatmotion

    def wdir(az):
        a = math.radians(az + 10.0)
        f = fp.state.face_at((h + 5.0 * math.cos(a), h + 5.0 * math.sin(a)))
        d = fm.wdir((math.cos(math.radians(az)), math.sin(math.radians(az))))
        return fm.apply((world[f][0], (0.0, 0.0, 0.0)), d)
    g = fm.frame_map(wdir(0), wdir(90), rays[0], rays[90], fm.w3(O))
    return [fm.compose(g, w) for w in world]


def drive(name, fn, a0, a1, n, ms, label):
    for i in range(1, n + 1):
        sid = f"{name}-{i}" if n > 1 else name
        lab = {k: f"{v} ({i}/{n})" if n > 1 else v for k, v in label.items()}
        fp.vertex_pose(sid, lab, O, angles_of(fn(a0 + (a1 - a0) * i / n)), ms=ms, substeps=1)


angles_of(shaping(89.0))  # the signs the toy leaves the flat sheet with
drive("shape", shaping, 90.0, 0.0, 6, 450, L4(
    "Push the four corners together from below: the four points rise and meet",
    "Empuja las cuatro esquinas desde abajo: las cuatro puntas suben y se juntan",
    "Poussez les quatre coins par en dessous : les quatre pointes montent et se rejoignent",
    "Empurre os quatro cantos por baixo: as quatro pontas sobem e juntam-se"))
OPEN = {"ns": L4("Open the mouth one way", "Abre la boca hacia un lado",
                 "Ouvrez la bouche dans un sens", "Abra a boca para um lado"),
        "ew": L4("Open the mouth the other way", "Abre la boca hacia el otro lado",
                 "Ouvrez la bouche dans l'autre sens", "Abra a boca para o outro lado")}
SHUT = L4("Close it", "Ciérrala", "Refermez-la", "Feche-a")
for axis in ("ns", "ew"):
    drive(f"open-{axis}", lambda t, a=axis: opened(t, a), 0.0, mouth, 3, 350, OPEN[axis])
    drive(f"close-{axis}", lambda t, a=axis: opened(t, a), mouth, 0.0, 3, 350, SHUT)
if rest != "closed":
    ax = rest[-2:]
    drive("rest", lambda t, a=ax: opened(t, a), 0.0, mouth, 3, 350, OPEN[ax])

built = fp.build("square")
present(built, upright(fp.pose.world, prev[1]), (0.0, 0.0, -1.0), U)
seq, worst, mid = diagram(built, fp.recs, JOINS)
print(built.summary())
print(f"kinematics: rest={rest} steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target(pose=True)}, title="Fortune teller")
