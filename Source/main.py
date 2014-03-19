#!/usr/bin/python

"""Python game: Panda Apocalypse.
Shubham Srivastava 
201101101

Note:
Our original plan was to create a zombie apocalypse, but we could not find a decent model of a zombie online.
Hence we used the panda model from panda3D's tutorials.
But the variable names all say zombie (since we implememted the models after everything else).
Thus anythin in the code saying zombie actually means an evil panda.
And anything saying pandaActor means the protagonist, ie, the Joker.
"""


from threading import Thread
import zombie
import time
import randomthings
from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, Vec3
from panda3d.core import NodePath
from panda3d.core import WindowProperties, PandaNode, Camera, TextNode
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce, PhysicsCollisionHandler
from panda3d.core import Vec3, Vec4, BitMask32
from panda3d.core import CollisionTraverser,CollisionNode, CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue,CollisionRay, CollisionHandlerEvent
from panda3d.core import Filename,AmbientLight,DirectionalLight, CollisionTube, CollisionSphere
#from panda3d.core import ConfigVariableString
from panda3d.core import loadPrcFileData
from pandac.PandaModules import *
import sys, random, os, math

class ReadKeys(DirectObject.DirectObject):
    def __init__(self,app,layer2d):
        self.disable_move=False
        self.disable_all=False
        self.disable_jump=False
        self.layer2d = layer2d
        self.old_cameraP = None
        self.old_cameraHPR = None
        self.app=app
        self.app.run_ = False
        self.accept('w', self.go, ['forward'])
        self.accept('a', self.go, ['left'])
        self.accept('d', self.go, ['right'])
        self.accept('s', self.go, ['back'])
        self.accept('w-up', self.up,[1])
        self.accept('a-up', self.up,[2])
        self.accept('d-up', self.up,[3])
        self.accept('s-up', self.up,[4])
        self.accept('space',self.jump)
        self.accept('shift-space',self.jump)
        self.accept('c',self.toggle_firstP)
        self.accept('enter',self.start_game)
        self.accept('p',self.pause)
        self.accept('r',self.restart)
        self.accept('q',self.lookBehind)
        self.accept('q-up',self.lookForward)
        
        self.accept('pandaWalker-into-zombieWalker',self.die)
        self.accept('zombieWalker-into-pandaWalker',self.die)
        
        self.accept('zombieBody-into-zombieDetector',self.die)
        self.accept('zombieDetector-into-zombieBody',self.die)
        self.accept('into',self.die)
        #Running
        self.accept('shift',self.shift)
        self.accept('shift-up', self.shift_up)
        self.accept('shift-w', self.run, ['forward'])
        self.accept('shift-a', self.run, ['left'])
        self.accept('shift-d', self.run, ['right'])
        self.accept('shift-s', self.run ,['back'])
        
        
        #Meelee Attack       
        self.accept('mouse3',self.meelee)
        
        
        #Ranged Attack
        self.accept('mouse1',self.ranged_start)
        self.accept('mouse1-up',self.ranged_stop)
    
    def restart(self):
        sys.exit(1)
    def pause(self):
        self.old_cameraP = self.app.camera.getPos()
        self.old_cameraHPR = self.app.camera.getHpr()
        self.app.camera.setPos(100,100,20)
        self.app.camera.lookAt(self.app.pandaActor)
        self.info="""
    Game has been paused. Press P to resume.
        
    Jump: Space
    Shoot: LeftClick
    Kick: RightClick
    Walk: A/W/S/D
    Run: Shift + A/W/S/D
    Back View: Q
    
        """
        self.layer2d.update_info(self.info)
        self.app.paused= not self.app.paused
        if not self.app.paused:
            self.app.camera.setPos(self.old_cameraP)
            self.app.camera.setHpr(self.old_cameraHPR)
    
    def start_game(self):
        self.layer2d.press_enter.setText('')
        self.app.game_started=True
    
    def lookBehind(self):
        self.app.mirror=True
    def lookForward(self):
        self.app.mirror=False
    
    def toggle_firstP(self):
        if self.app.is_firstP:
            self.app.is_firstP=False
        else:
            self.app.is_firstP=True
        self.app.shifted_cam=True
    def die(self,entry):
        print "aaaa Panda!"
        self.app.health -= 2
        self.layer2d.incBar(self.app.health)
        self.app.hurt_sound.play()
    def jump(self):
        if self.disable_all:
            return
        if self.disable_jump:
            return
        self.disable_move=True
        self.disable_jump=True
        self.app.taskMgr.doMethodLater(2,self.enableJump,'zombieTask_enableJump')
        if self.app.pandaActor.getCurrentAnim() not in ['run','walk4','breathe']:
            self.app.move_anim_queue += [(self.app.pandaActor,False,'breathe')]
        else:
            self.app.move_anim_queue += [(self.app.pandaActor,False,self.app.pandaActor.getCurrentAnim())]
        self.app.pandaActor.play('jump')
        
        self.app.pandaAN.getPhysicsObject().setVelocity(self.app.render.getRelativeVector(self.app.pandaActor,Vec3(0,0,30)))
    
    def enableJump(self,task):
        self.disable_jump=False
        self.disable_move=False
    def shift(self):
        temp = self.app.l + self.app.f + self.app.r + self.app.b
        if temp==0:
            return
        self.app.run_=True
        
        self.app.pandaActor.play('ready_to_run')
        self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
        
        #implement multi part actor and multiple animations later on.
        #self.pandaActor.stop()
        #direction = (self.app.l-self.app.r,self.app.f-self.app.b)
        #if direction==(1,0):
            ##self.pandaActor.loop("runleft")
            #self.app.pandaActor.play('ready_to_run')
            #self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
        #elif direction==(-1,0):
            ##self.pandaActor.loop("runright")
            #self.app.pandaActor.play('ready_to_run')
            #self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
        #elif direction[1]==1:
            ##self.pandaActor.loop("runforward")
            #self.app.pandaActor.play('ready_to_run')
            #self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
        #else:
            ##self.pandaActor.loop("runbackward")
            #self.app.pandaActor.play('ready_to_run')
            #self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
        
    def shift_up(self):
        self.app.run_ = False
        if self.app.pandaActor.getCurrentAnim()=="run":
            self.app.pandaActor.stop()
            #play ready to walk anim here
            self.app.move_anim_queue += [(self.app.pandaActor,False,"walk4")]
        if (self.app.pandaActor,False,"run") in self.app.move_anim_queue:
            self.app.move_anim_queue.remove((self.app.pandaActor,False,"run"))
            self.app.pandaActor.loop("walk4")
    
    #Stopping function
    def up(self,x):
        if x==1:
            self.app.f = 0
        elif x==2:
            self.app.l = 0
        elif x==3:
            self.app.r = 0
        elif x==4:
            self.app.b=0
        temp = self.app.l + self.app.f + self.app.r + self.app.b
        if self.disable_all or self.disable_move:
            return
        if temp==0:
            self.app.pandaActor.stop()
            self.app.anim_queue += [(self.app.pandaActor,False,"breathe")]
        self.app.move_anim_queue = []
    
    #Start running animation
    def start_run_anim(self):
        if self.app.pandaActor.getCurrentAnim()<>"walk4" and self.app.pandaActor.getCurrentAnim()<>"run":
            if self.app.run_:
                self.app.pandaActor.play('ready_to_run')
                self.app.move_anim_queue += [(self.app.pandaActor,False,"run")]
            else:
                self.app.pandaActor.loop('walk4')
    
    #Moving functions
    def go(self,where):
        if self.disable_all or self.disable_move:
            return
        if (where=='forward'):
            self.app.f = 1
        elif (where=='back'):
            self.app.b = 1
        elif (where=='right'):
            self.app.r = 1
        elif (where=='left'):
            self.app.l = 1
        self.start_run_anim()
    def run(self,where):
        if self.disable_all or self.disable_move:
            return
        self.app.run_=True
        self.go(where)
    
    #Attack-functions:
    def enable_all(self,task):
        self.disable_all=False
    def meelee(self):
        if self.disable_all:
            return
        print "Stomping"
        self.disable_all=True
        self.app.taskMgr.doMethodLater(1,self.enable_all,'zombieTask_enableKeys')
        self.app.meelee()
    def ranged_start(self):
        if self.disable_all:
            return
        print "Shooting"
        self.app.ranged_start()
    def ranged_stop(self):
        if self.disable_all:
            return
        print "stopping"
        self.app.ranged_stop()

