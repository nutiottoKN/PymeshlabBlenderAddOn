bl_info={
    "name": "PyMeshLab Tools",
    "author": "Karle Nutonen",
    "version": (0,1,2),
    "blender": (4,2,1),
    "location": "",
    "description":"",
    "category":"User Interface"   
}

import bpy
import pymeshlab as ml
import os
import gc
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

class MySettings(PropertyGroup):
    
    show_stats: bpy.props.BoolProperty(
        name="Show Statistics",
        description="",
        default=False
    )

    targetperc:FloatProperty(
        name="Target Face Percentage",
        description="",
        default=0.5,
        min=0.01,
        max=1.0
    )
    
    qualitythr: bpy.props.FloatProperty(
        name="Quality Threshold",
        description="",
        default=1.0,
        min=0.0,
        max=1.0
    )

    preserve_normals:BoolProperty(
        name="Preserve Normals",
        description="",
        default=True
    )

    preserve_boundaries: bpy.props.BoolProperty(
        name="Preserve Boundaries",
        description="",
        default=True
    )
    boundaryweight:FloatProperty(
        name="Boundary Preserving Weight",
        description="",
        default=1.0,
        min=0.01,
        max=1.0
    )
    
    preserve_topology: bpy.props.BoolProperty(
        name="Preserve Topology",
        description="",
        default=False
    )


def process_with_pymeshlab(filter_function, export_path="/tmp/exported_model.dae", processed_path="/tmp/processed_model.dae"):
    # Leiame aktiivse valitud objekti

    refObjName = bpy.context.active_object.name
    refObjMaterial = bpy.context.active_object.data.materials[:]

    bpy.ops.wm.collada_export(filepath=export_path, selected=True)
    
    # Kasutame PyMeshLabi, et mudelit töödelda
    ms = ml.MeshSet()
    ms.load_new_mesh(export_path)
    
    # Rakendame edasi antud PyMeshLabi filtri
    filter_function(ms)
    
    # Salvestame töödeldud mudeli
    ms.save_current_mesh(processed_path)
    
    # Kustutame algse objekti
    bpy.ops.object.delete()

    # Importime töödeldud mudeli tagasi Blenderisse
    bpy.ops.wm.collada_import(filepath=processed_path)

    # Tagastame imporditud objekti
    importedObj = bpy.context.active_object

    importedObj.name = refObjName
    importedObj.rotation_euler = [0,0,0,]

    for mat in refObjMaterial:
        importedObj.data.materials.append(mat)

    bpy.ops.object.shade_auto_smooth()
    bpy.ops.object.modifier_apply(modifier="Smooth by Angle")


class FILTER_RDV(Operator):
    bl_idname = "object.filter_rdv"
    bl_label = "Remove duplicate vertices"
    

    def execute(self, context):

        if not context.view_layer.objects.selected:
            self.report({'ERROR'}, "No object selected. Please select an object.")
            return {'CANCELLED'}
        
        def remove_duplicate_vertices_filter(ms):
            ms.meshing_remove_duplicate_vertices()

        process_with_pymeshlab(remove_duplicate_vertices_filter)

        return {'FINISHED'}

class FILTER_MCV(Operator):
    bl_idname = "object.filter_mcv"
    bl_label = "Merge close verices"

    def execute(self, context):

        if not context.view_layer.objects.selected:
            self.report({'ERROR'}, "No object selected. Please select an object.")
            return {'CANCELLED'}
        
        def merge_close_vertices_filter(ms):
            ms.meshing_merge_close_vertices()

        process_with_pymeshlab(merge_close_vertices_filter)

        return {'FINISHED'}

class FILTER_QECD(Operator):
    bl_idname = "object.filter_qecd"
    bl_label = "Simplify Mesh with PyMeshLab (.dae)"
    

    def execute(self, context):
        mytool = context.scene.my_tool

        if not context.view_layer.objects.selected:
            self.report({'ERROR'}, "No object selected. Please select an object.")
            return {'CANCELLED'}
        
        def quadric_edge_collapse_decimation_filter(ms):
            ms.meshing_decimation_quadric_edge_collapse(
                targetperc=mytool.targetperc,
                qualitythr=mytool.qualitythr,
                preserveboundary=mytool.preserve_boundaries,
                boundaryweight=mytool.boundaryweight,
                preservenormal = mytool.preserve_normals

            )

        process_with_pymeshlab(quadric_edge_collapse_decimation_filter)

        return {'FINISHED'}

        
        


class PYMESHLAB_TOOLS_PANEL(Panel):
    bl_label = "PyMeshLab Tools"
    bl_idname = "OBJECT_PT_pymeshlab"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab" 

    

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        if context.view_layer.objects.selected:
            activeObjName = context.view_layer.objects.active.name
        else:
            activeObjName = "NONE"
        layout.label(text="Selected object: {}".format(activeObjName))
        
        layout.prop(mytool, "show_stats", text="Show Stats")

        if mytool.show_stats:
            bpy.context.space_data.overlay.show_stats = True
        else:
            bpy.context.space_data.overlay.show_stats = False
        layout.row()

class CLEANING_FILTERS(Panel):
    bl_label = "Cleaningfilters"
    bl_idname = "OBJECT_CLEAN_Filters"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab"
    #bl_parent_id = "OBJECT_PT_pymeshlab"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

class RDV(Panel):
    bl_label = "Remove duplicate vertices"
    bl_idname = "OBJECT_RDV_Filter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab"
    bl_parent_id = "OBJECT_CLEAN_Filters"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.row()
        layout.operator("object.filter_rdv", text="Run filter")
        layout.row()

class MCV(Panel):
    bl_label = "Merge Close Vertices"
    bl_idname = "OBJECT_MCV_Filter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab"
    bl_parent_id = "OBJECT_CLEAN_Filters"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.row()
        layout.operator("object.filter_mcv", text="Run filter")
        layout.row()

class SIMPLIFICATION_FILTERS(Panel):
    bl_label = "Simplification filters"
    bl_idname = "OBJECT_SIMPL_Filters"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab"
    #bl_parent_id = "OBJECT_PT_pymeshlab"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

class QECD(Panel):
    bl_label = "Qudaric Edge Collapse Deximation"
    bl_idname = "OBJECT_QECD_Filter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PyMeshLab"
    bl_parent_id = "OBJECT_SIMPL_Filters"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool
        
        layout.prop(mytool, "targetperc", text="Target Face Percentage")
        layout.prop(mytool, "qualitythr", text="Quality Threshold")
        layout.prop(mytool, "preserve_boundaries", text="Preserve Boundaries")
        layout.prop(mytool, "boundaryweight", text="Boundary Preserving Weight")
        layout.prop(mytool, "preserve_normals", text="Preserve Normals")
        layout.prop(mytool, "preserve_topology", text="Preserve Topology")
        layout.row()
        layout.operator("object.filter_qecd", text="Run filter")
        layout.row()




classes = (
    MySettings,
    PYMESHLAB_TOOLS_PANEL,
    CLEANING_FILTERS,
    RDV,
    FILTER_RDV,
    MCV,
    FILTER_MCV,
    SIMPLIFICATION_FILTERS,
    FILTER_QECD,
    QECD
)

# Registration and removal functions.
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()