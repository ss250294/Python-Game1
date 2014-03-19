from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from panda3d.core import NodePath
from panda3d.core import WindowProperties, PandaNode, Camera, TextNode
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
from panda3d.core import Vec3, Vec4, BitMask32
from panda3d.core import CollisionTraverser,CollisionNode, CollisionSphere
from panda3d.core import CollisionHandlerQueue,CollisionRay,CollisionHandlerEvent
from panda3d.core import Filename,AmbientLight,DirectionalLight, CollisionTube
#from panda3d.core import ConfigVariableString
from panda3d.core import loadPrcFileData
import sys, random, os, math


class RandomThings:
    def __init__(self,app):
        self.app = app
    def add_random_things(self):
        pumpkin = self.app.loader.loadModel("models/pumpkin.egg")
        for i in range(20):
            placeholder = self.app.environ.attachNewNode("Dancer-Placeholder")
            placeholder.setPos(random.randint(-100,30),random.randint(-100,30),0)
            pumpkin.instanceTo(placeholder)
        