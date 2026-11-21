"""render_v01.py : Blender background render of print STLs, white matte on dark, three-quarter view, foot visible.
usage: blender -b -P render_v01.py -- <out_dir> <view: tq|top> <stl> [<stl> ...]   (skips a PNG that exists). No em dashes."""
import bpy, sys, os, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; out, view, stls = a[0], a[1], a[2:]
os.makedirs(out, exist_ok=True)
import glob
stls = [q for p in stls for q in (sorted(glob.glob(os.path.join(p, '*_v01.stl'))) if os.path.isdir(p) else [p])]   # a folder stands for every *_v01.stl in it
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
try:
    sc.cycles.device = 'GPU'; pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for d in pr.devices: d.use = True
except Exception as e: print('gpu setup', e)
sc.render.resolution_x = 1000; sc.render.resolution_y = 1000; sc.render.film_transparent = False
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.012, 0.012, 0.014, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
mat = bpy.data.materials.new('matte'); mat.use_nodes = True; b = mat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.86, 0.86, 0.84, 1); b.inputs['Roughness'].default_value = 0.75
gm = bpy.data.materials.new('ground'); gm.use_nodes = True; g = gm.node_tree.nodes['Principled BSDF']; g.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1); g.inputs['Roughness'].default_value = 0.9
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
def light(name, loc, energy, size):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.size = size; o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
for p in stls:
    png = os.path.join(out, os.path.splitext(os.path.basename(p))[0] + ('_render.png' if view == 'tq' else '_top.png'))
    if os.path.exists(png): print('exists', png); continue
    bpy.ops.wm.stl_import(filepath=p); o = bpy.context.selected_objects[0]; o.data.materials.append(mat)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    ctr = (mn + mx) / 2; o.location -= Vector((ctr.x, ctr.y, mn.z)); size = max((mx - mn).x, (mx - mn).y, (mx - mn).z); h = (mx - mn).z
    bpy.ops.mesh.primitive_plane_add(size=size * 30, location=(0, 0, -0.01)); gp = bpy.context.object; gp.data.materials.append(gm)
    L = [light('key', (size * 1.6, -size * 1.4, h + size * 1.6), 30 * size * size, size), light('fill', (-size * 2, -size * 0.6, h * 0.6 + size * 0.5), 7 * size * size, size * 1.5), light('rim', (0, size * 2, h + size), 14 * size * size, size)]
    cam_d.type = 'ORTHO'
    if view == 'tq':
        cam.location = Vector((size * 1.9, -size * 2.3, h * 0.5 + size * 1.25)); tgt = Vector((0, 0, h * 0.47)); cam_d.ortho_scale = max(h, (mx - mn).x, (mx - mn).y) * 1.32
    else:
        cam.location = Vector((0, 0, h + size * 3)); tgt = Vector((0, 0, 0)); cam_d.ortho_scale = max((mx - mn).x, (mx - mn).y) * 1.12
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = png; bpy.ops.render.render(write_still=True); print('rendered', png)
    for x in [o, gp] + L: bpy.data.objects.remove(x, do_unlink=True)
