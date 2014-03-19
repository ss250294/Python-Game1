from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from panda3d.core import *
if __name__=="__main__":
    import direct.directbase.DirectStart


 
# Add bar
bar = DirectWaitBar(text = "", value = 50, pos = (0,-1,.8), barColor = (0,1,0,0.8))

#Add crosshair
crosshair = OnscreenImage(image = 'crosshair.png', scale = 0.06)
crosshair.setTransparency(TransparencyAttrib.MAlpha)


# Add some text
bk_text = "Health:"
textObject = OnscreenText(text = bk_text, pos = (-1,0.9),scale = 0.07,fg=(0,1,0,1),align=TextNode.ALeft,mayChange=1, bg = (0,0,0,0.4),frame= (1,0,0,0.5))

info="center info"
information = OnscreenText(text = "", pos = (0,0.55), scale = 0.06, fg = (0,1,0,1), align=TextNode.ACenter, mayChange=1, frame= (1,1,1,0.9))
press_enter = OnscreenText(text = "Press Enter to Start Game", pos = (0,-0.9), scale = 0.09, fg = (1,0,0,1), bg = (1,1,1,0.8), align=TextNode.ACenter)
score_ = OnscreenText(text = "", pos = (0.5,0.9), scale = 0.07, fg = (0,1,0,1), align=TextNode.ALeft, mayChange=1, bg = (0,0,0,0.4),frame= (1,0,0,0.5))

general_information = OnscreenText(text = "P - Pause, Alt+F4 - Close", pos = (-1.4,0.8), scale = 0.06, fg = (0,1,0,1),  align=TextNode.ACenter, mayChange=1, bg = (0,0,0,0.4),frame= (1,0,0,0.5))
def update_info(infoo):
    information.setText(infoo)
def update_score(score):
    score_.setText("Pandas Killed: " + str(score))
def incBar(arg):
	bar['value'] =	arg
	text = "Health:"+str(bar['value'])+'%'
	textObject.setText(text)

if __name__=="__main__":
    run()
