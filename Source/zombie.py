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
from panda3d.core import loadPrcFileData
import sys, random, os, math

class Zombie:
    def __init__(self,zombie,app,i=0):
        self.app = app
        self.zombie = zombie
        self.zombie.setPythonTag('health',10+30*self.app.level)
        self.zombie.setTag('zombie','1')
        self.zombie.setPythonTag('dead',False)
        self.zombie.setScale(0.5,0.5,0.5)
        self.zombie.setX(-40)
        self.zombie.setY(-i*10)
        self.zombie.setZ(20)
        self.zombie.loop("walk")
        self.zombie.reparentTo(self.app.render)
        #Collision detection
        self.create_collider()
        
    def addPhy(self):
        self.zombieAN = ActorNode("ZombieActor")
        self.zombieActorPhysicsP = self.app.phy.attachNewNode(self.zombieAN)
        
        self.app.physicsMgr.attachPhysicalNode(self.zombieAN)
        self.zombie.reparentTo(self.zombieActorPhysicsP)
        self.zombieAN.getPhysicsObject().setMass(150)
    def create_collider(self):
        self.addPhy()
        
        #walker this has been commented because two collision detectors per panda were decreasing the fps
        #self.collision_sphere = CollisionSphere(0,0,2,2)
        #self.cnodePath = self.zombie.attachNewNode(CollisionNode('zombieWalker'))
        #self.cnodePath.node().addSolid(self.collision_sphere)
        #self.cnodePath.show()
        
        #body
        #self.zombie_body = CollisionSphere(0,0,10,4)
        self.zombie_body = CollisionSphere(0,0,7,7)
        self.zombie_body_NP = self.zombie.attachNewNode(CollisionNode('zombieBody'))
        self.zombie_body_NP.node().addSolid(self.zombie_body)
        #self.zombie_body_NP.show()
        
        #self.app.pusher.addCollider(self.cnodePath,self.zombieActorPhysicsP)
        self.app.pusher.addCollider(self.zombie_body_NP,self.zombieActorPhysicsP)
        #self.app.cTrav.addCollider(self.cnodePath,self.app.pusher)
        self.app.cTrav.addCollider(self.zombie_body_NP,self.app.pusher)
        
    
    def meelee(self):
        point = self.app.pandaActor.getRelativePoint(self.zombie,Point3(0,0,0))
        dist = point.getX()**2 + point.getY()**2 + point.getZ()**2
        if dist < 300:
            self.app.kicked.play()
            self.zombieAN.getPhysicsObject().setVelocity(self.app.render.getRelativeVector(self.app.pandaActor,Vec3(0,-30,0)))
            self.zombie.setPythonTag('health',self.zombie.getPythonTag('health')-10)
            if self.zombie.getPythonTag('health') <= 0 and self.zombie.getPythonTag('dead') <> True:
                self.zombie.setPythonTag('dead',True)
                self.app.panda_kill_count += 1
                self.app.zombie_die.play()
                    
class Zombies(DirectObject.DirectObject):
    def __init__(self,app):
        self.app = app
        self.zombies = []
        self.accept('bullet-into-zombieBody', self.gethit)
    def gethit(self,entry):
        entry.getFromNodePath().getParent().remove_node()
        x = entry.getIntoNodePath().getParent()
        print "Ouch"
        x.setPythonTag('health',x.getPythonTag('health')-10)
        if x.getPythonTag('health')<=0:
            self.app.panda_kill_count+=1
            self.app.zombie_die.play()
            if x.getPythonTag('dead') <> True:
                x.setPythonTag('dead',True)
            print self.app.level
            print self.app.panda_kill_count
    def add(self,i=0):
        print "adding"
        while i > 0:
            zombie = Zombie(Actor("models/panda",{"walk":"models/panda-walk"}),self.app,i)
            self.zombies.append(zombie)
            i-=1
    def moveZombie(self,task):
        if self.app.paused:
            return Task.cont
        self.tempval = 0
        for x in self.zombies:
            if x.zombie.getPythonTag('dead'):
                self.zombies.remove(x)
                x.zombie.removeNode()
                if self.app.panda_kill_count%5==0:
                    self.app.inside_level=False
                    self.app.level+=1
            else:
                self.tempval+=1
                x.zombie.lookAt(self.app.pandaActor)
                x.zombie.setHpr(x.zombie,180,0,0)
                if self.app.render.getRelativePoint(x.zombieActorPhysicsP,x.zombie.getPos())[2] < -10:
                    x.zombie.setPos(x.zombieActorPhysicsP.getRelativePoint(self.app.render,Point3(10,10,100)))
                x.zombie.setPos(x.zombie,0,-0.3-0.1*self.app.level,0)
        return Task.again
    def check_for_collisions_with_ground(self):
        return
        for x in self.zombies:
            x.check_for_collisions_with_ground()
    def meelee(self):
        for x in self.zombies:
            x.meelee()