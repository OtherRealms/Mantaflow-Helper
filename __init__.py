# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "MantaFlow Helper",
    "author" : "Pablo Tochez A. contact@pablotochez.com, Other Realms",
    "description" : "Provides controls for fluid baking",
    "blender" : (3, 6, 0),
    "version" : (0, 0, 3),
    "location" : "3D View -> N-Panel-> Mantaflow Helper",
    "warning" : "",
    "category" : "Interface"
}

import bpy
from bpy.props import*

class MFHELPER_PT_Panel(bpy.types.Panel):
    bl_label = "Mantaflow Helper"
    bl_idname = "MFHELPER_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "MantaflowHelper"
    

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.prop(scene, 'mf_domain')
        
    
        if scene.mf_domain != None:
            if scene.mf_domain.name not in scene.objects.keys():
                row = layout.row()
                row.alert = True
                row.label(text= "Domain Missing!",icon = "ERROR")
            else:
                row.operator("mantaflowhelper.select_domain" ,icon = 'RESTRICT_SELECT_OFF',text='')
        
            domain = scene.mf_domain.modifiers['Fluid'].domain_settings
            
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            col = flow
            col.prop(domain, 'resolution_max',text="Resolution Divisions")
            col.prop(domain,'cache_type')
            #col.separator()
            col.prop(domain, "cache_frame_start", text="Frame Start")
            col.prop(domain, "cache_frame_end", text="End")

            if domain.cache_type == "MODULAR":
                col = layout.column()
                col.separator()
                split = layout.split()
                bake_incomplete = (domain.cache_frame_pause_data < domain.cache_frame_end)
                
                if domain.has_cache_baked_data and not domain.is_cache_baking_data and bake_incomplete:
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Resume").mode = 0
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Free",icon = 'TRASH').mode = 1
                elif domain.is_cache_baking_data and not domain.has_cache_baked_data:
                    split.enabled = False
                    split.operator("mantaflowhelper.bake", text="Baking Data - ESC to pause").mode = 2
                elif not domain.has_cache_baked_data and not domain.is_cache_baking_data:
                    split.operator("mantaflowhelper.bake", text="Bake Data").mode = 0
                    split.operator("mantaflowhelper.bake", text="Free Data",icon = 'TRASH').mode = 1
                else:
                    col.operator("mantaflowhelper.bake", text="Free", icon = 'TRASH').mode = 1
            elif domain.cache_type == 'FINAL':
                col = layout.column()

                col.separator()
                split = layout.split()

                if domain.is_cache_baking_data and not domain.has_cache_baked_data:
                    split.enabled = False
                    split.operator("mantaflowhelper.bake", text="Baking All - ESC to pause").mode = 2
                elif not domain.has_cache_baked_data and not domain.is_cache_baking_data:
                    split.operator("mantaflowhelper.bake", text="Bake All").mode = 6
                else:
                    split.operator("mantaflowhelper.bake", text="Free All").mode = 7  
        elif context.active_object:
            layout.operator('mantaflowhelper.make_fluid')

        else:
            layout.label(text='No Active Object')
                            
