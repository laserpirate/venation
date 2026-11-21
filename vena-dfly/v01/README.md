# Dragonfly with venation wings v01, print set (Phase P3)

The E1 Skillet Clubtail print body with its solid wing slabs replaced by venation wings. Bambu P2S, PLA, 0.20 mm layers. One part per plate, flat on the bed as modelled: belly, feet and wings down. No rotation on the plate was needed.

| part | file stem | L x W x H mm (in) | margin to bed edge mm | g est | h est | open cells per wing (fore, hind) | check |
|---|---|---|---|---|---|---|---|
| D1 | VS05-01_D1-hybrid-fab_clubtail-3x_s07_179mm_v01 | 168 x 179 x 24 (6.63 x 7.03 x 0.96) | 44 / 39 | 39 | 2.0 | 3, 3 | FAIL (body overhang 1894 mm2; new wings 0.0 mm2) |
| D2 | VS05-03_D2-cells-fab_clubtail-3x_s07_179mm_v01 | 168 x 179 x 24 (6.63 x 7.03 x 0.96) | 44 / 39 | 38 | 2.0 | 4, 10 | FAIL (body overhang 1894 mm2; new wings 0.0 mm2) |

Set total: 77 g estimated (about $2.54), 4.0 h, about 2.0 h wall clock on 2 printers. Estimates from the mesh, not sliced.

## Read this before printing
- Both parts FAIL the no-supports rule, and the cause is the body, not the wings. The E1 body has legs and rounded undersides that face down more than 45 degrees (about 2090 mm2 on the source at this scale). This build was told to leave the body unchanged apart from scale. The new wings add 0.0 mm2: they are flat prisms on the bed.
- The E1 file printed before with these legs; whether it needs supports here is a slicer and owner call. Nothing in this folder claims the body is support-free.
- The wings are mostly closed. Nine named ribs at 3 mm fill most of a 21 mm chord, so few cells clear the 3 mm rule (see the counts above).

## What was built
- Scale 3.0 on the insect; the source file is the insect at 2.9, so the factor on the source is 1.0345. Overall 168 mm long, span 179 mm (the prompt expected about 189; 63 mm x 3 ignores the sweep of the wings, and the source at 2.9 spans 172.2).
- Wings: membrane 2.0 mm, named fab ribs 3.0 wide and 2.5 tall on top of it, grown veins (D1 only) 2.0 wide and 1.5 tall, pterostigma solid at rib height, a 2.0 mm rim all round, 2.0 mm of membrane between open cells.
- The old slabs are cut away under z 4.1 inside the wing outlines; whatever stood on them (feet, gussets, the thorax floor) is put back as straight pads down to the bed, so the feet over the wings stay attached.
- No fillet under the wing roots: the wings lie on the bed, so there is no underside to fillet. The roots run under the thorax and fuse with it.
- Mirrored label 0.6 mm deep under the thorax.

## Print order
1. D2 (cells fab), then D1.
