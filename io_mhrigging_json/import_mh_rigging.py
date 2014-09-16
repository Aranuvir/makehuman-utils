import bpy
import json
from . shared_mh_rigging import *
   
def createArmatureFromJsonFile(filePath):       

    with open(filePath) as data_file:    
        armatureData = json.load(data_file)     
    
    basemesh = getMakeHumanObject()     
    if "version" in armatureData:
        if armatureData['version'] > 99 and basemesh != None:
            
            print("Rigging file version: {0}".format(armatureData['version']))
            
            joints = armatureData['joints']
            name = armatureData['name']
            jointCoordinates = {}
            bones = armatureData['bones']
            weights = armatureData['weights']        
        
            for group, weights in weights.items():                
                newGroup = basemesh.vertex_groups.new(group)
                for weightData in weights:
                    newGroup.add([weightData[0]], weightData[1], 'REPLACE')
            
            for joint, vertices in joints.items():                            
                jointCoordinates[joint] = vertsindexToCentroid(vertices)                
            
            bpy.ops.object.add(
                type='ARMATURE', 
                enter_editmode=True,
                location=(0,0,0))
            
            newArmature = bpy.context.object
            newArmature.name = name
            newArmature.show_name = True
            amt = newArmature.data
            amt.name = name+'Amt'            
                
            for boneKey, boneData in bones.items():
                    # Create single bone
                    newBone = amt.edit_bones.new('Bone')                    
                    headKey = boneData['head']
                    tailKey = boneData['tail']
                    rollAngle = boneData['roll']                    
                    
                    headCoords = jointCoordinates[headKey]
                    tailCoords = jointCoordinates[tailKey]            
                    
                    newBone.name = boneKey
                    newBone.head = headCoords
                    newBone.tail = tailCoords
                    newBone.roll = rollAngle
                    
            for boneName, boneData in bones.items():        
                parentName = boneData['parent']
                if parentName != None:                    
                    amt.edit_bones[boneName].parent = amt.edit_bones[parentName]     

            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Give basemesh object an armature modifier, using vertex groups but
            # not envelopes
            mod = basemesh.modifiers.new('MyRigModif', 'ARMATURE')
            mod.object = newArmature
            mod.use_bone_envelopes = False
            mod.use_vertex_groups = True  
            basemesh.parent = newArmature                  
            return newArmature
    else:
        return None


def readRiggingFile(context, filepath):
    if getMakeHumanObject() != None:
        createArmatureFromJsonFile(filepath)
    else:
        bpy.ops.box1.message('INVOKE_DEFAULT')
    return {'FINISHED'}


"""
BLENDER GUI
The following functions and classes are used to create the interface in Blender.
The script will create a new category tab in the Blender tools column
"""

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportMHRigging(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_rigging.data"  # important since its how bpy.ops.import_rigging.data is constructed
    bl_label = "Import MakeHuman Rigging"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        return readRiggingFile(context, self.filepath)


if __name__ == "__main__":
    register()


