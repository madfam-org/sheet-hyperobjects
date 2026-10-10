# perforated-tear — a card with a perforated tear-off stub, pulled until the perforation parts.
#
# The perforation is a line with the `perforation` treatment and assignment C ("designed to
# separate"): the exporters draw it as a dashed cut (cut length / bridge length from the stock
# card), and the engine treats it as a hinge whose stiffness is multiplied by the stock's
# perf_factor (the bridge fraction) and which separates once its strain passes tear_strain.
# The body's far edge is pinned where it starts; the stub's far edge is pinned to a `translate`
# driver, so the `tear` distance control pulls the stub away in the plane of the card.
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


FACES = {  # the `appearance` block of each stock card (materials/<slug>/stock.json)
    "cardstock-160": "#f4efe6",
    "copy-80": "#f7f7f2",
    "cardstock-250": "#f4efe6",
    "kraft-120": "#b98a5a",
}
L4 = ("en", "es", "fr", "pt")


def i18n(*texts):
    return dict(zip(L4, texts, strict=True))


width = clamp(PARAM(lambda: width, 150.0), 80.0, 250.0)
height = clamp(PARAM(lambda: height, 60.0), 30.0, 150.0)
stub = clamp(PARAM(lambda: stub, 40.0), 15.0, 80.0)
pull = clamp(PARAM(lambda: pull, 10.0), 2.0, 30.0)
stock = PARAM(lambda: stock, "cardstock-160")
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by perforated-tear (choose {sorted(FACES)})")
if stub > width / 2.0:
    raise ValueError(f"a {stub} mm stub needs a card at least {2 * stub} mm wide (width {width})")

colour = FACES[stock]
card = pliego.Sheet("card", pliego.rectangle(width, height), stock=stock, front=colour,
                    back=colour, label=i18n("Card with tear-off stub", "Tarjeta con talón "
                                            "desprendible", "Carte à talon détachable",
                                            "Cartão com canhoto destacável"))
x = width - stub
perforation = card.perforate((x, 0.0), (x, height), kind="cut",
                             label=i18n("Perforation", "Perforación", "Perforation",
                                        "Picote"))
if perforation.assignment != "C" or perforation.treatment != "perforation":
    raise ValueError("the tear line must be a perforation designed to separate (C)")

body_edge = ((0.0, 0.0), (0.0, height))
stub_edge = ((width, 0.0), (width, height))
result = pliego.Assembly(
    [card],
    joins=[pliego.pin("body-hold", along=(card, body_edge)),
           pliego.pin("stub-grip", along=(card, stub_edge), mechanism="pull-stub")],
    mechanisms=[pliego.translate("pull-stub", "tear", (1.0, 0.0, 0.0), pull)],
    controls=[pliego.control("tear", "distance",
                             i18n("Pull the stub", "Jala el talón", "Tirer sur le talon",
                                  "Puxe o canhoto"), 0.0, 0.0, pull, "mm")],
    title="Perforated tear",
)
