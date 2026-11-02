# Overlay card · Tarjeta superpuesta · Carte de superposition · Cartão de sobreposição

| Language | Summary |
|---|---|
| en | A blank cardstock or PET overlay with keypad, window or custom rectangular openings, checked for connected material and minimum bridges. |
| es | Una tarjeta de cartulina o PET sin arte, con aberturas de teclado, ventana o rectángulos personalizados, verificada por continuidad y puentes mínimos. |
| fr | Une carte vierge en bristol ou PET avec ouvertures de clavier, fenêtre ou rectangles personnalisés, vérifiée pour sa continuité et ses ponts minimaux. |
| pt | Um cartão de cartolina ou PET sem arte, com aberturas de teclado, janela ou retângulos personalizados, verificado quanto à continuidade e às pontes mínimas. |

## Construction

The outline is a rectangle or a rounded rectangle of `panel_w × panel_h`.
The keypad pattern places `rows × columns` rectangular openings around its
centre at `pitch_x` and `pitch_y`. The window pattern places one central
opening. In the custom pattern, `cutouts` lists rectangles as
`centre_x,centre_y,width,height` in mm, separated by semicolons; the origin is
the lower-left corner of the sheet. Up to 32 explicit rectangles are accepted.

Every opening must leave the selected stock's minimum feature between itself,
another opening and the border. The rounded-outline border check conservatively
keeps the corner radius clear too. The native paper-cut analyzer additionally
checks connectivity, bridges and removed slivers. Malformed, overlapping or
out-of-border openings fail instead of being silently clipped. The defaults
and all presets are original archetypes, not measurements of Intellivision,
ColecoVision, Vectrex, Odyssey or another product's control panel.

No symbols, legends, game images, traced contours or printed artwork are
included. `cardstock-250` and `pet-125` use the platform's own material cards.
PET is not called acetate, and no acetate properties are invented: a future
acetate option needs an actual stock card. This is a flat cut part; it has no
invented fold program. Its FOLD and static GLB can be placed or lifted by an
experience's own choreography without duplicating the sheet geometry there.

## Exact panels and making

For a named panel, source its outline, cutout positions and stock in the
reference catalog first. A button count alone does not establish pitch or a
physical overlay outline. Fit a plain test cut to the actual panel before
printing or fabricating a final overlay; the geometric checks do not establish
attachment, friction, optical filtering or preservation suitability.

The geometry is original MADFAM work computed from the chosen parameters. No
commercial overlay drawing, crease pattern, title artwork or designer's diagram
is reproduced.
