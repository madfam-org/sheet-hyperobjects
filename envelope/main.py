"""Envelope — sheet-hyperobjects cartridge (Pliego).

One family: every common envelope from one generator, ``pliego.envelope.envelope``.

- ``style``: commercial, baronial, square, wallet, catalog, pocket, diamond flap, window;
- ``size`` (finished size): ISO 269 C4, C5, C6, DL; US #10, A2, A7;
- ``seal``: remoistenable gum or peel-and-seal strip on the seal flap.

The front panel is the address side (the print side); side flaps, bottom flap and seal flap
fold 180° behind it (side seams, glue zones on the bottom flap). Kinematic fold program: side
flaps, bottom flap, seal flap.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


style = str(PARAM(lambda: style, "commercial"))     # noqa: F821
size = str(PARAM(lambda: size, "dl"))               # noqa: F821
seal = str(PARAM(lambda: seal, "gum"))              # noqa: F821
stock = str(PARAM(lambda: stock, "copy-80"))        # noqa: F821

STOCKS = ("copy-80", "kraft-120", "cardstock-160", "elephant-hide-110")
if stock not in STOCKS:
    raise ValueError(f"envelope: stock must be one of {STOCKS}, got {stock!r}")

pack = pliego.envelope.envelope(style, size, stock, seal=seal)

result = pliego.dieline.assemble(
    [pack], title=f"Envelope ({style}, {size})",
    label={"en": "Fold program", "es": "Secuencia de doblado", "fr": "Séquence de pliage",
           "pt": "Sequência de dobras"},
    meta={"cartridge": "envelope",
          "params": {"style": style, "size": size, "seal": seal, "stock": stock}})
