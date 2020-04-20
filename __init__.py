
import bpy


bl_info = {
    "name": "CyclesColorBleeding",
    "author": "Jorge Hernandez Melendez",
    "version": (0, 1),
    "blender": (2, 83, 0),
    "location": "",
    "description": "Manage your color bleeding in Cycles",
    "warning": "",
    "wiki_url": "",
    "category": "Cycles",
    }


def importNodeGroup(nodeGroup):
    # si no esta ya importado el node group lo importo:
    if not any(ng.name == "ColorBleeding" for ng in bpy.data.node_groups):
        blendFileMatLibs = "ColorBleeding.blend" 
        path = bpy.utils.user_resource('SCRIPTS', "addons")
        path = path + "/CyclesColorBleeding/" + blendFileMatLibs + "/NodeTree/"
        bpy.ops.wm.append(filename=nodeGroup, directory=path)


class CYCLES_PT_color_bleeding(bpy.types.Panel):
    bl_label = "Color Bleeding"
    bl_category = "Color Bleeding"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene
        flow = layout.grid_flow(align=True)
        col = flow.column()
        col = layout.box()
        col.operator("ccb.append", text="Add Nodes")


class CyclesColorBleedingAppend(bpy.types.Operator):
    bl_idname = "ccb.append"
    bl_label = "Cycles Color Bleeding Append"
    bl_description = ""

    def execute(self, context):

        common_input_color_names = ['Base Color', 'Color']
        nodeGroup = "ColorBleeding"
        importNodeGroup(nodeGroup)

        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                for mat in ob.material_slots:
                    if mat.name:
                        if mat.material.node_tree:
                            # creo el nodo de ColorBleeding para cada uno de los materiales 
                            # si no existe previamente:
                            if not any(n.name == "ColorBleeding" for n in mat.material.node_tree.nodes):
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

        return {'FINISHED'}


all_classes = [
    CyclesColorBleedingAppend,
    CYCLES_PT_color_bleeding
]

def register():
    from bpy.utils import register_class

    if len(all_classes) > 1:
        for cls in all_classes:
            register_class(cls)
    else:
        register_class(all_classes[0])

def unregister():
    from bpy.utils import unregister_class

    if len(all_classes) > 1:
        for cls in reversed(all_classes):
            unregister_class(cls)
    else:
        unregister_class(all_classes[0])


if __name__ == "__main__":
    register()