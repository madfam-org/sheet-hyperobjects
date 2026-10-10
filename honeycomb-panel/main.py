"""Honeycomb panel — sheet-hyperobjects cartridge (Pliego).

Structural paper honeycomb: a core of paper ribbons glued to each other along alternate
stripes and pulled open into hexagonal cells, sandwiched between two liners. Generated from the
cell size (flat to flat) and the core height. Two modes:

- ``panel`` — the expanded core between its liners. The **expanded hexagonal core is the initial
  frame**: every ribbon stands folded into its trapezoidal wave (node walls, then walls at 60°),
  the node walls of neighbouring ribbons glued face to face (``glue`` joins the initial frame
  satisfies). The liners are rigid boards; the ``lift`` control raises the top liner off the core
  so the cells show (a ``translate`` mechanism the preview drives).
- ``expand`` — two ribbons glued along alternate stripes, flat as they leave the gluing line,
  pulled open into one row of cells. Both ribbons are posed from their bonded first node, so the
  pair stays exactly bonded at every instant: the kinematic program is exact.

**Geometry.** Cell size s is the hexagon's flat-to-flat width; the wall length is a = s/√3. A
ribbon repeats node wall (a, along the ribbon), wall rising at 60°, node wall, wall falling at
60°: period 3a along the panel, pitch a·√3/2 between ribbons. The node walls between two ribbons
are double (two plies glued), the others single.

**Densities** (printed and stated in the article). Per unit area of panel, the core holds
8/(3√3·a) mm of ribbon per mm², so its paper is ``gsm_core · h · 8/(3√3·a)`` g/m²; the bonded node
area adds ``g_node · h/(3·a·√3/2)`` (adhesive per bonded area, an estimate [E]). The core density
is that mass divided by the core height; the panel's areal density adds both liners and an
estimated adhesive line on each [E]. The script cross-checks the formula against the ribbons it
generates (which include the edge cells).

**Limits.** The liners are not glued to the core in the document (the lift would need the engine
then); the core's crushing strength, the ribbons' bending as they are pulled open and the
liners' bond are the physics engine's part. No strength rating is claimed.
"""

import math

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


run_mode = str(PARAM(lambda: mode, "panel"))             # noqa: F821 - injected by the runner
cell = float(PARAM(lambda: cell, 20.0))                  # noqa: F821 - flat-to-flat (mm)
core_height = float(PARAM(lambda: core_height, 25.0))    # noqa: F821 - core height (mm)
periods = round(float(PARAM(lambda: periods, 4)))        # noqa: F821 - cells along a ribbon
ribbons = round(float(PARAM(lambda: ribbons, 7)))        # noqa: F821 - ribbons in the core
core_stock = str(PARAM(lambda: core_stock, "kraft-120"))       # noqa: F821
liner_stock = str(PARAM(lambda: liner_stock, "kraftliner-150"))  # noqa: F821

if run_mode not in ("panel", "expand"):
    raise ValueError("honeycomb-panel: mode must be panel or expand")
if core_stock not in ("kraft-120", "kraftliner-150"):
    raise ValueError("honeycomb-panel: core_stock must be kraft-120 or kraftliner-150")
if liner_stock not in ("kraftliner-150", "cardstock-300", "greyboard-1500"):
    raise ValueError("honeycomb-panel: liner_stock must be kraftliner-150, cardstock-300 or "
                     "greyboard-1500")
cell = pliego.clamp(cell, 8.0, 40.0)
h = pliego.clamp(core_height, 5.0, 100.0)
periods = int(pliego.clamp(periods, 2, 8))
ribbons = int(pliego.clamp(ribbons, 3, 12))

a = cell / math.sqrt(3.0)                  # wall length
h1 = a * math.sqrt(3.0) / 2.0              # ribbon pitch (half the cell's flat-to-flat)
n_seg = 4 * periods + 1                    # node, wall, node, wall, … node
THETA = 60.0
S = math.sqrt(0.5)
STAND = (S, 0.0, 0.0, S)                   # +90° about X: sheet (u, v) → world (u, v, 0)
GLUE_NODE = 10.0                           # g/m² of bonded node area [E]
GLUE_LINER = 15.0                          # g/m² per liner face [E]
RIBBON = L4("Core ribbon", "Tira del núcleo", "Ruban d'âme", "Fita do núcleo")


def ribbon(sid, starts_low, k, z0, rest):
    """One ribbon: n_seg walls of width a, creased between them; starts_low picks the phase."""
    sh = pliego.Sheet(sid, pliego.rectangle(n_seg * a, h), stock=core_stock, grain_deg=0.0,
                      label={g: f"{v} {k}" for g, v in RIBBON.items()},
                      placement=pliego.Placement(origin=(0.0, 0.0, z0), rotation=STAND))
    turns = [THETA, -THETA, -THETA, THETA] if starts_low else [-THETA, THETA, THETA, -THETA]
    marks = []
    for i in range(1, n_seg):
        ang = turns[(i - 1) % 4]
        kind = "valley" if ang > 0 else "mountain"
        marks.append((sh.crease((i * a, 0.0), (i * a, h), kind, abs(ang),
                                rest=abs(ang) if rest else None), ang))
    return sh, marks


def bond(jid, lower, upper, i):
    """Glue the node wall i of `lower` to the same node of `upper` (same u: both run along +x)."""
    m = 0.5
    region = [(i * a + m, m), ((i + 1) * a - m, m), ((i + 1) * a - m, h - m), (i * a + m, h - m)]
    return pliego.glue(jid, lower, region, upper, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0), side="back")


