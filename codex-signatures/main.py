"""Codex signatures — sheet-hyperobjects cartridge (Pliego).

The platform's namesake: a printed press sheet (*pliego*) folded into a signature.

* `imposition`: `folio` (one fold, 4 pages), `quarto` (two folds, 8 pages) or `octavo` (three
  folds, 16 pages). Each fold halves the folded sheet across its longer side, through every
  layer; the last fold is the spine.
* mode `signature` — one press sheet and the fold program that folds it into the signature.
* mode `gathered` — `signatures` folded signatures gathered into a book block, shown as the
  initial frame, sewn with thread through their centre folds (`string` joins: sewing stations
  along each centre fold and kettle stitches linking each signature to the next at head and tail).
  The program opens the book at the centre of the first signature.

The crease pattern is not drawn: it is computed by folding the sheet with the kernel's
simple-fold model (`pliego.simplefold`), which also gives the stack of layers. The imposition is
computed from that stack — page 1 on the outer face whose spine lies on the binding side, pages
numbered down the stack — and checked against the classical rules: the side with page 1 (the
outer forme) carries pages 1, 4, 5, 8, …; the two pages either side of a spine fold add up to the
page count plus one; and, posed in 3-D by `pliego.kinematics`, every page's head points the same
way. The page numbers are written into the step notes; the studio draws no text on faces.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = PARAM(lambda: mode, "signature")                     # noqa: F821
imposition = PARAM(lambda: imposition, "octavo")            # noqa: F821
sheet_width = float(PARAM(lambda: sheet_width, 594.0))      # noqa: F821
sheet_height = float(PARAM(lambda: sheet_height, 420.0))    # noqa: F821
stock = PARAM(lambda: stock, "copy-80")                     # noqa: F821
binding = PARAM(lambda: binding, "left")                    # noqa: F821
signatures = round(float(PARAM(lambda: signatures, 3)))    # noqa: F821

FOLDS = {"folio": 1, "quarto": 2, "octavo": 3}
if mode not in ("signature", "gathered"):
    raise ValueError(f"codex-signatures: unknown mode {mode!r}")
if imposition not in FOLDS:
    raise ValueError(f"codex-signatures: imposition must be one of {sorted(FOLDS)}")
if stock not in ("copy-80", "washi-kozo-30", "kraft-120"):
    raise ValueError(f"codex-signatures: unsupported stock {stock!r}")
if binding not in ("left", "right"):
    raise ValueError(f"codex-signatures: binding must be left or right, got {binding!r}")
if not 2 <= signatures <= 6:
    raise ValueError(f"codex-signatures: signatures must be in [2, 6], got {signatures}")

W = pliego.clamp(sheet_width, 200.0, 1000.0)
H = pliego.clamp(sheet_height, 140.0, 1000.0)
NF = FOLDS[imposition]
NP = 2 ** (NF + 1)                 # pages per signature
OPEN = 2.0                         # a gathered signature's spine springs this many degrees open
CALIPER = float(pliego.resolve_stock(stock, None)["caliper_mm"])   # from the stock card


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── fold the press sheet (simple folds through every layer) ──────────────────

OUTLINE = [(0.0, 0.0), (W, 0.0), (W, H), (0.0, H)]


def fold_sheet(flips):
    """Fold in half across the longer side NF times (left over right, top down); flips[k] folds
    the other half over instead."""
    fs = pliego.simplefold.FoldedState.of(OUTLINE)
    owner = []                       # fold index of each crease segment
    for k in range(NF):
        pts = [p for lay in fs.layers for p in lay.image()]
        lx, hx = min(p.x for p in pts), max(p.x for p in pts)
        ly, hy = min(p.y for p in pts), max(p.y for p in pts)
        if hx - lx >= hy - ly - 1e-9:
            c = (lx + hx) / 2.0
            line = ((c, ly - 1.0), (c, hy + 1.0))      # left half over the right
        else:
            c = (ly + hy) / 2.0
            line = ((hx + 1.0, c), (lx - 1.0, c))      # top half down
        if flips[k]:
            line = (line[1], line[0])
        before = len(fs.creases)
        fs.fold(line, "valley")
        owner += [k] * (len(fs.creases) - before)
    return fs, owner


def centroid(poly):
    return (math.fsum(p.x for p in poly) / len(poly), math.fsum(p.y for p in poly) / len(poly))


def impose(fs):
    """Page numbers per layer from the folded stack: [(layer, first-face-up?, page a, page b)]."""
    layers = fs.layers                                     # bottom → top
    spine = fs.frames[-1].line
    d = spine.direction()
    pts = [p for lay in layers for p in lay.image()]
    cx = math.fsum(p.x for p in pts) / len(pts)
    cy = math.fsum(p.y for p in pts) / len(pts)
    if NF == 1:                    # the folio's head runs up the sheet
        head = (0.0, 1.0) if abs(d.y) > 0.5 else (1.0, 0.0)
    else:
        prev = fs.frames[-2].line
        s = (prev.p0.x - cx) * d.x + (prev.p0.y - cy) * d.y
        head = (d.x, d.y) if s > 0 else (-d.x, -d.y)
    # spine side seen from above (normal +z): right = head × n = (hy, −hx)
    sx = spine.p0.x + d.x * ((cx - spine.p0.x) * d.x + (cy - spine.p0.y) * d.y)
    sy = spine.p0.y + d.y * ((cx - spine.p0.x) * d.x + (cy - spine.p0.y) * d.y)
    right_top = (head[1], -head[0])
    side_top = "left" if (sx - cx) * right_top[0] + (sy - cy) * right_top[1] < 0 else "right"
    from_top = side_top == binding        # the top face is the front cover
    order = list(reversed(layers)) if from_top else list(layers)
    out = []
    for k, lay in enumerate(order):
        # the face met first when reading: the upward face (from the top) or the downward one
        front_first = (not lay.flipped) if from_top else lay.flipped
        out.append((lay, front_first, 2 * k + 1, 2 * k + 2))
    return out, head


fs, owner = fold_sheet([False] * NF)
pages, head = impose(fs)

# ── the press sheet with its folds ───────────────────────────────────────────

SHEET_LABEL = L4("Press sheet", "Pliego", "Feuille d'impression", "Folha de impressão")
FOLD_NAMES = ["fold-1", "fold-2", "fold-3"]


def make_sheet(sid, label):
    s = pliego.Sheet(sid, OUTLINE, stock=stock, grain_deg=90.0 if NF % 2 else 0.0, label=label)
    marks = []
    for (a, b, asg), k in zip(fs.creases, owner):
        name = "spine" if k == NF - 1 else FOLD_NAMES[k]
        marks.append((s.crease(a, b, "valley" if asg == "V" else "mountain", 180.0, name=name),
                      k))
    return s, marks


press, press_marks = make_sheet("press-sheet", SHEET_LABEL)
arr = press.build()

# Which face of the arrangement each layer is, and the page on each side of every face.
face_pages = {}                    # face → (front page, back page, head in sheet frame)
for lay, front_first, pa, pb in pages:
    c = pliego.Vec2(*centroid(lay.poly))
    fi = next(i for i, f in enumerate(arr.faces)
              if pliego.geometry.point_in_polygon(c, [arr.vertices[v] for v in f]) > 0)
    a, b, cc, dd = lay.xf[0], lay.xf[1], lay.xf[2], lay.xf[3]
    det = a * dd - b * cc          # inverse linear part maps the folded head into the sheet
    hx = (dd * head[0] - b * head[1]) / det
    hy = (-cc * head[0] + a * head[1]) / det
    face_pages[fi] = (pa, pb, (hx, hy)) if front_first else (pb, pa, (hx, hy))
if len(face_pages) != len(arr.faces) or len(arr.faces) != NP // 2:
    raise ValueError("codex-signatures: the folds did not divide the sheet into its leaves")

# ── classical checks ─────────────────────────────────────────────────────────

front = sorted(p for p, _, _ in face_pages.values())
back = sorted(p for _, p, _ in face_pages.values())
outer = sorted(p for p in range(1, NP + 1) if p % 4 in (0, 1))
inner = sorted(p for p in range(1, NP + 1) if p % 4 in (2, 3))
if not ((front == outer and back == inner) or (front == inner and back == outer)):
    raise ValueError(f"codex-signatures: formes {front}/{back} are not the outer/inner formes")
outer_side = "front" if front == outer else "back"
spine_edges = {e for m, k in press_marks if k == NF - 1 for e in m.edges()}
adj = pliego.kinematics.face_adjacency(arr)
for f, nbrs in adj.items():
    for g, e, _, _ in nbrs:
        if e in spine_edges:
            for side in (0, 1):
                if face_pages[f][side] + face_pages[g][side] != NP + 1:
                    raise ValueError("codex-signatures: pages across the spine do not add up "
                                     f"to {NP + 1}")
final = {}
for m, _ in press_marks:
    for e in m.edges():
        final[e] = m.fold_angle
tr = pliego.kinematics.face_transforms(arr, final, 0)
heads = []
for fi, (_, _, (hx, hy)) in face_pages.items():
    rm = tr[fi][0]
    v = (hx, 0.0, -hy)
    heads.append(tuple(rm[i][0] * v[0] + rm[i][1] * v[1] + rm[i][2] * v[2] for i in range(3)))
if any(sum(h[i] * heads[0][i] for i in range(3)) < 1.0 - 1e-6 for h in heads):
    raise ValueError("codex-signatures: the folded pages' heads do not all point the same way")

# ── the imposition, as text ──────────────────────────────────────────────────


def arrow(hx, hy):
    if abs(hy) >= abs(hx):
        return "" if hy > 0 else "↓"
    return "→" if hx > 0 else "←"


def forme_text(side, base=0):
    """Rows of the sheet top → bottom; the back is read turned over left to right."""
    cells = []
    for fi, (pf, pbk, (hx, hy)) in face_pages.items():
        cx, cy = centroid([arr.vertices[v] for v in arr.faces[fi]])
        if side == "front":
            cells.append((-round(cy, 3), round(cx, 3), f"{pf + base}{arrow(hx, hy)}"))
        else:
            cells.append((-round(cy, 3), -round(cx, 3), f"{pbk + base}{arrow(-hx, hy)}"))
    rows, cur, key = [], [], None
    for ky, _, txt in sorted(cells):
        if key is not None and ky != key:
            rows.append(" ".join(cur))
            cur = []
        key = ky
        cur.append(txt)
    rows.append(" ".join(cur))
    return " / ".join(rows)


outer_txt = forme_text(outer_side)
inner_txt = forme_text("back" if outer_side == "front" else "front")
FOLD_TEXT = [
    L4("First fold: in half across the long side", "Primer doblez: a la mitad, a lo ancho del "
       "lado largo", "Premier pli : en deux, en travers du grand côté",
       "Primeira dobra: ao meio, atravessando o lado maior"),
    L4("Second fold: in half again, at right angles", "Segundo doblez: otra vez a la mitad, en "
       "ángulo recto", "Deuxième pli : de nouveau en deux, à angle droit",
       "Segunda dobra: de novo ao meio, em ângulo reto"),
    L4("Third fold: in half again, at right angles", "Tercer doblez: otra vez a la mitad, en "
       "ángulo recto", "Troisième pli : de nouveau en deux, à angle droit",
       "Terceira dobra: de novo ao meio, em ângulo reto"),
]
SPINE_NOTE = L4("This fold is the spine. Pages now read 1 to {n} in order once the bolts are cut.",
                "Este doblez es el lomo. Las páginas se leen del 1 al {n} en orden en cuanto se "
                "cortan los pliegues de cabeza y de corte.",
                "Ce pli est le dos. Les pages se lisent de 1 à {n} dans l'ordre une fois les "
                "plis rognés.",
                "Esta dobra é a lombada. As páginas leem-se de 1 a {n} em ordem assim que se "
                "cortam as dobras de cabeça e de frente.")
FORME_NOTE = L4("Outer forme (side with page 1), top row first: {o}. Inner forme, sheet turned "
                "over: {i}. ↓ marks a page printed head down, ← → a head to the side.",
                "Forma exterior (la cara con la página 1), de la fila de arriba hacia abajo: {o}. "
                "Forma interior, con el pliego volteado: {i}. ↓ marca una página impresa de "
                "cabeza; ← → una cabeza de lado.",
                "Forme extérieure (côté de la page 1), rangée du haut d'abord : {o}. Forme "
                "intérieure, feuille retournée : {i}. ↓ marque une page imprimée tête en bas, "
                "← → une tête sur le côté.",
                "Forma exterior (o lado com a página 1), da fila de cima para baixo: {o}. Forma "
                "interior, com a folha virada: {i}. ↓ marca uma página impressa de cabeça para "
                "baixo; ← → uma cabeça de lado.")


def fill(tmpl, **kw):
    return {k: v.format(**kw) for k, v in tmpl.items()}


print(f"signature: {imposition} pages={NP} sheet={W:g}x{H:g}mm binding={binding} "
      f"outer=[{outer_txt}] inner=[{inner_txt}]")

ctl_label = L4("Fold the signature", "Doblar el cuadernillo", "Plier le cahier",
               "Dobrar o caderno")
if mode == "signature":
    steps = []
    state = {}
    for k in range(NF):
        moving = [(m, None) for m, kk in press_marks if kk == k]
        note = fill(FORME_NOTE, o=outer_txt, i=inner_txt) if k == 0 else None
        if k == NF - 1:
            note = fill(SPINE_NOTE, n=NP) if k else {
                lang: FORME_NOTE[lang].format(o=outer_txt, i=inner_txt) + " "
                + SPINE_NOTE[lang].format(n=NP) for lang in SPINE_NOTE}
        steps.append(pliego.Step(f"fold-{k + 1}", FOLD_TEXT[k], moving, duration_ms=2500,
                                 note=note))
        # each fold rotates its half-stack rigidly: linear in the angles; check the closure
        for t in (0.5, 1.0):
            for m, kk in press_marks:
                if kk == k:
                    for e in m.edges():
                        state[e] = t * m.fold_angle
            res = pliego.kinematics.closure_residual(arr, state)
            if res > 1e-6:
                raise ValueError(f"codex-signatures: fold {k + 1} does not close ({res:.3g} mm)")
    result = pliego.Assembly([press], controls=[pliego.sequence_control(label=ctl_label)],
                             sequence=pliego.Sequence(steps, mode="kinematic"),
                             title="Codex signature")
else:
    # Gathered: identical folded signatures stacked on their side, spine on the binding side.
    # The studio poses each sheet from its lowest-index face (the sheet's lower-left leaf), so the
    # book lies with that leaf's half of every signature underneath: page 1 up when that leaf is
    # in the second half of the signature, face down otherwise; the program opens the top one.
    root_face = next(fi for fi, (pf, pbk, _) in face_pages.items() if 1 in (pf, pbk))
    face_up = min(face_pages[0][0], face_pages[0][1]) > NP // 2
    pose = {e: a for e, a in final.items()}
    for e in spine_edges:
        pose[e] = math.copysign(180.0 - OPEN, final[e])
    p1_front = face_pages[root_face][0] == 1
    n1 = (0.0, 1.0, 0.0) if p1_front else (0.0, -1.0, 0.0)
    hx, hy = face_pages[root_face][2]
    hw = (hx, 0.0, -hy)
    s3 = (hw[1] * n1[2] - hw[2] * n1[1], hw[2] * n1[0] - hw[0] * n1[2],
          hw[0] * n1[1] - hw[1] * n1[0])
    # rotation taking page 1's normal to ±Y (up, or down for a face-down book), its head to −Z
    up = 1.0 if face_up else -1.0
    src = (n1, hw, s3)
    dst = ((0.0, up, 0.0), (0.0, 0.0, -1.0), (up, 0.0, 0.0))
    R = [[math.fsum(dst[k][i] * src[k][j] for k in range(3)) for j in range(3)]
         for i in range(3)]
    tr_ = R[0][0] + R[1][1] + R[2][2]
    if tr_ > 0:
        sq = math.sqrt(tr_ + 1.0) * 2.0
        quat = ((R[2][1] - R[1][2]) / sq, (R[0][2] - R[2][0]) / sq, (R[1][0] - R[0][1]) / sq,
                0.25 * sq)
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        sq = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2.0
        quat = (0.25 * sq, (R[0][1] + R[1][0]) / sq, (R[0][2] + R[2][0]) / sq,
                (R[2][1] - R[1][2]) / sq)
    elif R[1][1] > R[2][2]:
        sq = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2.0
        quat = ((R[0][1] + R[1][0]) / sq, 0.25 * sq, (R[1][2] + R[2][1]) / sq,
                (R[0][2] - R[2][0]) / sq)
    else:
        sq = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2.0
        quat = ((R[0][2] + R[2][0]) / sq, (R[1][2] + R[2][1]) / sq, 0.25 * sq,
                (R[1][0] - R[0][1]) / sq)
    pitch = (NP // 2) * CALIPER + 0.5          # one signature's thickness, plus air
    # The centre fold: the spine segment between the middle pages NP/2 and NP/2 + 1.
    mid = None
    for f, nbrs in adj.items():
        for g, e, va, vb in nbrs:
            if e in spine_edges and any({face_pages[f][sd], face_pages[g][sd]}
                                        == {NP // 2, NP // 2 + 1} for sd in (0, 1)):
                mid = (arr.vertices[va], arr.vertices[vb])
    if mid is None:
        raise ValueError("codex-signatures: the centre fold was not found")
    a0, b0 = mid
    if (b0 - a0).length() < 60.0:
        raise ValueError("codex-signatures: the spine is too short to sew")
    n_st = 2 + max(2, min(4, int((b0 - a0).length() // 60.0)))
    kettle = 10.0 / (b0 - a0).length()
    stations = [a0.lerp(b0, kettle + (1.0 - 2.0 * kettle) * j / (n_st - 1)) for j in range(n_st)]
    sheets, joins, initial = [], [], {}
    for k in range(signatures):
        s, marks = make_sheet(f"signature-{k + 1}", L4(
            f"Signature {k + 1}", f"Cuadernillo {k + 1}", f"Cahier {k + 1}", f"Caderno {k + 1}"))
        level = (signatures - 1 - k) if face_up else k
        s.placement = pliego.Placement(origin=(0.0, level * pitch, 0.0),
                                       rotation=quat)
        initial[s.id] = {"angles": dict(pose), "root": centroid(
            [arr.vertices[v] for v in arr.faces[root_face]])}
        for j in range(n_st - 1):
            joins.append(pliego.string(f"thread-{k + 1}-{j + 1}", (s, stations[j]),
                                       (s, stations[j + 1]),
                                       stations[j].distance(stations[j + 1])))
        if k:
            for j, end in ((0, "head"), (n_st - 1, "tail")):
                joins.append(pliego.string(f"kettle-{end}-{k}", (sheets[-1][0], stations[j]),
                                           (s, stations[j]), pitch))
        sheets.append((s, marks))
    top = 1 if face_up else signatures            # the signature on top of the pile
    s1, m1 = sheets[top - 1]
    c1, c2 = NP * (top - 1) + NP // 2, NP * (top - 1) + NP // 2 + 1
    open_t = [(m, 0.0) for m, kk in m1 if kk == NF - 1]
    shut_t = [(m, math.copysign(180.0 - OPEN, m.fold_angle)) for m, kk in m1 if kk == NF - 1]
    steps = [
        pliego.Step("open", L4(f"Open the book at the centre of signature {top} (pages {c1} "
                               f"and {c2})",
                               f"Abre el libro al centro del cuadernillo {top} (páginas {c1} "
                               f"y {c2})",
                               f"Ouvrez le livre au milieu du cahier {top} (pages {c1} et "
                               f"{c2})",
                               f"Abra o livro no centro do caderno {top} (páginas {c1} e "
                               f"{c2})"), open_t, duration_ms=2500,
                    note=L4(f"Signature k carries pages {NP}·(k − 1) + 1 to {NP}·k. The thread "
                            "runs inside each centre fold and kettle stitches tie the "
                            "signatures at head and tail.",
                            f"El cuadernillo k lleva las páginas {NP}·(k − 1) + 1 a {NP}·k. "
                            "El hilo corre por dentro de cada doblez central y las puntadas de "
                            "cadeneta unen los cuadernillos en cabeza y pie.",
                            f"Le cahier k porte les pages {NP}·(k − 1) + 1 à {NP}·k. Le fil "
                            "court à l'intérieur de chaque pli central et les points de chaînette "
                            "lient les cahiers en tête et en queue.",
                            f"O caderno k leva as páginas {NP}·(k − 1) + 1 a {NP}·k. A linha "
                            "corre por dentro de cada dobra central e os pontos de cadeneta "
                            "unem os cadernos na cabeça e no pé.")),
        pliego.Step("close", L4("Close the book", "Cierra el libro", "Fermez le livre",
                                "Feche o livro"), shut_t, duration_ms=2500),
    ]
    result = pliego.Assembly([s for s, _ in sheets], joins=joins,
                             controls=[pliego.sequence_control(label=L4(
                                 "Open the book", "Abrir el libro", "Ouvrir le livre",
                                 "Abrir o livro"))],
                             sequence=pliego.Sequence(steps, mode="kinematic"),
                             initial=initial, title="Gathered signatures")
    print(f"gathered: signatures={signatures} face_up={face_up} pitch={pitch:g}mm stations={n_st} "
          f"threads={len(joins)}")
