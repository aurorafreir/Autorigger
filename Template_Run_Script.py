"""
This script is used to call each of the build components from Build_Components.py, and should be modified
dependant on the needs of each character
"""

# Standard library imports
import sys
import os.path

# Third party imports
from maya import cmds
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


    def components_build(self):
        # Call each component piece, and set it's output variables
        # as class-wide variables for use in components_connect later

        # Basic character setup
        setupparts = components.character_setup()
        self.setupparts = setupparts

        # Spine setup
        spineparts = components.spine_setup(startjnt="Ct_Root_0_JNT", endjnt="Ct_Spine_4_JNT")

        self.spineparts = spineparts

        # Neck setup
        neckparts = components.neck_setup(neckjnt="Ct_Neck_0_JNT")
        self.neckparts = neckparts

        # Arm setup
        Lf_armparts = components.arm_setup(scapjnt="Lf_Clavicle_0_JNT", shouljnt="Lf_Arm_0_JNT",
                                             wristjnt="Lf_Arm_2_JNT")
        self.Lf_armparts = Lf_armparts

        Rt_armparts = components.arm_setup(scapjnt="Rt_Clavicle_0_JNT", shouljnt="Rt_Arm_0_JNT",
                                             wristjnt="Rt_Arm_2_JNT", flipped=True)
        self.Rt_armparts = Rt_armparts

        # Hand setup
        Lf_handparts = components.hand_setup()
        self.Lf_handparts = Lf_handparts
        Rt_handparts = components.hand_setup(flipped=True)
        self.Rt_handparts = Rt_handparts


        # Legs setup
        Lf_legparts = components.digileg(part_name="Lf_Leg", startjnt="Lf_Leg_0_JNT",
                                      kneejnt="Lf_Leg_1_JNT", anklejnt="Lf_Leg_2_JNT",
                                      heeljnt="Lf_Leg_3_JNT", footjnt="Lf_Paw_0_JNT")
        self.Lf_legparts = Lf_legparts

        Rt_legparts = components.digileg(part_name="Rt_Leg", startjnt="Rt_Leg_0_JNT",
                                      kneejnt="Rt_Leg_1_JNT", anklejnt="Rt_Leg_2_JNT",
                                      heeljnt="Rt_Leg_3_JNT", footjnt="Rt_Paw_0_JNT",
                                        flipped=1)
        self.Rt_legparts = Rt_legparts


    def components_connect(self):
        # Parent the Hips to the Root Control
        cmds.parent(self.spineparts.hipsgrp[0], self.setupparts.rootgroup[1])
        # Parent the Spine_RBN_Rig group to the Root_CTRL
        cmds.parent(self.spineparts.spinerbnrig, self.setupparts.main_rig_group)

        # Parent Neck to Chest
        cmds.parent(self.neckparts.neckgrp[0], self.spineparts.chestgrp[1])

        # Constrain Scapulas to Chest
        cmds.parentConstraint(self.spineparts.chestgrp[1], self.Lf_armparts.scapulagrp[0], maintainOffset=True)
        cmds.parentConstraint(self.spineparts.chestgrp[1], self.Rt_armparts.scapulagrp[0], maintainOffset=True)

        # Constrain hands to wrists
        cmds.parentConstraint(self.Lf_armparts.connectjnts[2], self.Lf_handparts.handgrp, maintainOffset=True)
        cmds.parentConstraint(self.Rt_armparts.connectjnts[2], self.Rt_handparts.handgrp, maintainOffset=True)

        # Parent constrain the head setup to the neck
        # Used in example rig, as the head rig was made manually
        cmds.parentConstraint(self.neckparts.neckgrp[1], "Head_GRP", maintainOffset=True)

        cmds.select(d=1)


    def rig_cleanup(self):
        # Lock all attrs on Root_GRP
        components.lockhideattr(self.setupparts.rootgroup[0], hide=False)
        # Lock all attrs on Hips_GRP, Chest_GRP, and Neck_GRP
        components.lockhideattr(self.spineparts.hipsgrp[0], hide=False)
        components.lockhideattr(self.spineparts.chestgrp[0], hide=False)
        components.lockhideattr(self.neckparts.neckgrp[0], hide=False)

        # Lock scale on Hand groups
        for side in [self.Lf_handparts.handgrp, self.Rt_handparts.handgrp]:
            components.lockhideattr(side, translation=False, rotate=False)

        # Controls Display Layer
        ctrlsdisplaylayer = self.setupparts.displayers[2]

        # Add the Scapula_CTRLs, ArmAttrs_CTRLs, IK_CTRLs, PV_CTRLs, and FK_CTRLs to the Controls_Disp layer
        for armside in [self.Lf_armparts, self.Rt_armparts]:
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside.scapulagrp[1], noRecurse=True)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside.armattrsgrp[1], noRecurse=True)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside.ikgrp[1], noRecurse=True)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside.pvgrp[1], noRecurse=True)
            cmds.editDisplayLayerMembers(ctrlsdisplaylayer, armside.fkctrls, noRecurse=True)

        # Add all Nurbs curve transforms (not the shapes) on the hand to the Controls_Disp layer
        # for part in [scapulagrp, armattrsgrp, ikgrp, pvgrp, fkctrls]:
        for grp in [self.Lf_handparts, self.Rt_handparts]:
            for ctrl in cmds.listRelatives(grp.handgrp, allDescendents=True, type="transform"):
                if "_CTRL" not in ctrl:
                    pass
                else:
                    cmds.editDisplayLayerMembers(self.setupparts.displayers[2], ctrl, noRecurse=True)

cb = Char_Builder()
cb.components_build()         # Call the components_build   function from the Char_Builder class
cb.components_connect()       # Call the components_connect function from the Char_Builder class
cb.rig_cleanup()              # Call the rig_cleanup        function from the Char_Builder class