class MyApp(ShowBase):
    def center_mouse(self):
        self.win.movePointer(0,self.win.getXSize()/2,self.win.getYSize()/2)
    def __init__(self):
        #Game variables
        self.health = 100
        self.panda_kill_count = 0
        self.level = 0
        
        #Implementation variables
        #self.color = [Vec4((204.0/255), (255.0/255), (204/255), 0.1),Vec4((0/255), (255.0/255), (255.0/255), 0.1),Vec4((255.0/255), (51.0/255), (255.0/255), 0.1),Vec4((153.0/255), (255.0/255), (153.0/255), 0.1),Vec4((255.0/255), (178.0/255), (102.0/255), 0.1),Vec4((229.0/255), (204.0/255), (255.0/255), 0.1)]
        self.color = [Vec4(0.4,0.4,0.4,0.1)]
        self.mirror=False
        self.paused=False
        self.displayed=False
        self.game_started=False
        self.randomthings_ = randomthings.RandomThings(self)
        self.shifted_cam=False
        self.is_firstP=False
        self.old_anim2 = None
        self.old_anim=None
        self.timeout=False
        (self.r,self.f,self.b,self.l)=(0,0,0,0)
        self.inside_level=False
        self.move_anim_queue=[]
        self.anim_queue=[]
        self.prev_time=0.0
        self.bullets = []
        self.rightspeed=0
        self.forwardspeed=0
        ShowBase.__init__(self)
        self.makeDefaultPipe()
        bb=self.pipe.getDisplayHeight()
        aa=self.pipe.getDisplayWidth()
        
        self.openDefaultWindow(size=(aa, bb))
        import layer2d
        self.layer2d = layer2d
        self.layer2d.update_info('Loading...')
        self.keyreader= ReadKeys(self,layer2d)
        
        #Sounds
        self.gunshot = self.loader.loadSfx("sounds/gunshot_se.ogg")
        self.gunshot.setLoop(False)
        
        self.music = self.loader.loadSfx("sounds/music.ogg")
        self.music.setLoop(True)
        
        
        self.zombie_die = self.loader.loadSfx('sounds/zombie_die.ogg')
        self.zombie_die.setLoop(False)
        
        self.kicked = self.loader.loadSfx('sounds/kicked.ogg')
        self.kicked.setLoop(False)
        
        self.hurt_sound = self.loader.loadSfx('sounds/hurt.ogg')
        self.hurt_sound.setLoop(False)
        
        self.dead_sound = self.loader.loadSfx('sounds/dead.ogg')
        self.dead_sound.setLoop(False)
        
        self.intro_sound = self.loader.loadSfx('sounds/intro.ogg')
        self.intro_sound.setLoop(False)
        self.intro_sound.play()
        
        
        self.enableParticles()
        self.center_mouse()
        #self.disableMouse()
        self.prev_pos = None
        if base.mouseWatcherNode.hasMouse():
            x=base.mouseWatcherNode.getMouseX()
            y=base.mouseWatcherNode.getMouseY()
            self.prev_pos = (x,y)
        #Hide cursor
        props = WindowProperties()
        props.setCursorHidden(True) 
        self.win.requestProperties(props)
        
        
        self.environ = self.loader.loadModel('models/ourworld')
        self.environ.setPos(0,0,0)
        self.environ.reparentTo(self.render)
        
        
        self.pandaActor = Actor("models/hero_anim", {'kick':'models/hero_anim-kick','unready_to_shoot':'models/hero_anim-unready_to_shoot','jump':'models/hero_anim-jump',"shooting":"models/hero_anim-shooting","ready_to_shoot":"models/hero_anim-ready_to_shoot","ready_to_walk":"models/hero_anim-ready_to_run","ready_to_run":"models/hero_anim-ready_to_run","walk4":"models/hero_anim-walk1", "breathe": "models/hero_anim-breathe", "run": "models/hero_anim-walk"})
        self.pandaActor.setPlayRate(3,'ready_to_shoot')
        self.pandaActor.setPlayRate(-1.0,"ready_to_walk")
        self.pandaActor.setPlayRate(1.5,'run')
        self.pandaActor.setPlayRate(1.5,'ready_to_run')
        self.pandaActor.reparentTo(self.render)
        self.pandaActor.setPos(self.environ,0,0,100)
        self.pandaActor.loop("breathe")
        
        self.phy = NodePath("PhysicsNode")
        self.phy.reparentTo(self.render)
        
        self.pandaAN = ActorNode("PandaActor")
        self.pandaActorPhysicsP = self.phy.attachNewNode(self.pandaAN)
        
        self.physicsMgr.attachPhysicalNode(self.pandaAN)
        self.pandaActor.reparentTo(self.pandaActorPhysicsP)
        
        
        #set mass of panda
        self.pandaAN.getPhysicsObject().setMass(100)
        
        #apply gravity
        self.gravityFN=ForceNode('world-forces')
        self.gravityFNP=self.environ.attachNewNode(self.gravityFN)
        self.gravityForce=LinearVectorForce(0,0,-30.81) #gravity acceleration
        self.gravityFN.addForce(self.gravityForce)
        self.physicsMgr.addLinearForce(self.gravityForce)
        
        
        #camera stuff
        self.camera.reparentTo(self.pandaActor)
        self.camera.lookAt(self.pandaActor)
        self.taskMgr.add(self.spinCameraTask, "zombieTask_SpinCameraTask")
        self.taskMgr.doMethodLater(0.01,self.movePandaTask,"zombieTask_movePandaTask")
        
        
        #Collision Handling
        self.cTrav = CollisionTraverser()
        self.collisionHandler = CollisionHandlerEvent()
        
        #Add collider for terrain
        self.groundCollider = self.environ.find("**/terrain")
        
        #Add walker for panda
        self.collision_sphere = CollisionSphere(0,0,1,1)
        self.collNode = CollisionNode('pandaWalker')
        self.cnodePath = self.pandaActor.attachNewNode(self.collNode)
        self.cnodePath.node().addSolid(self.collision_sphere)
        
        #AddZombieDetector for panda
        self.zombie_sphere = CollisionSphere(0,0,3,1)
        self.zomb_detector_node = CollisionNode('zombieDetector')
        self.zomb_detector_NP = self.pandaActor.attachNewNode(self.zomb_detector_node)
        self.zomb_detector_NP.node().addSolid(self.zombie_sphere)
        #self.zomb_detector_NP.show()
        
        #Add pusher against gravity
        self.pusher = PhysicsCollisionHandler()
        self.pusher.addCollider(self.cnodePath, self.pandaActorPhysicsP)
        self.pusher.addCollider(self.zomb_detector_NP,self.pandaActorPhysicsP)
        self.cTrav.addCollider(self.cnodePath,self.pusher)
        self.cTrav.addCollider(self.zomb_detector_NP,self.pusher)
        
        self.pusher.addInPattern('%fn-into-%in')
        self.pusher.addAgainPattern('%fn-again-%in')
        
        #Add collision handler patterns
        self.collisionHandler.addInPattern('%fn-into-%in')
        self.collisionHandler.addAgainPattern('%fn-again-%in')
        
        self.abientLight = AmbientLight("ambientLight")
        self.abientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
        self.directionalLight = DirectionalLight("directionalLight")
        self.directionalLight.setDirection(Vec3(-5, -5, -5))
        self.directionalLight.setColor(Vec4((229.0/255), (204.0/255), (255.0/255), 0.7))
        self.directionalLight.setSpecularColor(Vec4(0.4, 0.4, 0.4, 0.1))
        self.directionalLight.setShadowCaster(True,512,512)
        self.render.setLight(self.render.attachNewNode(self.abientLight))
        self.render.setLight(self.render.attachNewNode(self.directionalLight))
        self.render.setShaderAuto()
        
        #create zombie land
        self.zombieland = zombie.Zombies(self)
        self.taskMgr.doMethodLater(0.01,self.zombieland.moveZombie, "zombieTask_ZombieMover")
        layer2d.incBar(self.health)
        self.taskMgr.add(self.game_monitor,"zombieTask_gameMonitor")
        self.taskMgr.doMethodLater(2.7,self.music_play, "zombieTask_music")
        
        #Add random useless things:
        self.randomthings_.add_random_things()
    def music_play(self,task):
        self.music.play()
        return Task.done
    #def get_color(self):
     #   return self.color[min(len(self.color)-1,self.level)]
    
    #GameMonitor
    def game_monitor(self,task):
        if self.paused:
            return Task.cont
        #Update Score
        self.layer2d.update_score(self.panda_kill_count)
        #Check for health of actor
        if self.health <= 0:
            self.dead_sound.play()
            self.pandaActor.detachNode()
            print "LOL u ded"
            self.info = """Game Over..
    Score: """ + str(self.panda_kill_count) + """
    Press alt+f4 to quit the game.
    
    """
            self.layer2d.update_info(self.info)
            self.taskMgr.removeTasksMatching('zombieTask_*')
        
        if self.game_started<>True:
            if not self.displayed:
                self.display_information()
            self.pandaActor.setPos(self.pandaActorPhysicsP.getRelativePoint(self.render,Point3(10,10,100)))
            return Task.cont
        
        #Check if user is inside some level. if yes, pass.
        if self.inside_level or self.timeout:
            return Task.cont
        self.inside_level = True
        #self.health=100
        self.timeout=True
        print ".."
        #The next lines will be executed only when the user is in between two levels (or at the beginning of the game)
        #Display information based on game level
        self.display_information()
        print "HUEHUEHUEHUE"    
        #Schedule wave of zombies
        self.taskMgr.doMethodLater(10,self.addWave, "zombieTask_ZombieAdder")
        
        return Task.cont
        
            
    
    def addWave(self,task):
        ##add a wave of 5 zombies, depending on the level.
        ##speed of zombie increases with each level
        ##durability of zombie increases with each level.
        ##Wave ends when all zombies die.
        self.directionalLight.setSpecularColor(Vec4(0.4, 0.4, 0.4, 0.1))
        self.layer2d.update_info("level"+str(self.level))
        self.timeout=False
        self.zombieland.add(5)
        return Task.done
        
    
    #information displayer
    def display_information(self):
        #display information based on levels.
        print self.game_started
        self.displayed=True
        if self.game_started==False:
            info = """
    Welcome to PandaLand. Once upon a time, there used to be these cute

    little creatures called Pandas. They were lazy, funny, and

    adorable. But that is what we humans thought. Pandas are

    actually an evil alien race that spread from planet to planet,

    spreading destruction and terror everywhere. They ruled earth

    several billion years ago. But our super ancestors (Dinosaurs)

    fought agaisnt them with great valour and selflessness; and managed

    to save planet Earth from doom. But the pandas went into hiding

    (and became cute); until few days back! Now they seek to kill all.

    You, the Joker, are our only hope,since Batman has retired.

    Go Kill Pandas.For Mother Earth!
    
    

    """
            self.layer2d.information['bg'] = (0,0,0,0.8)
        else:
            self.layer2d.update_info('')
            if self.level==0:
                info="""
    Your game will start in a few seconds.
    This is the first level. Pandas will spawn
    and follow you. Shoot to kill.

    Test out your controls while
    they are still cute and harmless :)
    
    Jump: Space
    Shoot: LeftClick
    Kick: RightClick
    Walk: A/W/S/D
    
    For more information, press P.

"""
                
                self.layer2d.information['bg'] = (0,0,0,0.6)
            elif self.level==1:
                info="""
    Level 0 Completed!
    Starting Level 1.
    
    Pandas have turned evil
    and stronger. They will try
    to eat you up.

    To run:
    Press Shift + A/S/W/D

"""
            elif self.level==2:
                info="""
    Level 1 Completed!
    Starting Level 2.
    
    Pandas are even stronger now.
    They will get stronger by
    each level.

    Your automatic shooting speed has
    also improved due to experience
    gained.

"""
            elif self.level==3:
                info="""
    Level 2 Completed!
    Starting Level 3.
    
    Pandas also move faster
    by each level. They really
    want to eat you.

    But don't worry, you also 
    run faster as the levels
    proceed.
    
"""
            else:
                info = """
    Level """ + str(self.level-1) + """ Completed!
    Starting """ + str(self.level) + """ .
    
    Well done!
    Keep fighting, our fate lies
    in your hands.
    
"""
        self.layer2d.update_info(info)
    #self.create_bullet()
    def create_bullet(self):
        self.bullet = self.loader.loadModel('models/gun/bullet')
        self.gunshot.play()
        self.bulletAN = ActorNode("BulletNode")
        self.bulletActorPhysicsP = self.phy.attachNewNode(self.bulletAN)
        
        self.physicsMgr.attachPhysicalNode(self.bulletAN)
        self.bullet.reparentTo(self.bulletActorPhysicsP)
        self.bulletAN.getPhysicsObject().setMass(1)
        self.bullet.setPos(self.pandaActor,0,-3,3.5)
        self.bullet.setScale(0.1,0.1,0.1)
        self.bullet.setHpr(self.pandaActor,0,90,0)
        self.bullet.setP(self.camera.getP()+90)
        self.bullet_sphere = CollisionSphere(0,0,0,0.2)
        self.bullet_collNode = CollisionNode('bullet')
        self.bullet_cnodePath = self.bullet.attachNewNode(self.bullet_collNode)
        self.bullet_cnodePath.node().addSolid(self.bullet_sphere)
        
        #self.pusher.addCollider(self.bullet_cnodePath,self.bulletActorPhysicsP)
        self.cTrav.addCollider(self.bullet_cnodePath,self.collisionHandler)
        
        #self.bullet_cnodePath.show()
        self.bullets += [self.bullet]
    def bulletKiller(self,task):
        if self.paused:
            return Task.cont
        self.bullets[0].remove_node()
        self.bullets = self.bullets[1:]
        return Task.done
    
    
    def bulletThrower(self,task):
        if self.paused:
            return Task.cont
        #make bullet move
        if self.pandaActor.getCurrentAnim()<>'shooting' and self.pandaActor.getCurrentAnim()<>'ready_to_shoot':
            self.pandaActor.play('shooting')
        print "loL"
        self.create_bullet()
        
        self.bulletAN.getPhysicsObject().setVelocity(self.render.getRelativeVector(self.camera,Vec3(0,200,0)))
        
        self.taskMgr.doMethodLater(max(0.05,0.1*(5-self.level)),self.bulletThrower, "zombieTask_bulletThrower")
        self.taskMgr.doMethodLater(0.5,self.bulletKiller, "zombieTask_bulletKiller")
        
        self.prev=True
        
        if self.old_anim2==None:
            self.old_anim2='breathe'
        if self.old_anim2 not in ['run','walk4']:
            self.old_anim2='breathe'
        self.anim_queue = [(self.pandaActor,True,'unready_to_shoot'),(self.pandaActor,False,self.old_anim2)]
        return Task.done
        
    def movePandaTask(self,task):
        
        if self.paused:
            return Task.cont
        tempos = self.pandaActor.getPos()
        speed = 0.1
        if self.run_:
            speed+=0.3*self.level
        self.rightspeed = -(self.r-self.l)*speed
        self.forwardspeed = -(self.f-self.b)*speed
        if (self.r-self.l)<>0 and (self.f-self.b)<>0:
            #print self.forwardspeed
            #print self.rightspeed
            #sys.exit(0)
            self.rightspeed *= 0.7
            self.forwardspeed *= 0.7
        self.pandaActor.setPos(self.pandaActor,self.rightspeed, self.forwardspeed,0)
        return Task.again
    def spinCameraTask(self, task):
        if self.paused:
           
            return Task.cont
        if self.render.getRelativePoint(self.pandaActorPhysicsP,self.pandaActor.getPos())[2] < -10:
            self.pandaAN.getPhysicsObject().setVelocity(0,0,30)
            #self.pandaActor.setPos(self.pandaActorPhysicsP.getRelativePoint(self.render,Point3(10,10,100)))
        self.prev_time=task.time
        
            
            
        #play queued animations:
        for x in self.move_anim_queue+self.anim_queue:
            if x[0].getCurrentAnim()==None:
                if x[1]:
                    x[0].play(x[2])
                else:
                    x[0].loop(x[2])
                if x in self.move_anim_queue:
                    self.move_anim_queue.remove(x)
                elif x in self.anim_queue:
                    self.anim_queue.remove(x)
                    
        
        #Do other stuff
        if self.mouseWatcherNode.hasMouse():
            x=base.mouseWatcherNode.getMouseX()
            y=base.mouseWatcherNode.getMouseY()
            if self.prev_pos==None:
                self.prev_pos = (x,y)
            xx = self.prev_pos[0] - x
            yy = self.prev_pos[1] + y
            self.prev_pos = (xx,yy)
            
            self.pandaActor.setHpr(self.pandaActor,-20*(pi/2.0)*x,0,0)
            
            #self.camera.setHpr(self.pandaActor, 20*(pi/2.0)*x, 20*(pi/2.0)*yy, 0)
            if self.is_firstP:
                self.camera.lookAt(self.pandaActor)
                self.camera.setPos(self.pandaActor,0,0,4)
                self.camera.setHpr(self.camera,180,0,0)
                
            else:
                self.camera.setPos(self.pandaActor,0,8,5)
                self.camera.lookAt(self.pandaActor)
                if self.mirror:
                    self.camera.setY(-self.camera.getY())
                    self.camera.lookAt(self.pandaActor)
            self.camera.setHpr(self.camera,0,20*(pi/2.0)*yy,0)
        self.center_mouse()
        
        #zombie collisions
        return Task.cont
    
    #User Actions:
    def meelee(self):
        #Make actor stomp here. or something
        #Load animation
        self.zombieland.meelee()
        self.anim_queue += [(self.pandaActor,True,self.pandaActor.getCurrentAnim())]
        self.pandaActor.play('kick')
        #pass
    def ranged_start(self):
        #put animation here
        self.old_anim = self.pandaActor.getCurrentAnim()
        if self.old_anim not in  ['shooting','unready_to_shoot','ready_to_shoot'] :
            self.old_anim2 = self.old_anim
        if self.old_anim not in ['ready_to_shoot','shooting','unready_to_shoot']:
            self.pandaActor.play('ready_to_shoot')
        
        self.taskMgr.add(self.bulletThrower, "zombieTask_bulletThrower")
    def ranged_stop(self,task=None):
        if self.paused:
            return Task.cont
        #stop animation here
        if self.pandaActor.getCurrentAnim()<>'shooting' and task==None:
            self.pandaActor.play('shooting')
            self.taskMgr.remove("zombieTask_bulletThrower")
            self.taskMgr.doMethodLater(0.5,self.ranged_stop,'zombieTask_rangedStop')
            return Task.done
        self.taskMgr.remove("zombieTask_bulletThrower")
        return Task.done
        
loadPrcFileData('', 'fullscreen 1')
loadPrcFileData('', 'window-type none')
#loadPrcFileData('', 'show-frame-rate-meter #t')
loadPrcFileData('', 'support-threads #t')
loadPrcFileData('', 'hardware-animated-vertices #t')


app = MyApp()
app.run()
