"""count_photo_cells_v01.py : cells on one visible face of a Hyphae reference photo. A cell is a dark region of 6 px or more
(darker than its 9 px neighbourhood by 6 grey levels) inside the lamp silhouette; the mirror image under the lamp is cut off.
The far wall shows through the near one, so this is a count of dark openings seen from one side, not a survey.
usage: python count_photo_cells_v01.py <jpg> [...]    No em dashes."""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
for p in sys.argv[1:]:
    im = np.asarray(Image.open(p).convert('L'), float); im = im[:int(im.shape[0] * 0.84)]
    obj = ndi.binary_erosion(ndi.binary_fill_holes(ndi.binary_closing(im > 90, iterations=6)), iterations=3)
    lab, k = ndi.label(obj); obj = lab == (1 + int(np.argmax(ndi.sum(obj, lab, range(1, k + 1)))))
    dark = obj & (im < ndi.uniform_filter(im, 9) - 6) & (im < 170); l2, k2 = ndi.label(dark); s2 = ndi.sum(dark, l2, range(1, k2 + 1))
    print(os.path.basename(p),'cells on one face', int((s2 >= 6).sum()))
