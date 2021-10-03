"""
This script is used to call each of the build components from Build_Components.py, and should be modified
dependant on the needs of each character
"""

# Standard library imports
import sys
import os.path

# Third party imports
import maya.cmds as cmds
from maya import mel


# Local application imports
path_dir = "/home/aurorafreir/github/Autorigger"
if path_dir not in sys.path:
    sys.path.insert(0,path_dir)

import Build_Components as bc # Needs to be imported after modification to sys.path
reload(bc)

# Load the Build_Components class as components and set up it's class-wide variables
components = bc.BuildComponents(
    char_name="Char"
)

class Char_Builder(object):
    """
    This class handles each of the functions used to call each component build script, then connecting each
        of the components, and then performing rig clean up (hiding/locking attributes)
    Functions are ordered in line with the order of their use
    """

    def __init__(self):
        self.setupparts = []
        self.spineparts = []
        self.neckparts = []
        self.Lf_armparts = []
        self.Rt_armparts = []
        self.Lf_handparts = []
        self.Rt_handparts = []
        self.straprig = []

    def components_build(self):
        # Call each component piece, and set it's output variables
        # as class-wide variables for use in components_connect later

        # setupparts = rootgroup (Root_GRP, Root_CTRL)
        setupparts = components.character_setup()
        self.setupparts = setupparts

        # spineparts = hipsgrp (Hips_GRP, Hips_CTRL), chestgrp (Chest_GRP, Chest_CTRL),
        spineparts = components.spine_setup(startjnt="Ct_Root_0_JNT", endjnt="Ct_Chest_0_JNT")

        self.spineparts = spineparts

        # neckparts = neckgrp (Neck_GRP, Neck_CTRL),
        neckparts = components.neck_setup(neckjnt="Ct_Neck_0_JNT")
        self.neckparts = neckparts

        # armparts = shoulloc (Lf_Scapula_Shoulder_LOC), scapulagrp (Lf_Scapula_GRP, Lf_Scapula_CTRL),
        # armattrsgrp (Lf_ArmAttrs_GRP, Lf_ArmAttrs_CTRL), connectjnts (Lf_Arm_(0-2)_Connect_JNT),
        # ikgrp (Lf_Arm_IK_GRP, Lf_Arm_IK_CTRL), pvgrp (Lf_Arm_IK_PV_GRP, Lf_Arm_IK_PV_CTRL),
        # fkctrls (Lf_Arm_FK_0_CTRL, Lf_Arm_FK_1_CTRL, Lf_Arm_FK_2_CTRL)
        Lf_armparts = components.arm_setup(scapjnt="Lf_Clavicle_0_JNT", shouljnt="Lf_Arm_0_JNT",
                                             wristjnt="Lf_Arm_2_JNT")
        self.Lf_armparts = Lf_armparts

        Rt_armparts = components.arm_setup(scapjnt="Rt_Clavicle_0_JNT", shouljnt="Rt_Arm_0_JNT",
                                             wristjnt="Rt_Arm_2_JNT", flipped=True)
        self.Rt_armparts = Rt_armparts

        # handparts = handgrp (side_Hand_GRP),
        Lf_handparts = components.hand_setup()
        self.Lf_handparts = Lf_handparts
        Rt_handparts = components.hand_setup(flipped=True)
        self.Rt_handparts = Rt_handparts

        # straprig = crvrbn (Strap_GRP, Strap_CTRL)
        straprig = components.curve_rig(partname="Strap", startjnt="Strap_1_JNT", endjnt="Strap_16_JNT")
        self.straprig = straprig

    def components_connect(self):
        # Parent the Hips to the Root Control
        cmds.parent(self.spineparts[0][0], self.setupparts[0][1])
        # Parent the Spine_RBN_Rig group to the Root_CTRL
        cmds.parent(self.spineparts[2], self.setupparts[1])

        # Parent Neck to Chest
        cmds.parent(self.neckparts[0], self.spineparts[1][1])

        # Constrain Scapulas to Chest
        cmds.parentConstraint(self.spineparts[1][1], self.Lf_armparts[1][0], mo=1)
        cmds.parentConstraint(self.spineparts[1][1], self.Rt_armparts[1][0], mo=1)

        # Constrain hands to wrists
        cmds.parentConstraint(self.Lf_armparts[3][2], self.Lf_handparts, mo=1)
        cmds.parentConstraint(self.Rt_armparts[3][2], self.Rt_handparts, mo=1)

        # Skin strap NRB to bind joints
        bindjnts = cmds.listRelatives("Ct_Root_0_JNT", ad=1)
        strapcluster = cmds.skinCluster(bindjnts, "Strap_NRB", n="Strap_NRB_SkinCluster", sm=2)
        cmds.copySkinWeights(ss="Body_SkinCluster", ds=strapcluster[0], nm=1, sm=1)

        cmds.select(d=1)


    def rig_cleanup(self):
        # Lock all attrs on Root_GRP
        components.lockhideattr(self.setupparts[0][0], hide=False)
        # Lock all attrs on Hips_GRP, Chest_GRP, and Neck_GRP
        components.lockhideattr(self.spineparts[0][0], hide=False)
        components.lockhideattr(self.spineparts[1][0], hide=False)
        components.lockhideattr(self.neckparts[0], hide=False)

        # Lock scale on Hand groups
        for side in [self.Lf_handparts, self.Rt_handparts]:
            components.lockhideattr(side, translate=False, rotate=False)

        # Controls Display Layer
        ctrlsdisplaylayer = self.setupparts[2][2]

        # Add the Scapula_CTRLs, ArmAttrs_CTRLs, IK_CTRLs, PV_CTRLs, and FK_CTRLs to the Controls_Disp layer
        for armside in [self.Lf_armparts, self.Rt_armparts]:
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside[1][1], nr=1)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside[2][1], nr=1)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside[4][1], nr=1)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside[5][1], nr=1)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside[6], nr=1)

        # Add all Nurbs curve transforms (not the shapes) on the hand to the Controls_Disp layer
        for grp in [self.Lf_handparts, self.Rt_handparts]:
            for ctrl in cmds.listRelatives(grp, ad=1, type="transform"):
                if "_CTRL" not in ctrl:
                    pass
                else:
                    cmds.editDisplayLayerMembers(self.setupparts[2][2], ctrl, nr=1)


ac = Char_Builder()
ac.components_build()         # Call the components_build   function from the Char_Builder class
ac.components_connect()       # Call the components_connect function from the Char_Builder class
ac.rig_cleanup()              # Call the rig_cleanup        function from the Char_Builder class
