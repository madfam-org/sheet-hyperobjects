"""Jumping frog — sheet-hyperobjects cartridge (Pliego): the traditional index-card frog.
The X and the line through its centre are creased; the head collapses as one degree-6 vertex (a
waterbomb half-base, `pliego.flatvertex.collapse`); the front legs, the sides, the bottom and the
Z pleat are simple folds. Every fold is a `pliego.FoldProgram` operation on a layer-ordered flat
state, checked for layer order, Kawasaki and Maekawa; then the pleat opens and is pressed as 3-D
hinge poses about its two creases (`FoldProgram.hinge`). The jump itself waits for the physics
engine.
"""

import math

import pliego
import pliego.flatvertex  # noqa: F401 - the head's vertex collapse


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
card = P(lambda: card, "index-3x5")  # noqa: F821
stock = P(lambda: stock, "cardstock-160")  # noqa: F821
spring = C(float(P(lambda: spring, 35.0)), 0.0, 80.0)  # noqa: F821
CARDS = {"index-3x5": (76.2, 127.0), "index-4x6": (101.6, 152.4), "business": (50.8, 88.9)}
if card not in CARDS:
    raise ValueError(f"unknown card {card!r}")
W, H = CARDS[card]
O = (W / 2.0, H - W / 2.0)  # centre of the X
yb = H - W  # base of the head triangle
fp = pliego.FoldProgram([(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)], stock=stock,
                        label=L4("Index card", "Ficha", "Fiche bristol", "Ficha"),
                        front="#7fb069", back="#f4efe6")
UNFOLD = L4("Unfold", "Desdobla", "Dépliez", "Desdobre")

# ── 1. the X and the horizontal crease ─────────────────────────────────────
fp.fold("corner-right", L4("Fold the top right corner to the left edge",
                           "Dobla la esquina superior derecha hasta el borde izquierdo",
                           "Rabattez le coin supérieur droit sur le bord gauche",
                           "Dobre o canto superior direito até à aresta esquerda"),
        ((0.0, H), (W, yb)), "valley")
fp.unfold_last("unfold-right", UNFOLD)
fp.fold("corner-left", L4("Fold the top left corner to the right edge",
                          "Dobla la esquina superior izquierda hasta el borde derecho",
                          "Rabattez le coin supérieur gauche sur le bord droit",
                          "Dobre o canto superior esquerdo até à aresta direita"),
        ((0.0, yb), (W, H)), "valley", at=(1.0, H - 6.0))
fp.unfold_last("unfold-left", L4("Unfold: the creases make an X",
                                 "Desdobla: los pliegues forman una X",
                                 "Dépliez : les plis forment un X",
                                 "Desdobre: os vincos formam um X"))
fp.fold("fold-back", L4(
    "Mountain-fold the top behind along the line through the centre of the X",
    "Dobla en monte la parte de arriba hacia atrás por la línea que pasa por el centro de la X",
    "Pliez le haut en montagne vers l'arrière, sur la ligne qui passe par le centre du X",
    "Dobre em montanha a parte de cima para trás pela linha que passa pelo centro do X"),
    ((-10.0, O[1]), (W + 10.0, O[1])), "mountain")
fp.unfold_last("unfold-back", UNFOLD)

# ── 2. collapse the head: a waterbomb half-base, one rigid degree-6 vertex ────
N = 6
head = pliego.flatvertex.collapse(fp.state, O, {0: "mountain", 180: "mountain", 45: "valley",
                                                135: "valley", 225: "valley", 315: "valley"})
head.samples[:] = [k / (4 * N) for k in range(1, 4 * N + 1)]  # shown as six key states
HEAD = L4("Push the sides in and bring the top down: the head",
          "Empuja los lados hacia dentro y baja la parte de arriba: la cabeza",
          "Poussez les côtés vers l'intérieur et rabattez le haut : la tête",
          "Empurre os lados para dentro e baixe a parte de cima: a cabeça")
fp.add("collapse", HEAD, head, ms=450 * N)

# ── 3. front legs, body, spring ────────────────────────────────────────────
LEGS = L4("Fold the two bottom corners of the triangle up to its top point: front legs",
          "Dobla hacia arriba las dos puntas inferiores del triángulo hasta su vértice: las patas "
          "delanteras",
          "Rabattez les deux pointes inférieures du triangle jusqu'à son sommet : les pattes avant",
          "Dobre para cima as duas pontas de baixo do triângulo até ao vértice: as patas da frente")
m = (W / 4.0, yb + W / 4.0)
fp.fold("front-legs", LEGS, ((m[0] + 40.0, m[1] - 40.0), (m[0] - 40.0, m[1] + 40.0)), "valley",
        sheet_points=[(6.0, H - 2.0)])