class MFHELPER_PT_particles(bpy.types.Panel):
    bl_label = "Particles"
    bl_parent_id = 'MFHELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        ob = context.scene.mf_domain
        return ob != None and ob.modifiers['Fluid'].domain_settings.domain_type == 'LIQUID'

    def draw_header(self, context):
        scene = context.scene
        md = scene.mf_domain.modifiers['Fluid'].domain_settings

    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        domain = domain = scene.mf_domain.modifiers['Fluid'].domain_settings
        is_baking_any = domain.is_cache_baking_any
        has_baked_particles = domain.has_cache_baked_particles
        

        using_particles = domain.use_spray_particles or domain.use_foam_particles or domain.use_bubble_particles
        
        layout.use_property_decorate = False
        

        col = layout.column(align=False)
        col.use_property_split = True

        
        col.prop(domain, "sndparticle_combined_export")
        col = layout.column(align=False)
        col.enabled = not is_baking_any and not has_baked_particles
        
        col.use_property_split = False
        col.prop(domain, "particle_scale", text="Upres Factor")
        col.prop(domain, "sndparticle_potential_radius", text="Potential Radius")
        col.prop(domain, "sndparticle_update_radius", text="Particle Update Radius")
        col.prop(domain, "sndparticle_life_max", text="Particle Life Max")
        col.prop(domain, "sndparticle_life_min", text="Particle Life Min")
        col.prop(domain, "sndparticle_sampling_trappedair", text="Trapped Air Particle Sampling")
        col.prop(domain, "sndparticle_potential_max_trappedair", text="Trapped Air Potential Max")
        col.prop(domain, "sndparticle_potential_min_trappedair", text="Trapped Air Potential Min")
        col.separator()

        #col = layout.column(align=True)
        

        col.prop(domain, "use_spray_particles", text="Spray")

        if domain.use_spray_particles:
            col = layout.column(align=True)
            col.enabled = not is_baking_any and not has_baked_particles
            col.prop(domain, "sndparticle_potential_max_energy", text="Kinetic Energy Potential Maximum")
            col.prop(domain, "sndparticle_potential_min_energy", text="Minimum")
            col.separator()

        col.prop(domain, "use_foam_particles", text="Foam")

        if domain.use_foam_particles:
            col = layout.column(align=True)
            col.enabled = not is_baking_any and not has_baked_particles
            col.prop(domain, "sndparticle_potential_max_wavecrest", text="Wave Crest Potential Maximum")
            col.prop(domain, "sndparticle_potential_min_wavecrest", text="Minimum")
            col.prop(domain, "sndparticle_sampling_wavecrest", text="Wave Crest Particle Sampling")
            col.separator()

        col.prop(domain, "use_bubble_particles", text="Bubbles")

        if domain.use_bubble_particles:
            col = layout.column(align=True)
            col.enabled = not is_baking_any and not has_baked_particles
            
            col.prop(domain, "sndparticle_bubble_buoyancy", text="Bubble Buoyancy")
            col.prop(domain, "sndparticle_bubble_drag", text="Bubble Drag")
            col.separator()



        if domain.cache_type == 'MODULAR' and True in (domain.use_spray_particles,domain.use_foam_particles,domain.use_bubble_particles):
            col = layout.column()
            col.separator()

            # Deactivate bake operator if data has not been baked yet.
            note_flag = True
            if using_particles and not domain.has_cache_baked_data and domain.cache_type == 'MODULAR':
                note = layout.split()
                note_flag = False
                note.enabled = note_flag
                note.label(icon='INFO', text="Unbaked Data: Bake Data first.")

            else:
                split = layout.split()
                bake_incomplete = (domain.cache_frame_pause_particles < domain.cache_frame_end)
                if domain.has_cache_baked_particles and not domain.is_cache_baking_particles and bake_incomplete:
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Resume",icon = 'PARTICLES').mode =8
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Free",icon = 'PARTICLES').mode = 9
                elif not domain.has_cache_baked_particles and domain.is_cache_baking_particles:
                    split.enabled = False
                    split.operator("mantaflowhelper.bake", text="Baking Particles - ESC to pause",icon = 'PARTICLES').mode =2
                elif not domain.has_cache_baked_particles and not domain.is_cache_baking_particles:
                    split.operator("mantaflowhelper.bake", text="Bake Particles",icon = 'PARTICLES').mode =8
                else:
                    split.operator("mantaflowhelper.bake", text="Free Particles",icon = 'PARTICLES').mode =9

