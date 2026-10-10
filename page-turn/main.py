# page-turn — one leaf hinged at its spine: the simplest sheet hyperobject in the commons.
#
# The kernel's book generator (pliego.book.leaf) writes the leaf, its `leaf` mechanism (0° = the
# page lies to the right of the spine, 180° = turned to the left), the page-turn angle control and
# the pin that holds the spine edge in the world. The engine bends the paper physically as the
# drive point travels along the free edge, so a stiff card turns flat while thin paper curls.
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


# Face colours mirror the `appearance` block of each stock card (materials/<slug>/stock.json).
FACES = {
    "copy-80": ("#f7f7f2", "#f7f7f2"),
    "kami": ("#d9382b", "#f6f3ec"),
    "cardstock-160": ("#f4efe6", "#f4efe6"),
    "washi-kozo-30": ("#f3eee2", "#f3eee2"),
}

width = clamp(PARAM(lambda: width, 148.0), 60.0, 300.0)
height = clamp(PARAM(lambda: height, 210.0), 80.0, 420.0)
stock = PARAM(lambda: stock, "copy-80")
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by page-turn (choose {sorted(FACES)})")

result = pliego.book.leaf(width=width, height=height, stock=stock)
leaf_sheet = result.sheet("leaf")
recto, verso = FACES[stock]
leaf_sheet.front = pliego.Face(recto)
leaf_sheet.back = pliego.Face(verso)
result.title = "Page turn"
