# paper-bridge-load — a strip of paper spans a gap between two supports and carries a weight.
#
# Flat, the strip sags under the weight. Fold its two long edges up into walls and the same paper
# carries it: the walls put material far from the bending axis, and a beam's bending stiffness grows
# with the cube of its depth. The fold program folds the walls (if the section has any), then lets
# go of the weight, a small square of greyboard held above the middle of the span. Gravity, contact
# and the two supports do the rest in the physics engine.
#
# Geometry (sheet-local mm, y-up): the beam is a `length` × `width` rectangle, `length` = span plus
# a bearing at each end. Walls are valley creases along the length at `wall` from each long edge.
# The supports are two greyboard boards (the tops of two stacks of books, rigid in the engine); the
# strip rests on them by contact and friction, so it can slide in as it sags, as on a table. The
# `gap` control moves the right-hand board outward. The weight is pinned along its mid-line until
# the step "load" unties the pin (spec §5.20).
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


SECTIONS = ("flat", "channel", "deep-channel")
STOCKS = ("copy-80", "cardstock-160")
FACES = {"copy-80": ("#f7f7f2", "#f7f7f2"), "cardstock-160": ("#efe9dc", "#efe9dc")}

span = clamp(PARAM(lambda: span, 180.0), 100.0, 260.0)
width = clamp(PARAM(lambda: width, 60.0), 40.0, 90.0)
section = str(PARAM(lambda: section, "channel"))
stock = str(PARAM(lambda: stock, "copy-80"))
weight_size = clamp(PARAM(lambda: weight_size, 30.0), 20.0, 40.0)
if section not in SECTIONS:
    raise ValueError(f"paper-bridge-load: section must be one of {SECTIONS}, got {section!r}")
if stock not in STOCKS:
    raise ValueError(f"paper-bridge-load: stock must be one of {STOCKS}, got {stock!r}")

BEARING = 20.0       # paper resting on each support (mm)
HEIGHT = 60.0        # the supports hold the deck this high above the table (mm)
GAP = 4.0            # the weight starts this far above the deck (mm)
length = span + 2.0 * BEARING
wall = {"flat": 0.0, "channel": 0.2, "deep-channel": 0.3}[section] * width
floor = width - 2.0 * wall
# the weight sits on the deck between the walls, with a little play
weight_size = min(weight_size, floor - 4.0) if wall > 0 else min(weight_size, width - 4.0)
if weight_size < 10.0:
    raise ValueError("paper-bridge-load: the deck between the walls is too narrow for the weight")

front, back = FACES[stock]
BOARD = 60.0         # each support board is BOARD × (width + 20) mm
REST = 0.8           # strip mid-surface above the board tops (half the two contact thicknesses)
TRAVEL = 15.0        # the right-hand support moves out at most this far (less than the bearing)
beam = pliego.Sheet(
    "beam", pliego.rectangle(length, width), stock=stock, grain_deg=0.0,
    label=L4("Bridge strip", "Tira del puente", "Bande du pont", "Tira da ponte"),
    front=front, back=back,
    placement=pliego.Placement(origin=(0.0, HEIGHT + REST, 0.0)))
supports = []
for sid, x0b, lab in (("support-left", BEARING - BOARD, L4("Left support", "Apoyo izquierdo", "Appui gauche", "Apoio esquerdo")),
                      ("support-right", length - BEARING, L4("Right support", "Apoyo derecho", "Appui droit", "Apoio direito"))):
    supports.append(pliego.Sheet(
        sid, pliego.rectangle(BOARD, width + 20.0), stock="greyboard-1500", grain_deg=0.0, label=lab,
        front="#8f8a80", back="#8f8a80", kinematic="widen",
        placement=pliego.Placement(origin=(x0b, HEIGHT, 10.0))))
walls = []
if wall > 0:
    walls.append(beam.valley((0.0, wall), (length, wall), angle=90.0,
                             label=L4("Near wall", "Pared de este lado", "Paroi avant",
                                      "Parede da frente")))
    walls.append(beam.valley((0.0, width - wall), (length, width - wall), angle=90.0,
                             label=L4("Far wall", "Pared del otro lado", "Paroi arrière",
                                      "Parede de trás")))

# the weight: a greyboard square over the middle of the span, centred across the deck
# (placement: sheet (u, v) -> (u, 0, -v) + origin)
x0 = length / 2.0 - weight_size / 2.0
z0 = -width / 2.0 + weight_size / 2.0
weight = pliego.Sheet(
    "weight", pliego.square(weight_size), stock="greyboard-1500", grain_deg=0.0,
    label=L4("Weight", "Peso", "Poids", "Peso"), front="#8f8a80", back="#8f8a80",
    placement=pliego.Placement(origin=(x0, HEIGHT + GAP, z0)))

joins = [
    pliego.pin("hold-weight", along=(weight, [(0.0, weight_size / 2.0), (weight_size, weight_size / 2.0)])),
]

steps = []
if walls:
    steps.append(pliego.Step(
        "fold-walls", L4("Fold both walls up", "Dobla las dos paredes hacia arriba",
                         "Relever les deux parois", "Dobre as duas paredes para cima"),
        [(m, 90.0) for m in walls], duration_ms=2000,
        note=L4("Two valley folds along the strip turn it into a channel.",
                "Dos dobleces en valle a lo largo de la tira la convierten en un canal.",
                "Deux plis vallée le long de la bande en font une gouttière.",
                "Duas dobras em vale ao longo da tira a transformam numa calha.")))
steps.append(pliego.Step(
    "load", L4("Let go of the weight", "Suelta el peso", "Lâcher le poids", "Solte o peso"),
    [(m, 90.0) for m in walls], duration_ms=1500, release_joins=["hold-weight"],
    note=L4("The weight drops onto the middle of the span.",
            "El peso cae sobre el centro del claro.",
            "Le poids tombe au milieu de la portée.",
            "O peso cai no meio do vão.")))
steps.append(pliego.Step(
    "carry", L4("Watch the bridge carry it", "Mira cómo lo sostiene el puente",
                "Regarder le pont le porter", "Veja a ponte sustentá-lo"),
    [(m, 90.0) for m in walls], duration_ms=3000,
    note=L4("Flat, the strip sags; with walls, the same paper holds the weight up.",
            "Plana, la tira se pandea; con paredes, el mismo papel sostiene el peso.",
            "À plat, la bande fléchit ; avec des parois, le même papier porte le poids.",
            "Plana, a tira cede; com paredes, o mesmo papel sustenta o peso.")))

result = pliego.Assembly(
    [beam, weight] + supports, joins=joins,
    mechanisms=[pliego.translate("widen", "gap", (1.0, 0.0, 0.0), TRAVEL, [supports[1]])],
    controls=[pliego.sequence_control(label=L4("Load test", "Prueba de carga",
                                               "Essai de charge", "Teste de carga")),
              pliego.control("gap", "distance", L4("Move the right support out", "Aleja el apoyo derecho",
                                                   "Écarter l'appui droit", "Afaste o apoio direito"),
                             0.0, 0.0, TRAVEL, "mm")],
    sequence=pliego.Sequence(steps, mode="physical"),
    title="Paper bridge under load",
    meta={"cartridge": "paper-bridge-load",
          "params": {"span": span, "width": width, "section": section, "stock": stock,
                     "weight_size": weight_size}})
