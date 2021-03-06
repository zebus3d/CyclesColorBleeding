
import bpy, os

bl_info = {
    "name": "CyclesColorBleeding",
    "author": "Jorge Hernandez Melendez",
    "version": (0, 2),
    "blender": (2, 83, 0),
    "location": "",
    "description": "Manage your color bleeding in Cycles",
    "warning": "",
    "wiki_url": "",
    "category": "Cycles",
    }

from bpy.props import (FloatProperty, PointerProperty)
from bpy.types import (Panel, Operator, PropertyGroup)


def importNodeGroup(nodeGroup):
    # si no esta ya importado el node group lo importo:
    if not any(ng.name == "ColorBleeding" for ng in bpy.data.node_groups):
        blendFileMatLibs = "ColorBleeding.blend"
        path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        path = os.path.join(path, blendFileMatLibs, "NodeTree")
        bpy.ops.wm.append(filename=nodeGroup, directory=path)


class myProperties(PropertyGroup):
    ccb_brightness : bpy.props.FloatProperty(
        name="Brightness",
        soft_min=0.0,
        # soft_max=1.0,
        default=1.0,
        precision=3,
        description="")

    ccb_saturation : bpy.props.FloatProperty(
        name="Saturation",
        soft_min=0.0,
        # soft_max=1.0,
        default=1.0,
        precision=3,
        description="")
    
    ccb_factor : bpy.props.FloatProperty(
        name="Factor",
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        default=1.0,
        description="")


class CYCLES_PT_color_bleeding(Panel):
    bl_label = "Color Bleeding"
    bl_category = "Color Bleeding"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        ccb = scene.ccb

        layout.use_property_split = True
        layout.use_property_decorate = False

        flow = layout.grid_flow(align=True)
        col = flow.column()
        # col = layout.box()
        col.operator("ccb.append", text="Add ColorBleeding")
        layout.prop(ccb, "ccb_brightness", text="Brightness")
        layout.prop(ccb, "ccb_saturation", text="Saturation")
        layout.prop(ccb, "ccb_factor", text="Factor")
        col.operator("ccb.rm", text="Remove ColorBleeding")


class RemoveColorBleedingAppend(Operator):
    bl_idname = "ccb.rm"
    bl_label = "Remove Cycles Color Bleeding"
    bl_description = "Remove ColorBleeding node to selected objects"

    def execute(self, context):
        objects = bpy.context.selected_objects
        if len(objects):
            for ob in objects:
                if ob.type == 'MESH':
                    for mat in ob.material_slots:
                        if mat.name:
                            if mat.material.node_tree:
                                if 'ColorBleeding' in mat.material.node_tree.nodes:
                                    ColorBleeding = mat.material.node_tree.nodes['ColorBleeding']
                                    materialOutput = mat.material.node_tree.nodes['Material Output']
                                    mat_izquierda = ColorBleeding.inputs['Shader'].links[0].from_node
                                    # elimino el material ColorBleeding:
                                    mat.material.node_tree.nodes.remove(ColorBleeding)
                                    # los pongo en su sitio:
                                    materialOutput.location.x = materialOutput.location.x - 200
                                    # ahora los reconecto:
                                    matOIn = materialOutput.inputs['Surface']
                                    mat_izquierda_out = mat_izquierda.outputs[0]
                                    mat.material.node_tree.links.new(mat_izquierda_out, matOIn)
        else:
            self.report({'WARNING'}, 'Only can remove node from selected objects!')
        
        return {'FINISHED'}


