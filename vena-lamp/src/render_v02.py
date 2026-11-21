"""render_v02.py : Blender background render of lamp STLs lit from inside. Translucent PLA stand-in: a rough clear surface
over a scattering volume, so thin windows pass more light than ribs. Dark ground, three-quarter view.
usage: blender -b -P render_v02.py -- <out_dir> <px> <samples> <stl> [<stl> ...]   (skips a PNG that exists). No em dashes."""
import bpy, sys, os, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; out, px, smp, stls = a[0], int(a[1]), int(a[2]), a[3:]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc.render.engine = 'CYCLES'; sc.cycles.samples = smp; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 24; sc.cycles.transmission_bounces = 16; sc.cycles.volume_bounces = 8; sc.cycles.transparent_max_bounces = 16
try:
    sc.cycles.device = 'GPU'; pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for d in pr.devices: d.use = True
except Exception as e: print('gpu setup', e)
sc.render.resolution_x = px; sc.render.resolution_y = px; sc.view_settings.view_transform = 'Filmic'; sc.view_settings.look = 'Medium High Contrast'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.004, 0.005, 1)
mat = bpy.data.materials.new('pla'); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
om = nt.nodes.new('ShaderNodeOutputMaterial'); gl = nt.nodes.new('ShaderNodeBsdfGlass'); gl.inputs['Roughness'].default_value = 0.55; gl.inputs['IOR'].default_value = 1.2
gl.inputs['Color'].default_value = (1, 1, 1, 1)
vs = nt.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Color'].default_value = (0.96, 0.95, 0.92, 1); vs.inputs['Density'].default_value = 1.7; vs.inputs['Anisotropy'].default_value = 0.3
va = nt.nodes.new('ShaderNodeVolumeAbsorption'); va.inputs['Color'].default_value = (0.9, 0.86, 0.78, 1); va.inputs['Density'].default_value = 0.4
ad = nt.nodes.new('ShaderNodeAddShader'); nt.links.new(vs.outputs[0], ad.inputs[0]); nt.links.new(va.outputs[0], ad.inputs[1])
nt.links.new(gl.outputs[0], om.inputs['Surface']); nt.links.new(ad.outputs[0], om.inputs['Volume'])
gm = bpy.data.materials.new('ground'); gm.use_nodes = True; g = gm.node_tree.nodes['Principled BSDF']; g.inputs['Base Color'].default_value = (0.03, 0.03, 0.033, 1); g.inputs['Roughness'].default_value = 0.6
em = bpy.data.materials.new('lamp'); em.use_nodes = True; e = em.node_tree.nodes['Principled BSDF']; e.inputs['Emission Color'].default_value = (1.0, 0.86, 0.66, 1); e.inputs['Emission Strength'].default_value = 60.0
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam; cam_d.type = 'ORTHO'
for p in stls:
    png = os.path.join(out, os.path.splitext(os.path.basename(p))[0] + '_lit.png')
    if os.path.exists(png): print('exists', png); continue
    bpy.ops.wm.stl_import(filepath=p); o = bpy.context.selected_objects[0]; o.data.materials.append(mat)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    size = max((mx - mn).x, (mx - mn).y); h = (mx - mn).z
    bpy.ops.mesh.primitive_plane_add(size=size * 40, location=(0, 0, -0.02)); gp = bpy.context.object; gp.data.materials.append(gm)
    bpy.ops.mesh.primitive_cylinder_add(radius=min(9.0, size * 0.1), depth=h * 0.5, location=(0, 0, h * 0.32)); bulb = bpy.context.object; bulb.data.materials.append(em)
    d = bpy.data.lights.new('fill', 'AREA'); d.energy = 0.25 * size * size; d.size = size * 2; fl = bpy.data.objects.new('fill', d); sc.collection.objects.link(fl)
    fl.location = (size * 2, -size * 2.2, h + size); fl.rotation_euler = (Vector((0, 0, h / 2)) - fl.location).to_track_quat('-Z', 'Y').to_euler()
    m = max(h, size); cam.location = Vector((m * 1.9, -m * 2.3, h * 0.5 + m * 1.05)); tgt = Vector((0, 0, h * 0.47)); cam_d.ortho_scale = m * 1.28
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = png; bpy.ops.render.render(write_still=True); print('rendered', png)
    for x in [o, gp, bulb, fl]: bpy.data.objects.remove(x, do_unlink=True)
