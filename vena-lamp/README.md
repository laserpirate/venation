# vena-lamp, print files

Machine: Bambu P2S, 0.4 mm nozzle, 0.20 mm layers, no supports, one part per plate. Later pieces may move to an Objet 260 or an X1 Carbon; nothing here is prepared for those.
Nothing in this folder has been sliced. PASS means the mesh checks passed; grams and hours are estimates from mesh volume.
Filament: white PLA is what the lab machines carry. These pieces are drawn to be lit from inside, so a transparent or translucent PLA is the intended material; the filament choice is open. A polycarbonate filament was named for the clear pieces; the lab P2S takes unmodified PLA only, so nothing here assumes it.
Base: each foot sleeves over a plain cylinder of the named diameter (internal diameter = base + 0.5 mm), light inside, cable through the 3 x 4 mm notch. That base is an assumption; no product has been named.
Every part prints foot down, open top up. The artifact ID is engraved inside the collar bore (0.45 mm deep), because the foot ring is 2 to 3 mm wide and an underside label would not be readable; the test piece has 45, 65, 85 cut into its underside.

## Print order
The test piece first, then VS06a-02, then the rest by estimated hours, shortest first.

| # | sheet tile | file stem | technique | L x W x H mm (in) | margin to bed edge mm | least mm | g est | h est | check |
|---|---|---|---|---|---|---|---|---|---|
| 1 | test piece | `vena-lamp-test--windows-VS06a-01__01_s23_b3.20in_h46mm_v01` | T1, windows 0.45, 0.65, 0.85 mm | 15 x 56 x 46 (0.60 x 2.22 x 1.80) | 120.4 / 99.8 | window 2.5 | 6 | 0.8 | PASS |
| 2 | VS06a-02 | `vena-lamp-egg--cells-VS04-12__02_s23_b2.00in_h190mm_v01` | T1 window 0.85 mm | 96 x 96 x 183 (3.78 x 3.78 x 7.20) | 79.9 / 79.9 | window 3.7 | 101 | 6.6 | PASS |
| 3 | VS06a-08 | `vena-lamp-cyl--closed-VS04-01__01_s07_b2.00in_h180mm_v01` | T2 open, graded | 58 x 58 x 172 (2.28 x 2.27 x 6.77) | 99.1 / 99.1 | hole 2.8 | 34 | 3.5 | PASS |
| 4 | VS06a-06 | `vena-lamp-cyl--cells-VS04-12__01_s23_b1.75in_h165mm_v01` | T1 window 0.85 mm | 50 x 50 x 157 (1.97 x 1.97 x 6.19) | 103.0 / 103.0 | window 3.7 | 41 | 3.6 | PASS |
| 5 | VS06b-05 | `vena-lamp-cyl--leaf-wrap1-VS02-04__01_s07_b2.25in_h200mm_v01` | T1 window 0.85 mm | 65 x 63 x 199 (2.56 x 2.47 x 7.84) | 95.5 / 96.6 | window 1.6 | 55 | 4.7 | PASS |
| 6 | VS06b-06 | `vena-lamp-cyl--leaf-wrap3-VS02-04__01_s07_b2.25in_h200mm_v01` | T1 window 0.85 mm | 65 x 66 x 199 (2.56 x 2.59 x 7.84) | 95.5 / 95.1 | window 1.6 | 61 | 5.0 | PASS |
| 7 | VS06c-03 | `vena-lamp-cyl--leaf-wrap6-VS02-04__02_s07_b2.25in_h200mm_v01` | T1 window 0.85 mm | 66 x 66 x 190 (2.59 x 2.60 x 7.48) | 95.2 / 95.0 | window 1.5 | 67 | 5.2 | PASS |
| 8 | VS06c-04 | `vena-lamp-cyl--leaf-wrap8-VS02-04__02_s07_b2.25in_h200mm_v01` | T1 window 0.85 mm | 66 x 66 x 190 (2.59 x 2.59 x 7.48) | 95.1 / 95.1 | window 1.5 | 70 | 5.3 | PASS |
| 9 | VS06a-05 | `vena-lamp-cyl--hybrid-VS04-07__01_s07_b2.25in_h200mm_v01` | T1 window 0.85 mm | 64 x 64 x 194 (2.52 x 2.51 x 7.62) | 96.0 / 96.1 | window 1.6 | 73 | 5.5 | PASS |
| 10 | VS06a-01 | `vena-lamp-egg--cells-VS04-12__01_s23_b2.00in_h190mm_v01` | T1 window 0.85 mm | 96 x 96 x 183 (3.79 x 3.79 x 7.20) | 79.8 / 79.8 | window 5.7 | 91 | 6.2 | PASS |
| 11 | VS06b-09 | `vena-lamp-egg--wing-wrap1-VS03-04__02_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 103 x 101 x 199 (4.07 x 3.98 x 7.83) | 76.4 / 77.4 | window 1.5 | 87 | 6.2 | PASS |
| 12 | VS06a-04 | `vena-lamp-egg--closed-VS04-01__01_s07_b2.00in_h190mm_v01` | T1 window 0.85 mm | 96 x 96 x 184 (3.79 x 3.77 x 7.24) | 79.9 / 80.1 | window 1.6 | 94 | 6.3 | PASS |
| 13 | VS06c-08 | `vena-lamp-cyl--cells-wide-VS04-12__01_s23_b2.25in_h175mm_v01` | T1 window 0.85 mm | 101 x 101 x 170 (3.99 x 3.99 x 6.71) | 77.4 / 77.4 | window 3.6 | 102 | 6.5 | PASS |
| 14 | VS06b-10 | `vena-lamp-egg--leaf-wrap3-VS02-04__01_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 103 x 104 x 199 (4.05 x 4.08 x 7.83) | 76.5 / 76.2 | window 1.5 | 97 | 6.6 | PASS |
| 15 | VS06a-03 | `vena-lamp-egg--cells-VS04-12__03_s23_b2.00in_h190mm_v01` | T1 window 0.85 mm | 96 x 96 x 183 (3.78 x 3.78 x 7.21) | 80.0 / 80.0 | window 2.9 | 105 | 6.8 | PASS |
| 16 | VS06c-09 | `vena-lamp-egg--cells-winopen-VS04-12__02_s23_b2.00in_h190mm_v01` | T1 below, open above | 97 x 97 x 183 (3.80 x 3.80 x 7.20) | 79.7 / 79.7 | window 4.2, hole 4.8 | 106 | 6.8 | PASS |
| 17 | VS06b-01 | `vena-lamp-egg--wing-wrap1-VS03-04__01_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 103 x 101 x 199 (4.07 x 3.99 x 7.83) | 76.4 / 77.4 | window 1.5 | 110 | 7.2 | PASS |
| 18 | VS06a-07 | `vena-lamp-egg--cells-VS04-12__04_s23_b2.00in_h190mm_v01` | T2 open, graded | 98 x 98 x 182 (3.84 x 3.84 x 7.15) | 79.2 / 79.2 | hole 2.2 | 117 | 7.3 | PASS |
| 19 | VS06c-01 | `vena-lamp-egg--wing-wrap6-VS03-04__02_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 105 x 103 x 178 (4.12 x 4.06 x 7.02) | 75.7 / 76.5 | window 1.5 | 117 | 7.3 | PASS |
| 20 | VS06b-02 | `vena-lamp-egg--wing-wrap3-VS03-04__01_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 103 x 104 x 199 (4.06 x 4.10 x 7.83) | 76.4 / 76.0 | window 1.5 | 116 | 7.5 | PASS |
| 21 | VS06c-02 | `vena-lamp-egg--wing-wrap8-VS03-04__02_s07_b2.00in_h200mm_v01` | T1 window 0.85 mm | 105 x 105 x 178 (4.12 x 4.12 x 7.02) | 75.6 / 75.6 | window 1.5 | 122 | 7.5 | PASS |
| 22 | VS06c-07 | `vena-lamp-egg--wing-wrap3-winopen-VS03-04__01_s07_b2.00in_h200mm_v01` | T1 below, open above | 103 x 104 x 199 (4.06 x 4.10 x 7.83) | 76.4 / 76.0 | window 2.0, hole 2.0 | 121 | 7.7 | PASS |
| 23 | VS06a-11 | `vena-lamp-free--closed-tilt-VS04-01__01_s11_b2.25in_h215mm_v01` | T1 window 0.85 mm | 119 x 119 x 209 (4.69 x 4.69 x 8.24) | 68.4 / 68.4 | window 1.5 | 121 | 7.8 | PASS |
| 24 | VS06a-12 | `vena-lamp-free--hybrid-fine-VS04-12__01_s05_b2.00in_h228mm_v01` | T1 window 0.85 mm | 101 x 102 x 221 (3.99 x 4.01 x 8.71) | 77.3 / 77.1 | window 1.5 | 133 | 8.5 | PASS |
| 25 | VS06c-06 | `vena-lamp-free--hybrid-fine-winopen-VS04-12__01_s05_b2.00in_h228mm_v01` | T1 below, open above | 102 x 102 x 221 (3.99 x 4.01 x 8.69) | 77.3 / 77.0 | window 2.0, hole 2.0 | 140 | 8.8 | PASS |
| 26 | VS06a-10 | `vena-lamp-cyl--cells-VS04-12__02_s23_b6.00in_h200mm_v01` | T1 window 0.85 mm | 158 x 158 x 193 (6.24 x 6.24 x 7.59) | 48.8 / 48.8 | window 4.6 | 173 | 10.0 | PASS |
| 27 | VS06a-09 | `vena-lamp-egg--closed-VS04-01__02_s07_b6.00in_h220mm_v01` | T1 window 0.85 mm | 177 x 178 x 212 (6.97 x 6.99 x 8.36) | 39.4 / 39.2 | window 1.5 | 187 | 10.9 | PASS |

Set total: 27 parts, 2647 g estimated (about $87.35 at $0.033 per gram), 176.1 h of printing, about 88.0 h wall clock on 2 printers.

## The test piece
`vena-lamp-test--windows-VS06a-01__01`: a 60 x 40 mm curved patch of the VS06a-01 pattern, standing on a 7 mm foot. Three bands of windows side by side: 0.45 mm, 0.65 mm, 0.85 mm, marked 45, 65, 85 under the foot. Print it in the filament meant for the lamps, hold it against the light, and pick the thinnest band that is closed everywhere and does not string. Every lamp here is built at 0.85 mm; a thinner window means a rebuild.

## Which pieces are fine work
All of them. The lab recommends 2 mm walls; these go under it on purpose:
- T1 window: skin 0.85 mm, ribs from 1.2 mm wide (2.0 mm deep plus relief).
- T2 open, graded (VS06a-07, VS06a-08): veins taper to 1.6 mm and holes to 2.0 mm above mid height.
- T1 below, open above (VS06c-06, 07, 09): ribs from 1.6 mm, holes from 2.0 mm, windows 0.85 mm in the lowest third.

## What was checked, and what was not
Checked on every mesh in this folder, after the label cut and after an STL reload: watertight, one shell, no non-manifold edges, footprint inside 203 x 203 mm, height under 256 mm, no down-facing strip wider than 1.0 mm (faces over 45.5 degrees, above the first 0.75 mm). Window thickness, least window and least hole come from the pattern field of the build; two meshes were also measured by rays (least wall 0.81 and 0.84 mm).
Not checked: a slice. Whether a 0.85 mm skin prints as two clean lines, where the seam lands, stringing across windows and open cells, and how the rim tips come out are unknown until the test piece and VS06a-02 are printed. Under every rib the skin is thicker than 0.85 mm for 1 to 2 mm (a 42 degree chamfer, the price of no supports), so a window glows less evenly near its top edge than the renders show.

## Included, and left out
- All twelve pieces of VS06a.
- From VS06b the 1 and 3 panel wraps. The owner named the wing wraps (VS06b-01, 02, 09). The leaf wraps (VS06b-05, 06, 10) are included on a reading of his note, not on his word.
- From VS06c every piece that passes: the four oblique rims, the wide cylinder, and three with windows below and open cells above (VS06c-06, 07, 09).
- Gallery only, no print files: VS06b-03, 04, 07, 08, 11 (superseded by the oblique rim versions) and VS06c-05 (its saved STL was not watertight on reload; VS06c-09 is the same design rebuilt).

## Files per part
stem.stl, stem_plate.3mf (centred on the 256 mm bed), stem_bed.png (bed overlay with the 9 in and 8 in squares), stem_lit.png (lit from inside, a stand-in material), stem_render.png (matte), stem_check.json. `SLICE_NOTES_v01.md` has the slicer settings for the first two prints; `sliced\` is empty and waits for sliced files.