class CyclesColorBleedingAppend(Operator):
    bl_idname = "ccb.append"
    bl_label = "Cycles Color Bleeding"
    bl_description = "Add ColorBleeding node to selected objects"

    def execute(self, context):        
        objects = bpy.context.selected_objects

        common_input_color_names = ['Base Color', 'Color']
        nodeGroup = "ColorBleeding"        
        
        if len(objects):
            importNodeGroup(nodeGroup)
            for ob in objects:
                if ob.type == 'MESH':
                    for mat in ob.material_slots:
                        if mat.name:
                            if mat.material.node_tree:
                                # creo el nodo de ColorBleeding para cada uno de los materiales 
                                # si no existe ya:
                                if 'ColorBleeding' not in mat.material.node_tree.nodes:
                                    ColorBleeding = mat.material.node_tree.nodes.new("ShaderNodeGroup")
                                    ColorBleeding.name = 'ColorBleeding'
                                    ColorBleeding.label = 'ColorBleeding'
                                    ColorBleeding.node_tree = bpy.data.node_groups['ColorBleeding']
                                    # mo = bpy.context.selected_objects[0].material_slots['Material'].material.node_tree.nodes['Material Output']
                                    # bpy.context.selected_objects[0].material_slots['Material'].material.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node
                                    materialOutput = mat.material.node_tree.nodes['Material Output']
                                    mat_izquierda = materialOutput.inputs['Surface'].links[0].from_node

                                    # mat_izquierda_socket = materialOutput.inputs['Surface'].links[0].from_socket.type
                                    # los pongo en su sitio:
                                    loc = materialOutput.location
                                    ColorBleeding.location = loc
                                    materialOutput.location.x = materialOutput.location.x + 200
                                    # ahora los conecto:
                                    ccb_in = ColorBleeding.inputs['Shader']
                                    ccb_out = ColorBleeding.outputs['Shader']
                                    matOIn = materialOutput.inputs['Surface']
                                    mat_izquierda_out = mat_izquierda.outputs[0]
                                    mat.material.node_tree.links.new(matOIn, ccb_out)
                                    mat.material.node_tree.links.new(ccb_in, mat_izquierda_out)

                                    for i in mat_izquierda.inputs:
                                        if i.name in common_input_color_names:
                                            if len(i.links):
                                                # print('conectado')
                                                # si tiene un color conectado se lo conecto:
                                                ccb_in = ColorBleeding.inputs['Color']
                                                mat_izquierda = mat_izquierda.inputs[i.name].links[0].from_node
                                                mat_izquierda_out = mat_izquierda.outputs[0]
                                                mat.material.node_tree.links.new(ccb_in, mat_izquierda_out)
                                            else:
                                                # print('desconectado')
                                                mat_izquierda = mat_izquierda.inputs[i.name]
                                                ccb_in = ColorBleeding.inputs['Color'].default_value = mat_izquierda.default_value


                                    # Creo los drivers:
                                    ########################
                                    # Driver Brightness:
                                    driver = ColorBleeding.inputs['Brightness'].driver_add("default_value").driver
                                    driver.variables.new()
                                    driver.variables[0].name = 'ccb_brightness'
                                    driver.variables[0].type= 'SINGLE_PROP'
                                    driver.variables['ccb_brightness'].targets[0].id_type = 'SCENE'
                                    driver.variables['ccb_brightness'].targets[0].id = bpy.data.scenes['Scene']
                                    driver.variables['ccb_brightness'].targets[0].data_path = 'ccb.ccb_brightness'
                                    driver.expression = "ccb_brightness"
                                    # Driver Saturation:
                                    driver = ColorBleeding.inputs['Saturation'].driver_add("default_value").driver
                                    driver.variables.new()
                                    driver.variables[0].name = 'ccb_saturation'
                                    driver.variables[0].type= 'SINGLE_PROP'
                                    driver.variables['ccb_saturation'].targets[0].id_type = 'SCENE'
                                    driver.variables['ccb_saturation'].targets[0].id = bpy.data.scenes['Scene']
                                    driver.variables['ccb_saturation'].targets[0].data_path = 'ccb.ccb_saturation'
                                    driver.expression = "ccb_saturation"
                                    # Driver Factor:
                                    driver = ColorBleeding.inputs['Factor'].driver_add("default_value").driver
                                    driver.variables.new()
                                    driver.variables[0].name = 'ccb_factor'
                                    driver.variables[0].type= 'SINGLE_PROP'
                                    driver.variables['ccb_factor'].targets[0].id_type = 'SCENE'
                                    driver.variables['ccb_factor'].targets[0].id = bpy.data.scenes['Scene']
                                    driver.variables['ccb_factor'].targets[0].data_path = 'ccb.ccb_factor'
                                    driver.expression = "ccb_factor"
        else:
            self.report({'WARNING'}, 'Only can add node to selected objects!')
        
        return {'FINISHED'}


all_classes = [
    myProperties,
    CyclesColorBleedingAppend,
    CYCLES_PT_color_bleeding,
    RemoveColorBleedingAppend
]

def register():
    from bpy.utils import register_class

    if len(all_classes) > 1:
        for cls in all_classes:
            register_class(cls)
    else:
        register_class(all_classes[0])
    
    bpy.types.Scene.ccb = bpy.props.PointerProperty(type=myProperties)

def unregister():
    from bpy.utils import unregister_class

    if len(all_classes) > 1:
        for cls in reversed(all_classes):
            unregister_class(cls)
    else:
        unregister_class(all_classes[0])
    
    del bpy.types.Scene.ccb


if __name__ == "__main__":
    register()