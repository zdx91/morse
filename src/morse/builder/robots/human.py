import logging; logger = logging.getLogger("morserobots." + __name__)
from morse.builder import bpymorse
from morse.builder import GroundRobot
from morse.builder.actuators import Armature
from morse.builder.sensors import ArmaturePose

class Human(GroundRobot):
    """ Append a human model to the scene.

    It also exposes a :doc:`human posture component <../sensors/human_posture>`
    that can be accessed by the ``armature`` member.

    Usage example:

    .. code-block:: python

       #! /usr/bin/env morseexec

       from morse.builder import *

       human = Human()
       human.translate(x=5.5, y=-3.2, z=0.0)
       human.rotate(z=-3.0)

       human.armature.add_stream('pocolibs')

    Currently, only one human per simulation is supported.

    Detailed documentation
    ----------------------

    The MORSE human avatar is based on a 3D model generated from MakeHuman, and stored in human_rig.blend.

    The model is rigged with an armature ('HumanSkeleton'), used to control the
    postures of the human and to deform accordingly the human mesh.

    This armature is used by MORSE as both a :doc:`sensor to read and export
    the human pose <../sensors/armature_pose>` and :doc:`an actuator
    <../actuators/armature>` to modify the pose.

    TODO: give code examples to read and modify the pose

    The armature defines 5 particular points (**IK targets**) that can be
    manipulated to control the human model in a simpler way: the head, the two
    wrists and the two feet.

    """

    # list of human bones that we want to control via IK targets
    IK_TARGETS = ["head", "wrist_L", "wrist_R", "foot_L", "foot_R"]

    def __init__(self, filename='human_rig', name = None):
        """ The 'style' parameter is only to switch to the mocap_human file.

        :param filename: the human model. Default: 'human_rig'
        """
        GroundRobot.__init__(self, filename, name)
        self.properties(classpath = "morse.robots.human.Human")

        self.armature = None

        try:
            self.armature = Armature(armature_name = "HumanSkeleton")
            self.append(self.armature)
        except KeyError:
            logger.error("Could not find the human armature! (I was looking " +\
                         "for an object called 'HumanSkeleton' in the children " + \
                         "objects of the human). I won't be able to export the " + \
                         "human pose to any middleware.")

        if self.armature:
            self.armature.create_ik_targets(self.IK_TARGETS)
            for t, name in self.armature.ik_targets:
                t.parent = self._bpy_object

            # Add an armature sensor. "joint_stateS" to match standard ROS spelling.
            self.joint_states = ArmaturePose("joint_states")
            self.armature.append(self.joint_states)


    def add_interface(self, interface):
        if interface == "socket":
            self.joint_states.add_stream("socket")
            self.armature.add_service('socket')

        elif interface == "ros":

            self.joint_states.add_stream("ros")

            self.armature.add_service("ros")
            self.armature.add_overlay("ros",
              "morse.middleware.ros.overlays.armatures.ArmatureController")

        elif interface == "pocolibs":
            self.armature.properties(classpath="morse.sensors.human_posture.HumanPosture")
            self.add_stream(interface)

