"""Paper cup — sheet-hyperobjects cartridge (Pliego): the traditional folded cup and the rolled
drinking cone (cucurucho). The cup is folded flat by `pliego.FoldProgram` operations on a
layer-ordered flat state (layer order, Kawasaki and Maekawa checked), its front flap tucked into
the pocket in front (`FoldProgram.tuck`); the cone is the square rolled about the middle of one
edge by hinge poses about flat facet lines (real paper curves smoothly).
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
cone_angle = C(float(P(lambda: cone_angle, 22.0)), 15.0, 30.0)  # noqa: F821
stock = P(lambda: stock, "copy-80")  # noqa: F821
run_mode = P(lambda: mode, "cup")  # noqa: F821
S0, h = size, size / 2.0
fm, JOINS = pliego.flatmotion, set()
fp = pliego.FoldProgram([(0.0, 0.0), (S0, 0.0), (S0, S0), (0.0, S0)], stock=stock,
                        label=L4("Square", "Cuadrado", "Carré", "Quadrado"),
                        front="#f4efe6", back="#2a9d8f")


def unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


if run_mode == "cup":
    fp.rotate(45.0, (h, h))  # the square turned 45° (a diamond), centred on (h, h)
    d = S0 / math.sqrt(2.0)

    def o(x, y):
        """A point of the diamond's frame (centred on the origin) in the folded frame."""
        return (x + h, y + h)

    corner = {}
    for p in fp.state.outline:
        w = fp.state.to_folded(p)
        corner[(round((w[0] - h) / d), round((w[1] - h) / d))] = (p[0] + 0.03 * (h - p[0]),
                                                                 p[1] + 0.03 * (h - p[1]))
    fp.fold("triangle", L4("Fold the square in half along a diagonal: a triangle, point up",
                           "Dobla el cuadrado por la mitad por una diagonal: un triángulo con la "
                           "punta arriba",
                           "Pliez le carré en deux selon une diagonale : un triangle, pointe en "
                           "haut",
                           "Dobre o quadrado ao meio por uma diagonal: um triângulo com a ponta "
                           "para cima"),
            (o(d + 1.0, 0.0), o(-d - 1.0, 0.0)), "valley")
    # the corner R lands on the opposite edge and the folded edge comes out level (67.5° line)
    r2 = math.sqrt(2.0)
    a, b = ((3.0 - 2.0 * r2) * d, 0.0), ((r2 - 1.0) * d, (2.0 - r2) * d)
    t = 2.0
    fp.fold("corner-right", L4("Fold the right corner to the left edge, so its top edge lies "
                               "level",
                               "Dobla la esquina derecha hasta el borde izquierdo, con su borde "
                               "superior horizontal",
                               "Rabattez le coin droit sur le bord gauche, son bord supérieur à "
                               "l'horizontale",
                               "Dobre o canto direito até à aresta esquerda, com a aresta de cima "
                               "na horizontal"),
            (o(a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])),
             o(a[0] - t * (b[0] - a[0]), a[1] - t * (b[1] - a[1]))), "valley")
    fp.fold("corner-left", L4("Fold the left corner across to the right edge the same way",
                              "Dobla la esquina izquierda hasta el borde derecho de la misma "
                              "manera",
                              "Rabattez le coin gauche sur le bord droit de la même façon",
                              "Dobre o canto esquerdo até à aresta direita da mesma maneira"),
            (o(-a[0] + t * (b[0] - a[0]), a[1] - t * (b[1] - a[1])),
             o(-a[0] - t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))), "valley")
    y_top = (2.0 - r2) * d
    fp.tuck("front-flap", L4("Fold the front top flap down into the pocket in front",
                             "Dobla la solapa superior de delante hacia abajo, dentro del bolsillo "
                             "delantero",
                             "Rabattez le rabat supérieur avant dans la poche de devant",
                             "Dobre a aba de cima da frente para baixo, para dentro do bolso da "
                             "frente"),
            (o(-d, y_top), o(d, y_top)), "valley", sheet_points=[corner[(0, -1)]],
            pocket=(o(0.0, y_top - 0.1 * d), 1), ms=1500)
    fp.fold("back-flap", L4("Fold the back top flap down behind: the cup",
                            "Dobla la solapa superior de atrás hacia atrás: el vaso",
                            "Rabattez le rabat supérieur arrière derrière : le gobelet",
                            "Dobre a aba de cima de trás para trás: o copo"),
            (o(-d, y_top), o(d, y_top)), "mountain", sheet_points=[corner[(0, 1)]])
    built = fp.build("square")
    wld = [fm.compose((fm.ID_RIGID[0], (-h, 0.0, h)), pliego.flatstate.embed3(f.xf))
           for f in fp.state.faces]  # the diamond's centre at the origin
    present(built, wld, (0.0, 1.0, 0.0), (0.0, 0.0, -1.0))  # stand the flat cup up, mouth on top
    title = "Paper cup"
