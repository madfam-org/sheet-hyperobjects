"""Corrugated board — sheet-hyperobjects cartridge (Pliego).

Corrugation itself: fluted media glued between liners. One family, three modes:

- ``board``: single face, single wall, double wall or triple wall, any of the A, B, C, E and F
  flute profiles; the liners lie in place and each medium is fed flat and corrugated, flute by
  flute, until it fits between them (kinematic program);
- ``craft``: craft corrugated paper — single face with the flutes exposed on top, in colour;
- ``section``: a cut template of the board's cross-section at a chosen scale, with a foot that
  folds so the section stands on the table.

Geometry comes from ``pliego.corrugate`` and the flute table of ``pliego.board`` (the model the
board stock cards are derived from): pitch from flutes per metre, flute height, a trapezoid
medium whose take-up equals the stock model's sinusoid. The sheets are the component papers
(kraftliner and kraft medium); the combined board's physics lives on the corrugated stock cards.
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


mode = str(PARAM(lambda: mode, "board"))                    # noqa: F821
construction = str(PARAM(lambda: construction, "single-wall"))   # noqa: F821
flute = str(PARAM(lambda: flute, "B"))                      # noqa: F821
inner_flute = str(PARAM(lambda: inner_flute, "C"))          # noqa: F821
length = float(PARAM(lambda: length, 80.0))                 # noqa: F821
width = float(PARAM(lambda: width, 60.0))                   # noqa: F821
liner = str(PARAM(lambda: liner, "kraftliner-150"))         # noqa: F821
medium = str(PARAM(lambda: medium, "kraft-120"))            # noqa: F821
scale = float(PARAM(lambda: scale, 5.0))                    # noqa: F821
color = str(PARAM(lambda: color, "#d23c3c"))                # noqa: F821

FLUTES = ("A", "B", "C", "E", "F")
WALLS = {"single-face": 1, "single-wall": 1, "double-wall": 2, "triple-wall": 3}
if construction not in WALLS:
    raise ValueError(f"corrugated-board: construction must be one of {tuple(WALLS)}")
if flute not in FLUTES or inner_flute not in FLUTES:
    raise ValueError(f"corrugated-board: flutes must be in {FLUTES}")
if mode not in ("board", "craft", "section"):
    raise ValueError(f"corrugated-board: unknown mode {mode!r}")
length = pliego.clamp(length, 40.0, 200.0)
width = pliego.clamp(width, 30.0, 150.0)
scale = pliego.clamp(scale, 1.0, 10.0)
if mode == "craft":
    construction = "single-face"

t_liner = pliego.board.caliper(liner)
t_medium = pliego.board.caliper(medium)
flutes = {"single-face": [flute], "single-wall": [flute], "double-wall": [flute, inner_flute],
          "triple-wall": [flute, flute, inner_flute]}[construction]


def L4(en, es, fr, pt):
    return {"en": en, "es": es, "fr": fr, "pt": pt}


def layer(role, t, f=None):
    d = {"role": role, "gsm": 100.0, "caliper_um": t * 1000.0, "E_md_gpa": 6.5,
         "E_cd_gpa": 2.8, "status": "estimated", "basis": "geometry only (this cartridge)"}
    if f:
        d["flute"] = f
    return d


layers = [layer("liner", t_liner)]
for f in flutes:
    layers.append(layer("medium", t_medium, f))
    if construction != "single-face":
        layers.append(layer("liner", t_liner))
if construction == "single-face":
    layers.reverse()                          # top first: the flutes face up, exposed
build = {"kind": "corrugated", "model": "pliego.board v1", "layers": layers}
slabs = pliego.corrugate.stack(build)          # bottom up
meta = {"cartridge": "corrugated-board",
        "params": {"construction": construction, "flute": flute, "inner_flute": inner_flute,
                   "length": length, "width": width, "liner": liner, "medium": medium,
                   "scale": scale, "color": color}}
KRAFT = "#b5865a"

if mode == "section":
    # a single-face board's flutes face up, so the foot folds on the flat liner below
    sec_build = build
    n_sec = max(2, round(length / pliego.corrugate.wall(flutes[-1], t_medium * 1000).pitch))
    outline, voids = pliego.corrugate.section(sec_build, n_sec)
    sec_len = outline[1][0]
    s = scale
    foot = 12.0
    sheet = pliego.Sheet(
        "section", [(0.0, -foot), (sec_len * s, -foot)] + [(x * s, z * s) for x, z in outline[2:]],
        stock="cardstock-300", grain_deg=0.0,
        label=L4("Cross-section template", "Plantilla del corte transversal",
                 "Gabarit de la coupe", "Gabarito do corte transversal"))
    for v in voids:
        sheet.hole([(x * s, z * s) for x, z in v])
    stand = sheet.valley((0.0, 0.0), (sec_len * s, 0.0), 90.0, treatment="score", name="foot")
    step = pliego.Step("stand-up", L4("Fold the foot and stand the section up",
                                      "Dobla el pie y pon el corte de pie",
                                      "Pliez le pied et dressez la coupe",
                                      "Dobre o pé e ponha o corte em pé"), [(stand, 90.0)])
    result = pliego.Assembly(
        [sheet], controls=[pliego.sequence_control(label=L4(
            "Stand up", "Poner de pie", "Dresser", "Pôr em pé"))],
        sequence=pliego.Sequence([step], mode="kinematic"),
        title=f"Corrugated board cross-section ({''.join(flutes)}, x{scale:g})", meta=meta)
else:
    sheets, positions, steps = [], {}, []
    liner_k = medium_k = 0
    strips = []
    for slab, lay in zip(slabs, reversed(layers)):
        if slab.role == "medium":
            medium_k += 1
            w = pliego.corrugate.wall(slab.flute, t_medium * 1000.0)
            n = max(2, round(length / w.pitch))
            sid = f"medium-{medium_k}"
            fs = pliego.corrugate.fluted_strip(
                sid, slab.flute, n, width, medium_um=t_medium * 1000.0, stock=medium,
                label=L4(f"Fluted medium {medium_k} ({slab.flute} flute)",
                         f"Médium ondulado {medium_k} (flauta {slab.flute})",
                         f"Cannelure {medium_k} (profil {slab.flute})",
                         f"Miolo ondulado {medium_k} (onda {slab.flute})"),
                front=color if mode == "craft" else KRAFT,
                back=color if mode == "craft" else KRAFT)
            sheets.append(fs.sheet)
            strips.append(fs)
            positions[sid] = slab.z1 - t_medium / 2.0       # height of the top lands
        else:
            liner_k += 1
            sid = f"liner-{liner_k}"
            sheets.append(pliego.Sheet(
                sid, pliego.rectangle(1.0, 1.0), stock=liner,
                label=L4(f"Liner {liner_k}", f"Liner {liner_k}", f"Couverture {liner_k}",
                         f"Capa {liner_k}")))
            positions[sid] = (slab.z0 + slab.z1) / 2.0
    board_len = max(fs.board_length for fs in strips)
    for k, sh in enumerate(sheets):            # liners get their real size now
        if sh.id.startswith("liner"):
            sheets[k] = pliego.Sheet(sh.id, pliego.rectangle(board_len, width), stock=liner,
                                     grain_deg=0.0, label=sh.label,
                                     front=KRAFT if mode != "craft" else "#efe6d6",
                                     back=KRAFT if mode != "craft" else "#efe6d6")
    for k, fs in enumerate(strips, start=1):
        n = len(fs.marks)
        thirds = [fs.marks[i * n // 3:(i + 1) * n // 3] for i in range(3)]
        angles = dict(zip(fs.marks, fs.angles))
        for j, group in enumerate(thirds, start=1):
            if not group:
                continue
            steps.append(pliego.Step(
                f"corrugate-{k}-{j}",
                L4(f"Feed medium {k} through the corrugating rolls ({j}/3)",
                   f"Pasa el médium {k} por los rodillos corrugadores ({j}/3)",
                   f"Passez la cannelure {k} entre les cylindres onduleurs ({j}/3)",
                   f"Passe o miolo {k} pelos rolos onduladores ({j}/3)"),
                [(m, angles[m]) for m in group], duration_ms=900))

    def initial(sheet_id, uv):
        return (uv[0], positions[sheet_id], -uv[1])

    result = pliego.Assembly(
        sheets, controls=[pliego.sequence_control(label=L4(
            "Corrugate", "Corrugar", "Onduler", "Ondular"))],
        sequence=pliego.Sequence(steps, mode="kinematic"), initial=initial,
        title=f"Corrugated board ({construction}, {''.join(flutes)})", meta=meta)
