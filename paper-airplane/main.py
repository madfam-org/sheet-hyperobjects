"""Paper airplane — sheet-hyperobjects cartridge (Pliego): one family, every common plane.
Designs: classic dart, glider, delta, flat-nose square plane, canard (original MADFAM) and ring
wing. Each is folded flat by `pliego.FoldProgram` operations on a layer-ordered flat state (layer
order, Kawasaki and Maekawa checked after every fold; slits cut through the layers), then opened
to its 3-D form (dihedral, winglets, trim; the ring rolled into a hoop) by hinge poses.
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
design = P(lambda: design, "dart")  # noqa: F821
paper = P(lambda: paper, "a4")  # noqa: F821
winglets = P(lambda: winglets, "none")  # noqa: F821
stock = P(lambda: stock, "copy-80")  # noqa: F821
keel = float(P(lambda: keel, 0.0))  # noqa: F821
dihedral = C(float(P(lambda: dihedral, 6.0)), 0.0, 20.0)  # noqa: F821
winglet_height = C(float(P(lambda: winglet_height, 12.0)), 6.0, 25.0)  # noqa: F821
trim = C(float(P(lambda: trim, 0.0)), -20.0, 30.0)  # noqa: F821
nose_folds = int(C(int(P(lambda: nose_folds, 0)), 0, 3))  # noqa: F821
ring_width = C(float(P(lambda: ring_width, 45.0)), 30.0, 70.0)  # noqa: F821
SIZES = {"a4": (210.0, 297.0), "letter": (215.9, 279.4), "square": (210.0, 210.0)}
if design not in ("dart", "glider", "delta", "square", "canard", "ring") or paper not in SIZES \
        or winglets not in ("none", "up", "down"):
    raise ValueError(f"unknown design/paper/winglets {design!r} {paper!r} {winglets!r}")
W, H = SIZES[paper]
c = W / 2.0
KEEL = {"dart": 0.12, "glider": 0.08, "delta": 0.16, "square": 0.10, "canard": 0.10, "ring": 0.1}
k = max(0.06 * W, min(0.22 * W, keel if keel > 0 else KEEL[design] * W))
SPREAD, FRONT, BACK = 16.0, "#f4efe6", "#4f7cac"  # spread: angle between the fuselage sides
JOINS, fm = set(), pliego.flatmotion


def mirror(p):  # the left half's sheet point matching a right-half one
    return (2.0 * c - p[0], p[1])


def joined(sid, label, lines, **kw):
    """Folds the diagram shows as one step: `sid`, then `sid`-2 … merged into it."""
    for i, (line, direction, extra) in enumerate(lines):
        extra = extra if isinstance(extra, dict) else extra()
        fp.fold(sid if i == 0 else f"{sid}-{i + 1}", label, line, direction, **{**kw, **extra})
        JOINS.add(f"{sid}-{i + 1}") if i else None


def half(sx, below=math.inf):
    """Every layer of the right (sx = 1) or left (−1) half, below the sheet height `below`: a
    side's wing, foreplane or winglet folds with all of that side's paper beyond the line (its
    folded-in flaps too)."""
    pts = [fp.state.poly(f) for f in range(len(fp.state.faces))]
    return {"faces": [f for f, poly in enumerate(pts)
                      if (sum(q[0] for q in poly) / len(poly) - c) * sx > 0
                      and sum(q[1] for q in poly) / len(poly) < below]}


def roll_band(sid, label, top, n, depth, width):
    joined(sid, label, [(((-10.0, top - i * depth), (width + 10.0, top - i * depth)), "valley", {})
                        for i in range(1, n + 1)])
    return top - n * depth


def at3(p):
    """World position of a sheet point in the current pose."""
    return fm.apply(fp.pose.world[fp.state.face_at(p)], fm.w3(p))


def unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


if design == "ring":  # the ring wing: a strip rolled into a hoop
    LR, N, OVER = H, 16, 0.06 * H
    fp = pliego.FoldProgram([(0.0, 0.0), (LR, 0.0), (LR, ring_width), (0.0, ring_width)],
                            stock=stock, label=L4("Strip", "Tira", "Bande", "Tira"),
                            front=FRONT, back=BACK)
    nb = 2 + nose_folds
    roll_band("leading-edge", L4(
        f"Fold the leading edge over {nb} times, 6 mm each: the weighted rim",
        f"Dobla el borde de ataque {nb} veces, 6 mm cada vez: el aro lastrado",
        f"Repliez le bord d'attaque {nb} fois, 6 mm à chaque fois : le bord lesté",
        f"Dobre o bordo de ataque {nb} vezes, 6 mm de cada vez: o aro com lastro"),
        ring_width, nb, 6.0, LR)
    s = (LR - OVER) / N
    lines = [i * s for i in range(1, N + 1)]
    ROLL = L4("Roll the strip into a hoop and tuck the end inside the start",
              "Enrolla la tira en un aro y mete el final dentro del principio",
              "Roulez la bande en anneau et glissez la fin dans le début",
              "Enrole a tira num aro e encaixe o fim dentro do início")
    for i, u in enumerate(lines):  # score the segment lines (no motion, no step)
        fp.crease(f"score-{i + 1}", ROLL, ((u, ring_width + 10.0), (u, -10.0)), "valley")
    for i, u in enumerate(lines):  # roll: each segment turns 360/N about its line, all at once
        fp.hinge("roll" if i == 0 else f"roll-{i + 1}", ROLL, ((u, -10.0), (u, ring_width + 10.0)),
                 360.0 / N, at=(u + s / 2.0, 1.0), ms=2500)
        JOINS.add(f"roll-{i + 1}") if i else None
    perf = {"ring_diameter_mm": round((LR - OVER) / math.pi, 1)}
    built = fp.build("strip")
else:
    fp = pliego.FoldProgram([(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)], stock=stock,
                            label=L4("Sheet", "Hoja", "Feuille", "Folha"), front=FRONT, back=BACK)
    fp.fold("fold-in-half", L4("Valley-fold the sheet in half lengthwise",
                               "Dobla la hoja por la mitad a lo largo, en valle",
                               "Pliez la feuille en deux dans la longueur, en vallée",
                               "Dobre a folha ao meio no comprimento, em vale"),
            ((c, -10.0), (c, H + 10.0)), "valley")
    fp.unfold_last("unfold", L4("Unfold: the centre line is marked",
                                "Desdobla: queda marcada la línea central",
                                "Dépliez : la ligne centrale est marquée",
                                "Desdobre: a linha central fica marcada"), ms=1000)
    top = H
    if design in ("dart", "glider", "delta"):
        joined("corners", L4("Fold the two top corners to the centre line",
                             "Dobla las dos esquinas de arriba hasta la línea central",
                             "Rabattez les deux coins du haut sur la ligne centrale",
                             "Dobre os dois cantos de cima até à linha central"),
               [(((0.0, H - c), (c, H)), "valley", {}), (((c, H), (W, H - c)), "valley", {})])
    if design == "dart":
        t = math.tan(math.radians(22.5))
        joined("edges", L4("Fold the new slanted edges to the centre line again",
                           "Vuelve a doblar los nuevos bordes inclinados hasta la línea central",
                           "Rabattez à nouveau les nouveaux bords obliques sur la ligne centrale",
                           "Dobre outra vez as novas arestas inclinadas até à linha central"),
               [(((c - 400.0 * t, H - 400.0), (c, H)), "valley", {}),
                (((c, H), (c + 400.0 * t, H - 400.0)), "valley", {})])
    if design == "glider":
        fp.fold("nose-down", L4("Fold the top triangle down: a blunt leading edge",
                                "Dobla hacia abajo el triángulo de arriba: un borde de ataque romo",
                                "Rabattez le triangle du haut : un bord d'attaque émoussé",
                                "Dobre para baixo o triângulo de cima: um bordo de ataque rombo"),
                ((-10.0, H - c), (W + 10.0, H - c)), "valley")
        top = H - c
    nb, depth = nose_folds, 10.0
    if design == "square":
        nb, depth = 2 + nose_folds, 0.05 * H
    elif design == "canard":
        nb, depth = 1 + nose_folds, 0.06 * H
    if nb:
        top = roll_band("nose-weight", L4(
            f"Roll the nose over {nb} time(s), {depth:.0f} mm each: weight forward",
            f"Enrolla la nariz {nb} vez/veces, {depth:.0f} mm cada vez: peso adelante",
            f"Roulez le nez {nb} fois, {depth:.0f} mm à chaque fois : du poids à l'avant",
            f"Enrole o nariz {nb} vez(es), {depth:.0f} mm de cada vez: peso à frente"),
            top, nb, depth, W)
    fp.fold("fold-half", L4("Valley-fold in half along the centre line, the flaps inside",
                            "Dobla en valle por la mitad sobre la línea central, con las solapas "
                            "por dentro",
                            "Pliez en deux en vallée sur la ligne centrale, les rabats à "
                            "l'intérieur",
                            "Dobre em vale ao meio pela linha central, com as abas por dentro"),
            ((c, -10.0), (c, H + 10.0)), "valley")
    y_slit, kc = 0.62 * top, k + 0.42 * (c - k)
    if design == "canard":
        fp.cut("slit", L4("Cut a slit through both layers between the foreplane and the main wing",
                          "Corta una ranura a través de las dos capas, entre el plano delantero y "
                          "el ala principal",
                          "Fendez les deux couches entre le plan canard et l'aile principale",
                          "Corte uma fenda nas duas camadas, entre o plano dianteiro e a asa "
                          "principal"),
               ((W + 10.0, y_slit), (c + k, y_slit)))
    st = fp.state
    x2 = max(q[0] for f in range(len(st.faces)) for q in st.image(f) if abs(q[1]) < 1e-6) \
        - 6.0 - (winglet_height if winglets != "none" else 0.0)
    x1, e = max(c + k + 4.0, x2 - 0.22 * (c - k)), 0.05 * H
    xm = (x1 + x2) / 2.0
    tabs = abs(trim) > 0.5 and x2 - x1 >= 10.0
    if tabs:
        SLITS = L4("Cut two short slits into each trailing edge: the elevator tabs",
                   "Corta dos ranuras cortas en cada borde de salida: las aletas del timón de "
                   "profundidad",
                   "Entaillez deux courtes fentes dans chaque bord de fuite : les volets de "
                   "profondeur",
                   "Corte duas fendas curtas em cada bordo de fuga: as abas do profundor")
        fp.cut("elevator-slits", SLITS, ((x1, -10.0), (x1, e)))
        fp.cut("elevator-slits-2", SLITS, ((x2, -10.0), (x2, e)))
        fp.crease("tab-hinges", SLITS, ((x2 + 5.0, e), (x1 - 5.0, e)), "valley",
                  sheet_points=[(xm, e / 2.0), mirror((xm, e / 2.0))])
        JOINS.add("elevator-slits-2")
    delta = design == "delta"
    wing = ((c, top), (c + k, 0.0)) if delta else ((c + k, H + 10.0), (c + k, -10.0))
    on_wing = (lambda t: (c + k * (1.0 - t / top), t)) if delta else (lambda t: (c + k, t))
    below = y_slit if design == "canard" else math.inf  # the wing ends at the slit
    joined("wings", L4("Fold each wing down along the wing line, the front layer then the back "
                       "one",
                       "Dobla cada ala hacia abajo por la línea del ala, primero la capa de "
                       "delante y luego la de atrás",
                       "Rabattez chaque aile le long de la ligne d'aile, la couche avant puis la "
                       "couche arrière",
                       "Dobre cada asa para baixo pela linha da asa, primeiro a camada da frente e "
                       "depois a de trás"),
           [(wing, "mountain", lambda: half(1, below)), (wing, "valley", lambda: half(-1, below))])
    fore = ((c + kc, H + 10.0), (c + kc, -10.0))
    cs = (W - 2.0, (y_slit + top) / 2.0)
    if design == "canard":
        joined("foreplane", L4("Fold each foreplane down along its own line, further from the keel",
                               "Dobla cada plano delantero hacia abajo por su propia línea, más "
                               "lejos de la quilla",
                               "Rabattez chaque plan canard le long de sa propre ligne, plus loin "
                               "de la quille",
                               "Dobre cada plano dianteiro para baixo pela sua própria linha, "
                               "mais longe da quilha"),
               [(fore, "mountain", lambda: half(1)), (fore, "valley", lambda: half(-1))])
    st = fp.state
    xw0 = min(q[0] for f in range(len(st.faces)) for q in st.image(f))  # the folded wing tips
    xw = xw0 + winglet_height
    winglet = ((xw, -10.0), (xw, H + 10.0))
    if winglets != "none":
        joined("winglets", L4(
            f"Fold the outer {winglet_height:.0f} mm of each wing over: the winglets",
            f"Dobla los {winglet_height:.0f} mm exteriores de cada ala: las aletas marginales",
            f"Repliez les {winglet_height:.0f} mm extérieurs de chaque aile : les winglets",
            f"Dobre os {winglet_height:.0f} mm exteriores de cada asa: os winglets"),
            [(winglet, "mountain", lambda: half(1)), (winglet, "valley", lambda: half(-1))])
    # ── open into the 3-D plane: hinge poses about the existing creases ──────
    st = fp.state
    OPEN = L4(f"Open the wings to {dihedral:.0f}° of dihedral and set the trim",
              f"Abre las alas a {dihedral:.0f}° de diedro y ajusta el compensador",
              f"Ouvrez les ailes à {dihedral:.0f}° de dièdre et réglez le compensateur",
              f"Abra as asas a {dihedral:.0f}° de diedro e ajuste o compensador")
    # the left half lifts about the keel: picked at a point of its keel strip near the nose, with
    # every left layer there (a flap whose crease lies along the keel goes with its own half)
    yk = 0.85 * top
    q = st.to_folded((c - (on_wing(yk)[0] - c) / 2.0, yk))
    stack = [p[0] < c for f, p in st.layers_at(q)  # the layers on the keel's lifting side
             if sum(v[0] for v in st.image(f)) / len(st.image(f)) > c]
    n = len(stack) - max((i + 1 for i, left in enumerate(stack) if not left), default=0)
    fp.hinge("open", OPEN, ((c, -10.0), (c, H + 10.0)), SPREAD, at=q, layers=n, ms=2000)
    out = 90.0 + SPREAD / 2.0 + dihedral  # 180° − the wing fold, 90° − spread/2 − dihedral
    yw = y_slit / 2.0 if design == "canard" else 0.2 * top
    low = st.to_folded(((on_wing(yw)[0] + W) / 2.0, yw))
    specs = [{"line": wing, "turn": -out, "at": low, "layers": 1, "from_": "bottom"},
             {"line": wing, "turn": out, "at": low, "layers": 1}]
    if design == "canard":
        hi = st.to_folded(((c + kc + W) / 2.0, cs[1]))
        specs += [{"line": fore, "turn": -out, "at": hi, "layers": 1, "from_": "bottom"},
                  {"line": fore, "turn": out, "at": hi, "layers": 1}]
    fp.hinges("open-wings", OPEN, specs)
    K, A, B = at3((c, 2.0)), at3(on_wing(2.0)), at3(mirror(on_wing(2.0)))
    kd = unit(tuple(a - b for a, b in zip(at3((c, top - 5.0)), K, strict=True)))
    up = tuple((A[i] + B[i]) / 2.0 - K[i] for i in range(3))
    up = unit(tuple(up[i] - sum(up[j] * kd[j] for j in range(3)) * kd[i] for i in range(3)))

    def side_turns(sid, line, turn, at, probe, ref, want):
        """Turn the flap at the folded point `at` (top layer: the left side; bottom layer: the
        right) about `line` so the sheet point `probe` ends `want` (±1) along `up`, seen from
        the sheet point `ref` beside it: by `turn`, or the other way round if that is wrong."""
        specs = []
        for sx, frm in ((1.0, "bottom"), (-1.0, "top")):
            pr, rf = (probe, ref) if sx > 0 else (mirror(probe), mirror(ref))
            fa = fp.state.face_at(pr)
            rb = fp.pose.extra(fp.state.face_at(rf))
            p0, d0 = line[0], (line[1][0] - line[0][0], line[1][1] - line[0][1])
            o, o2 = fm.apply(rb, fm.w3(p0)), fm.apply(rb, fm.w3((p0[0] + d0[0], p0[1] + d0[1])))
            sense = 1.0 if (d0[0] * (at[1] - p0[1]) - d0[1] * (at[0] - p0[0])) > 0 else -1.0
            for tv in (turn * (1.0 if sx > 0 else -1.0), turn * (-1.0 if sx > 0 else 1.0)):
                g = fm.rot_line(o, tuple(o2[i] - o[i] for i in range(3)),
                                sense * math.radians(tv))
                w = fm.apply(g, fm.apply(fp.pose.world[fa], fm.w3(pr)))
                r = at3(rf)
                if sum((w[i] - r[i]) * up[i] for i in range(3)) * want > 0:
                    break
            specs.append({"line": line, "turn": tv, "at": at, "layers": 1, "from_": frm})
        fp.hinges(sid, OPEN, specs)
        JOINS.add(sid)

    if winglets != "none":
        wl = st.to_folded((W - winglet_height / 2.0, 3.0))
        side_turns("open-winglets", winglet, 90.0, wl, (W - 1.0, 3.0),
                   (W - winglet_height - 4.0, 3.0), 1.0 if winglets == "up" else -1.0)
    if tabs:
        side_turns("open-trim", ((x1 - 5.0, e), (x2 + 5.0, e)), abs(trim),
                   st.to_folded((xm, e / 2.0)), (xm, 0.5), (xm, e + 4.0), math.copysign(1.0, trim))
    JOINS.add("open-wings")
    wld, faces = fp.pose.world, range(len(fp.state.faces))
    lat = (up[1] * kd[2] - up[2] * kd[1], up[2] * kd[0] - up[0] * kd[2],
           up[0] * kd[1] - up[1] * kd[0])
    tot, cg = 0.0, (0.0, 0.0, 0.0)  # span and CG: uniform paper, all layers
    for f in faces:  # each face's area centroid, carried into the world by its pose
        poly = fp.state.poly(f)
        cr = [poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly))]
        a = 0.5 * sum(cr)
        g = fm.apply(wld[f], fm.w3(tuple(sum((poly[i - 1][j] + poly[i][j]) * cr[i]
                                              for i in range(len(poly))) / (6.0 * a)
                                          for j in (0, 1))))
        tot, cg = tot + abs(a), tuple(cg[i] + abs(a) * g[i] for i in range(3))
    allp = [fm.apply(wld[f], fm.w3(p)) for f in faces for p in fp.state.poly(f)]

    def dot(u, v):
        return sum(u[i] * v[i] for i in range(3))
    s_hi, s_lo = max(dot(x, kd) for x in allp), min(dot(x, kd) for x in allp)
    cgs = s_hi - dot(cg, kd) / tot
    perf = {"span_mm": round(max(dot(x, lat) for x in allp) - min(dot(x, lat) for x in allp), 1),
            "length_mm": round(s_hi - s_lo, 1), "cg_from_nose_mm": round(cgs, 1),
            "cg_from_nose_pct": round(100.0 * cgs / (s_hi - s_lo), 1)}
    built = fp.build("sheet")
    present(built, wld, kd, up)

seq, worst, mid = diagram(built, fp.recs, JOINS)
print(built.summary())
print(f"kinematics: design={design} steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e} " + " ".join(f"{a}={v}" for a, v in perf.items()))
cuts = any(r.move is not None and r.move.kind == "cut" for r in fp.recs)
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={} if cuts else {"folded": built.target(pose=True)},  # a slit's two
    title="Paper airplane")                                    # sides share their end vertices
