# vena-land, print files

Machine: Bambu P2S, 0.4 mm nozzle, 0.20 mm layers, no supports, one part per plate. Later pieces may move to an Objet 260 or an X1 Carbon; nothing here is prepared for those.
Nothing in this folder has been sliced. PASS means the mesh checks passed; grams and hours are estimates from mesh volume.
Filament: white PLA as loaded; the filament choice is open.
Four tiles, one per typology, each a 100 x 100 mm solid on a 3 mm base, flat side down. Pattern studies: no scale, no vertical exaggeration set. The artifact ID is cut mirrored into the underside, 0.6 mm deep.

| file stem | typology | L x W x H mm (in) | g est | h est | features under 2 mm, percent of plan | check |
|---|---|---|---|---|---|---|
| `vena-land-wave--cells-VS02-16__01_s07_t100mm_r20mm_v01` | waveform mounds | 100 x 100 x 19 (3.94 x 3.94 x 0.73) | 60 | 2.9 | 7.71 | PASS |
| `vena-land-berm--ovate-VS02-04__01_s07_t100mm_r20mm_v01` | berm | 100 x 100 x 23 (3.94 x 3.94 x 0.91) | 63 | 3.1 | 0.01 | PASS |
| `vena-land-terr--wing-VS03-04__01_s07_t100mm_r20mm_v01` | terraces | 100 x 100 x 23 (3.94 x 3.94 x 0.91) | 72 | 3.5 | 0.02 | PASS |
| `vena-land-pond--blob-VS02-10__01_s07_t100mm_r20mm_v01` | pond cells | 100 x 100 x 22 (3.94 x 3.94 x 0.87) | 130 | 6.2 | 0.03 | PASS |

Set: 325 g estimated (about $10.72), 15.7 h, about 7.8 h wall clock on 2 printers. Grams assume 15 percent infill under a 0.85 mm skin. Print order as listed, shortest first.

## The rule behind each typology
Veins are structure, cells are fill.
- berm: veins are ridges; crest height follows Murray width, sides fall 1 in 1.5.
- waveform mounds: cells are mounds, taller where the cell is larger; veins are the swales between them.
- pond cells: cells are basins, deeper where the cell is larger; veins are the dikes at plateau level.
- terraces: distance from the primary veins cut into steps, 3 mm tread, 2 mm riser.

## What was checked, and what was not
Checked: watertight, one shell, no non-manifold edges, footprint, height. A heightfield has no overhangs; the only down faces are the roofs of the label letters.
Not checked: a slice. Ridge crests and dike tops narrower than 2 mm are reported per tile, not removed. On the waveform cells tile they are 7.7 percent of the plan; expect soft crests there.

## The other twelve
All sixteen studies of sheet VS08 are in `00_export_svg\vena-land\` as a 16 bit heightfield PNG (0 = 0 mm, 65535 = 20 mm), a contour SVG at 1 mm and a graph.json. Only these four are solids.

## Files per tile
stem.stl, stem_plate.3mf, stem_bed.png, stem_render.png (matte), stem_check.json.
