"""Folding carton — sheet-hyperobjects cartridge (Pliego).

One family: the folding cartons cut from one sheet of paperboard, from inside dimensions.
``style`` selects the closures (one generator, ``pliego.dieline.carton``):

- straight tuck end — tuck lids top and bottom, both on the back panel;
- reverse tuck end — top tuck on the back panel, bottom tuck on the front panel;
- seal end — four flaps at each end, the outer flap glued over the inner one;
- crash-lock (auto) bottom with a tuck top — the minor bottom flaps carry a diagonal crease
  whose glue triangle is glued to the neighbouring major flap;
- 1-2-3 (snap-lock) bottom with a tuck top.

Panels are inside + the board caliper; the fold program is kinematic (a face tree). Optional:
a die-cut window in the front panel, and brand artwork (``assets/brand-mark.svg``, original
placeholder art) placed inside the front panel's safe area (``pliego:artwork``).
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


style = str(PARAM(lambda: style, "reverse-tuck"))      # noqa: F821
length = float(PARAM(lambda: length, 80.0))            # noqa: F821
width = float(PARAM(lambda: width, 40.0))              # noqa: F821
depth = float(PARAM(lambda: depth, 120.0))             # noqa: F821
stock = str(PARAM(lambda: stock, "folding-boxboard-300"))   # noqa: F821
window = bool(PARAM(lambda: window, False))            # noqa: F821
branding = bool(PARAM(lambda: branding, True))         # noqa: F821

STOCKS = ("folding-boxboard-300", "sbs-board-350", "cardstock-300", "kraftliner-150")
if stock not in STOCKS:
    raise ValueError(f"folding-carton: stock must be one of {STOCKS}, got {stock!r}")
width = min(width, length)

pack = pliego.dieline.carton(length, width, depth, stock, style=style, window=window)

artwork = []
if branding:
    xs = [p[0] for p in pack.panels["front"].polygon]
    ys = [p[1] for p in pack.panels["front"].polygon]
    safe = pack.block["safe_mm"]
    side = 0.5 * min(max(xs) - min(xs), max(ys) - min(ys))
    cx = (min(xs) + max(xs)) / 2.0
    top = max(ys) - safe - side * 0.25
    artwork.append(pliego.press.artwork(
        "brand-mark", pack.sheet, "assets/brand-mark.svg", (cx - side / 2.0, top - side),
        (side, side), side="front", panel="front", clip="panel"))

result = pliego.dieline.assemble(
    [pack], title=f"Folding carton ({style})", artwork=artwork,
    label={"en": "Fold program", "es": "Secuencia de armado", "fr": "Séquence de montage",
           "pt": "Sequência de montagem"},
    meta={"cartridge": "folding-carton",
          "params": {"style": style, "length": length, "width": width, "depth": depth,
                     "stock": stock, "window": window, "branding": branding}})
