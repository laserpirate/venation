# vena-samples · sample plates of the flat studies · v01 · 21 Nov 2026

**Fine, below lab minimum.** Membranes are 0.6 mm and ribs start at 0.8 mm wide; the lab recommends 2.0 mm. Nothing here is sliced or printed; grams and hours are estimates from solid volume (1.24 g per cm3, 22 g per hour, 8 s per layer at 0.20 mm).

## What a tile is
- Pattern tile (VS02, VS03): 45 x 45 mm, wings 95 x 45 mm. Frame 2.0 mm wide and 2.0 mm tall, 5.0 mm wide on the lower edge, where the study ID stands 0.4 mm proud at 3 mm cap height. Membrane 0.6 mm inside the frame. Ribs 0.8 to 2.4 mm wide and 1.2 to 2.0 mm tall in all, by Murray width (width by its square, so only the main veins are wide). Flat underside; the ID is engraved mirrored, 0.6 mm deep, under the wide edge.
- Thinning, one rule for every tile: links, then veins from the thinnest, and cells from the smallest, are dropped until gaps under 0.8 mm are no more than 12 percent of the rib area and at least 45 percent of the outline is open membrane. Named wing veins and the outline always stay. Gaps under 0.8 mm that remain (the wedges where ribs meet) are closed as rib. Nothing is redrawn. Kept share of the 32 pattern tiles: 8 to 83 percent; each tile`s count is on the plate map and in its check file.
- Six VS02 wing tiles (01, 02, 03, 05, 06, 07) do not reach the open-membrane share even with every cell dropped: their named veins alone, at one width by the VS02 rule, cover more than 55 percent. They are kept as the rule requires and print as dense plates.
- Landform tile (VS08): the heightfield as a solid, 45 x 45 mm, base 2.0 mm, relief scaled to 6.0 mm at its highest, landform 38 x 38 mm inside the same frame at base level; the sheet number (VS08-01 to 16) stands on the lower edge and the full ID is engraved mirrored underneath in two lines.

## Plates and print order
| order | plate | tiles | size mm | grams est. | hours est. | cost est. USD | tiles PASS / FAIL | IDs |
|---|---|---|---|---|---|---|---|---|
| 1 | `vena-samples--VS02__01` | 9 | 198.0 x 198.0 | 44.3 | 2.0 | 1.46 | 9 / 0 | VS02-01, VS02-02, VS02-03, VS02-04, VS02-05, VS02-06, VS02-07, VS02-08, VS02-09 |
| 2 | `vena-samples--VS02__02` | 7 | 198.0 x 96.0 | 19.7 | 0.9 | 0.65 | 7 / 0 | VS02-10, VS02-11, VS02-12, VS02-13, VS02-14, VS02-15, VS02-16 |
| 3 | `vena-samples--VS03__01` | 8 | 197.0 x 198.0 | 46.0 | 2.1 | 1.52 | 8 / 0 | VS03-01, VS03-02, VS03-03, VS03-04, VS03-05, VS03-06, VS03-07, VS03-08 |
| 4 | `vena-samples--VS03__02` | 8 | 198.0 x 147.0 | 33.8 | 1.6 | 1.12 | 8 / 0 | VS03-09, VS03-10, VS03-11, VS03-12, VS03-13, VS03-14, VS03-15, VS03-16 |
| 5 | `vena-samples--VS08__01` | 16 | 198.0 x 198.0 | 162.7 | 7.5 | 5.37 | 16 / 0 | VS08-01, VS08-02, VS08-03, VS08-04, VS08-05, VS08-06, VS08-07, VS08-08, VS08-09, VS08-10, VS08-11, VS08-12, VS08-13, VS08-14, VS08-15, VS08-16 |

Set: 306 g, 14.1 h, 10.11 USD estimated. Wall clock on two printers: 7.5 h (one runs the landform plate, the other the four pattern plates).
Print the first VS02 plate first: it is the test of the 0.6 mm membrane and the 0.8 mm ribs. Flat side down, no supports, no brim needed. Filament: white PLA shows the relief; a translucent PLA shows the membrane against light. SimplyPrint, the fine-detail profile, 0.20 mm layers or finer.

## Files
- Per tile: `vena-samples--<ID>_t<w>x<h>mm_v01.stl` and `_check.json` (the checks are run on the STL as saved and reloaded).
- Per plate: `<plate>_plate.3mf` (tiles arranged, centred on the 256 mm bed), `_bed.png` (footprint against the 203 mm square), `_map.png` (which ID sits where), `_top.png` (shaded height image from above; not a render).
- `vena-samples_set_v01.json`: every number above. `height\`: the tile heightfields the images are made from.

## Checks
48 tiles: PASS 48, FAIL 0. Rule: as saved and reloaded: watertight, one shell, 0 non-manifold edges, footprint in 203 x 203, height in 256, widest down-facing strip 1.0 mm or less (the engraved underside ID is the only down face). The 2.0 mm lab minimum wall is not met by design: fine, below lab minimum.
Plates: footprint inside 203 x 203 mm with the margins printed on each bed overlay; height under 256 mm. A plate is several parts on one 3MF because they fit the square together.
