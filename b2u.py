

bl_info = {
    "name" : "Blender to Unreal Engine",
    "blender" : (2, 80, 0),
    "category": "Import-Export"
}


import os

import bpy
from bpy.types import Operator


bpy.types.Scene.export_folder = bpy.props.StringProperty(name="Export folder", subtype="DIR_PATH", description="Directory to export the fbx files into.")


class BLENDER_TO_UNREAL_ENGINE_PT_Panel(bpy.types.Panel):
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "To Unreal Engine!"
    bl_category = "Export"

    def draw(self, context):
        
        layout = self.layout
        
        row = layout.row()
        row.label(text="Folder containing 'Props/' and 'Structures'")
        
        row = layout.row()
        col = row.column()
        col.prop(context.scene, "export_folder", text="")
        col = row.column()
        col.operator('object.bex_ot_openfolder', text='', icon="FILE_TICK")
        
        layout.label(text="Auto UV")
        row = layout.row()
        row.operator("b2ue.autouv")
        
        layout.label(text="Auto Lightmap")
        row = layout.row()
        row.operator("b2ue.autolightmap")
        
        layout.label(text="Export Structures")
        row = layout.row()
        row.operator("b2ue.structures")
        
        layout.label(text="Export Props")
        row = layout.row()
        row.operator("b2ue.props")



def export_function(context, is_prop=False):
    
    basedir = os.path.abspath(bpy.path.abspath(context.scene.export_folder)) + "/" + ("Props/" if is_prop else "Structures/")

    if not basedir:
        raise Exception("Blend file is not saved")

    view_layer = bpy.context.view_layer
    obj_active = view_layer.objects.active
    selection = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')

    for obj in selection:
        obj.select_set(True)
        
        # Move object to origin if its a prop
        original_location = obj.location.copy()
        if is_prop:
            bpy.ops.object.location_clear()
        
        bpy.ops.object.transform_apply(rotation=True, scale=True, location=False)
        
        view_layer.objects.active = obj
        name = bpy.path.clean_name(obj.name)
        fn = os.path.join(basedir, name) # the file path
        bpy.ops.export_scene.fbx(
            filepath=fn + ".fbx",
            use_selection=True,
            mesh_smooth_type='FACE',
            object_types={'MESH'},
            axis_forward='X',
        )
        obj.select_set(False)
        
        if is_prop:
            obj.location = original_location



    view_layer.objects.active = obj_active

    for obj in selection:
        obj.select_set(True)




class StructuresToUnrealEngine(bpy.types.Operator):

    bl_idname = "b2ue.structures"
    bl_label = "Export Structures"

    def execute(self, context):
        export_function(context, is_prop=False)
        return {'FINISHED'}


class PropsToUnrealEngine(bpy.types.Operator):

    bl_idname = "b2ue.props"
    bl_label = "Export Props"

    def execute(self, context):
        export_function(context, is_prop=True)
        return {'FINISHED'}


class BATEX_OT_OpenFolder(Operator):
    """
    Found from: https://github.com/jayanam/batex/blob/master/bex_folder_op.py
    """
  
    bl_idname = "object.bex_ot_openfolder"
    bl_label = "Open folder."
    bl_description = "Open the export folder" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=context.scene.export_folder)
        return {'FINISHED'}


class AutoUV(Operator):
    bl_idname = "b2ue.autouv"
    bl_label = "Auto UV"
    
    def execute(self, context):
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select_set(True)
            bpy.ops.object.editmode_toggle()
            
#            mesh = context.active_object.data
            mesh = obj.data
            if len(mesh.uv_layers) == 0: mesh.uv_layers.new()
            mesh.uv_layers.active_index = 0
            mesh.uv_layers.active.name = "UVMap"
            
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.uv.smart_project()
            
            bpy.ops.object.editmode_toggle()
            obj.select_set(False)
            
        for obj in selection:
            obj.select_set(True)
            
        return {'FINISHED'}
    

class AutoLightmap(Operator):
    bl_idname = "b2ue.autolightmap"
    bl_label = "Auto Lightmap"
    
    def execute(self, context):
        view_layer = bpy.context.view_layer
        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select_set(True)
            bpy.ops.object.editmode_toggle()
            
            mesh = obj.data
            if len(mesh.uv_layers) == 1: mesh.uv_layers.new()
            mesh.uv_layers.active_index = 1
            mesh.uv_layers.active.name = "Lightmap"
            
            bpy.ops.mesh.select_all(action='SELECT')
            
            bpy.ops.uv.lightmap_pack(
                PREF_IMG_PX_SIZE = 512,
                PREF_MARGIN_DIV = 0.35
            )
            
            bpy.ops.object.editmode_toggle()
            obj.select_set(False)
            
        for obj in selection:
            obj.select_set(True)
            
        return {'FINISHED'}


register_fn, unregister_fn = bpy.utils.register_classes_factory((BLENDER_TO_UNREAL_ENGINE_PT_Panel, AutoUV, AutoLightmap, StructuresToUnrealEngine, PropsToUnrealEngine, BATEX_OT_OpenFolder))


def register():
    register_fn()


def unregister():
    unregister_fn()
    
    
if __name__=='__main__':
    register()
