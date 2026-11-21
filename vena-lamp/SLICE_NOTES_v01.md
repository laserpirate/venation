# Slice notes v01: the test piece and VS06a-02

For `vena-lamp-test--windows-VS06a-01__01_s23_b3.20in_h46mm_v01` and `vena-lamp-egg--cells-VS04-12__02_s23_b2.00in_h190mm_v01`. Slice both in SimplyPrint and save the sliced files into `sliced\`. Nothing else in this folder depends on them.

## Settings
- Profile: start from the Fab Lab profile `FabLab Default` in SimplyPrint (fine-detail if the default leaves gaps in the windows).
- Layer height 0.20 mm. Nozzle 0.4 mm.
- Wall generator: Arachne, if the profile allows the change. Classic walls drop features under two line widths; Arachne varies the line width and keeps a 0.45 or 0.65 mm skin as one line.
- Seam: aligned or back. Random scatters blobs over the windows.
- Supports: off. Brim: only if the collar lifts on a first try.
- Infill does not matter: no wall here is thick enough to carry any.

## What to look for in the slice preview
- Every window is there, as one or two wall lines, in every layer. Scrub through the height of one cell on each band of the test piece.
- No gap where a window meets a rib. A missing line there is a slit in the print.
- On the test piece the 0.45 mm band is the one most likely to vanish. If it is missing with Arachne on, that thickness is out for this printer and profile; note it.
- On VS06a-02 look at the rim tips last: single tips under 1.2 mm wide may be dropped by the slicer. That changes the rim, not the lamp.
- Estimated time and filament from the slicer replace the mesh estimates in the README (101 g, 6.6 h for VS06a-02).