m = (3.0 * W / 4.0, yb + W / 4.0)
fp.fold("front-legs-2", LEGS, ((m[0] + 40.0, m[1] + 40.0), (m[0] - 40.0, m[1] - 40.0)),
        "valley", sheet_points=[(W - 6.0, H - 2.0)])
SIDES = L4("Fold the long sides in to meet at the centre line",
           "Dobla los lados largos hacia dentro hasta que se junten en la línea central",
           "Rabattez les grands côtés vers l'intérieur jusqu'à la ligne centrale",
           "Dobre os lados compridos para dentro até se encontrarem na linha central")
fp.fold("sides", SIDES, ((W / 4.0, -10.0), (W / 4.0, H + 10.0)), "valley",
        sheet_points=[(2.0, 2.0)])
fp.fold("sides-2", SIDES, ((3.0 * W / 4.0, H + 10.0), (3.0 * W / 4.0, -10.0)), "valley",
        sheet_points=[(W - 2.0, 2.0)])
fp.fold("bottom-up", L4("Fold the bottom up to the base of the head",
                        "Dobla la parte de abajo hacia arriba hasta la base de la cabeza",
                        "Remontez le bas jusqu'à la base de la tête",
                        "Dobre a parte de baixo até à base da cabeça"),
        ((W + 10.0, yb / 2.0), (-10.0, yb / 2.0)), "valley", sheet_points=[(W / 2.0, 1.0)])
fp.fold("pleat", L4("Fold that flap back down in half: the spring pleat",
                    "Dobla esa solapa de nuevo hacia abajo, por la mitad: el pliegue resorte",
                    "Rabattez ce rabat vers le bas, en deux : le pli ressort",
                    "Dobre essa aba outra vez para baixo, ao meio: a prega mola"),
        ((-10.0, 3.0 * yb / 4.0), (W + 10.0, 3.0 * yb / 4.0)), "valley",
        sheet_points=[(W / 2.0, 1.0)])

# open the pleat so the frog sits on its spring; then press it, the way a finger loads the jump:
# 3-D hinge poses, the bottom flap about the lower crease and the pleat's flap about its crease
LOW = ((W / 4.0, yb / 2.0), (3.0 * W / 4.0, yb / 2.0))              # the bottom-up crease
TOP = ((W / 4.0, 3.0 * yb / 4.0), (3.0 * W / 4.0, 3.0 * yb / 4.0))  # the pleat's crease
ON = (5.0 * W / 8.0, 0.6 * yb)  # a point on the pleat's flap, the top layer
fp.hinge("spring", L4("Turn the frog over and let the pleat open: it rests on its spring",
                      "Da la vuelta a la rana y deja que el pliegue se abra: descansa sobre su "
                      "resorte",
                      "Retournez la grenouille et laissez le pli s'ouvrir : elle repose sur son "
                      "ressort",
                      "Vire a rã e deixe a prega abrir: ela assenta sobre a sua mola"),
         LOW, spring, at=ON, layers=1, ms=1500)
fp.hinge("spring-2", "", TOP, spring, at=ON, layers=1)
fp.hinge("press", L4("Press the back end down: the pleat flattens and stores the jump",
                     "Presiona la parte de atrás: el pliegue se aplana y guarda el salto",
                     "Appuyez sur l'arrière : le pli s'aplatit et emmagasine le saut",
                     "Pressione a parte de trás: a prega achata-se e guarda o salto"),
         LOW, 5.0 - spring, at=ON, layers=1)
fp.hinge("press-2", "", TOP, 5.0 - spring, at=ON, layers=1)

built = fp.build("card")
fm, wld, st = pliego.flatmotion, fp.pose.world, fp.state


def at3(p):
    """World position of a sheet point at the end of the program."""
    return fm.apply(wld[st.face_at(p)], fm.w3(p))


tail, nose = at3((W / 2.0, yb / 2.0 + 2.0)), at3((W / 2.0, yb - 2.0))
fwd = tuple(nose[k] - tail[k] for k in range(3))
fwd = tuple(x / math.sqrt(sum(y * y for y in fwd)) for x in fwd)
r = wld[st.face_at((W / 2.0, yb - 5.0))][0]
present(built, wld, fwd, (-r[0][1], -r[1][1], -r[2][1]))
seq, worst, mid = diagram(built, fp.recs, {"front-legs-2", "sides-2", "spring-2", "press-2"},
                          split={"collapse": (parts_of("collapse", HEAD, N), None)})
print(built.summary())
print(f"kinematics: card={card} steps={len(seq.steps)} max_closure_mm={worst:.3e} "
      f"max_linear_midpoint_closure_mm={mid:.3e}")
result = pliego.Assembly(
    [built.sheet],
    controls=[pliego.sequence_control(label=L4(
        "Fold program", "Secuencia de pliegues", "Séquence de pliage", "Sequência de dobras"))],
    sequence=seq, targets={"folded": built.target(pose=True)}, title="Jumping frog")
