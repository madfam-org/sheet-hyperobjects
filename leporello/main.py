"""Leporello (accordion book) — sheet-hyperobjects cartridge (Pliego).

One long strip divided into `panels` equal panels by scored folds that alternate valley,
mountain, valley, … . Folded, the panels stack into a closed book; pulled open, the strip
reads as one continuous surface.

Geometry, assignment and the fold program come from the kernel (`pliego.book.leporello`):
every crease folds to 180° (valley +180°, mountain −180°), and the fold program has one step
that closes the book, run in kinematic mode (rigid panels: the folded state is exact). This
script chooses the parameters and relabels the program's clock as the Close control — 0 is
the strip lying open and flat, 1 is the book closed.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


panels = round(float(PARAM(lambda: panels, 8)))
panel_width = float(PARAM(lambda: panel_width, 100.0))
panel_height = float(PARAM(lambda: panel_height, 150.0))
stock = str(PARAM(lambda: stock, "cardstock-160"))

STOCKS = ("cardstock-160", "cardstock-250", "kraft-120", "elephant-hide-110")
if stock not in STOCKS:
    raise ValueError(f"leporello: stock must be one of {STOCKS}, got {stock!r}")
if not 2 <= panels <= 24:
    raise ValueError(f"leporello: panels must be an integer in [2, 24], got {panels}")

result = pliego.book.leporello(
    panels=panels,
    width=panel_width,
    height=panel_height,
    stock=stock,
    sheet_id="leporello",
    label={"en": "Accordion strip", "es": "Tira en acordeón", "fr": "Bande en accordéon",
           "pt": "Tira em sanfona"},
    title="Leporello",
    meta={"cartridge": "leporello",
          "params": {"panels": panels, "panel_width": panel_width,
                     "panel_height": panel_height, "stock": stock}},
)
result.controls = [pliego.sequence_control(
    "sequence", {"en": "Close", "es": "Cerrar", "fr": "Fermer", "pt": "Fechar"})]

# Self-check (fail loud): the creases alternate and every one folds a full 180°.
creases = [m for m in result.sheets[0].marks if m.assignment in ("M", "V")]
if len(creases) != panels - 1:
    raise ValueError("leporello: expected one crease between each pair of panels")
for k, mark in enumerate(creases):
    expected = "V" if k % 2 == 0 else "M"
    if mark.assignment != expected or abs(abs(mark.fold_angle) - 180.0) > 1e-9:
        raise ValueError(f"leporello: crease {k + 1} is {mark.assignment} "
                         f"{mark.fold_angle}°, expected {expected} 180°")
