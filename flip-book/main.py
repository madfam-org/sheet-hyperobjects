"""Flip book — sheet-hyperobjects cartridge (Pliego).

A thumbed stack of pages: the kineograph. Every page is its own sheet, a binding margin and a
picture area separated by a scored hinge line; the margins are stacked one caliper apart and
padded (glued) along the spine into a block (`pliego:stacks`, binding `padding`). One sequence
control thumbs the whole book in a staggered cascade:

* `thumbing = riffle` (default): the thumb bends all the pages back, then lets them spring free
  one at a time; the bottom page lands first and the pile builds up, so frame 1 is drawn on the
  last page and the cover carries the last frame;
* `thumbing = flick`: the thumb lifts the free edge and the pages flick over the spine one at a
  time from the cover, so frame 1 is drawn on the cover.

Why this design: the studio preview drives sequences across sheets but cannot drive a `leaf`
mechanism from a shared clock with a stagger, nor bend paper. A scored hinge inside each page
sheet (binding margin = the sheet's root face) is a rigid hinge the preview turns exactly, and
the program's per-page angles are piecewise linear in time, which is exactly how the preview
blends steps. The padding and the paper's spring are the physics engine's.

The studio draws no art, so the pictures are not on the sheets (no fake score lines on the
fabrication layers). `frames = bouncing-ball` computes a frame plan instead: for every frame,
the page that carries it and the ball's centre measured from the hinge line and the tail edge;
it is written into the step notes and checked to lie inside the picture area.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


pages = PARAM(lambda: pages, 24)                                # noqa: F821
page_width = float(PARAM(lambda: page_width, 127.0))            # noqa: F821
page_height = float(PARAM(lambda: page_height, 76.2))           # noqa: F821
binding_margin = float(PARAM(lambda: binding_margin, 10.0))     # noqa: F821
stock = PARAM(lambda: stock, "cardstock-160")                   # noqa: F821
thumbing = PARAM(lambda: thumbing, "riffle")                    # noqa: F821
frames = PARAM(lambda: frames, "bouncing-ball")                 # noqa: F821
riffle_speed = float(PARAM(lambda: riffle_speed, 12.0))         # noqa: F821

# Caliper (mm) of each offered stock, from its stock card; the stack pitch must equal it
# (spec rule 12 fails loud on a mismatch).
CALIPER = {"copy-80": 0.1, "cardstock-160": 0.2, "cardstock-250": 0.3}
if stock not in CALIPER:
    raise ValueError(f"flip-book: stock must be one of {sorted(CALIPER)}, got {stock!r}")
if thumbing not in ("riffle", "flick"):
    raise ValueError(f"flip-book: thumbing must be riffle or flick, got {thumbing!r}")
if frames not in ("bouncing-ball", "blank"):
    raise ValueError(f"flip-book: frames must be bouncing-ball or blank, got {frames!r}")

N = round(pliego.clamp(float(pages), 12.0, 48.0))
W = pliego.clamp(page_width, 50.0, 150.0)       # spine → fore-edge
H = pliego.clamp(page_height, 40.0, 110.0)      # along the spine
# The padded margin (the hinge score sits at u = M), at most a third of the page so the picture
# area keeps at least twice the margin and 30 mm (W ≥ 50 mm).
M = min(pliego.clamp(binding_margin, 6.0, 20.0), math.floor(W / 3.0 * 10.0) / 10.0)
PPS = pliego.clamp(riffle_speed, 6.0, 24.0)     # pages released per second
if W - M < 2.0 * M or W - M < 30.0:
    raise ValueError("flip-book: the picture area must be at least 30 mm and twice the margin")
PITCH = CALIPER[stock]
FLIP = 0.25                 # share of the riffle one page takes to turn
STEPS = max(8, min(24, N // 2))     # cascade steps
FLAT = 180.0                # a turned page (flick) lies over the spine
LIFT = 35.0                 # flick: the thumb lifts the top page's free edge this far
BACK = 100.0                # riffle: the bent-back stack stands this far past upright …
FAN = min(0.5, 24.0 / (N - 1))      # … fanned this much per page (the top page outermost)


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


# ── the pages: one sheet each, stacked bottom → top ──────────────────────────

COLS = 6
sheets, hinges = [], []
layout = {}
for j in range(1, N + 1):                        # j = 1 is the cover (top of the stack)
    level = N - j                                # 0 = bottom sheet of the stack
    s = pliego.Sheet(f"page-{j:02d}", [(0, 0), (W, 0), (W, H), (0, H)], stock=stock,
                     grain_deg=90.0,
                     label=L4(f"Page {j}", f"Página {j}", f"Page {j}", f"Página {j}"),
                     placement=pliego.Placement(origin=(0.0, level * PITCH, 0.0)))
    hinges.append(s.crease((M, 0), (M, H), "valley", FLAT, treatment="score", name="hinge"))
    s.label_edge("spine", (0, 0), (0, H))
    s.label_edge("fore-edge", (W, 0), (W, H))
    arr = s.build()
    xs = [arr.vertices[v].x for v in arr.faces[0]]
    if len(arr.faces) != 2 or max(xs) > M + 1e-6:
        raise ValueError("flip-book: the binding margin must be the page's root face, so the "
                         "page turns about the hinge and the margin stays in the block")
    sheets.append(s)
    k = j - 1
    layout[s.id] = ((k % COLS) * (W + 10.0), (k // COLS) * (H + 10.0))

# ── the cascade: per-page angles, piecewise linear in time ───────────────────


def start_angle(j):
    """Angle of page j once the thumb has bent the stack (step 1)."""
    if thumbing == "flick":
        return LIFT * (N - j) / (N - 1)
    return BACK + (N - j) * FAN


def release_order():
    """Pages in the order they spring free: frame f is carried by the f-th page released."""
    return list(range(N, 0, -1)) if thumbing == "riffle" else list(range(1, N + 1))


END = 0.0 if thumbing == "riffle" else FLAT
ORDER = release_order()
START = {j: (r / (N - 1)) * (1.0 - FLIP) for r, j in enumerate(ORDER)}


def angle_at(j, t):
    a0 = start_angle(j)
    x = pliego.clamp((t - START[j]) / FLIP, 0.0, 1.0)
    return a0 + (END - a0) * x


def check_stacking(state, when):
    """Top-to-bottom angles never increase: rigid zero-thickness pages never pass through each
    other in the preview (page j sits above page j + 1 at the hinge)."""
    for j in range(1, N):
        if state[j] < state[j + 1] - 1e-9:
            raise ValueError(f"flip-book: page {j} passes through page {j + 1} at {when}")


# ── the frame plan (no marks on the sheets) ──────────────────────────────────

R = max(3.0, round(0.07 * min(W - M, H)))        # ball radius
X0, X1 = M + 0.30 * (W - M) + R, W - 4.0 - R     # travel: the outer part of the picture area
Y0, Y1 = 4.0 + R, H - 4.0 - R                    # floor and top of the bounce
BOUNCES = max(1, round(N / 12))


def ball(f):
    t = (f - 1) / (N - 1)
    x = X0 + (X1 - X0) * t
    ph = (t * BOUNCES) % 1.0 if f < N else 0.0
    y = Y0 + (Y1 - Y0) * (1.0 - (2.0 * ph - 1.0) ** 2)
    return round(x - M), round(y)      # from the hinge line, from the tail edge


plan = {}
for f, j in enumerate(ORDER, start=1):
    bx, by = ball(f)
    if not (R - 1 <= bx <= W - M - R + 1 and R - 1 <= by <= H - R + 1):
        raise ValueError(f"flip-book: frame {f}'s ball leaves the picture area")
    plan[f] = (j, bx, by)


def cap(text):
    return text[:1].upper() + text[1:]


def frame_note(fs):
    if not fs:
        return None
    if frames == "blank":
        a, b = fs[0], fs[-1]
        pa, pb = plan[a][0], plan[b][0]
        rng = f"{a}" if a == b else f"{a}–{b}"
        prg = f"{pa}" if a == b else f"{pa}–{pb}"
        return L4(f"Frames {rng} spring free (pages {prg}).",
                  f"Se sueltan los cuadros {rng} (páginas {prg}).",
                  f"Les images {rng} s'échappent (pages {prg}).",
                  f"Soltam-se os quadros {rng} (páginas {prg}).")
    en, es, fr, pt = [], [], [], []
    for f in fs:
        j, bx, by = plan[f]
        en.append(f"frame {f}, page {j}: ball at {bx} mm from the hinge, {by} mm up")
        es.append(f"cuadro {f}, página {j}: pelota a {bx} mm de la bisagra y {by} mm de alto")
        fr.append(f"image {f}, page {j} : balle à {bx} mm de la charnière, {by} mm de haut")
        pt.append(f"quadro {f}, página {j}: bola a {bx} mm da dobradiça, {by} mm de altura")
    return L4(*(cap("; ".join(x)) + "." for x in (en, es, fr, pt)))


# ── the program ──────────────────────────────────────────────────────────────

edge_of = {j: hinges[j - 1] for j in range(1, N + 1)}
first = ORDER[0]
if thumbing == "riffle":
    bend_label = L4("Bend all the pages back with your thumb",
                    "Dobla todas las páginas hacia atrás con el pulgar",
                    "Courbez toutes les pages vers l'arrière avec le pouce",
                    "Curve todas as páginas para trás com o polegar")
else:
    bend_label = L4("Lift the free edge with your thumb",
                    "Levanta el canto libre con el pulgar",
                    "Soulevez le bord libre avec le pouce",
                    "Levante a borda livre com o polegar")
def num(x, comma):
    t = f"{x:g}"
    return t.replace(".", ",") if comma else t


area = {c: f"{num(W - M, c)} × {num(H, c)} mm" for c in (False, True)}
D = int(2 * R)
ball_txt = (L4(f" The ball is {D} mm across.", f" La pelota mide {D} mm de diámetro.",
               f" La balle fait {D} mm de diamètre.", f" A bola tem {D} mm de diâmetro.")
            if frames == "bouncing-ball" else L4("", "", "", ""))
bend_note = L4(f"Frame 1 is drawn on page {first}; draw near the free edge, inside the "
               f"{area[False]} beyond the hinge, and trace each frame over the one before."
               + ball_txt["en"],
               f"El cuadro 1 va en la página {first}; dibuja cerca del canto libre, dentro de "
               f"los {area[False]} que quedan después de la bisagra, y calca cada cuadro sobre "
               "el anterior." + ball_txt["es"],
               f"L'image 1 se dessine sur la page {first} ; dessinez près du bord libre, dans "
               f"les {area[True]} au-delà de la charnière, et calquez chaque image sur la "
               "précédente." + ball_txt["fr"],
               f"O quadro 1 vai na página {first}; desenhe perto da borda livre, dentro dos "
               f"{area[True]} depois da dobradiça, e decalque cada quadro sobre o anterior."
               + ball_txt["pt"])
bent = {j: start_angle(j) for j in range(1, N + 1)}
check_stacking(bent, "the bend")
steps = [pliego.Step("bend", bend_label, [(edge_of[j], bent[j]) for j in range(1, N + 1)],
                     duration_ms=1200, note=bend_note)]

total_s = (N - 1) / PPS / (1.0 - FLIP)           # the release front passes N pages at PPS
step_ms = int(max(100, round(1000.0 * total_s / STEPS)))
assigned = []
for i in range(1, STEPS + 1):
    t0, t1 = (i - 1) / STEPS, i / STEPS
    state = {j: angle_at(j, t1) for j in range(1, N + 1)}
    check_stacking(state, f"cascade step {i}")
    fs = [f for f, j in enumerate(ORDER, start=1)
          if (t0 < START[j] <= t1) or (i == 1 and START[j] == 0.0)]
    assigned += fs
    if fs:
        rng = f"{fs[0]}" if len(fs) == 1 else f"{fs[0]}–{fs[-1]}"
        label = L4(f"Frames {rng} spring free", f"Se sueltan los cuadros {rng}",
                   f"Les images {rng} s'échappent", f"Soltam-se os quadros {rng}")
    else:
        label = L4("The pages keep turning", "Las páginas siguen pasando",
                   "Les pages continuent de tourner", "As páginas continuam a passar")
    steps.append(pliego.Step(f"riffle-{i:02d}", label,
                             [(edge_of[j], state[j]) for j in range(1, N + 1)],
                             duration_ms=step_ms, note=frame_note(fs)))
if sorted(assigned) != list(range(1, N + 1)):
    raise ValueError("flip-book: every frame must spring free in exactly one step")
final = {j: angle_at(j, 1.0) for j in range(1, N + 1)}
if any(abs(a - END) > 1e-9 for a in final.values()):
    raise ValueError("flip-book: the riffle did not finish every page")
program = pliego.Sequence(steps, mode="kinematic")

stack = pliego.stack("block", [s for s in reversed(sheets)], PITCH, bond="none",
                     binding=((0.0, 0.0), (0.0, H)))

print(f"flip: pages={N} page={W:g}x{H:g}mm margin={M:g}mm stock={stock} "
      f"thumbing={thumbing} first-frame=page-{first:02d} frames={frames} "
      f"ball=r{R:g}mm bounces={BOUNCES} riffle={total_s:.2f}s steps={len(steps)} "
      f"pitch={PITCH:g}mm")

result = pliego.Assembly(
    sheets,
    controls=[pliego.sequence_control(label=L4("Thumb the book", "Hojear el libro",
                                               "Feuilleter le livre", "Folhear o livro"))],
    sequence=program,
    stacks=[stack],
    layout=layout,
    title="Flip book",
)
