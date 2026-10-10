"""Parallel-fold pop-up — sheet-hyperobjects cartridge (Pliego).

A strip of card with three scored folds is glued across the gutter of a spread: its first
panel at `left_depth` from the gutter on the left page, its last panel at `right_depth` on the
right page. Opening the spread to 90° raises a box: a step whose top is parallel to the left
page and whose front is parallel to the right page.

Geometry and kinematics come from the kernel (`pliego.popup.parallel_fold`): in cross-section
the piece is a four-bar linkage G–A–F–B (G the gutter, A and B the glue lines, F the fold).
The panel lengths are fixed to the opposite sides (A–F = right_depth, F–B = left_depth), so the
linkage is a parallelogram at every opening — flat at 0° and 180° and never locked. This script
chooses the parameters, refuses any combination that would not close flat or would stick out
of the closed book, and returns the assembly (two kinematic boards on a `hinge`, the piece,
two glue joins, the `open` control).
"""

import pliego


def PARAM(get, default):
    try:
        return get()
    except NameError:
        return default


page_width = float(PARAM(lambda: page_width, 150.0))
page_height = float(PARAM(lambda: page_height, 200.0))
left_depth = float(PARAM(lambda: left_depth, 40.0))
right_depth = float(PARAM(lambda: right_depth, 50.0))
piece_width = float(PARAM(lambda: piece_width, 60.0))
piece_offset = float(PARAM(lambda: piece_offset, 70.0))
tab_width = float(PARAM(lambda: tab_width, 12.0))
opening = float(PARAM(lambda: opening, 90.0))

TOL_MM = 1e-6

popup = pliego.popup.parallel_fold(
    p=left_depth,
    q=right_depth,
    piece_width=piece_width,
    at=piece_offset,
    tab=tab_width,
    width=page_width,
    height=page_height,
    s1=right_depth,           # A–F equals G–B ...
    s2=left_depth,            # ... and F–B equals G–A: a parallelogram, flat at 0° and 180°
    default_open=opening,
)

# Closure: flat at 0° and 180°, no lock at any whole degree in between (fail loud).
closure = popup.closure(step=1.0)
if not closure["ok"]:
    raise ValueError(f"parallel-fold-popup: the piece does not close flat ({closure})")


def piece_extent(phi):
    """World bounding box of the piece's vertices at opening φ."""
    pose = popup.pose(phi)
    piece = popup.sheets[-1]
    pts = [pose[piece.id](v.x, v.y) for v in piece.build().vertices]
    return ([min(p[k] for p in pts) for k in range(3)],
            [max(p[k] for p in pts) for k in range(3)])


# Containment: closed, the folded strip reaches left_depth + right_depth from the gutter and
# must stay inside the closed book; opened flat, inside the spread.
lo, hi = piece_extent(0.0)
if lo[0] < -page_width - TOL_MM or hi[0] > TOL_MM or lo[2] < -page_height - TOL_MM \
        or hi[2] > TOL_MM:
    raise ValueError("parallel-fold-popup: the closed piece sticks out of the book — keep "
                     "left_depth + right_depth within the page width")
lo, hi = piece_extent(180.0)
if lo[0] < -page_width - TOL_MM or hi[0] > page_width + TOL_MM \
        or lo[2] < -page_height - TOL_MM:
    raise ValueError("parallel-fold-popup: the opened piece does not fit the spread")

result = popup.assembly()