class MFHELPER_PT_noise(bpy.types.Panel):
    bl_label = "Use Noise"
    bl_parent_id = 'MFHELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        ob = context.scene.mf_domain
        return ob != None and ob.modifiers['Fluid'].domain_settings.domain_type == 'GAS'

    def draw_header(self, context):
        scene = context.scene
        md = scene.mf_domain.modifiers['Fluid'].domain_settings
        is_baking_any = md.is_cache_baking_any
        self.layout.enabled = not is_baking_any
        self.layout.prop(md, "use_noise", text="")
    
    def draw(self,context):
        layout = self.layout
        scene= context.scene
        domain = scene.mf_domain.modifiers['Fluid'].domain_settings

        split = layout.split()

        if domain.use_noise:
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            flow.enabled = not domain.is_cache_baking_any and not domain.has_cache_baked_data

            col = flow.column()
            col.prop(domain, "noise_scale", text="Upres Factor")
            col.prop(domain, "noise_strength", text="Strength")

            col = flow.column()
            col.prop(domain, "noise_pos_scale", text="Scale")
            col.prop(domain, "noise_time_anim", text="Time")

            if domain.cache_type == 'MODULAR':
                bake_incomplete = (domain.cache_frame_pause_noise < domain.cache_frame_end)
                
                if  not domain.has_cache_baked_data:
                    note = layout.split()
                    note_flag = False
                    note.enabled = note_flag
                    note.label(icon='INFO', text="Unbaked Data: Bake Data first.")

                elif domain.has_cache_baked_noise and not domain.is_cache_baking_noise and bake_incomplete :
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Resume Noise").mode = 3
                    col = split.column()
                    col.operator("mantaflowhelper.bake", text="Free Noise",icon = 'TRASH').mode = 4
                elif not domain.has_cache_baked_noise and domain.is_cache_baking_noise:
                    split.enabled = False
                    split.operator("mantaflowhelper.bake", text="Baking Data - ESC to pause").mode = 2
                else:
                    split = layout.split()

                    split.operator("mantaflowhelper.bake", text="Bake Noise").mode = 3

                    split.operator("mantaflowhelper.bake", text="Free Noise",icon = 'TRASH').mode = 4

