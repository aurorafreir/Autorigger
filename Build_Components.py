"""
This script houses each of the rig components' build scripts, to get called by each rig's build scripts
"""

# Standard library imports

# Third party imports
from maya import cmds

# Local application imports



"""
TODO UPDATES
- Check all variable names to be consistent with all_lower_case var names
- Swap out all short flag names for more readable long flag names
- Swap out `var + "" + var` for "{}{}".format(var, var)
"""


class BuildComponents(object):
    """
    This class has functions for each of the body parts required for most rigs, to be called by
        each character's specific build script
    """
    def __init__(self, char_name):
        # Set up char_name as a class-wide variable to be used in the class' functions
        self.char_name = char_name
        self.enum_kwargs = {
            "exists":True,
            "hidden":False,
            "keyable":True,
            "attributeType": "enum",
        }


    def lerp(self, min,
             max, percent): #linear_interpolate
        # Return float between min and max based on the percent (0-1)
        return ((max - min) * percent) + min


    def vector_lerp(self, min,
                    max, percent): #vector_linear_interpolate
        # Get a 3 axis point between min (x,y,z) and max (x,y,z) based on the percent (0-1), and return (x,y,z)
        x = self.lerp(min[0], max[0], percent)
        y = self.lerp(min[1], max[1], percent)
        z = self.lerp(min[2], max[2], percent)

        return x, y, z


    def create_follicle(self, nurbssurf,
                        uPos=0.0, vPos=0.0):
        # Create a follicle object, and attach it to the NURBS surface (nurbssurf)
        follicle = cmds.createNode('follicle')

        follicle_parent = cmds.listRelatives(follicle, parent=True)[0]
        cmds.connectAttr("{}.local".format(nurbssurf), "{}.inputSurface".format(follicle))
        cmds.connectAttr("{}.worldMatrix[0]".format(nurbssurf), "{}.inputWorldMatrix".format(follicle))
        for name, n in zip(["Rotate", "Translate"], ["r", "t"]):
            cmds.connectAttr("{}.out{}".format(follicle, name), "{}.{}".format(follicle_parent, n))
        for uv, pos in zip(["U", "V"], [uPos, vPos]):
            cmds.setAttr("{}.parameter{}".format(follicle, uv), pos)
        for tr in ["t", "r"]:
            cmds.setAttr("{}.{}".format(follicle_parent, tr), lock=True)

        return follicle


    def lockhideattr(self, obj="",
                     hide=True, lock=True,
                     translate=True, rotate=True,
                     scale=True, visibility=True):
        if not translate and not rotate and not scale and not visibility:
            raise Exception("lockhideattr function for {} not set to do anything!".format(obj))

        attrs = []
        if translate:
            attrs.append("translate")
        if rotate:
            attrs.append("rotate")
        if scale:
            attrs.append("scale")

        kwargs = {

        }

        if hide:
            kwargs.append("keyable":0)
            kwargs.append("channelBox":0)
        if lock:
            kwargs.append("lock":1)

        for attr in attrs:
            for xyz in ["X", "Y", "Z"]:
                cmds.setAttr("{}.{}{}".format(obj, attr, xyz), **kwargs)
        if visibility:
            cmds.setAttr("{}.visibility".format(obj), **kwargs)


    def controllers_setup(self, part_name,
                          shape="circle", scale=(1,1,1),
                          rotation=(0,0,0), position=(0,0,0),
                          colour=""):
        # To be used by other parts of this script for creating a variety of controllers
        # Create empty group
        newgroup = cmds.group(name="{}_GRP".format(part_name), empty=True)
        shapename = "{}_CTRL".format(part_name)

        if shape in "circle":
            # Create circle NURBS curve
            newshape = cmds.circle(name=shapename, constructionHistory=False)
            newshape = newshape[0] # Make sure that newshape is only a single string instead of [objectname,  shapename]

        elif shape in "square":
            # Create square NURBS curve
            newshape = cmds.curve(degree=1, 
                                    point=[(-.5, .5, 0), (.5, .5, 0), (.5, -.5, 0), (-.5, -.5, 0), (-.5, .5, 0)],
                                    name=shapename)

        elif shape in "cube":
            # Create cube NURBS curve
            newshape = cmds.curve(degree=1,
                                    point=[(-0.5, -0.5, .5), (-0.5, .5, .5), (.5, .5, .5), (.5, -0.5, .5), (.5, -0.5, -0.5), (.5, .5, -0.5),
                                     (-0.5, .5, -0.5), (-0.5, -0.5, -0.5), (.5, -0.5, -0.5), (.5, .5, -0.5), (.5, .5, .5),
                                     (-0.5, .5, .5), (-0.5, .5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, .5), (.5, -0.5, .5)],
                                    name=shapename)

        elif shape in "pointedsquare":
            newshape = cmds.curve(degree=1,
                                    point=[(0,0,0), (1,1,0), (2,1,0), (2,2,0), (1,2,0), (1,1,0)],
                                    name=shapename)

        elif shape in "starcircle":
            newshape = cmds.circle(name=shapename, constructionHistory=False)
            newshape = newshape[0]
            cmds.select(deselect=True)
            for x in range(0, 7)[::2]:
                cmds.select('{}.cv[{}]'.format(newshape, x), toggle=False, add=True)
            cmds.selectMode(component=True)
            cmds.xform(scale=(.4, .4, .4))
            cmds.selectMode(object=True)
            cmds.bakePartialHistory(newshape)


        elif shape in "scapctrl":
            newshape = cmds.curve(degree=1,
                                    point=[(0,0,-2), (1,1,-2), (1,2,0), (1,1,2), (0,0,2),
                                     (-1,1,2), (-1,2,0), (-1,1,-2), (0,0,-2)],
                                    name=shapename)
        else:
            raise ValueError("Shape {} not recognised".format(shape))


        # Scale, rotate, and transform new NURBS object
        cmds.xform(newshape, scale=scale, rotation=rotation, translate=position)

        # Freeze transforms and bake control history
        cmds.makeIdentity(newshape, applyTrue)
        cmds.bakePartialHistory(newshape)


        # Set controller colour
        shapeshape = cmds.listRelatives(newshape, shapes=True, children=True)[0]
        cmds.setAttr("{}.overrideEnabled".format(shapeshape), True)
        if not colour:
            pass
        elif colour in "blue":
            cmds.setAttr("{}.overrideColor".format(shapeshape), 18)
        elif colour in "yellow":
            cmds.setAttr("{}.overrideColor".format(shapeshape), 22)

        # Parent the new NURBS object to the created group
        cmds.parent(newshape, newgroup)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselect=True)

        # Pass back out the name of the controller's group and controller itself
        return newgroup, newshape


    def twopointnurbpatch(self, part_name="",
                          startjnt="", endjnt=""):
        # Get start and end jnt's position and rotation
        start_pos = cmds.xform(startjnt, query=True, translate=True, worldSpace=True)
        start_rot = cmds.xform(startjnt, query=True, rotation=True,  worldSpace=True)
        end_pos =   cmds.xform(endjnt,   query=True, translate=True, worldSpace=True)

        mid_pos = self.vector_lerp(start_pos, end_pos, .5)

        for locator in ["Start", "Mid", "End"]:
            # For each item in list, create a locator and joint, and parent the joint to the locator
            newloc = cmds.spaceLocator(name="{}_{}_LOC".format(part_name, locator))
            cmds.joint(name="{}_{}_JNT".format(part_name, locator))
            cmds.parent(newloc, "{}_RIGJOINTS".format(part_name))

        startloc = "{}_Start_LOC".format(part_name)
        midloc = "{}_Mid_LOC".format(part_name)
        endloc = "{}_End_LOC".format(part_name)

        cmds.xform(startloc, translate=start_pos, rotation=start_rot, worldSpace=True)
        cmds.xform(midloc,   translate=mid_pos,   rotation=start_rot, worldSpace=True)
        cmds.xform(endloc,   translate=end_pos,   rotation=start_rot, worldSpace=True)

        # Set joint orient for the start joint using a temporary joint placed at the end object location
        tempjnt = cmds.joint(name="temp_JNT")
        cmds.xform(tempjnt, translate=end_pos, worldSpace=True)
        cmds.parent(tempjnt, "{}_Start_JNT".format(part_name))
        cmds.joint("{}_Start_JNT".format(part_name), edit=True, orientJoint="xyz")
        cmds.delete(tempjnt)

        # Copy joint orient from start joint and apply to all subsequent joints
        for joint in ["Mid", "End"]:
            cmds.joint("{}_{}_JNT".format(part_name, joint), edit=True, orientation=(cmds.joint("{}_Start_JNT".format(part_name), query=True, orientation=True)))

        # Create curve based on joint positions, then duplicate first joint and parent curve to joint
        for i, trans in zip(["A", "B"], [(0, 1, 0), (0, -1, 0)]):
            newcrv = cmds.curve(name="{}_{}_CrvTemp".format(part_name, i), degree=1,
                                point=[start_pos,
                                   self.vector_lerp(start_pos, end_pos, .25),
                                   self.vector_lerp(start_pos, end_pos, .50),
                                   self.vector_lerp(start_pos, end_pos, .75),
                                   end_pos])
            newjnt = cmds.duplicate("{}_Start_JNT".format(part_name), name="{}_{}_JNT".format(part_name, i))
            cmds.parent(newcrv, newjnt)
            cmds.parent(newjnt, world=True)
            # Move both joints 1 unit away from each other in +y and -y
            cmds.xform(newjnt[0], translate=trans, relative=True, objectSpace=True)

        # Loft the two curves to create a NURBS surface
        nrbpatch = cmds.loft("{}_A_CrvTemp".format(part_name), "{}_B_CrvTemp".format(part_name), name="{}_NRB".format(part_name))
        nrbpatch = cmds.bakePartialHistory(nrbpatch)

        # Rebuild the surface to be smooth rather than faceted
        cmds.rebuildSurface(nrbpatch, replaceOriginal=True)

        # Delete two temporary curves, as they aren't needed any more
        for i in ["A", "B"]:
            cmds.delete("{}_{}_JNT".format(part_name, i))

        return nrbpatch, (startloc, midloc, endloc)


    def jointbasednurbpatch(self, part_name="",
                            startjnt="", endjnt="",
                            maxjntcount=21, reverse=False):
        # Create list for all the joints between startjnt and endjnt
        rbnjnts = [endjnt]
        # Start at endjnt, go upwards until you hit startjnt, adding each joint to the Spinejnts list
        # Max out at (maxjntcount) passes through this array, in which case throw an error
        for joint in range(0, maxjntcount):
            if 1 < joint < (maxjntcount-1):
                rbnjnts.append(tempjnt[0])
                tempjnt = cmds.listRelatives(tempjnt, parent=True)
                if tempjnt[0] == startjnt:
                    break
            elif joint == maxjntcount-1:
                raise Exception("Could not find {} during this loop, check that it is correctly named".format(startjnt))
            elif joint == 0:
                tempjnt = cmds.listRelatives(endjnt, parent=True)

        rbnjnts.append(startjnt)

        # Reverse rbnjnts, as the list will be created in reverse order, starting at endjnt and ending at startjnt
        rbnjnts.reverse()

        rbnjntscount = len(rbnjnts)

        # Append each joints' positions to rbnjntspos
        rbnjntspos = []
        for joint in rbnjnts:
            rbnjntspos.append(cmds.xform(joint, query=True, translate=True, worldSpace=True))

        for i, trans in zip(["A", "B"], [(0, 1, 0), (0, -1, 0)]):
            newcrv = cmds.curve(name="{}_{}_CrvTemp".format(part_name, i), degree=1, p=rbnjntspos)
            cmds.select(deselect=True)
            newjnt = cmds.duplicate("{}_1_JNT".format(part_name), name="{}_{}_JNT".format(part_name, i), parentOnly=True)
            cmds.parent(newcrv, newjnt)
            cmds.parent(newjnt, world=True)
            # Move both joints 1 unit away from each other in +y and -y
            cmds.xform(newjnt, translate=trans, relative=True, objectSpace=True)

        # Loft the two curves to create a NURBS surface
        nrbpatch = cmds.loft("{}_A_CrvTemp".format(part_name), "{}_B_CrvTemp".format(part_name), name="{}_NRB".format(part_name)
        nrbpatch = cmds.bakePartialHistory(nrbpatch)

        # Delete two temporary curves, as they aren't needed any more
        for crv in ["A", "B"]:
            cmds.delete("{}_{}_JNT".format(part_name, crv))

        return nrbpatch, rbnjntscount


    def ribbon_setup(self, part_name="",
                     startjnt="", endjnt="",
                     bindjointcount=5, method="twoloc",
                     skin=True, reverse=False):
        # To be used by other parts of this script or externally for creating ribbon rigs
        # Create a group for the current ribbon setup, and make some child groups for it
        rbngrp = cmds.group(n="{}_RBN_Rig".format(part_name), empty=True)
        for group in ["FOLLICLES", "RIGJOINTS"]:
            cmds.group(name="{}_{}".format(part_name, group), parent="{}_RBN_Rig".format(part_name), empty=True)
        if method == "twoloc":
            nrbpatch = self.twopointnurbpatch(part_name=part_name,
                                              startjnt=startjnt, endjnt=endjnt)
        elif method == "jointbased":
            nrbpatch = self.jointbasednurbpatch(part_name=part_name,
                                                startjnt=startjnt, endjnt=endjnt,
                                                reverse=reverse)
            bindjointcount = nrbpatch[1]

        cmds.parent(nrbpatch[0], "{}_RBN_Rig".format(part_name))

        rbnjoints = []

        # Create a specific number of follicles on the new NURBS surface based on bindjointcount
        foll_cur_name = 0
        flcgrp = part_name + "_FOLLICLES"
        for i in range(0, bindjointcount):
            # Create follicle on the nurbs surface using the create_follicle function
            # Then rename it and parent it to the FOLLICLES group
            follicle = self.create_follicle(nrbpatch[0][0], 0.5, i / (bindjointcount - 1.00))
            follicle = cmds.listRelatives(follicle, parentranslate=True)
            newfol = cmds.rename(follicle, "{}_{}_FLC".format(part_name, str(foll_cur_name))
            cmds.parent(newfol, flcgrp)

            # Create joint for follicle and parent to follicle
            jnt = cmds.joint(name=newfol.replace("_FLC", "_Connect_JNT"))
            rbnjoints.append(jnt)
            foll_cur_name = foll_cur_name + 1


        if skin:
            # Create a list of the joints to be used for skinning the nrb surface
            rbnskinjoints = [
                "{}_Start_JNT".format(part_name), 
                "{}_End_JNT".format(part_name), 
                "{}_Mid_JNT".format(part_name)
            ]

            # Apply a skinCluster to the nrb surface using the joints in rbnskinjoints
            cmds.skinCluster(rbnskinjoints, nrbpatch[0], name="{}_RBN_SkinCluster".format(part_name))

        cmds.hide(rbngrp)
        for part in [rbngrp, flcgrp]:
            self.lockhideattr(part, hide=False)
        self.lockhideattr("{}_RIGJOINTS".format(part_name), translate=False, rotate=False, hide=False)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselect=True)

        return nrbpatch[1], rbnjoints, rbngrp


    def character_setup(self):
        # Create character's group setup
        pgroup = "{}_CharacterRig".format(self.char_name)
        # If the group does not exist, create one
        if not cmds.ls(pgroup):
            parentgroup = cmds.group(name=pgroup, empty=True)
        else:
            parentgroup = pgroup
        self.lockhideattr(pgroup, hide=False)

        # Create the sub-groups for the main group
        for group in ["Meshes", "BindJoints", "Rig"]:
            if not cmds.ls(self.char_name + "_" + group):
                newgrp = cmds.group(name="{}_{}".format(self.char_name, group), parent=parentgroup, empty=True)
                self.lockhideattr(newgrp, hide=False)

        main_rig_group = "{}_Rig".format(self.char_name)

        # Create root control at 0,0,0 and parent it to the _Rig group
        rootgroup = self.controllers_setup(part_name="Root", scale=(40,40,40), rotation=(90,0,0))
        cmds.parent(rootgroup[0], main_rig_group)

        # Lock and hide scale and vis on root ctrl
        self.lockhideattr(rootgroup[1], translate=False, rotate=False)

        # Create 3 display layers, one each for Meshes, Joints, and Controls
        displayers = []
        for dl in ["Meshes", "Joints", "Controls"]:
            dl_name = "{}_Disp".format(dl)
            if not cmds.ls(dl_name):
                cmds.createDisplayLayer(name=dl_name, empty=True)
            displayers.append(dl_name)

        # Add Root_CTRL to Controls display layer
        cmds.editDisplayLayerMembers(displayers[2], rootgroup[1])

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselect=True)

        class CharSetup:
            def __init__(self, rootgroup, main_rig_group, displayers):
                self.rootgroup = rootgroup
                self.main_rig_group = main_rig_group
                self.displayers = displayers
            
        return CharSetup(rootgroup, main_rig_group, displayers)



    def spine_setup(self, startjnt="",
                    endjnt="", scale=1,
                    rotation=(0,0,0), position=(0,0,0)):
        # Create list for all the joints between startjnt and endjnt
        spinejnts = [endjnt]
        # Start at endjnt, go upwards until you hit startjnt, adding each joint to the Spinejnts list
        # Max out at 21 passes through this array, in which case throw an error
        for joint in range(0,21):
            if 1 < joint < 20:
                spinejnts.append(tempjnt[0])
                tempjnt = cmds.listRelatives(tempjnt, parent=True)
                if tempjnt[0] == startjnt:
                    break
            elif joint == 20:
                print("Could not find {} during this loop, check that it is correctly named".format(startjnt))
                break
            elif joint == 0:
                tempjnt = cmds.listRelatives(endjnt, parent=True)

        spinejnts.append(startjnt)

        # Reverse Spinejnts, as the list will be created in reverse order, starting at endjnt and ending at startjnt
        spinejnts.reverse()

        # Create ribbon for spine based on startjnt and endjnt
        spinerbnlocs = self.ribbon_setup(part_name="Ct_Spine", startjnt=startjnt,
                                         endjnt=endjnt, method="twoloc",
                                         bindjointcount=6)

        # Create a control for the Hips at the Ct_Hips_JNT location
        hipsgrp =  self.controllers_setup(part_name="Hips", shape="cube",
                                          scale=(50,5,40) * scale, rotation=rotation)
        cmds.xform(hipsgrp[0], worldSpace=True, translate=cmds.xform(startjnt, worldSpace=True, translate=True, query=True)) # TODO reformat these to be oredered correctly
        cmds.xform(hipsgrp[0], worldSpace=True, rotation= cmds.xform(startjnt, worldSpace=True, rotation=True,  query=True))
        # Create a control for the Chest bend at the position of the middle locator from the ribbon
        chestgrp = self.controllers_setup(part_name="Chest", shape="cube",
                                          scale=(50,5,40), rotation=rotation)
        cmds.xform(chestgrp[0], worldSpace=True, translate=cmds.xform(spinerbnlocs[0][1], worldSpace=True, translate=True, query=True))
        cmds.xform(chestgrp[0], worldSpace=True, rotation= cmds.xform(spinerbnlocs[0][1], worldSpace=True, rotation=True,  query=True))

        self.lockhideattr(hipsgrp[1], translate=False, rotate=False)
        self.lockhideattr(chestgrp[1], rotate=False)

        # Parent the chest's offset group to the Hips' Controller
        cmds.parent(chestgrp[0], hipsgrp[1])

        # Move the chest Ctrl's pivot to the position of the first spine joint
        cmds.xform(chestgrp[1], piv=(cmds.xform(spinejnts[0], query=True, worldSpace=True, translate=True)), worldSpace=True)

        # Parent constrain the controllers to the ribbon's locators
        # Parent constrain the Hips_CTRL to the first locator on the spine ribbon
        cmds.parentConstraint(hipsgrp[1], spinerbnlocs[0][0], maintainOffset=True)
        # Parent constrain the Chest_CTRL to the second locator on the spine ribbon
        cmds.parentConstraint(spinerbnlocs[0][0], spinerbnlocs[0][2], spinerbnlocs[0][1], maintainOffset=True)
        # Parent constrain the Chest_CTRL to the third locator on the spine ribbon
        cmds.parentConstraint(chestgrp[1], spinerbnlocs[0][2], maintainOffset=True)

        # Parent constrain ribbon joints to bind joints
        for bindjnt, connectjnt in zip(spinejnts, spinerbnlocs[1]):
            cmds.parentConstraint(connectjnt, bindjnt, maintainOffset=True)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselect=True)

        class Spine:
            def __init__(self, hipsgrp, chestgrp):
                self.hipsgrp = hipsgrp
                self.chestgrp = chestgrp
                self.spinerbnrig = "Ct_Spine_RBN_Rig"
            
        return Spine(hipsgrp, chestgrp)


    def neck_setup(self, neckjnt="",
                   scale=1, rotation=(0,-90,0),
                   position=(5,0,-3)):
        # Create neck controller and position it at the location of the neck joint
        neckgrp = self.controllers_setup(part_name="Neck", shape="circle",
                                         scale=(10,10,10) * scale,
                                         rotation=rotation,
                                         position=position)
        neckpos = cmds.xform(neckjnt, query=True, translate=True, worldSpace=True)
        neckrot = cmds.xform(neckjnt, query=True, rotation=True,  worldSpace=True)
        cmds.xform(neckgrp, translate=neckpos, rotation=neckrot, worldSpace=True)

        # Make sure that the controller's pivot is where the Neck joint is
        cmds.xform(neckgrp[1], pivot=(cmds.xform(neckjnt, query=True, translate=True, worldSpace=True)), worldSpace=True)

        # Parent constrain the neck controller to the neck joint
        cmds.parentConstraint(neckgrp[1], neckjnt, maintainOffset=True)

        # Lock and hide all attrs other than rotation
        self.lockhideattr(neckgrp[1], rotate=False)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselect=True)


        class Neck:
            def __init__(self, neckgrp):
                self.neckgrp = neckgrp
            
        return Neck(neckgrp)


    def arm_setup(self, scapjnt="",
                  shouljnt="", wristjnt="",
                  twist=False, flipped=False):
        # Set up the side variable for naming
        if flipped:
            side="Rt"
            colour="blue"
        else:
            side="Lf"
            colour="yellow"

        # TODO check this works
        elbow_jnt = cmds.listRelatives(wristjnt, p=1)[0] 

        # Create a group for the overall arm setup
        armgrp = cmds.group(name="{}_Arm".format(side), parent="{}_Rig".format(self.char_name), empty=True)
        self.lockhideattr(armgrp, hide=False)

        # FKIK SETUP

        # Duplicate shoulder setup and rename all joints under it and including itself
        fkikgrp = cmds.group(name="{}_Arm_FKIK".format(side), parent=armgrp, empty=True)
        cmds.hide(fkikgrp)
        self.lockhideattr(fkikgrp, hide=False)
        shouldupl = cmds.duplicate(shouljnt, name=shouljnt.replace("_JNT", "_Connect_JNT"))
        cmds.parent(shouldupl[0], fkikgrp)
        for childjnt in cmds.listRelatives(shouldupl[0], children=True, allDescendents=True, fullPath=True):
            # Rename each child joint to have the same _Connect_JNT naming
            # The split("|")[-1] is to select the last part of the fullpath object name, convert
            #       to string, and then replace the name
            cmds.rename(childjnt, str(childjnt.split("|")[-1]).replace("_JNT", "_Connect_JNT"))

        # Create a list with the _Connect_JNT joints in it
        connectjnts = []
        for jnt in range(0,3):
            connectjnts.append("{}_Arm_{}_Connect_JNT".format(side, str(jnt)))

        # Delete unneeded joints
        cmds.delete(cmds.listRelatives(wristjnt.replace("_JNT", "_Connect_JNT"), children=True, fullPath=True)[0])

        # Duplicate twice for FK and IK joint chains
        for ikfk in ["FK", "IK"]:
            newshoul = cmds.duplicate(shouldupl[0], n=shouldupl[0].replace("_Connect_JNT", "_" + ikfk + "_JNT"))
            for childjnt in cmds.listRelatives(newshoul[0], children=True, allDescendents=True, fullPath=True):
                # Rename each child joint to have the same _IKFK_JNT naming
                cmds.rename(childjnt, str(childjnt.split("|")[-1]).replace("_Connect_JNT", "_" + ikfk + "_JNT"))

        # Create constraints from IK and FK joints to the Connect joints
        cmds.parentConstraint(shouljnt.replace("_JNT", "_FK_JNT"),
                              shouljnt.replace("_JNT", "_IK_JNT"),
                              shouljnt.replace("_JNT", "_Connect_JNT"))
        for jnts in [cmds.listRelatives(wristjnt, parent=True)[0], wristjnt]:
            cmds.orientConstraint(jnts.replace("_JNT", "_FK_JNT"),
                                  jnts.replace("_JNT", "_IK_JNT"),
                                  jnts.replace("_JNT", "_Connect_JNT"))


        # SCAPULA

        # Create controller for scapula, then position and set pivot point for group and controller
        scapulagrp = self.controllers_setup(part_name=side + "_Scapula", shape="scapctrl",
                                            position=(14,0,0), scale=(4,4,4),
                                            colour=colour)
        cmds.xform(scapulagrp[0], translate=cmds.xform(scapjnt, query=True, translate=True, worldSpace=True), worldSpace=True)
        if flipped:
            cmds.xform(scapulagrp[0], scale=(-1,1,1))
        cmds.xform(scapulagrp[1], pivot=(cmds.xform(scapjnt, query=True, translate=True, worldSpace=True)), worldSpace=True)

        self.lockhideattr(scapulagrp[1], rotate=False)
        self.lockhideattr(scapulagrp[0], translate=False, rotate=False)


        # Create a locator parented to the scapula in the position of the shouljnt
        shoulloc = cmds.spaceLocator(n=side + "_Scapula_Shoulder_LOC")
        cmds.xform(shoulloc, t=(cmds.xform(shouljnt, query=True, translate=True, worldSpace=True)), worldSpace=True)
        cmds.parent(shoulloc[0], scapulagrp[1])
        cmds.setAttr(shoulloc[0] + ".visibility", 0)
        self.lockhideattr(shoulloc[0])

        # Scapula ctrl to scapula jnt constraint
        cmds.parentConstraint(scapulagrp[1], scapjnt, maintainOffset=True)

        # Parent scapula group to the arm group
        cmds.parent(scapulagrp[0], armgrp)


        # ARM ATTRS SETUP

        # Create pointedsquare control and position at shoulder location
        if flipped:
            armattrsgrp = self.controllers_setup(part_name="{}_Arm_Attrs".format(side), shape="pointedsquare",
                                                 scale=(-6,6,6), colour=colour)
        else:
            armattrsgrp = self.controllers_setup(part_name="{}_Arm_Attrs".format(side), shape="pointedsquare",
                                                 scale=(6,6,6), colour=colour)
        cmds.xform(armattrsgrp, translate=(cmds.xform(shoulloc, query=True, translate=True, worldSpace=True)), worldSpace=True)

        # Parent arm attrs group to arm group
        cmds.parent(armattrsgrp[0], armgrp)

        # Parent constrain arm attrs group to the scapula's
        cmds.parentConstraint(shoulloc[0], armattrsgrp[0], maintainOffset=True)

        self.lockhideattr(armattrsgrp[1])
        self.lockhideattr(armattrsgrp[0], translate=False, rotate=False)


        # Create FKIK, and space switching attributes for each arm
        cmds.select(armattrsgrp[1])
        cmds.addAttr(shortName="FKIK", longName="FKIK", min=0, max=1, dv=0, exists=True, hidden=False, keyable=True)

        # TODO Edit this to make it global

        cmds.addAttr(shortName="Pos_SS", longName="Position_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.addAttr(shortName="Rot_SS", longName="Rotation_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.select(deselect=True)

        # FKIK switching setup
        # Create math node to reverse (1 - fkikattr)
        fkikreverse = cmds.createNode("floatMath", name="{}_Arm_FKIK_Reverse_FM".format(side))
        cmds.setAttr("{}.operation".format(fkikreverse), 1)
        cmds.connectAttr("{}.FKIK".format(armattrsgrp[1]), "{}.floatB".format(fkikreverse))

        for connectjnt in [shouljnt, elbow_jnt, wristjnt]:
            if connectjnt in shouljnt:
                ocpc = "parent"
            else:
                ocpc = "orient"
            constraint = "{}_{}Constraint1".format(connectjnt.replace("_JNT", "_Connect_JNT"), ocpc)
            cmds.connectAttr("{}.FKIK".format(armattrsgrp[1]), "{}.{}W1".format(constraint, connectjnt.replace("_JNT", "_IK_JNT")))
            cmds.connectAttr("{}.outFloat".format(fkikreverse), "{}.{}W0".format(constraint, connectjnt.replace("_JNT", "_FK_JNT")))


        # IK SETUP
        # Check that the IK shoulder joint's Preffered Angle is 0,0,0
            for xyz in ["X", "Y", "Z"]:
                cmds.setAttr("{}.preferredAngle{}".format(connectjnt.replace("_JNT", "_IK_JNT"), xyz), 0)

        # Create an IK handle for the IK joints
        arm_ikh = cmds.ikHandle(startJoint=shouljnt.replace("_JNT", "_IK_JNT"), endEffector=wristjnt.replace("_JNT", "_IK_JNT"), name="{}_Arm_IK_IKH".format(side))
        cmds.hide(arm_ikh)

        # Parent IK handle to the arm group
        cmds.parent(arm_ikh[0], armgrp)

        # Parent constrain Connect joints to bind joints
        for connectjnt in [shouljnt, elbow_jnt, wristjnt]:
            cmds.parentConstraint(connectjnt.replace("_JNT", "_Connect_JNT"), connectjnt)


        # CONTROLS
        # FK Controls
        fkctrls = []
        fkgrps = []
        for fkjoint in [shouljnt, elbow_jnt, wristjnt]:
            fkgrp = self.controllers_setup(part_name=fkjoint.replace("_JNT", "_FK"), shape="circle",
                                           colour=colour, scale=(6,6,6),
                                           rotation=(0,90,0))
            cmds.xform(fkgrp[0], translate=(cmds.xform(fkjoint, query=True, translate=True, worldSpace=True)), rotation=(cmds.xform(fkjoint, query=True, rotation=True, worldSpace=True)), worldSpace=True)
            cmds.parentConstraint(fkgrp[1], fkjoint.replace("_JNT", "_FK_JNT"))

            if fkjoint == shouljnt:
                cmds.parent(fkgrp[0], armgrp)
            else:
                # cmds.parent(fkgrp[0], side + "_Arm_" + str(fkjoint-1) + "_FK_CTRL")
                # cmds.parent(fkgrp[0], fkjoint.split("_JNT")[0][:-1] + str(int(fkjoint.split("_JNT")[0][-1])-1) + "_FK_CTRL")
                cmds.parent(fkgrp[0], cmds.listRelatives(fkjoint, p=1)[0].replace("_JNT", "_FK_CTRL"))

            fkgrps.append(fkgrp)
            fkctrls.append(fkgrp[1])

        # Parent constrain FK shoulder to Scapula
        cmds.parentConstraint(scapulagrp[1], shouljnt.replace("_JNT", "_FK_GRP"), maintainOffset=True)

        # Point constrain Shoulder IK joint to Scapula
        cmds.pointConstraint(shoulloc, shouljnt.replace("_JNT", "_IK_JNT"), maintainOffset=True)

        # Set vis for Shoulder FK group based on FKIK attr
        cmds.connectAttr(fkikreverse + ".outFloat", shouljnt.replace("_JNT", "_FK_GRP") + ".visibility")

        for fkgrp in fkgrps:
            self.lockhideattr(fkgrp[0])
            self.lockhideattr(fkgrp[1], rotate=False)


        # IK Controls
        # IKHandle control
        ikgrp = self.controllers_setup(part_name=side + "_Arm_IK", shape="starcircle",
                                       colour=colour, scale=(6,6,6),
                                       rotation=(0,90,0))
        cmds.xform(ikgrp[0], t=(cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), translate=True, query=True, worldSpace=True)),
                   ro=(cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), rotation=True, query=True, worldSpace=True)), worldSpace=True)
        cmds.parentConstraint(ikgrp[1], arm_ikh[0])
        cmds.orientConstraint(ikgrp[1], wristjnt.replace("_JNT", "_IK_JNT"))
        cmds.parent(ikgrp[0], armgrp)
        cmds.connectAttr(armattrsgrp[1] + ".FKIK", ikgrp[0] + ".visibility")

        self.lockhideattr(ikgrp[0], translate=False, rotate=False, visibility=False)
        self.lockhideattr(ikgrp[1], translate=False, rotate=False)

        # PV Control
        pvgrp = self.controllers_setup(part_name=side + "_Arm_IK_PV", shape="starcircle",
                                       colour=colour, scale=(6,6,6),
                                       rotation=(0,0,0))
        cmds.xform(pvgrp[0],
                   t=(self.vector_lerp(cmds.xform(shouljnt.replace("_JNT", "_IK_JNT"), query=True, translate=True, worldSpace=True),
                                       cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), query=True, translate=True, worldSpace=True),
                                       .5)), worldSpace=True)
        tempaimconst = cmds.aimConstraint((elbow_jnt).replace("_JNT", "_IK_JNT"), pvgrp[0])
        cmds.delete(tempaimconst)
        cmds.xform(pvgrp[0], translate=(50,0,0), relative=True, objectSpace=True)

        cmds.parent(pvgrp[0], armgrp)

        cmds.poleVectorConstraint(pvgrp[1], arm_ikh[0])

        cmds.connectAttr(armattrsgrp[1] + ".FKIK", pvgrp[0] + ".visibility")

        self.lockhideattr(pvgrp[0], visibility=False)
        self.lockhideattr(pvgrp[1], translate=False, rotate=False)


        # Space Switching
        constraints = ["Root_CTRL", "Hips_CTRL", "Chest_CTRL"]
        if flipped:
            constraints.append("Rt_Scapula_Shoulder_LOC")
        else:
            constraints.append("Lf_Scapula_Shoulder_LOC")

        constraintsnames = ["Root", "Hips", "Chest", "Shoulder"]

        # Create locators for each of the input objects at their 0,0,0
        for obj in constraints:
            loc = cmds.spaceLocator(n="{}_{}_SS_LOC".format(side, obj))[0]
            cmds.xform(loc, translate=cmds.xform(ikgrp[1], query=True, translate=True, worldSpace=True), worldSpace=True)
            cmds.parent(loc, obj)
            cmds.hide(loc)

            self.lockhideattr(loc)

        constraintslocs = []
        for entry in constraints:
            constraintslocs.append(side + "_" + entry + "_SS_LOC")

        cmds.pointConstraint(constraintslocs, ikgrp[0], maintainOffset=True)
        cmds.orientConstraint(constraintslocs, ikgrp[0], maintainOffset=True)

        # Create setup for Space Switching for the IK hand group
        for longname, shortname in zip(["Rotation", "Position"], ["Rot", "Pos"]):
            for name, num in zip(constraintsnames, [0, 1, 2, 3]):
                condnode = cmds.createNode("condition", n=side + "_Arm_" + name + "_" + shortname + "SS_COND")
                cmds.connectAttr(armattrsgrp[1] + "." + longname + "_Space_Switching", condnode + ".secondTerm")
                cmds.setAttr(condnode + ".firstTerm", num)
                for i, j in zip(["True", "False"], [1, 0]):
                    cmds.setAttr(condnode + ".colorIf" + i + "R", j)
        for i, x in zip(["orient", "point"], ["Rot", "Pos"]):
            for name, nameshort, num in zip(constraintslocs, constraintsnames, [0, 1, 2, 3]):
                cmds.connectAttr(side + "_Arm_" + nameshort + "_" + x + "SS_COND.outColor.outColorR",
                                 ikgrp[0] + "_" + i + "Constraint1." + name + "W" + str(num))


        class Arm:
            def __init__(self, shoulloc, scapulagrp, armattrsgrp, connectjnts, ikgrp, pvgrp, fkctrls):
                self.shoulloc = shoulloc
                self.scapulagrp = scapulagrp
                self.armattrsgrp = armattrsgrp 
                self.connectjnts = connectjnts 
                self.ikgrp = ikgrp
                self.pvgrp = pvgrp
                self.fkctrls = fkctrls
            
        return Arm(shoulloc, scapulagrp, armattrsgrp, connectjnts, ikgrp, pvgrp, fkctrls)


    def hand_setup(self, flipped=False):
        # Set up variables for both left and right side hands, both for naming and controller colouring
        if flipped:
            side = "Rt"
            colour = "blue"
        else:
            side = "Lf"
            colour = "yellow"

        # Create overall hand group
        handgrp = cmds.group(n="{}_Hand_GRP".format(side), empty=1)

        fingers = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

        # Loop over each finger and create it's controls for each
        for finger in fingers:
            # Set finger joint count for thumb seperately, as it only has 3 joints
            if finger == "Thumb":
                fingercount = 3
            else:
                fingercount = 4

            for fjoint in range(0, fingercount):
                # Set up a variable for the finger naming
                finger_name_short = "{}_{}_{}".format(side, finger, str(fjoint))

                # Create a controller for the fingers, with seperate controller setups for the first
                # joint in each finger, with joint 0's controller being parallel to the joint
                if fjoint == 0:
                    fingergrp = self.controllers_setup(part_name=finger_name_short, shape="square",
                                                       colour=colour, rotation=(0,0,0),
                                                       scale=(4,1,2), position=(2,0,3))
                    # Fix the pivot point for the controller to make sure it matches the joint's position
                    cmds.xform(fingergrp[1], pivot=(cmds.xform(fingergrp[0], translate=1, query=1, worldSpace=1)), worldSpace=1)
                else:
                    fingergrp = self.controllers_setup(part_name=finger_name_short, shape="square",
                                                       colour=colour, rotation=(0,90,0),
                                                       scale=(2,2,3))

                # Create an offset group, in the same position/rotation as the finger joint's group. (0,0,0) relatively
                # This is used for the hand's Fist and Spread attributes
                offsetgrp = cmds.group(name=finger_name_short + "_Offset_GRP", empty=1, parent=fingergrp[0])
                # Then parent the controller to the offset group
                cmds.parent(fingergrp[1], offsetgrp)

                # Get the position/rotation of the joint, and place the controller's group where the joint is
                # If this is for the right side hand, get all the transforms and rotations from the left hand
                # to position the controller's group in the correct position, as it'll be flipped later
                if flipped:
                    cmds.xform(fingergrp[0], translate=(cmds.xform(finger_name_short.replace("Rt", "Lf") + "_JNT", query=1, translate=1, worldSpace=1)),
                               rotation=(cmds.xform(finger_name_short.replace("Rt", "Lf") + "_JNT", query=1, rotation=1, worldSpace=1)), worldSpace=1)
                else:
                    cmds.xform(fingergrp[0], translate=(cmds.xform("{}_JNT".format(finger_name_short), query=1, translate=1, worldSpace=1)),
                               rotation=(cmds.xform("{}_JNT".format(finger_name_short), query=1, rotation=1, worldSpace=1)), worldSpace=1)

                # For the first controller's group, parent it to the handgrp group
                if fjoint == 0:
                    cmds.parent(fingergrp[0], handgrp)
                # and for subsequent controllers, parent the controller's group to the previous controller
                else:
                    cmds.parent(fingergrp[0], "{}_{}_{}_CTRL".format(side, finger, str(fjoint-1)))


        # Create controller for hand attributes (Fist, Spread)
        handattrsgrp = self.controllers_setup(part_name="{}_Hand_Attrs".format(side), shape="starcircle", position=(0,0,4), scale=(2,2,2), colour=colour)
        # Position and rotate the controller at the hand location
        cmds.xform(handattrsgrp, translate=(cmds.xform("Lf_Hand_1_JNT", translate=1, query=1, worldSpace=1)),
                   rotation=(cmds.xform("Lf_Hand_1_JNT", rotation=1, query=1, worldSpace=1)), worldSpace=1)
        # Parent to main hand group
        cmds.parent(handattrsgrp[0], handgrp)

        # Create Fist and Spread attributes on hand attr control
        for attr in ["Fist", "Spread"]:
            cmds.addAttr(handattrsgrp[1], shortName=attr, longName=attr, min=0, max=1, defaultValue=0, exists=1, hidden=0, keyable=1)


        # Hand Fist
        # Create Remap node for first joint in fingers
        fingeroneremap =   cmds.createNode("remapValue", name="{}_Finger_1_Fist_REMAP".format(side))
        cmds.setAttr(fingeroneremap + ".outputMax", 70)
        fingertwothreeremap = cmds.createNode("remapValue", name="{}_Finger_23_Fist_REMAP".format(side))
        cmds.setAttr(fingertwothreeremap + ".outputMax", 90)

        thumbzeroremap = cmds.createNode("remapValue", name=side + "{}_Finger_0_Fist_REMAP".format(side))
        cmds.setAttr(thumbzeroremap + ".outputMax", 10)
        thumbonetworemap = cmds.createNode("remapValue", name=side + "_Thumb_12_Fist_REMAP")
        cmds.setAttr(thumbonetworemap + ".outputMax", 45)

        # Connect handattrs Fist attribute to fist remap nodes
        for remapnode in [fingeroneremap, fingertwothreeremap, thumbzeroremap, thumbonetworemap]:
            cmds.connectAttr(handattrsgrp[1] + ".Fist", remapnode + ".i")

        # Connect fingerzeroremap and fingertwothreeremap to the finger's Offset_GRP groups (excluding thumb)
        for finger in fingers[1:]:
            cmds.connectAttr(fingeroneremap  + ".outValue", side + "_" + finger + "_1_Offset_GRP.rotateY")
            for joint in range(2,4):
                cmds.connectAttr(fingertwothreeremap  + ".outValue", side + "_" + finger + "_" + str(joint) + "_Offset_GRP.rotateY")

        # Connect thumbzeroremap and thumbonetworemap to the thumb's Offset_GRP groups
        cmds.connectAttr("{}.outValue".format(thumbzeroremap), "{}_Thumb_0_Offset_GRP.rotateY".format(side))
        for joint in range(1, 3):
            cmds.connectAttr("{}.outValue".format(thumbonetworemap), "{}_Thumb_{}_Offset_GRP.rotateY".format(side, str(joint)))


        # Hand Spread
        for finger, remapvalue in zip(fingers, [-20, -10, -3, 10, 20]):
            if finger == "Thumb":
                joint = 0
            else:
                joint = 1
            
            strjoint = str(joint)

            remapnode = cmds.createNode("remapValue", name="{}_{}_{}_Spread_REMAP".format(side, finger, strjoint))
            cmds.setAttr("{}.outputMax".format(remapnode), remapvalue)
            cmds.connectAttr("{}.Spread".format(handattrsgrp[1]), "{}.i".format(remapnode))
            cmds.connectAttr("{}.outValue".format(remapnode), "{}_{}_{}_Offset_GRP.rotateZ".format(side, finger, strjoint))


        # Flip the entire handgrp group if this is for a right side hand
        if flipped:
            cmds.xform(handgrp, scale=(-1,1,1))


        # Loop through each finger for parent constraining each control to it's joint, and attribute locking and hiding
        for finger in fingers:
            # Set finger joint count for thumb seperately, as it only has 3 joints
            if finger == "Thumb":
                fingercount = 3
            else:
                fingercount = 4

            for fjoint in range(0, fingercount):
                # Set up a variable for the finger naming
                finger_name_short = "{}_{}_{}".format(side, finger, str(fjoint))

                # Create parent constraints from each finger controller to it's respective joint
                cmds.parentConstraint("{}_CTRL".format(finger_name_short), "{}_JNT".format(finger_name_short), maintainOffset=True)

                # TODO check this works

                lock_unkeyframe = {
                    "lock":True,
                    "keyable":False
                }

                # Lock and hide respective attributes for each control
                for xyz in ["X", "Y", "Z"]:
                    # Lock and hide translate, rotation, and scale for each main joint group
                    for attr in ["translate", "rotate", "scale"]:
                        for item in [finger_name_short, handattrsgrp[0], handattrsgrp[1]]:ß
                            cmds.setAttr("{}_GRP.{}{}".format(item, attr, xyz), **lock_unkeyframe)
                    # Lock and hid translate and scale for offset groups and controls
                    for attr in ["translate", "scale"]:
                        cmds.setAttr("{}_Offset_GRP.{}{}".format(finger_name_short, attr, xyz), **lock_unkeyframe)
                        cmds.setAttr("{}_CTRL.{}{}".format(finger_name_short, attr, xyz), **lock_unkeyframe)


                # Lock and hide visibility for each grp, offset grp, and control on the fingers
                for finger_item in ["GRP", "Offset_GRP", "CTRL"]:
                    cmds.setAttr("{}_{}.visibility".format(finger_name_short, finger_item), **lock_unkeyframe)

                cmds.setAttr("{}.visibility".format(handattrsgrp[1]), **lock_unkeyframe)


        cmds.parent(handgrp, self.char_name + "_Rig")

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(deselectranslate=True)

        class Hand:
            def __init__(self, handgrp):
                self.handgrp = handgrp
            
        return Hand(handgrp)


    def curve_rig(self, part_name="",
                  startjnt="", endjnt=""):
        # Create curve based ribbon based on the joints from startjnt to endjnt
        crvrbn = self.ribbon_setup(part_name=part_name,
                                   startjnt=startjnt, endjnt=endjnt,
                                   method="jointbased", skin=False,
                                   reverse=True)

        # Parent the curve's group to the _Rig group
        cmds.parent(crvrbn[2], self.char_name + "_Rig")

        # Parent constrain the ribbon's joints to the bind joints
        for jnt in range(0, crvrbn[0]):
            cmds.parentConstraint(part_name + "_" + str(jnt) + "_Connect_JNT", part_name + "_" + str(jnt+1) + "_JNT", maintainOffset=True)

        return crvrbn


    def fkchain(self, part_name="",
                startjnt="", endjnt="",
                scale=1, maxjntcount=21,
                shape=""):
        # Get all the joints between startjnt and endjnt
        fkjnts = []
        for joint in range(0, maxjntcount):
            if 1 < joint < (maxjntcount-1):
                fkjnts.append(tempjnt[0])
                tempjnt = cmds.listRelatives(tempjnt, p=1)
                if tempjnt[0] == startjnt:
                    break
            elif joint == maxjntcount-1:
                print("Could not find " + startjnt + " during this loop, check that it is correctly named")
                break
            elif joint == 0:
                tempjnt = cmds.listRelatives(endjnt, p=1)

        fkjnts.append(startjnt)
        # Reverse rbnjnts, as the list will be created in reverse order, starting at endjnt and ending at startjnt
        fkjnts.reverse()

        # Create a controller for each joint in the FK chain, position it at it's joint, and parent constrain it
        for jnt, num in zip(fkjnts, range(0, len(fkjnts))):
            fkgrp = self.controllers_setup(part_name=part_name + "_" + str(num), shape=shape,
                                           scale=(3*scale, 3*scale, 3*scale))
            cmds.xform(fkgrp[0], translate=(cmds.xform(jnt, translate=True, query=True, worldSpace=True)), ro=(cmds.xform(jnt, rotation=True, query=True, worldSpace=True)), worldSpace=True)
            if num == 0:
                fkgrpone = fkgrp
                self.lockhideattr(fkgrp[0], translate=False, rotate=False)
                self.lockhideattr(fkgrp[1], rotate=False)
            else:
                cmds.parent(fkgrp[0], part_name + "_" + str(num-1) + "_CTRL")
                self.lockhideattr(fkgrp[0])
                self.lockhideattr(fkgrp[1], rotate=False)
            cmds.parentConstraint(fkgrp[1], jnt)

        # Parent the first FK controller's group to the _Rig group
        cmds.parent(fkgrpone[0], self.char_name + "_Rig")

        cmds.select(deselect=True)

        return fkgrpone


    def digileg(self, part_name="",
                startjnt="", kneejnt="",
                anklejnt="", heeljnt="",
                footjnt="", flipped=False):

        if flipped:
            side="Rt"
            colour="blue"
        else:
            side="Lf"
            colour="yellow"

        # Overall leg group
        leggrp = cmds.group(name=part_name, empty=True)
        cmds.parent(leggrp, self.char_name + "_Rig")


        # Create FKIK setup
        legfkikgrp = cmds.group(name=part_name + "_FKIK", empty=True, parent=leggrp)
        # Duplicate startjnt > heeljnt
        for cnt, jnt in enumerate([startjnt, kneejnt, anklejnt, heeljnt]):
            newjnt = cmds.duplicate(jnt, parentOnly=True, name=jnt.replace("_JNT", "_Connect_JNT"))
            if jnt == startjnt:
                cnctjntone = newjnt[0]
                cmds.parent(newjnt, world=True)
            else:
                cmds.parent(newjnt, startjnt.replace("0", str(cnt-1)).replace("_JNT", "_Connect_JNT"))

        cmds.parent(cnctjntone, legfkikgrp)

        for fkik in ["FK", "IK"]:
            tempjnt = cmds.duplicate(cnctjntone, name=cnctjntone.replace("Connect", fkik))
            for childjnt in cmds.listRelatives(tempjnt[0], children=True, allDescendants=True, fullPath=True):
                # Rename each child joint to have the same _IKFK_JNT naming
                cmds.rename(childjnt, str(childjnt.split("|")[-1]).replace("_Connect_JNT", "_" + fkik + "_JNT"))

        # Constraints from FK and IK joints to Connect joints
        cmds.parentConstraint(startjnt.replace("_JNT", "_FK_JNT"), startjnt.replace("_JNT", "_IK_JNT"), startjnt.replace("_JNT", "_Connect_JNT"))
        for jnt in [kneejnt, anklejnt, heeljnt]:
            bindjointorientconstraint = cmds.orientConstraint(jnt.replace("_JNT", "_FK_JNT"),
                                                              jnt.replace("_JNT", "_IK_JNT"),
                                                              jnt.replace("_JNT", "_Connect_JNT"))
            cmds.setAttr(bindjointorientconstraint[0] + ".interpType", 0)

        # Create FK chain
        fkjnts = cmds.listRelatives(cnctjntone.replace("Connect", "FK"), allDescendents=True, c=1)
        fkjnts.append(cnctjntone.replace("Connect", "FK"))
        fkjnts.reverse()
        for cnt, jnt in enumerate(fkjnts):
            fkgrp = self.controllers_setup(part_name=part_name + "_FK_" + str(cnt), scale=(10,10,10), rotation=(0,90,0), colour=colour)
            cmds.xform(fkgrp[0], t=(cmds.xform(jnt, translate=True, query=True, worldSpace=True)), ro=(cmds.xform(jnt, rotation=True, query=True, worldSpace=True)), worldSpace=True)
            self.lockhideattr(fkgrp[1], rotate=False)
            if cnt == 0:
                fkgrpone = fkgrp
                cmds.parent(fkgrp[0], leggrp)
            else:
                cmds.parent(fkgrp[0], part_name + "_FK_" + str((cnt-1)) + "_CTRL")
            cmds.parentConstraint(fkgrp[1], jnt)


        # Create secondary IK Leg
        # Create reverse Foot>Ankle joint chain
        # Create IK Foot controller and PV control
        ikgrp = self.controllers_setup(part_name=part_name + "_IK_Foot", shape="circle", rotation=(90,0,0), scale=(10,10,20), colour=colour)
        footjntpos = cmds.xform(footjnt, translate=True, query=True, worldSpace=True)
        cmds.xform(ikgrp[0], t=(footjntpos[0], 0, footjntpos[2]), worldSpace=True)
        cmds.parent(ikgrp[0], leggrp)
        self.lockhideattr(ikgrp[0], visibility=False)
        self.lockhideattr(ikgrp[1], rotate=False, translate=False)

        # Create IK Reverse Controller
        ikrevgrp = self.controllers_setup(part_name=part_name + "_IK_Rev_Foot", shape="square", scale=(10,10,10), colour=colour)
        cmds.xform(ikrevgrp[0], translate=(cmds.xform(heeljnt, translate=True, query=True, worldSpace=True)))
        cmds.xform(ikrevgrp[0], rotation=(cmds.xform(anklejnt, rotation=True, query=True, worldSpace=True)))
        cmds.xform(ikrevgrp[0], translate=(0, 7, -7), relative=1)
        cmds.xform(ikrevgrp[1], pivot=(cmds.xform(heeljnt, translate=True, query=True, worldSpace=True)), worldSpace=True)

        cmds.parent(ikrevgrp[0], leggrp)
        self.lockhideattr(ikrevgrp[1], rotate=False, translate=False)



        # Create Attrs group and controller
        if flipped:
            legattrsgrp = self.controllers_setup(part_name=side + "_Leg_Attrs", shape="pointedsquare", scale=(-8, 8, 8),
                                                 colour=colour)
        else:
            legattrsgrp = self.controllers_setup(part_name=side + "_Leg_Attrs", shape="pointedsquare", scale=(8, 8, 8),
                                                 colour=colour)
        cmds.xform(legattrsgrp[0], t=(cmds.xform(cnctjntone, translate=True, query=True, worldSpace=True)), worldSpace=True)
        # Parent arm attrs group to arm group
        cmds.parent(legattrsgrp[0], leggrp)
        # Parent constrain arm attrs group to the scapula's
        cmds.parentConstraint(cnctjntone, legattrsgrp[0], maintainOffset=True)
        self.lockhideattr(legattrsgrp[1])


        # Create FKIK, and space switching attributes for each leg
        cmds.select(legattrsgrp[1])
        cmds.addAttr(sn="FKIK", ln="FKIK", min=0, max=1, dv=0, ex=1, h=0, k=1)
        cmds.addAttr(sn="Pos_SS", ln="Position_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.addAttr(sn="Rot_SS", ln="Rotation_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.select(deselect=True)
        # default FKIK attr to IK
        cmds.setAttr(legattrsgrp[1] + ".FKIK", 1)


        # FKIK switching setup
        # Create math node to reverse (1 - fkikattr)
        fkikreverse = cmds.createNode("floatMath", n=side + "_Arm_FKIK_Reverse_FM")
        cmds.setAttr(fkikreverse + ".operation", 1)
        cmds.connectAttr(legattrsgrp[1] + ".FKIK", fkikreverse + ".floatB")

        for connectjnt in [startjnt, kneejnt, anklejnt, heeljnt]:
            if connectjnt == startjnt:
                ocpc = "parent"
            else:
                ocpc = "orient"
            cnctjntshort = connectjnt.replace("_JNT", "")
            constraint = cnctjntshort + "_Connect_JNT_" + ocpc + "Constraint1"
            cmds.connectAttr(legattrsgrp[1] + ".FKIK", constraint + "." + cnctjntshort + "_IK_JNTW1")
            cmds.connectAttr(fkikreverse + ".outFloat", constraint + "." + cnctjntshort + "_FK_JNTW0")

        # FK and IK Controls visibility
        cmds.connectAttr(legattrsgrp[1] + ".FKIK", ikgrp[0] + ".visibility")
        cmds.connectAttr(fkikreverse + ".outFloat", fkgrpone[0] + ".visibility")


        # Create IK Eval chain leg
        ikevaljntone = cmds.joint(n=part_name + "_IK_Eval_0_JNT")
        cmds.xform(ikevaljntone, t=cmds.xform(startjnt, query=True, translate=True, worldSpace=True))

        ikevaljnttwopos = self.vector_lerp(cmds.xform(kneejnt, query=True, translate=True, worldSpace=True), cmds.xform(anklejnt, query=True, translate=True, worldSpace=True), .5)
        ikevaljnttwoposzposone = cmds.xform(kneejnt, query=True, translate=True, worldSpace=True)
        ikevaljnttwoposzpostwo = cmds.xform(anklejnt, query=True, translate=True, worldSpace=True)
        ikevaljnttwopos = (ikevaljnttwopos[0], ikevaljnttwopos[1], min(ikevaljnttwoposzposone[2], ikevaljnttwoposzpostwo[2])-5)
        ikevaljnttwo = cmds.joint(n=part_name + "_IK_Eval_1_JNT")
        cmds.xform(ikevaljnttwo, t=ikevaljnttwopos, worldSpace=True)

        ikevaljntthree = cmds.joint(n=part_name + "_IK_Eval_2_JNT")
        cmds.xform(ikevaljntthree, t=cmds.xform(heeljnt, query=True, translate=True, worldSpace=True), worldSpace=True)
        cmds.select(deselect=True)

        cmds.parent(ikevaljntone, leggrp)

        evalikh = cmds.ikHandle(n=part_name + "_IK_Eval_IKH", sj=ikevaljntone, ee=ikevaljntthree)
        cmds.select(deselect=True)

        # Reverse IK Eval lower leg
        ikevalrevjntone = cmds.joint(n=part_name + "_IK_EvalRev_0_JNT")
        cmds.xform(ikevalrevjntone, t=cmds.xform(heeljnt, query=True, translate=True, worldSpace=True), worldSpace=True)
        ikevalrevjnttwo = cmds.joint(n=part_name + "_IK_EvalRev_1_JNT")
        cmds.xform(ikevalrevjnttwo, t=cmds.xform(anklejnt, query=True, translate=True, worldSpace=True), worldSpace=True)

        cmds.parent(ikevalrevjntone, leggrp)

        # IK solver for upper IK leg (IK startjnt to IK anklejnt)
        upperikh = cmds.ikHandle(n=part_name + "_UpperIK_IKH",
                                 sj=startjnt.replace("_JNT", "_IK_JNT"), ee=anklejnt.replace("_JNT", "_IK_JNT"))

        cmds.parent(upperikh[0], leggrp)

        cmds.parentConstraint(ikevalrevjnttwo, upperikh[0], maintainOffset=True)

        cmds.parent(evalikh[0], ikgrp[1])

        #todo comment this
        lowerikh = cmds.ikHandle(n=part_name + "_LowerIK_IKH",
                                 sj=anklejnt.replace("_JNT", "_IK_JNT"), ee=heeljnt.replace("_JNT", "_IK_JNT"),
                                 sol="ikSCsolver")

        cmds.parentConstraint(ikevalrevjntone, lowerikh[0])

        cmds.parent(lowerikh[0], leggrp)

        ikjorientconst = cmds.orientConstraint(ikgrp[1], heeljnt.replace("_JNT", "_IK_JNT"), maintainOffset=True)
        cmds.setAttr(ikjorientconst[0] + ".interpType", 0)

        cmds.parentConstraint(ikevaljntthree, ikrevgrp[0], maintainOffset=True)
        cmds.parentConstraint(ikrevgrp[1], ikevalrevjntone, maintainOffset=True)

        self.lockhideattr(ikrevgrp[0], visibility=False)


        # Parent constrain Connect joints to bind joints
        for i in [startjnt, kneejnt, anklejnt, heeljnt]:
            bindjparentconst = cmds.parentConstraint(i.replace("_JNT", "_Connect_JNT"), i, maintainOffset=True)

        # Point constrain the upper _IK_JNT to the hips
        cmds.parentConstraint(cmds.listRelatives(startjnt, p=1), startjnt.replace("_JNT", "_IK_JNT"), maintainOffset=True)
        cmds.parentConstraint(cmds.listRelatives(startjnt, p=1), ikevaljntone, maintainOffset=True)

        for i in [ikevalrevjntone, ikevaljntone, evalikh, lowerikh, upperikh, legfkikgrp]:
            cmds.hide(i)
