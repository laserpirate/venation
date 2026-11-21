# vena-studies, the pattern lab

- src/: every version of the page (v01, v02, v02b, v02c, v03, v04), wing_geom.js, the sheet, build, check and staging scripts, the specs of each sheet.
- contacts/: the study sheets VS02 to VS08 as PNG, each with a check file (caption asserts, captions as printed). contact_v02_0838.png is the first issue of VS02, before study IDs. VS06c has two issues; v02 states a failure found after v01.
- export_svg/: the vector and graph export of VS02-10.

Sheet check: every caption starts with its ID, sits inside its own tile, overlaps no other tile, does not overflow, and is 16 px IBM Plex Mono. The 16 VS02 tiles drawn by v02b, v02c, v03 and v04 are byte-equal to the ones v02 drew.
