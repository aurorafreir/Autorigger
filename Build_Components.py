"""
This script houses each of the rig components' build scripts, to get called by each rig's build scripts
"""

# Standard library imports

# Third party imports
from maya import cmds

# Local application imports



"""
TODO UPDATES
- Clean up Twist code to be less destructive
- Clean up function outputs to use dictionaries instead of arbitrary lists
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

        cmds.connectAttr(nurbssurf + ".local", follicle + ".inputSurface")
        cmds.connectAttr(nurbssurf + ".worldMatrix[0]", follicle + ".inputWorldMatrix")
        for name, n in zip(["Rotate", "Translate"], ["r", "t"]):
            cmds.connectAttr(follicle + ".out" + name, cmds.listRelatives(follicle, p=1)[0] + "." + n)
        for uv, pos in zip(["U", "V"], [uPos, vPos]):
            cmds.setAttr(follicle + ".parameter" + uv, pos)
        for tr in ["t", "r"]:
            cmds.setAttr(cmds.listRelatives(follicle, p=1)[0] + "." + tr, lock=1)

        return follicle


    def lockhideattr(self, obj="",
                     hide=True, lock=True,
                     translate=True, rotate=True,
                     scale=True, visibility=True):
        if not translate and not rotate and not scale and not visibility:
            print("lockhideattr function for " + obj + " not set to do anything!")
            return

        attrs = []
        if translate:
            attrs.append("translate")
        if rotate:
            attrs.append("rotate")
        if scale:
            attrs.append("scale")

        cb=1
        l=0
        k=1
        if hide:
            k=0
            cb=0
        if lock:
            l=1

        for attr in attrs:
            for xyz in ["X", "Y", "Z"]:
                cmds.setAttr(obj + "." + attr + xyz, l=l, k=k, cb=cb )
        if visibility:
            cmds.setAttr(obj + ".visibility", l=l, k=k, cb=cb)


    def controllers_setup(self, partname,
                          shape="circle", scale=(1,1,1),
                          rotation=(0,0,0), position=(0,0,0),
                          colour=""):
        # To be used by other parts of this script for creating a variety of controllers
        # Create empty group
        newgroup = cmds.group(n=partname + "_GRP", em=1)
        shapename = partname + "_CTRL"

        if shape in "circle":
            # Create circle NURBS curve
            newshape = cmds.circle(n=shapename, ch=0)
            newshape = newshape[0] # Make sure that newshape is only a single string instead of [objectname + shapename]

        elif shape in "square":
            # Create square NURBS curve
            newshape = cmds.curve(d=1, p=[(-.5, .5, 0), (.5, .5, 0), (.5, -.5, 0), (-.5, -.5, 0), (-.5, .5, 0)],
                n=shapename)

        elif shape in "cube":
            # Create cube NURBS curve
            newshape = cmds.curve(d=1,
                    p=[(-0.5, -0.5, .5), (-0.5, .5, .5), (.5, .5, .5), (.5, -0.5, .5), (.5, -0.5, -0.5), (.5, .5, -0.5),
                       (-0.5, .5, -0.5), (-0.5, -0.5, -0.5), (.5, -0.5, -0.5), (.5, .5, -0.5), (.5, .5, .5),
                       (-0.5, .5, .5), (-0.5, .5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, .5), (.5, -0.5, .5)],
               n=shapename)

        elif shape in "pointedsquare":
            newshape = cmds.curve(d=1,
                                  p=[(0,0,0), (1,1,0), (2,1,0), (2,2,0), (1,2,0), (1,1,0)],
                                  n=shapename)

        elif shape in "starcircle":
            newshape = cmds.circle(n=shapename, ch=0)
            newshape = newshape[0]
            cmds.select(d=1)
            for x in range(0, 7)[::2]:
                cmds.select(newshape + '.cv[{}]'.format(x), tgl=0, add=True)
            cmds.selectMode(co=1)
            cmds.xform(s=(.4, .4, .4))
            cmds.selectMode(o=1)
            cmds.bakePartialHistory(newshape)


        elif shape in "scapctrl":
            newshape = cmds.curve(d=1,
                                  p=[(0,0,-2), (1,1,-2), (1,2,0), (1,1,2), (0,0,2),
                                     (-1,1,2), (-1,2,0), (-1,1,-2), (0,0,-2)],
                                  n=shapename)
        else:
            raise ValueError("Shape not recognised")


        # Scale, rotate, and transform new NURBS object
        cmds.xform(newshape, s=scale, ro=rotation, t=position)

        # Freeze transforms and bake control history
        cmds.makeIdentity(newshape, apply=1)
        cmds.bakePartialHistory(newshape)


        # Set controller colour
        shapeshape = cmds.listRelatives(newshape, s=1, c=1)[0]
        cmds.setAttr(shapeshape + ".overrideEnabled", 1)
        if not colour:
            pass
        elif colour in "blue":
            cmds.setAttr(shapeshape + ".overrideColor", 18)
        elif colour in "yellow":
            cmds.setAttr(shapeshape + ".overrideColor", 22)

        # Parent the new NURBS object to the created group
        cmds.parent(newshape, newgroup)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

        # Pass back out the name of the controller's group and controller itself
        return newgroup, newshape


    def twopointnurbpatch(self, partname="",
                          startjnt="", endjnt=""):
        # Get start and end jnt's position and rotation
        start_pos = cmds.xform(startjnt, ws=1, t=1, q=1)
        start_rot = cmds.xform(startjnt, ws=1, ro=1, q=1)
        end_pos = cmds.xform(endjnt, ws=1, t=1, q=1)

        mid_pos = self.vector_lerp(start_pos, end_pos, .5)

        for locator in ["Start", "Mid", "End"]:
            # For each item in list, create a locator and joint, and parent the joint to the locator
            newloc = cmds.spaceLocator(n=partname + "_" + locator + "_LOC")
            cmds.joint(n=partname + "_" + locator + "_JNT")
            cmds.parent(newloc, partname + "_RIGJOINTS")
        startloc = partname + "_Start_LOC"
        midloc = partname + "_Mid_LOC"
        endloc = partname + "_End_LOC"

        cmds.xform(startloc, t=start_pos, ro=start_rot, ws=1)
        cmds.xform(midloc, t=mid_pos, ro=start_rot, ws=1)
        cmds.xform(endloc, t=end_pos, ro=start_rot, ws=1)

        # Set joint orient for the start joint using a temporary joint placed at the end object location
        tempjnt = cmds.joint(n="temp_JNT")
        cmds.xform(tempjnt, t=end_pos, ws=1)
        cmds.parent(tempjnt, partname + "_Start_JNT")
        cmds.joint(partname + "_Start_JNT", e=1, oj="xyz")
        cmds.delete(tempjnt)

        # Copy joint orient from start joint and apply to all subsequent joints
        for joint in ["Mid", "End"]:
            cmds.joint(partname + "_" + joint + "_JNT", e=1, o=(cmds.joint(partname + "_Start_JNT", q=1, o=1)))

        # Create curve based on joint positions, then duplicate first joint and parent curve to joint
        for i, trans in zip(["A", "B"], [(0, 1, 0), (0, -1, 0)]):
            newcrv = cmds.curve(n=partname + "_" + i + "_CrvTemp", d=1,
                                p=[start_pos,
                                   self.vector_lerp(start_pos, end_pos, .25),
                                   self.vector_lerp(start_pos, end_pos, .50),
                                   self.vector_lerp(start_pos, end_pos, .75),
                                   end_pos])
            newjnt = cmds.duplicate(partname + "_Start_JNT", n=partname + "_" + i + "_JNT")
            cmds.parent(newcrv, newjnt)
            cmds.parent(newjnt, w=1)
            # Move both joints 1 unit away from each other in +y and -y
            cmds.xform(newjnt[0], t=trans, r=1, os=1)

        # Loft the two curves to create a NURBS surface
        nrbpatch = cmds.loft(partname+ "_A_CrvTemp", partname + "_B_CrvTemp", n=partname + "_NRB")
        nrbpatch = cmds.bakePartialHistory(nrbpatch)

        # Rebuild the surface to be smooth rather than faceted
        cmds.rebuildSurface(nrbpatch, rpo=1)

        # Delete two temporary curves, as they aren't needed any more
        for i in ["A", "B"]:
            cmds.delete(partname + "_" + i + "_JNT")

        return nrbpatch, (startloc, midloc, endloc)


    def jointbasednurbpatch(self, partname="",
                            startjnt="", endjnt="",
                            maxjntcount=21, reverse=False):
        # Create list for all the joints between startjnt and endjnt
        rbnjnts = [endjnt]
        # Start at endjnt, go upwards until you hit startjnt, adding each joint to the Spinejnts list
        # Max out at (maxjntcount) passes through this array, in which case throw an error
        for joint in range(0, maxjntcount):
            if 1 < joint < (maxjntcount-1):
                rbnjnts.append(tempjnt[0])
                tempjnt = cmds.listRelatives(tempjnt, p=1)
                if tempjnt[0] == startjnt:
                    break
            elif joint == maxjntcount-1:
                print("Could not find " + startjnt + " during this loop, check that it is correctly named")
                break
            elif joint == 0:
                tempjnt = cmds.listRelatives(endjnt, p=1)

        rbnjnts.append(startjnt)

        # Reverse rbnjnts, as the list will be created in reverse order, starting at endjnt and ending at startjnt
        rbnjnts.reverse()

        rbnjntscount = len(rbnjnts)

        # Append each joints' positions to rbnjntspos
        rbnjntspos = []
        for joint in rbnjnts:
            rbnjntspos.append(cmds.xform(joint, t=1, q=1, ws=1))

        for i, trans in zip(["A", "B"], [(0, 1, 0), (0, -1, 0)]):
            newcrv = cmds.curve(n=partname + "_" + i + "_CrvTemp", d=1, p=rbnjntspos)
            cmds.select(d=1)
            newjnt = cmds.duplicate(partname + "_1_JNT", n=partname + "_" + i + "_JNT", po=1)
            cmds.parent(newcrv, newjnt)
            cmds.parent(newjnt, w=1)
            # Move both joints 1 unit away from each other in +y and -y
            cmds.xform(newjnt, t=trans, r=1, os=1)

        # Loft the two curves to create a NURBS surface
        nrbpatch = cmds.loft(partname + "_A_CrvTemp", partname + "_B_CrvTemp", n=partname + "_NRB")
        nrbpatch = cmds.bakePartialHistory(nrbpatch)

        # Delete two temporary curves, as they aren't needed any more
        for i in ["A", "B"]:
            cmds.delete(partname + "_" + i + "_JNT")

        return nrbpatch, rbnjntscount


    def ribbon_setup(self, partname="",
                     startjnt="", endjnt="",
                     bindjointcount=5, method="twoloc",
                     skin=True, reverse=False):
        # To be used by other parts of this script or externally for creating ribbon rigs
        # Create a group for the current ribbon setup, and make some child groups for it
        rbngrp = cmds.group(n=partname + "_RBN_Rig", em=1)
        for group in ["FOLLICLES", "RIGJOINTS"]:
            cmds.group(n=partname + "_" + group, p=partname + "_RBN_Rig", em=1)
        if method == "twoloc":
            nrbpatch = self.twopointnurbpatch(partname=partname,
                                              startjnt=startjnt, endjnt=endjnt)
        elif method == "jointbased":
            nrbpatch = self.jointbasednurbpatch(partname=partname,
                                                startjnt=startjnt, endjnt=endjnt,
                                                reverse=reverse)
            bindjointcount = nrbpatch[1]

        cmds.parent(nrbpatch[0], partname + "_RBN_Rig")

        rbnjoints = []

        # Create a specific number of follicles on the new NURBS surface based on bindjointcount
        foll_cur_name = 0
        flcgrp = partname + "_FOLLICLES"
        for i in range(0, bindjointcount):
            # Create follicle on the nurbs surface using the create_follicle function
            # Then rename it and parent it to the FOLLICLES group
            follicle = self.create_follicle(nrbpatch[0][0], 0.5, i / (bindjointcount - 1.00))
            follicle = cmds.listRelatives(follicle, p=1)
            newfol = cmds.rename(follicle, partname + "_" + str(foll_cur_name) + "_FLC")
            cmds.parent(newfol, flcgrp)

            # Create joint for follicle and parent to follicle
            jnt = cmds.joint(n=newfol.replace("_FLC", "_Connect_JNT"))
            rbnjoints.append(jnt)
            foll_cur_name = foll_cur_name + 1


        if skin:
            # Create a list of the joints to be used for skinning the nrb surface
            rbnskinjoints = [
                partname + "_Start_JNT", partname + "_End_JNT", partname + "_Mid_JNT"
            ]

            # Apply a skinCluster to the nrb surface using the joints in rbnskinjoints
            cmds.skinCluster(rbnskinjoints, nrbpatch[0], n=partname + "_RBN_SkinCluster")

        cmds.hide(rbngrp)
        for i in [rbngrp, flcgrp]:
            self.lockhideattr(i, hide=False)
        self.lockhideattr(partname + "_RIGJOINTS", translate=False, rotate=False, hide=False)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

        return nrbpatch[1], rbnjoints, rbngrp


    def character_setup(self):
        # Create character's group setup
        pgroup = self.char_name + "_CharacterRig"
        # If the group does not exist, create one
        if not cmds.ls(pgroup):
            parentgroup = cmds.group(n=pgroup, em=1)
        else:
            parentgroup = pgroup
        self.lockhideattr(pgroup, hide=False)

        # Create the sub-groups for the main group
        for group in ["Meshes", "BindJoints", "Rig"]:
            if not cmds.ls(self.char_name + "_" + group):
                newgrp = cmds.group(n=self.char_name + "_" + group, p=parentgroup, em=1)
                self.lockhideattr(newgrp, hide=False)

        main_rig_group = self.char_name + "_Rig"

        # Create root control at 0,0,0 and parent it to the _Rig group
        rootgroup = self.controllers_setup(partname="Root", scale=(40,40,40), rotation=(90,0,0))
        cmds.parent(rootgroup[0], main_rig_group)

        # Lock and hide scale and vis on root ctrl
        self.lockhideattr(rootgroup[1], translate=False, rotate=False)

        # Create 3 display layers, one each for Meshes, Joints, and Controls
        displayers = []
        for dl in ["Meshes", "Joints", "Controls"]:
            if not cmds.ls(dl + "_Disp"):
                cmds.createDisplayLayer(n=dl + "_Disp", e=1)
            displayers.append(dl + "_Disp")

        # Add Root_CTRL to Controls display layer
        cmds.editDisplayLayerMembers(displayers[2], rootgroup[1])

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

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
                tempjnt = cmds.listRelatives(tempjnt, p=1)
                if tempjnt[0] == startjnt:
                    break
            elif joint == 20:
                print("Could not find " + startjnt + " during this loop, check that it is correctly named")
                break
            elif joint == 0:
                tempjnt = cmds.listRelatives(endjnt, p=1)

        spinejnts.append(startjnt)

        # Reverse Spinejnts, as the list will be created in reverse order, starting at endjnt and ending at startjnt
        spinejnts.reverse()

        # Create ribbon for spine based on startjnt and endjnt
        spinerbnlocs = self.ribbon_setup(partname="Ct_Spine", startjnt=startjnt,
                                         endjnt=endjnt, method="twoloc",
                                         bindjointcount=6)

        # Create a control for the Hips at the Ct_Hips_JNT location
        hipsgrp =  self.controllers_setup(partname="Hips", shape="cube",
                                          scale=(50,5,40) * scale, rotation=rotation)
        cmds.xform(hipsgrp[0], ws=1, t= cmds.xform(startjnt, ws=1, t=1,  q=1))
        cmds.xform(hipsgrp[0], ws=1, ro=cmds.xform(startjnt, ws=1, ro=1, q=1))
        # Create a control for the Chest bend at the position of the middle locator from the ribbon
        chestgrp = self.controllers_setup(partname="Chest", shape="cube",
                                          scale=(50,5,40), rotation=rotation)
        cmds.xform(chestgrp[0], ws=1, t= cmds.xform(spinerbnlocs[0][1], ws=1, t=1,  q=1))
        cmds.xform(chestgrp[0], ws=1, ro=cmds.xform(spinerbnlocs[0][1], ws=1, ro=1, q=1))

        self.lockhideattr(hipsgrp[1], translate=False, rotate=False)
        self.lockhideattr(chestgrp[1], rotate=False)

        # Parent the chest's offset group to the Hips' Controller
        cmds.parent(chestgrp[0], hipsgrp[1])

        # Move the chest Ctrl's pivot to the position of the first spine joint
        cmds.xform(chestgrp[1], piv=(cmds.xform(spinejnts[0], q=1, ws=1, t=1)), ws=1)

        # Parent constrain the controllers to the ribbon's locators
        # Parent constrain the Hips_CTRL to the first locator on the spine ribbon
        cmds.parentConstraint(hipsgrp[1], spinerbnlocs[0][0], mo=1)
        # Parent constrain the Chest_CTRL to the second locator on the spine ribbon
        cmds.parentConstraint(spinerbnlocs[0][0], spinerbnlocs[0][2], spinerbnlocs[0][1], mo=1)
        # Parent constrain the Chest_CTRL to the third locator on the spine ribbon
        cmds.parentConstraint(chestgrp[1], spinerbnlocs[0][2], mo=1)

        # Parent constrain ribbon joints to bind joints
        for bindjnt, connectjnt in zip(spinejnts, spinerbnlocs[1]):
            cmds.parentConstraint(connectjnt, bindjnt, mo=1)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

        return hipsgrp, chestgrp, "Ct_Spine_RBN_Rig"


    def neck_setup(self, neckjnt="",
                   scale=1, rotation=(0,-90,0),
                   position=(5,0,-3)):
        # Create neck controller and position it at the location of the neck joint
        neckgrp = self.controllers_setup(partname="Neck", shape="circle",
                                         scale=(10,10,10) * scale,
                                         rotation=rotation,
                                         position=position)
        neckpos = cmds.xform(neckjnt, q=1, ws=1,  t=1)
        neckrot = cmds.xform(neckjnt, q=1, ws=1, ro=1)
        cmds.xform(neckgrp, ws=1, t=neckpos, ro=neckrot)

        # Make sure that the controller's pivot is where the Neck joint is
        cmds.xform(neckgrp[1], piv=(cmds.xform(neckjnt, q=1, ws=1, t=1)), ws=1)

        # Parent constrain the neck controller to the neck joint
        cmds.parentConstraint(neckgrp[1], neckjnt, mo=1)

        # Lock and hide all attrs other than rotation
        self.lockhideattr(neckgrp[1], rotate=False)

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

        return neckgrp


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

        # Create a group for the overall arm setup
        armgrp = cmds.group(n=side + "_Arm", p=self.char_name + "_Rig", em=1)
        self.lockhideattr(armgrp, hide=False)

        # FKIK SETUP

        # Duplicate shoulder setup and rename all joints under it and including itself
        fkikgrp = cmds.group(n=side + "_Arm_FKIK", p=armgrp, em=1)
        cmds.hide(fkikgrp)
        self.lockhideattr(fkikgrp, hide=False)
        shouldupl = cmds.duplicate(shouljnt, n=shouljnt.replace("_JNT", "_Connect_JNT"))
        cmds.parent(shouldupl[0], fkikgrp)
        for childjnt in cmds.listRelatives(shouldupl[0], c=1, ad=1, f=1):
            # Rename each child joint to have the same _Connect_JNT naming
            # The split("|")[-1] is to select the last part of the fullpath object name, convert
            #       to string, and then replace the name
            cmds.rename(childjnt, str(childjnt.split("|")[-1]).replace("_JNT", "_Connect_JNT"))

        # Create a list with the _Connect_JNT joints in it
        connectjnts = []
        for jnt in range(0,3):
            connectjnts.append(side + "_Arm_" + str(jnt) + "_Connect_JNT")

        # Delete unneeded joints
        cmds.delete(cmds.listRelatives(wristjnt.replace("_JNT", "_Connect_JNT"), c=1, f=1)[0])

        # Duplicate twice for FK and IK joint chains
        for ikfk in ["FK", "IK"]:
            newshoul = cmds.duplicate(shouldupl[0], n=shouldupl[0].replace("_Connect_JNT", "_" + ikfk + "_JNT"))
            for childjnt in cmds.listRelatives(newshoul[0], c=1, ad=1, f=1):
                # Rename each child joint to have the same _IKFK_JNT naming
                cmds.rename(childjnt, str(childjnt.split("|")[-1]).replace("_Connect_JNT", "_" + ikfk + "_JNT"))

        # Create constraints from IK and FK joints to the Connect joints
        cmds.parentConstraint(shouljnt.replace("_JNT", "_FK_JNT"),
                              shouljnt.replace("_JNT", "_IK_JNT"),
                              shouljnt.replace("_JNT", "_Connect_JNT"))
        for jnts in [cmds.listRelatives(wristjnt, p=1)[0], wristjnt]:
            cmds.orientConstraint(jnts.replace("_JNT", "_FK_JNT"),
                                  jnts.replace("_JNT", "_IK_JNT"),
                                  jnts.replace("_JNT", "_Connect_JNT"))


        # SCAPULA

        # Create controller for scapula, then position and set pivot point for group and controller
        scapulagrp = self.controllers_setup(partname=side + "_Scapula", shape="scapctrl",
                                            position=(14,0,0), scale=(4,4,4),
                                            colour=colour)
        cmds.xform(scapulagrp[0], t=cmds.xform(scapjnt, q=1, t=1, ws=1), ws=1)
        if flipped:
            cmds.xform(scapulagrp[0], s=(-1,1,1))
        cmds.xform(scapulagrp[1], piv=(cmds.xform(scapjnt, q=1, t=1, ws=1)), ws=1)

        self.lockhideattr(scapulagrp[1], rotate=False)
        self.lockhideattr(scapulagrp[0], translate=False, rotate=False)


        # Create a locator parented to the scapula in the position of the shouljnt
        shoulloc = cmds.spaceLocator(n=side + "_Scapula_Shoulder_LOC")
        cmds.xform(shoulloc, t=(cmds.xform(shouljnt, t=1, q=1, ws=1)), ws=1)
        cmds.parent(shoulloc[0], scapulagrp[1])
        cmds.setAttr(shoulloc[0] + ".visibility", 0)
        self.lockhideattr(shoulloc[0])

        # Scapula ctrl to scapula jnt constraint
        cmds.parentConstraint(scapulagrp[1], scapjnt, mo=1)

        # Parent scapula group to the arm group
        cmds.parent(scapulagrp[0], armgrp)


        # ARM ATTRS SETUP

        # Create pointedsquare control and position at shoulder location
        if flipped:
            armattrsgrp = self.controllers_setup(partname=side + "_Arm_Attrs", shape="pointedsquare",
                                                 scale=(-6,6,6), colour=colour)
        else:
            armattrsgrp = self.controllers_setup(partname=side + "_Arm_Attrs", shape="pointedsquare",
                                                 scale=(6,6,6), colour=colour)
        cmds.xform(armattrsgrp, t=(cmds.xform(shoulloc, t=1, q=1, ws=1)), ws=1)

        # Parent arm attrs group to arm group
        cmds.parent(armattrsgrp[0], armgrp)

        # Parent constrain arm attrs group to the scapula's
        cmds.parentConstraint(shoulloc[0], armattrsgrp[0], mo=1)

        self.lockhideattr(armattrsgrp[1])
        self.lockhideattr(armattrsgrp[0], translate=False, rotate=False)


        # Create FKIK, and space switching attributes for each arm
        cmds.select(armattrsgrp[1])
        cmds.addAttr(sn="FKIK", ln="FKIK", min=0, max=1, dv=0, ex=1, h=0, k=1)
        cmds.addAttr(sn="Pos_SS", ln="Position_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.addAttr(sn="Rot_SS", ln="Rotation_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.select(d=1)

        # FKIK switching setup
        # Create math node to reverse (1 - fkikattr)
        fkikreverse = cmds.createNode("floatMath", n=side + "_Arm_FKIK_Reverse_FM")
        cmds.setAttr(fkikreverse + ".operation", 1)
        cmds.connectAttr(armattrsgrp[1] + ".FKIK", fkikreverse + ".floatB")

        for connectjnt in [shouljnt, cmds.listRelatives(wristjnt, p=1)[0], wristjnt]:
            if connectjnt in shouljnt:
                ocpc = "parent"
            else:
                ocpc = "orient"
            constraint = connectjnt.replace("_JNT", "_Connect_JNT") + "_" + ocpc + "Constraint1"
            cmds.connectAttr(armattrsgrp[1] + ".FKIK", constraint + "." + connectjnt.replace("_JNT", "_IK_JNT") + "W1")
            cmds.connectAttr(fkikreverse + ".outFloat", constraint + "." + connectjnt.replace("_JNT", "_FK_JNT") + "W0")


        # IK SETUP
        # Check that the IK shoulder joint's Preffered Angle is 0,0,0
            for xyz in ["X", "Y", "Z"]:
                cmds.setAttr(connectjnt.replace("_JNT", "_IK_JNT") + ".preferredAngle" + xyz, 0)

        # Create an IK handle for the IK joints
        arm_ikh = cmds.ikHandle(sj=shouljnt.replace("_JNT", "_IK_JNT"), ee=wristjnt.replace("_JNT", "_IK_JNT"), n=side + "_Arm_IK_IKH")
        cmds.hide(arm_ikh)

        # Parent IK handle to the arm group
        cmds.parent(arm_ikh[0], armgrp)

        # Parent constrain Connect joints to bind joints
        for connectjnt in [shouljnt, cmds.listRelatives(wristjnt, p=1)[0], wristjnt]:
            cmds.parentConstraint(connectjnt.replace("_JNT", "_Connect_JNT"), connectjnt)


        # CONTROLS
        # FK Controls
        fkctrls = []
        fkgrps = []
        for fkjoint in [shouljnt, cmds.listRelatives(wristjnt, p=1)[0], wristjnt]:
            fkgrp = self.controllers_setup(partname=fkjoint.replace("_JNT", "_FK"), shape="circle",
                                           colour=colour, scale=(6,6,6),
                                           rotation=(0,90,0))
            cmds.xform(fkgrp[0], t=(cmds.xform(fkjoint, t=1, q=1, ws=1)), ro=(cmds.xform(fkjoint, ro=1, q=1, ws=1)), ws=1)
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
        cmds.parentConstraint(scapulagrp[1], shouljnt.replace("_JNT", "_FK_GRP"), mo=1)

        # Point constrain Shoulder IK joint to Scapula
        cmds.pointConstraint(shoulloc, shouljnt.replace("_JNT", "_IK_JNT"), mo=1)

        # Set vis for Shoulder FK group based on FKIK attr
        cmds.connectAttr(fkikreverse + ".outFloat", shouljnt.replace("_JNT", "_FK_GRP") + ".visibility")

        for fkgrp in fkgrps:
            self.lockhideattr(fkgrp[0])
            self.lockhideattr(fkgrp[1], rotate=False)


        # IK Controls
        # IKHandle control
        ikgrp = self.controllers_setup(partname=side + "_Arm_IK", shape="starcircle",
                                       colour=colour, scale=(6,6,6),
                                       rotation=(0,90,0))
        cmds.xform(ikgrp[0], t=(cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), t=1, q=1, ws=1)),
                   ro=(cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), ro=1, q=1, ws=1)), ws=1)
        cmds.parentConstraint(ikgrp[1], arm_ikh[0])
        cmds.orientConstraint(ikgrp[1], wristjnt.replace("_JNT", "_IK_JNT"))
        cmds.parent(ikgrp[0], armgrp)
        cmds.connectAttr(armattrsgrp[1] + ".FKIK", ikgrp[0] + ".visibility")

        self.lockhideattr(ikgrp[0], translate=False, rotate=False, visibility=False)
        self.lockhideattr(ikgrp[1], translate=False, rotate=False)

        # PV Control
        pvgrp = self.controllers_setup(partname=side + "_Arm_IK_PV", shape="starcircle",
                                       colour=colour, scale=(6,6,6),
                                       rotation=(0,0,0))
        cmds.xform(pvgrp[0],
                   t=(self.vector_lerp(cmds.xform(shouljnt.replace("_JNT", "_IK_JNT"), q=1, t=1, ws=1),
                                       cmds.xform(wristjnt.replace("_JNT", "_IK_JNT"), q=1, t=1, ws=1),
                                       .5)), ws=1)
        tempaimconst = cmds.aimConstraint((cmds.listRelatives(wristjnt, p=1)[0]).replace("_JNT", "_IK_JNT"), pvgrp[0])
        cmds.delete(tempaimconst)
        cmds.xform(pvgrp[0], t=(50,0,0), r=1, os=1)

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
            loc = cmds.spaceLocator(n=side + "_" +obj + "_SS_LOC")[0]
            cmds.xform(loc, t=cmds.xform(ikgrp[1], q=1, t=1, ws=1), ws=1)
            cmds.parent(loc, obj)
            cmds.hide(loc)

            self.lockhideattr(loc)

        constraintslocs = []
        for entry in constraints:
            constraintslocs.append(side + "_" + entry + "_SS_LOC")

        cmds.pointConstraint(constraintslocs, ikgrp[0], mo=1)
        cmds.orientConstraint(constraintslocs, ikgrp[0], mo=1)

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

        # Ribbon Twist Setup
        if twist:
            # Upper Arm Twist
            arm0rbn = self.ribbon_setup(partname=side + "_0_Twist_RBN",
                                        startjnt=connectjnts[0], endjnt=connectjnts[1],
                                        bindjointcount=6)
            cmds.parent(arm0rbn[2], self.char_name + "_Rig")

            # Connect shoulder loc to upper loc
            cmds.parentConstraint(shoulloc, arm0rbn[0][0], mo=1)
            # Constrain middle ribbon locator to both end joints
            midconst = cmds.parentConstraint(cmds.listRelatives(arm0rbn[0][2], c=1, type="joint"),
                                  cmds.listRelatives(arm0rbn[0][0], c=1, type="joint"),
                                  arm0rbn[0][1], mo=1)
            cmds.setAttr(midconst[0] + ".interpType", 0)
            # Connect Connect_0_JNT to lower loc
            cmds.parentConstraint(side + "_Arm_0_Connect_JNT", arm0rbn[0][2], mo=1)
            # Connect Connect_0_JNT to lower jnt
            cmds.parentConstraint(side + "_Arm_0_Connect_JNT", cmds.listRelatives(arm0rbn[0][0], c=1, type="joint"), sr="x", mo=1)

            # Lower Arm Twist
            arm1rbn = self.ribbon_setup(partname=side + "_1_Twist_RBN",
                                        startjnt=connectjnts[1], endjnt=connectjnts[2],
                                        bindjointcount=6)
            cmds.parent(arm1rbn[2], self.char_name + "_Rig")

            # Parent Constrain lower arm ribbon group to the elbow _Connect_JNT
            cmds.parentConstraint(connectjnts[1], cmds.listRelatives(arm1rbn[0][0], p=1, type="transform"), mo=1)

            # Constrain middle ribbon locator to both end joints
            midconst = cmds.parentConstraint(cmds.listRelatives(arm1rbn[0][2], c=1, type="joint"),
                                  cmds.listRelatives(arm1rbn[0][0], c=1, type="joint"),
                                  arm1rbn[0][1], mo=1)
            cmds.setAttr(midconst[0] + ".interpType", 0)

            # If a right arm, needs to have +180 to the rotateX attr, else can be connected straight from rotateX to rotateX
            if flipped:
                invnode = cmds.createNode("floatMath", n=side + "_1_Twist_RBN_plus180x_FM")
                cmds.connectAttr(connectjnts[2] + ".rotateX", invnode + ".floatA")
                cmds.setAttr(invnode + ".floatB", 180)
                cmds.connectAttr(invnode + ".outFloat", arm1rbn[0][2] + ".rotateX")
            else:
                cmds.connectAttr(connectjnts[2] + ".rotateX", arm1rbn[0][2]  + ".rotateX")

            # Create upper twist joints and attach to bind skeleton
            for cnctjnt, slicenum in zip(["0", "1"], [[0,1], [1,2]]):
                for jnt, perc in zip(range(1,5), [.2, .4, .6, .8]):
                    newjnt = cmds.joint(n=side + "_Arm_" + cnctjnt + "_Twist_" + str(jnt) + "JNT")
                    cmds.xform(newjnt,
                               t=self.vector_lerp(cmds.xform(connectjnts[slicenum[0]], t=1, q=1, ws=1),
                                                  cmds.xform(connectjnts[slicenum[1]], t=1, q=1, ws=1),
                                                  perc),
                               ro=(cmds.xform(connectjnts[slicenum[0]], ro=1, q=1, ws=1)), ws=1)
                    if jnt == 1:
                        cmds.makeIdentity(newjnt)
                        cmds.parent(newjnt, connectjnts[slicenum[0]].replace("_Connect_JNT", "_JNT"))
                    elif jnt == 4:
                        cmds.parent(connectjnts[slicenum[1]].replace("_Connect_JNT", "_JNT"), newjnt)
                cmds.select(d=1)


            # Parent constrain joints to bind skeleton
            for cnctjnt in ["0", "1"]:
                for jnt in range(0,5):
                    if 1 < jnt < 5:
                        cmds.parentConstraint(side + "_" + cnctjnt + "_Twist_RBN_" + str(jnt) + "_Connect_JNT",
                                              side + "_Arm_" + cnctjnt + "_Twist_" + str(jnt) + "JNT", mo=1)
                    elif jnt == 0:
                        cmds.delete(cmds.listRelatives(side + "_Arm_" + cnctjnt + "_JNT", c=1, type="constraint"))
                        cmds.parentConstraint(side + "_" + cnctjnt + "_Twist_RBN_" + str(jnt) + "_Connect_JNT",
                                              side + "_Arm_" + cnctjnt + "_JNT", mo=1)


        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)


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
        handgrp = cmds.group(n=side + "_Hand_GRP", em=1)

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
                fingernameshort = side + "_" + finger + "_" + str(fjoint)

                # Create a controller for the fingers, with seperate controller setups for the first
                # joint in each finger, with joint 0's controller being parallel to the joint
                if fjoint == 0:
                    fingergrp = self.controllers_setup(partname=fingernameshort, shape="square",
                                                       colour=colour, rotation=(0,0,0),
                                                       scale=(4,1,2), position=(2,0,3))
                    # Fix the pivot point for the controller to make sure it matches the joint's position
                    cmds.xform(fingergrp[1], piv=(cmds.xform(fingergrp[0], t=1, q=1, ws=1)), ws=1)
                else:
                    fingergrp = self.controllers_setup(partname=fingernameshort, shape="square",
                                                       colour=colour, rotation=(0,90,0),
                                                       scale=(2,2,3))

                # Create an offset group, in the same position/rotation as the finger joint's group. (0,0,0) relatively
                # This is used for the hand's Fist and Spread attributes
                offsetgrp = cmds.group(n=fingernameshort + "_Offset_GRP", em=1, p=fingergrp[0])
                # Then parent the controller to the offset group
                cmds.parent(fingergrp[1], offsetgrp)

                # Get the position/rotation of the joint, and place the controller's group where the joint is
                # If this is for the right side hand, get all the transforms and rotations from the left hand
                # to position the controller's group in the correct position, as it'll be flipped later
                if flipped:
                    cmds.xform(fingergrp[0], t=(cmds.xform(fingernameshort.replace("Rt", "Lf") + "_JNT", q=1, t=1, ws=1)),
                               ro=(cmds.xform(fingernameshort.replace("Rt", "Lf") + "_JNT", q=1, ro=1, ws=1)), ws=1)
                else:
                    cmds.xform(fingergrp[0], t=(cmds.xform(fingernameshort + "_JNT", q=1, t=1, ws=1)),
                               ro=(cmds.xform(fingernameshort + "_JNT", q=1, ro=1, ws=1)), ws=1)

                # For the first controller's group, parent it to the handgrp group
                if fjoint == 0:
                    cmds.parent(fingergrp[0], handgrp)
                # and for subsequent controllers, parent the controller's group to the previous controller
                else:
                    cmds.parent(fingergrp[0], side + "_" + finger + "_" + str(fjoint-1) + "_CTRL")


        # Create controller for hand attributes (Fist, Spread)
        handattrsgrp = self.controllers_setup(partname=side + "_Hand_Attrs", shape="starcircle", position=(0,0,4), scale=(2,2,2), colour=colour)
        # Position and rotate the controller at the hand location
        cmds.xform(handattrsgrp, t=(cmds.xform("Lf" + "_Hand_1_JNT", t=1, q=1, ws=1)),
                   ro=(cmds.xform("Lf" + "_Hand_1_JNT", ro=1, q=1, ws=1)), ws=1)
        # Parent to main hand group
        cmds.parent(handattrsgrp[0], handgrp)

        # Create Fist and Spread attributes on hand attr control
        for attr in ["Fist", "Spread"]:
            cmds.addAttr(handattrsgrp[1], sn=attr, ln=attr, min=0, max=1, dv=0, ex=1, h=0, k=1)


        # Hand Fist
        # Create Remap node for first joint in fingers
        fingeroneremap =   cmds.createNode("remapValue", n=side + "_Finger_1_Fist_REMAP")
        cmds.setAttr(fingeroneremap + ".outputMax", 70)
        fingertwothreeremap = cmds.createNode("remapValue", n=side + "_Finger_23_Fist_REMAP")
        cmds.setAttr(fingertwothreeremap + ".outputMax", 90)

        thumbzeroremap = cmds.createNode("remapValue", n=side + "_Finger_0_Fist_REMAP")
        cmds.setAttr(thumbzeroremap + ".outputMax", 10)
        thumbonetworemap = cmds.createNode("remapValue", n=side + "_Thumb_12_Fist_REMAP")
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
        cmds.connectAttr(thumbzeroremap + ".outValue", side + "_Thumb_0_Offset_GRP.rotateY")
        for joint in range(1, 3):
            cmds.connectAttr(thumbonetworemap+ ".outValue",
                             side + "_Thumb_" + str(joint) + "_Offset_GRP.rotateY")


        # Hand Spread
        for finger, remapvalue in zip(fingers, [-20, -10, -3, 10, 20]):
            if finger == "Thumb":
                joint = 0
            else:
                joint = 1
            remapnode = cmds.createNode("remapValue", n=side + "_" + finger + "_" + str(joint) + "_Spread_REMAP")
            cmds.setAttr(remapnode + ".outputMax", remapvalue)
            cmds.connectAttr(handattrsgrp[1] + ".Spread", remapnode + ".i")
            cmds.connectAttr(remapnode + ".outValue", side + "_" + finger + "_" + str(joint) + "_Offset_GRP.rotateZ")


        # Flip the entire handgrp group if this is for a right side hand
        if flipped:
            cmds.xform(handgrp, s=(-1,1,1))


        # Loop through each finger for parent constraining each control to it's joint, and attribute locking and hiding
        for finger in fingers:
            # Set finger joint count for thumb seperately, as it only has 3 joints
            if finger == "Thumb":
                fingercount = 3
            else:
                fingercount = 4

            for fjoint in range(0, fingercount):
                # Set up a variable for the finger naming
                fingernameshort = side + "_" + finger + "_" + str(fjoint)

                # Create parent constraints from each finger controller to it's respective joint
                cmds.parentConstraint(fingernameshort + "_CTRL", fingernameshort + "_JNT", mo=1)

                # Lock and hide respective attributes for each control
                for xyz in ["X", "Y", "Z"]:
                    # Lock and hide translate, rotation, and scale for each main joint group
                    for attr in ["translate", "rotate", "scale"]:
                        cmds.setAttr(fingernameshort + "_GRP." + attr + xyz, l=1)
                        cmds.setAttr(handattrsgrp[0] + "." + attr + xyz, l=1, k=0)
                        cmds.setAttr(handattrsgrp[1] + "." + attr + xyz, l=1, k=0)
                    # Lock and hid translate and scale for offset groups and controls
                    for attr in ["translate", "scale"]:
                        cmds.setAttr(fingernameshort + "_Offset_GRP." + attr + xyz, l=1)
                        cmds.setAttr(fingernameshort + "_CTRL." + attr + xyz, l=1, k=0)

                # Lock and hide visibility for each grp, offset grp, and control
                cmds.setAttr(fingernameshort + "_GRP.visibility", l=1)
                cmds.setAttr(fingernameshort + "_Offset_GRP.visibility", l=1, k=0)
                cmds.setAttr(fingernameshort + "_CTRL.visibility", l=1, k=0)
                cmds.setAttr(handattrsgrp[1] + ".visibility", l=1, k=0)


        cmds.parent(handgrp, self.char_name + "_Rig")

        # Deselect everything to make sure it doesn't mess with other parts of the code
        cmds.select(d=1)

        class Hand:
            def __init__(self, handgrp):
                self.handgrp = handgrp
            
        return Hand(handgrp)


    def curve_rig(self, partname="",
                  startjnt="", endjnt=""):
        # Create curve based ribbon based on the joints from startjnt to endjnt
        crvrbn = self.ribbon_setup(partname=partname,
                                   startjnt=startjnt, endjnt=endjnt,
                                   method="jointbased", skin=False,
                                   reverse=True)

        # Parent the curve's group to the _Rig group
        cmds.parent(crvrbn[2], self.char_name + "_Rig")

        # Parent constrain the ribbon's joints to the bind joints
        for jnt in range(0, crvrbn[0]):
            cmds.parentConstraint(partname + "_" + str(jnt) + "_Connect_JNT", partname + "_" + str(jnt+1) + "_JNT", mo=1)

        return crvrbn


    def fkchain(self, partname="",
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
            fkgrp = self.controllers_setup(partname=partname + "_" + str(num), shape=shape,
                                           scale=(3*scale, 3*scale, 3*scale))
            cmds.xform(fkgrp[0], t=(cmds.xform(jnt, t=1, q=1, ws=1)), ro=(cmds.xform(jnt, ro=1, q=1, ws=1)), ws=1)
            if num == 0:
                fkgrpone = fkgrp
                self.lockhideattr(fkgrp[0], translate=False, rotate=False)
                self.lockhideattr(fkgrp[1], rotate=False)
            else:
                cmds.parent(fkgrp[0], partname + "_" + str(num-1) + "_CTRL")
                self.lockhideattr(fkgrp[0])
                self.lockhideattr(fkgrp[1], rotate=False)
            cmds.parentConstraint(fkgrp[1], jnt)

        # Parent the first FK controller's group to the _Rig group
        cmds.parent(fkgrpone[0], self.char_name + "_Rig")

        cmds.select(d=1)

        return fkgrpone


    def digileg(self, partname="",
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
        leggrp = cmds.group(n=partname, em=1)
        cmds.parent(leggrp, self.char_name + "_Rig")


        # Create FKIK setup
        legfkikgrp = cmds.group(n=partname + "_FKIK", em=1, p=leggrp)
        # Duplicate startjnt > heeljnt
        for cnt, jnt in enumerate([startjnt, kneejnt, anklejnt, heeljnt]):
            newjnt = cmds.duplicate(jnt, po=1, n=jnt.replace("_JNT", "_Connect_JNT"))
            if jnt == startjnt:
                cnctjntone = newjnt[0]
                cmds.parent(newjnt, w=1)
            else:
                cmds.parent(newjnt, startjnt.replace("0", str(cnt-1)).replace("_JNT", "_Connect_JNT"))

        cmds.parent(cnctjntone, legfkikgrp)

        for fkik in ["FK", "IK"]:
            tempjnt = cmds.duplicate(cnctjntone, n=cnctjntone.replace("Connect", fkik))
            for childjnt in cmds.listRelatives(tempjnt[0], c=1, ad=1, f=1):
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
        fkjnts = cmds.listRelatives(cnctjntone.replace("Connect", "FK"), ad=1, c=1)
        fkjnts.append(cnctjntone.replace("Connect", "FK"))
        fkjnts.reverse()
        for cnt, jnt in enumerate(fkjnts):
            fkgrp = self.controllers_setup(partname=partname + "_FK_" + str(cnt), scale=(10,10,10), rotation=(0,90,0), colour=colour)
            cmds.xform(fkgrp[0], t=(cmds.xform(jnt, t=1, q=1, ws=1)), ro=(cmds.xform(jnt, ro=1, q=1, ws=1)), ws=1)
            self.lockhideattr(fkgrp[1], rotate=False)
            if cnt == 0:
                fkgrpone = fkgrp
                cmds.parent(fkgrp[0], leggrp)
            else:
                cmds.parent(fkgrp[0], partname + "_FK_" + str((cnt-1)) + "_CTRL")
            cmds.parentConstraint(fkgrp[1], jnt)


        # Create secondary IK Leg
        # Create reverse Foot>Ankle joint chain
        # Create IK Foot controller and PV control
        ikgrp = self.controllers_setup(partname=partname + "_IK_Foot", shape="circle", rotation=(90,0,0), scale=(10,10,20), colour=colour)
        footjntpos = cmds.xform(footjnt, t=1, q=1, ws=1)
        cmds.xform(ikgrp[0], t=(footjntpos[0], 0, footjntpos[2]), ws=1)
        cmds.parent(ikgrp[0], leggrp)
        self.lockhideattr(ikgrp[0], visibility=False)
        self.lockhideattr(ikgrp[1], rotate=False, translate=False)

        # Create IK Reverse Controller
        ikrevgrp = self.controllers_setup(partname=partname + "_IK_Rev_Foot", shape="square", scale=(10,10,10), colour=colour)
        cmds.xform(ikrevgrp[0], t=(cmds.xform(heeljnt, t=1, q=1, ws=1)))
        cmds.xform(ikrevgrp[0], ro=(cmds.xform(anklejnt, ro=1, q=1, ws=1)))
        cmds.xform(ikrevgrp[0], t=(0, 7, -7), r=1)
        cmds.xform(ikrevgrp[1], piv=(cmds.xform(heeljnt, t=1, q=1, ws=1)), ws=1)

        cmds.parent(ikrevgrp[0], leggrp)
        self.lockhideattr(ikrevgrp[1], rotate=False, translate=False)



        # Create Attrs group and controller
        if flipped:
            legattrsgrp = self.controllers_setup(partname=side + "_Leg_Attrs", shape="pointedsquare", scale=(-8, 8, 8),
                                                 colour=colour)
        else:
            legattrsgrp = self.controllers_setup(partname=side + "_Leg_Attrs", shape="pointedsquare", scale=(8, 8, 8),
                                                 colour=colour)
        cmds.xform(legattrsgrp[0], t=(cmds.xform(cnctjntone, t=1, q=1, ws=1)), ws=1)
        # Parent arm attrs group to arm group
        cmds.parent(legattrsgrp[0], leggrp)
        # Parent constrain arm attrs group to the scapula's
        cmds.parentConstraint(cnctjntone, legattrsgrp[0], mo=1)
        self.lockhideattr(legattrsgrp[1])


        # Create FKIK, and space switching attributes for each leg
        cmds.select(legattrsgrp[1])
        cmds.addAttr(sn="FKIK", ln="FKIK", min=0, max=1, dv=0, ex=1, h=0, k=1)
        cmds.addAttr(sn="Pos_SS", ln="Position_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.addAttr(sn="Rot_SS", ln="Rotation_Space_Switching", enumName="Root:Hips:Chest:Scapula", **self.enum_kwargs)
        cmds.select(d=1)
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
        ikevaljntone = cmds.joint(n=partname + "_IK_Eval_0_JNT")
        cmds.xform(ikevaljntone, t=cmds.xform(startjnt, q=1, t=1, ws=1))

        ikevaljnttwopos = self.vector_lerp(cmds.xform(kneejnt, q=1, t=1, ws=1), cmds.xform(anklejnt, q=1, t=1, ws=1), .5)
        ikevaljnttwoposzposone = cmds.xform(kneejnt, q=1, t=1, ws=1)
        ikevaljnttwoposzpostwo = cmds.xform(anklejnt, q=1, t=1, ws=1)
        ikevaljnttwopos = (ikevaljnttwopos[0], ikevaljnttwopos[1], min(ikevaljnttwoposzposone[2], ikevaljnttwoposzpostwo[2])-5)
        ikevaljnttwo = cmds.joint(n=partname + "_IK_Eval_1_JNT")
        cmds.xform(ikevaljnttwo, t=ikevaljnttwopos, ws=1)

        ikevaljntthree = cmds.joint(n=partname + "_IK_Eval_2_JNT")
        cmds.xform(ikevaljntthree, t=cmds.xform(heeljnt, q=1, t=1, ws=1), ws=1)
        cmds.select(d=1)

        cmds.parent(ikevaljntone, leggrp)

        evalikh = cmds.ikHandle(n=partname + "_IK_Eval_IKH", sj=ikevaljntone, ee=ikevaljntthree)
        cmds.select(d=1)

        # Reverse IK Eval lower leg
        ikevalrevjntone = cmds.joint(n=partname + "_IK_EvalRev_0_JNT")
        cmds.xform(ikevalrevjntone, t=cmds.xform(heeljnt, q=1, t=1, ws=1), ws=1)
        ikevalrevjnttwo = cmds.joint(n=partname + "_IK_EvalRev_1_JNT")
        cmds.xform(ikevalrevjnttwo, t=cmds.xform(anklejnt, q=1, t=1, ws=1), ws=1)

        cmds.parent(ikevalrevjntone, leggrp)

        # IK solver for upper IK leg (IK startjnt to IK anklejnt)
        upperikh = cmds.ikHandle(n=partname + "_UpperIK_IKH",
                                 sj=startjnt.replace("_JNT", "_IK_JNT"), ee=anklejnt.replace("_JNT", "_IK_JNT"))

        cmds.parent(upperikh[0], leggrp)

        cmds.parentConstraint(ikevalrevjnttwo, upperikh[0], mo=1)

        cmds.parent(evalikh[0], ikgrp[1])

        #todo comment this
        lowerikh = cmds.ikHandle(n=partname + "_LowerIK_IKH",
                                 sj=anklejnt.replace("_JNT", "_IK_JNT"), ee=heeljnt.replace("_JNT", "_IK_JNT"),
                                 sol="ikSCsolver")

        cmds.parentConstraint(ikevalrevjntone, lowerikh[0])

        cmds.parent(lowerikh[0], leggrp)

        ikjorientconst = cmds.orientConstraint(ikgrp[1], heeljnt.replace("_JNT", "_IK_JNT"), mo=1)
        cmds.setAttr(ikjorientconst[0] + ".interpType", 0)

        cmds.parentConstraint(ikevaljntthree, ikrevgrp[0], mo=1)
        cmds.parentConstraint(ikrevgrp[1], ikevalrevjntone, mo=1)

        self.lockhideattr(ikrevgrp[0], visibility=False)


        # Parent constrain Connect joints to bind joints
        for i in [startjnt, kneejnt, anklejnt, heeljnt]:
            bindjparentconst = cmds.parentConstraint(i.replace("_JNT", "_Connect_JNT"), i, mo=1)

        # Point constrain the upper _IK_JNT to the hips
        cmds.parentConstraint(cmds.listRelatives(startjnt, p=1), startjnt.replace("_JNT", "_IK_JNT"), mo=1)
        cmds.parentConstraint(cmds.listRelatives(startjnt, p=1), ikevaljntone, mo=1)

        for i in [ikevalrevjntone, ikevaljntone, evalikh, lowerikh, upperikh, legfkikgrp]:
            cmds.hide(i)