# ── densities (closed form) and the generated geometry's check ──────────────────────────────
gsm_core = pliego.resolve_stock(core_stock, None)["gsm"]
gsm_liner = pliego.resolve_stock(liner_stock, None)["gsm"]
t_liner = pliego.board.caliper(liner_stock)
paper = gsm_core * h * 8.0 / (3.0 * math.sqrt(3.0) * a)          # g/m² of panel
glue_core = GLUE_NODE * h / (3.0 * h1)                             # g/m² of panel
core_density = (paper + glue_core) / h                             # g/m²/mm = kg/m³
areal = 2.0 * gsm_liner + paper + glue_core + 2.0 * GLUE_LINER     # g/m²
Lx = 3.0 * a * periods + a                 # the panel's plan extent (node to node)
Lz = ribbons * h1                          # each ribbon spans one pitch
gen = gsm_core * ribbons * n_seg * a * h / (Lx * Lz)

sheets, joins = [], []
if run_mode == "panel":
    for k in range(ribbons):
        low = k % 2 == 0
        z0 = k * h1 if low else (k + 1) * h1
        sh, marks = ribbon(f"ribbon-{k + 1}", low, k + 1, z0 - Lz / 2.0, True)
        sheets.append((sh, marks))
    for k in range(ribbons - 1):
        lower, upper = sheets[k][0], sheets[k + 1][0]
        first = 2 if k % 2 == 0 else 0           # the lower ribbon's upper nodes
        for i in range(first, n_seg, 4):
            joins.append(bond(f"bond-{k + 1}-{i}", lower, upper, i))
    z_lo, z_hi = -Lz / 2.0, Lz / 2.0
    LINER = {"bottom": L4("Bottom liner", "Cara inferior", "Peau inférieure", "Face inferior"),
             "top": L4("Top liner", "Cara superior", "Peau supérieure", "Face superior")}
    bottom = pliego.Sheet("liner-bottom", pliego.rectangle(Lx, Lz), stock=liner_stock,
                          label=LINER["bottom"], kinematic="lift-liner",
                          placement=pliego.Placement(origin=(0.0, -t_liner / 2.0, z_lo),
                                                     rotation=(1.0, 0.0, 0.0, 0.0)))
    top = pliego.Sheet("liner-top", pliego.rectangle(Lx, Lz), stock=liner_stock,
                       label=LINER["top"], kinematic="lift-liner",
                       placement=pliego.Placement(origin=(0.0, h + t_liner / 2.0, z_hi)))
    travel = round(max(30.0, 1.5 * h), 1)
    initial = {sh.id: {"angles": {m: ang for m, ang in marks}, "root": (a / 2.0, h / 2.0)}
               for sh, marks in sheets}
    result = pliego.Assembly(
        [bottom] + [sh for sh, _m in sheets] + [top], joins=joins,
        mechanisms=[pliego.translate("lift-liner", "lift", (0.0, 1.0, 0.0), travel, [top])],
        controls=[pliego.control("lift", "distance",
                                 L4("Lift the top liner", "Levanta la cara superior",
                                    "Soulever la peau supérieure", "Levante a face superior"),
                                 0.0, 0.0, travel, "mm")],
        initial=initial, title=f"Honeycomb panel (cell {cell:g} mm, core {h:g} mm)",
        layout={s.id: (0.0, k * (max(h, Lz) + 10.0)) for k, s in
                enumerate([bottom] + [sh for sh, _m in sheets] + [top])},
        meta={"cartridge": "honeycomb-panel", "mode": "panel",
              "params": {"cell": cell, "core_height": h, "periods": periods,
                         "ribbons": ribbons, "core_stock": core_stock,
                         "liner_stock": liner_stock}})
else:
    upper_first, uf_marks = ribbon("ribbon-a", False, 1, 0.0, False)   # first node: its upper
    lower_first, lf_marks = ribbon("ribbon-b", True, 2, 0.0, False)    # first node: its lower
    for i in range(0, n_seg, 4):
        joins.append(bond(f"bond-{i}", upper_first, lower_first, i))
    step = pliego.Step("expand", L4("Pull the glued ribbons open into cells",
                                    "Abre las tiras pegadas hasta formar las celdas",
                                    "Étirez les rubans collés pour ouvrir les alvéoles",
                                    "Abra as fitas coladas até formar as células"),
                       [(m, ang) for m, ang in uf_marks + lf_marks], duration_ms=2400,
                       note=L4("The glued stripes stay face to face at every instant.",
                               "Las franjas pegadas siguen cara a cara en todo momento.",
                               "Les bandes collées restent face à face à chaque instant.",
                               "As faixas coladas continuam face a face a todo o momento."))
    result = pliego.Assembly(
        [upper_first, lower_first], joins=joins,
        controls=[pliego.sequence_control(label=L4("Expand", "Expandir", "Expanser",
                                                   "Expandir"))],
        sequence=pliego.Sequence([step], mode="kinematic"),
        initial={"ribbon-a": {"angles": {}, "root": (a / 2.0, h / 2.0)},
                 "ribbon-b": {"angles": {}, "root": (a / 2.0, h / 2.0)}},
        title="Honeycomb core: one row of cells opening",
        layout={"ribbon-a": (0.0, 0.0), "ribbon-b": (0.0, h + 10.0)},
        meta={"cartridge": "honeycomb-panel", "mode": "expand",
              "params": {"cell": cell, "core_height": h, "periods": periods,
                         "core_stock": core_stock}})

print(f"honeycomb-panel: cell {cell:g} mm (wall {a:.2f} mm), core {h:g} mm: core paper "
      f"{paper:.1f} g/m², node glue {glue_core:.1f} g/m², core density {core_density:.1f} kg/m³; "
      f"panel areal density {areal:.0f} g/m² ({liner_stock} liners)"
      + (f"; generated ribbons {gen:.1f} g/m² over {Lx:.0f} x {Lz:.0f} mm (edge cells included)"
         if run_mode == "panel" else ""))