else:
    # the drinking cone (cucurucho): the square rolled about the midpoint of its bottom edge
    A = (h, 0.0)
    al = math.radians(cone_angle)
    turn_dev = 360.0 * math.sin(al)  # development angle of one turn of the cone, degrees
    n_turn = 12
    delta = turn_dev / n_turn
    k = int(180.0 / delta - 1e-9)
    gens = [(math.sin(al) * math.cos(math.radians(360.0 * i / n_turn)),
             math.sin(al) * math.sin(math.radians(360.0 * i / n_turn)), -math.cos(al))
            for i in range(-1, 2)]

    def cross(u, v):
        return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])

    def dot(u, v):
        return sum(u[i] * v[i] for i in range(3))
    n1, n2 = unit(cross(gens[0], gens[1])), unit(cross(gens[1], gens[2]))
    rho = math.degrees(math.atan2(dot(unit(gens[1]), cross(n1, n2)), dot(n1, n2)))
    ROLL = L4(f"Roll the square into a cone around the middle of one edge ({cone_angle:.0f}° "
              "half-angle)",
              f"Enrolla el cuadrado en un cono alrededor del centro de un borde ({cone_angle:.0f}° "
              "de semiángulo)",
              f"Roulez le carré en cône autour du milieu d'un bord ({cone_angle:.0f}° de "
              "demi-angle)",
              f"Enrole o quadrado num cone em torno do meio de uma aresta ({cone_angle:.0f}° de "
              "semiângulo)")
    lines = [math.radians(i * delta) for i in range(1, k + 1)]
    for i, th in enumerate(lines):  # the facet lines, scored flat (no motion, no step)
        fp.crease(f"facet-{i + 1}", ROLL, (A, (A[0] + 3.0 * S0 * math.cos(th),
                                               A[1] + 3.0 * S0 * math.sin(th))), "valley")
    for i, th in enumerate(lines):  # every facet line turns at once: the paper beyond each line
        ts = min(th + math.radians(delta / 2.0), (th + math.pi) / 2.0)
        fp.hinge("roll" if i == 0 else f"roll-{i + 1}", ROLL,
                 (A, (A[0] + math.cos(th), A[1] + math.sin(th))), abs(rho),
                 at=(A[0] + 20.0 * math.cos(ts), A[1] + 20.0 * math.sin(ts)), ms=3000)
        JOINS.add(f"roll-{i + 1}") if i else None
    built = fp.build("square")
    wld, st = fp.pose.world, fp.state

    def at3(p):
        return fm.apply(wld[st.face_at(p)], fm.w3(p))
    axis = (0.0, 0.0, 0.0)
    for th in lines:
        tm = th - math.radians(delta / 2.0)
        g = unit(tuple(x - y for x, y in zip(
            at3((A[0] + 20.0 * math.cos(tm), A[1] + 20.0 * math.sin(tm))),
            at3((A[0] + 10.0 * math.cos(tm), A[1] + 10.0 * math.sin(tm))), strict=True)))
        axis = tuple(axis[i] + g[i] for i in range(3))
    up = unit(axis)
    present(built, wld, unit(cross(up, (1.0, 0.0, 0.0) if abs(up[0]) < 0.9 else (0.0, 0.0, 1.0))),
            up)
    title = "Drinking cone"

seq, worst, mid = diagram(built, fp.recs, JOINS)
print(built.summary())
print(f"kinematics: mode={run_mode} steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target(pose=run_mode == "cone")}, title=title)
