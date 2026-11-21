# Lamps v01, print set (Phase P2)

Bambu P2S, PLA, 0.4 mm nozzle, 0.20 mm layers, no supports. One part per plate. Every part prints foot down, open top up.
Grams and hours are estimates from the mesh (not sliced): grams = 1.24 g/cm3 x min(volume, area x 0.85 mm + 15 % of volume); hours = grams / 22 + layers x 8 s.

| tile | file stem | L x W x H mm (in) | margin to bed edge mm | g est | h est | holes | check |
|---|---|---|---|---|---|---|---|
| VS04-01 | `VS04-01_L1-closed_egg_s07_170mm_v01` | 88 x 88 x 168 (3.46 x 3.46 x 6.63) | 84 / 84 | 92 | 6.1 | 84 | PASS |
| VS04-02 | `VS04-02_L1-closed_egg_s23_170mm_v01` | 88 x 88 x 170 (3.46 x 3.46 x 6.68) | 84 / 84 | 90 | 6.0 | 86 | PASS |
| VS04-03 | `VS04-03_L2-closed_egg-6-ovate_s07_170mm_v01` | 90 x 89 x 170 (3.56 x 3.51 x 6.69) | 83 / 83 | 97 | 6.3 | 96 | PASS |
| VS04-04 | `VS04-04_L2-closed_egg-6-ovate_s23_170mm_v01` | 90 x 89 x 170 (3.56 x 3.51 x 6.69) | 83 / 83 | 98 | 6.3 | 69 | PASS |
| VS04-05 | `VS04-05_L3-cells-fab_egg-8-wings_s07_170mm_v01` | 90 x 90 x 170 (3.56 x 3.56 x 6.69) | 83 / 83 | 115 | 7.1 | 125 | PASS |
| VS04-06 | `VS04-06_L3-cells-fab_egg-8-wings_s23_170mm_v01` | 90 x 90 x 170 (3.56 x 3.56 x 6.69) | 83 / 83 | 115 | 7.1 | 134 | PASS |
| VS04-07 | `VS04-07_L4-hybrid_cylinder_s07_150mm_v01` | 103 x 103 x 150 (4.06 x 4.06 x 5.90) | 76 / 76 | 123 | 7.3 | 200 | PASS |
| VS04-08 | `VS04-08_L4-hybrid_cylinder_s23_150mm_v01` | 103 x 103 x 150 (4.06 x 4.06 x 5.90) | 76 / 76 | 122 | 7.2 | 204 | PASS |
| VS04-09 | `VS04-09_L5-open_mound_s07_160mm_v01` | 160 x 122 x 89 (6.30 x 4.81 x 3.51) | 48 / 67 | 103 | 5.7 | 139 | PASS |
| VS04-10 | `VS04-10_L5-open_mound_s23_160mm_v01` | 160 x 122 x 89 (6.30 x 4.81 x 3.51) | 48 / 67 | 104 | 5.7 | 136 | PASS |
| VS04-11 | `VS04-11_L6-cells_egg_s07_170mm_v01` | 85 x 85 x 170 (3.34 x 3.35 x 6.69) | 86 / 86 | 86 | 5.8 | 317 | PASS |
| VS04-12 | `VS04-12_L6-cells_egg_s23_170mm_v01` | 85 x 85 x 170 (3.34 x 3.35 x 6.69) | 86 / 86 | 85 | 5.8 | 313 | PASS |

Set total: 1230 g estimated (about $40.59 at $0.033 per gram), 76.4 h of printing, about 38.2 h wall clock on 2 printers.

## Files per part
stem.stl, stem_plate.3mf (part centred on the 256 mm bed), stem_bed.png (bed overlay with the 9 in and 8 in squares), stem_render.png, stem_check.json (every number above and the build statistics).

## Print order
1. VS04-11 (L6 control, lightest): it proves the hole roofs and the shell at 2.0 mm before anything else is printed.
2. VS04-01 (L1, the reference form).
3. One seed of each of L2, L3, L4, L5, in that order.
4. The second seeds.

## What the check means
- watertight, one shell, 0 non-manifold edges; footprint inside 203 x 203 mm; height under 256 mm.
- overhang: faces more than 45.5 degrees below horizontal, above the label (z over 0.75 mm). Each hole comes to a point at the top, and the mesh leaves a strip there; a part passes when the widest such strip is 1.0 mm or less. The total area and the largest patch are in the check file.
- walls by construction: shell 2.0 mm, veins 2.0 to 4.5 mm wide and 1.5 mm proud, cell walls 2.4 mm, at least 4.7 mm of shell across a vein between two holes; an opening test at 2.0 mm on the shell mask reports the share of thinner area (pass at 1 % or less).
- holes are cut only where a 3 mm circle fits; smaller cells stay closed. Hole roofs rise at 59 degrees or steeper. Hole edges carry a 0.8 mm chamfer inside and 0.4 mm outside.
- foot: solid ring 18 mm tall, clear hole 50 mm (L4: 80 mm, L5 follows the outline; the ring is 10 or 16 mm wide), cable notch 3 x 4 mm with a pointed top, mirrored label 0.6 mm deep on the underside.

Not checked here: a real slice. Run the lab profile in the print queue and read the first layers of VS04-11 before committing the set.
