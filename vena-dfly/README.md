# vena-dfly, print files

Machine: Bambu P2S, 0.4 mm nozzle, 0.20 mm layers, no supports, one part per plate. Later pieces may move to an Objet 260 or an X1 Carbon; nothing here is prepared for those.
Nothing in this folder has been sliced. PASS means the mesh checks passed; grams and hours are estimates from mesh volume.
Filament: white PLA as loaded; a transparent or translucent PLA shows the wing membrane against light. The filament choice is open.
Print flat, belly and wings on the bed. The artifact ID is cut mirrored into the bed face under the thorax and abdomen, 0.6 mm deep.

| file stem | wings | L x W x H mm (in) | margin to bed edge mm | g est | h est | down-facing mm2, widest strip mm | check |
|---|---|---|---|---|---|---|---|
| `vena-dfly-phys--cells-VS03-04__01_s07_3x_span178mm_v01` | cells fab: VS03-04 fore, VS03-08 hind | 168 x 178 x 24 (6.63 x 7.03 x 0.96) | 43.8 / 38.8 | 36 | 1.9 | 73, 0.54 | PASS |
| `vena-dfly-phys--open-VS03-01__01_s07_3x_span178mm_v01` | open: VS03-01 fore, VS03-05 hind | 168 x 178 x 24 (6.63 x 7.03 x 0.96) | 43.8 / 38.8 | 36 | 1.9 | 72, 0.54 | PASS |

Both: 72 g estimated (about $2.38), 3.8 h, about 1.9 h wall clock on 2 printers. Print order: the open variant first; its ribs are fewer and wider apart.

## What changed against v01
- Body: v01 kept the E1 body as it was and failed the no-supports rule (1894 mm2 of down-facing faces). Here every layer rests on the one under it: 45 degree chamfers under the legs and the rounded undersides, and webs 0.75 mm wide down to the bed where a chamfer alone would end in mid air. 2.7 cm3 added to 43.2. The plan outline is unchanged; from the side the legs now stand on thin webs.
- Wings: a closed membrane 0.4 mm thick (two layers) with ribs 2.0 to 3.6 mm wide and 1.2 to 3.0 mm tall, wider and taller where the vein carries more. No cell is opened.
- Eyes: hexagonal facets, 1.6 mm pitch, 0.3 mm relief, left off where the eye surface looks down or into the head.

## Fine work, below the lab minimum
The membrane (0.4 mm) and the webs under the legs (0.75 mm). Both are under the 2 mm recommendation on purpose.

## What was checked, and what was not
Checked: watertight, one shell, no non-manifold edges, footprint, height, no down-facing strip wider than 1.0 mm. The remaining down-facing area is the rounded smoothing of the grid and the roofs of the label letters, in patches of about 1 mm2.
Not checked: a slice. The vein sets were thinned to fit 2 mm ribs on a 21 mm chord, so the wings carry far fewer veins than the studies they are named for; the counts are in each check file. The body was rebuilt on a 0.25 mm grid, so it is slightly softer than the E1 mesh.

## Files per variant
stem.stl, stem_plate.3mf, stem_bed.png, stem_top.png and stem_tq.png (matte), stem_backlit.png (left wings over a light table, a stand-in material), stem_check.json.
