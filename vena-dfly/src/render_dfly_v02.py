"""render_dfly_v02.py : three Blender views of a dragonfly STL: top and three-quarter (matte on dark), and a back-lit close-up of the
left wings (translucent stand-in over a light table). usage: blender -b -P render_dfly_v02.py -- <out_dir> <px> <stl> [...]. No em dashes."""
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; out, px, stls = a[0], int(a[1]), a[2:]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True; sc.cycles.volume_bounces = 6
try:
    sc.cycles.device = 'GPU'; pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for d in pr.devices: d.use = True
except Exception as e: print('gpu setup', e)
sc.render.resolution_x = px; sc.render.resolution_y = px
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.012, 0.012, 0.014, 1)
mat = bpy.data.materials.new('matte'); mat.use_nodes = True; b = mat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.86, 0.86, 0.84, 1); b.inputs['Roughness'].default_value = 0.75
gm = bpy.data.materials.new('ground'); gm.use_nodes = True; g = gm.node_tree.nodes['Principled BSDF']; g.inputs['Base Color'].default_value = (0.02, 0.02, 0.022, 1); g.inputs['Roughness'].default_value = 0.9
tm = bpy.data.materials.new('pla'); tm.use_nodes = True; nt = tm.node_tree; nt.nodes.clear(); om = nt.nodes.new('ShaderNodeOutputMaterial'); gl = nt.nodes.new('ShaderNodeBsdfGlass'); gl.inputs['Roughness'].default_value = 0.55; gl.inputs['IOR'].default_value = 1.2
vs = nt.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 1.7; vs.inputs['Anisotropy'].default_value = 0.3; va = nt.nodes.new('ShaderNodeVolumeAbsorption'); va.inputs['Density'].default_value = 0.4
ad = nt.nodes.new('ShaderNodeAddShader'); nt.links.new(vs.outputs[0], ad.inputs[0]); nt.links.new(va.outputs[0], ad.inputs[1]); nt.links.new(gl.outputs[0], om.inputs['Surface']); nt.links.new(ad.outputs[0], om.inputs['Volume'])
em = bpy.data.materials.new('table'); em.use_nodes = True; e = em.node_tree.nodes['Principled BSDF']; e.inputs['Emission Color'].default_value = (1.0, 0.9, 0.75, 1); e.inputs['Emission Strength'].default_value = 0.9
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam; cam_d.type = 'ORTHO'
def light(name, loc, energy, size):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.size = size; o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
for p in stls:
    stem = os.path.splitext(os.path.basename(p))[0]
    bpy.ops.wm.stl_import(filepath=p); o = bpy.context.selected_objects[0]
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    ctr = (mn + mx) / 2; o.location -= Vector((ctr.x, ctr.y, mn.z)); size = max((mx - mn).x, (mx - mn).y); h = (mx - mn).z
    bpy.ops.mesh.primitive_plane_add(size=size * 30, location=(0, 0, -0.01)); gp = bpy.context.object
    for view in ('top', 'tq', 'backlit'):
        png = os.path.join(out, stem + '_' + view + '.png')
        if os.path.exists(png): continue
        o.data.materials.clear(); gp.data.materials.clear(); L = []
        if view == 'backlit':
            o.data.materials.append(tm); gp.data.materials.append(em); cam.location = Vector((-size * 0.25, size * 0.27, h + size * 3)); cam.rotation_euler = (0, 0, 0); cam_d.ortho_scale = size * 0.56
        else:
            o.data.materials.append(mat); gp.data.materials.append(gm)
            L = [light('key', (size * 1.6, -size * 1.4, h + size * 1.6), 30 * size * size, size), light('fill', (-size * 2, -size * 0.6, h * 0.6 + size * 0.5), 7 * size * size, size * 1.5), light('rim', (0, size * 2, h + size), 14 * size * size, size)]
            if view == 'top': cam.location = Vector((0, 0, h + size * 3)); cam.rotation_euler = (0, 0, 0); cam_d.ortho_scale = size * 1.12
            else:
                cam.location = Vector((-size * 1.5, -size * 1.9, size * 1.25)); cam.rotation_euler = (Vector((0, 0, h * 0.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam_d.ortho_scale = size * 1.15
        sc.render.filepath = png; bpy.ops.render.render(write_still=True); print('rendered', png)
        for x in L: bpy.data.objects.remove(x, do_unlink=True)
    for x in [o, gp]: bpy.data.objects.remove(x, do_unlink=True)
