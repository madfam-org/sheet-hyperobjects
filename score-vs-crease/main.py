# score-vs-crease — two identical cards of heavy stock folded side by side, one scored first.
#
# Both cards carry the same valley fold line down their middle. On the left card the line has the
# `score` treatment (a scoring pass made before folding; sheet-document spec §4: the hinge
# stiffness is multiplied by the stock's score_factor, with a lower yield); on the right card it
# is a plain `crease` (folded by hand with nothing prepared). One physical step folds both cards
# at once, so the viewer shows the two hinges answering the same drive; `target:folded` is the
# exact pose of the folded pair.
# Both cards are long grain (grain_deg 90): the fold runs parallel to the grain, as it should.
import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, float(value)))


FACES = {  # the `appearance` block of each stock card (materials/<slug>/stock.json)
    "cardstock-300": "#f2ede3",
    "cardstock-250": "#f4efe6",
    "cardstock-160": "#f4efe6",
    "kraft-120": "#b98a5a",
}
L4 = ("en", "es", "fr", "pt")


def i18n(*texts):
    return dict(zip(L4, texts, strict=True))


stock = PARAM(lambda: stock, "cardstock-300")
width = clamp(PARAM(lambda: width, 210.0), 80.0, 300.0)
height = clamp(PARAM(lambda: height, 148.0), 60.0, 300.0)
angle = clamp(PARAM(lambda: angle, 180.0), 30.0, 180.0)
if stock not in FACES:
    raise ValueError(f"stock {stock!r} is not offered by score-vs-crease (choose {sorted(FACES)})")

colour = FACES[stock]
fold_x = width / 2.0
scored = pliego.Sheet("scored", pliego.rectangle(width, height), stock=stock,
                      grain_deg=90.0, front=colour, back=colour,
                      label=i18n("Scored card", "Cartulina hendida", "Carte rainée",
                                 "Cartão vincado"))
plain = pliego.Sheet("unscored", pliego.rectangle(width, height), stock=stock,
                     grain_deg=90.0, front=colour, back=colour,
                     label=i18n("Unscored card", "Cartulina sin hender", "Carte non rainée",
                                "Cartão sem vinco"))
score_line = scored.score((fold_x, 0.0), (fold_x, height), kind="valley", angle=angle,
                          label=i18n("Scored fold line", "Línea hendida", "Ligne rainée",
                                     "Linha vincada"))
crease_line = plain.valley((fold_x, 0.0), (fold_x, height), angle=angle, treatment="crease",
                           label=i18n("Fold line, not scored", "Línea de doblez sin hendir",
                                      "Ligne de pli non rainée", "Linha de dobra sem vinco"))
if score_line.treatment != "score" or crease_line.treatment != "crease":
    raise ValueError("the comparison needs one scored and one plain crease")

step = pliego.Step(
    "fold-both",
    i18n("Fold both cards in half", "Dobla las dos cartulinas a la mitad",
         "Plier les deux cartes en deux", "Dobre os dois cartões ao meio"),
    [(score_line, None), (crease_line, None)], duration_ms=2500,
    note=i18n("Same card, same drive: only the treatment of the line differs.",
              "La misma cartulina y el mismo impulso: solo cambia el tratamiento de la línea.",
              "Même carte, même geste : seul le traitement de la ligne change.",
              "O mesmo cartão e o mesmo gesto: só muda o tratamento da linha."))
result = pliego.Assembly(
    [scored, plain],
    controls=[pliego.sequence_control(label=i18n("Fold program", "Secuencia de pliegues",
                                                 "Séquence de pliage", "Sequência de dobras"))],
    sequence=pliego.Sequence([step], mode="physical"),
    targets={"folded": {"scored": {"angles": {score_line: angle}},
                        "unscored": {"angles": {crease_line: angle}}}},
    title="Score vs crease",
)