class MFHELPER_PT_mesh(bpy.types.Panel):
    bl_label = "Mesh"
    bl_parent_id = 'MFHELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        ob = context.scene.mf_domain
        return ob != None and ob.modifiers['Fluid'].domain_settings.domain_type == 'LIQUID'

    def draw_header(self, context):
        scene = context.scene
        md = scene.mf_domain.modifiers['Fluid'].domain_settings
        is_baking_any = md.is_cache_baking_any
        self.layout.enabled = not is_baking_any
        self.layout.prop(md, "use_mesh", text="")

    def draw(self,context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        domain = scene.mf_domain.modifiers['Fluid'].domain_settings
        if domain.cache_type == 'MODULAR':

            # Deactivate bake operator if data has not been baked yet.
            note_flag = True
            if domain.use_mesh and not domain.has_cache_baked_data:
                note = layout.split()
                note_flag = False
                note.enabled = note_flag
                note.label(icon='INFO', text="Unbaked Data: Bake Data first.")

            split = layout.split()
            split.enabled = domain.has_cache_baked_data and note_flag

            bake_incomplete = (domain.cache_frame_pause_mesh < domain.cache_frame_end)
            if domain.has_cache_baked_mesh and not domain.is_cache_baking_mesh and bake_incomplete:
                col = split.column()
                col.operator("mantaflowhelper.bake", text="Resume").mode = 10
                col = split.column()
                col.operator("mantaflowhelper.bake", text="Free").mode = 11
            elif not domain.has_cache_baked_mesh and domain.is_cache_baking_mesh:
                split.enabled = False
                split.operator("mantaflowhelper.bake", text="Baking Mesh - ESC to pause").mode = 2
            elif not domain.has_cache_baked_mesh and not domain.is_cache_baking_mesh:
                split.operator("mantaflowhelper.bake", text="Bake Mesh",icon = 'MESH_ICOSPHERE').mode = 10
            else:
                split.operator("mantaflowhelper.bake", text="Free Mesh",icon = 'MESH_ICOSPHERE').mode = 11

class MFHELPER_OT_selectDomain(bpy.types.Operator):
    bl_idname = "mantaflowhelper.select_domain" 
    bl_label = "Select" 
    bl_description = "Select Domain" 

    @classmethod
    def poll(self,context):
        return context.scene.mf_domain
                
    def execute(self,context):
        for obj in context.selectable_objects:
            obj.select_set(state=False)
        scene = context.scene
        domain = scene.mf_domain
        domain.select_set(state=True)
        context.view_layer.objects.active = domain
        for area in context.window.screen.areas:
            if area.type == 'PROPERTIES':
                area.spaces[0].context = 'PHYSICS'

        return {'FINISHED'}

class MFHELPER_OT_bake(bpy.types.Operator):
    bl_idname = "mantaflowhelper.bake" 
    bl_label = "Bake"
    bl_description = "Bake" 

    mode: IntProperty()
    @classmethod
    def poll(self,context):
        return context.scene.mf_domain

    def execute(self,context):
        override = bpy.context.copy()
        override['active_object'] = context.scene.mf_domain
        override['object'] = context.scene.mf_domain
        override['selected_objects'] = [context.scene.mf_domain]

        with context.temp_override(**override):
            if self.mode ==0:
                bpy.ops.fluid.bake_data('INVOKE_DEFAULT')
            elif self.mode == 1:
                bpy.ops.fluid.free_data('INVOKE_DEFAULT')
            elif self.mode == 2:
                bpy.ops.fluid.pause_bake('INVOKE_DEFAULT')
            elif self.mode == 3:
                bpy.ops.fluid.bake_noise('INVOKE_DEFAULT')
            elif self.mode == 4:
                bpy.ops.fluid.free_noise('INVOKE_DEFAULT')
            elif self.mode == 5:
                bpy.ops.fluid.free_noise('INVOKE_DEFAULT')
            elif self.mode == 6:
                bpy.ops.fluid.bake_all('INVOKE_DEFAULT')
            elif self.mode == 7:
                bpy.ops.fluid.free_all('INVOKE_DEFAULT')
            elif self.mode == 8:
                bpy.ops.fluid.bake_particles('INVOKE_DEFAULT')
            elif self.mode == 9:
                bpy.ops.fluid.free_particles('INVOKE_DEFAULT')
            elif self.mode == 10:
                bpy.ops.fluid.bake_mesh('INVOKE_DEFAULT')
            elif self.mode == 11:
                bpy.ops.fluid.free_mesh('INVOKE_DEFAULT')


        return {'FINISHED'}

class MFHELPER_OT_make_fluid(bpy.types.Operator):
    bl_idname = "mantaflowhelper.make_fluid" 
    bl_label = "Make Domain"
    bl_description = "Assign fluid modifiers to active object" 

    mode: IntProperty()
    @classmethod
    def poll(self,context):
        return context.active_object

    def execute(self,context):
        ob = context.active_object
        for _mod in ob.modifiers:
            if _mod.type == 'FLUID':
                self.report({'WARNING'},"Fluid already exists")
                return {'FINISHED'}

        mod = ob.modifiers.new("Fluid",type='FLUID')
        mod.fluid_type = 'DOMAIN'
        context.scene.mf_domain = ob
        return {'FINISHED'}

def domain_callback(self,object):
    try:
        if object.name in bpy.context.scene.objects.keys() and object.modifiers['Fluid'].fluid_type == 'DOMAIN':
            return object
    except:
        return None

classes = (MFHELPER_OT_selectDomain,MFHELPER_OT_make_fluid, MFHELPER_OT_bake,
           MFHELPER_PT_Panel,  MFHELPER_PT_mesh, MFHELPER_PT_noise, MFHELPER_PT_particles, 
           )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.mf_domain = PointerProperty(name = 'Domain', type = bpy.types.Object, poll = domain_callback)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


    del bpy.types.Scene.mf_domain


