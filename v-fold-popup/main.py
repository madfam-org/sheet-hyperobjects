"""V-fold pop-up — sheet-hyperobjects cartridge (Pliego).

A kite of card, folded on its long axis, is glued across the gutter of a spread: each half
glued along a line at `glue_angle` from the gutter. Opening the spread pulls the two glue
lines apart and the fold rises; closing it folds the piece flat inside the book.

Geometry and kinematics come from the kernel (`pliego.popup.v_fold`): the piece is a
degree-4 vertex on the gutter whose fold line is solved in closed form at every opening.
With the piece half-angle equal to the glue angle (β = α) the mechanism is flat at 0° and
at 180° and never locks in between. This script only chooses the parameters, refuses any
combination that would not close flat or would stick out of the closed book, and returns
the assembly (two kinematic boards on a `hinge`, the piece, two glue joins, `open`).
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))
page_height = float(PARAM(lambda: page_height, 200.0))
glue_angle = float(PARAM(lambda: glue_angle, 40.0))
glue_length = float(PARAM(lambda: glue_length, 50.0))
piece_height = float(PARAM(lambda: piece_height, 80.0))
piece_offset = float(PARAM(lambda: piece_offset, 40.0))
tab_width = float(PARAM(lambda: tab_width, 10.0))
opening = float(PARAM(lambda: opening, 90.0))

TOL_MM = 1e-6

popup = pliego.popup.v_fold(
    alpha=glue_angle,
    beta=glue_angle,          # β = α: flat at both extremes (β < α locks, β > α stands at 180°)
    glue_len=glue_length,
    apex=piece_height,
    at=piece_offset,
    tab=tab_width,
    width=page_width,
    height=page_height,
    default_open=opening,
)

# Closure: flat at 0° and 180°, no lock at any whole degree in between (fail loud).
closure = popup.closure(step=1.0)
if not closure["ok"]:
    raise ValueError(f"v-fold-popup: the piece does not close flat ({closure})")


def piece_extent(phi):
    """World bounding box of the piece's vertices at opening φ."""
    pose = popup.pose(phi)
    piece = popup.sheets[-1]
    pts = [pose[piece.id](v.x, v.y) for v in piece.build().vertices]
    return ([min(p[k] for p in pts) for k in range(3)],
            [max(p[k] for p in pts) for k in range(3)])


# Containment: closed, the piece must lie inside the closed book (x in [-W, 0], z in [-H, 0]);
# opened flat, inside the spread (x in [-W, W]).
lo, hi = piece_extent(0.0)
if lo[0] < -page_width - TOL_MM or hi[0] > TOL_MM or lo[2] < -page_height - TOL_MM \
        or hi[2] > TOL_MM:
    raise ValueError("v-fold-popup: the closed piece sticks out of the book — lower "
                     "piece_height or glue_angle, or enlarge the page")
lo, hi = piece_extent(180.0)
if lo[0] < -page_width - TOL_MM or hi[0] > page_width + TOL_MM \
        or lo[2] < -page_height - TOL_MM:
    raise ValueError("v-fold-popup: the opened piece does not fit the spread")

result = popup.assembly()
