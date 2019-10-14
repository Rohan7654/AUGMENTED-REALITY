import numpy as np
import cv2
import cv2.aruco as aruco
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import pygame
width = 640
height=480
gamedisplay = pygame.display.set_mode((640,480))
color=[255,255,255]
gamedisplay.fill(color)
pygame.display.update()
texture_object = None
texture_background = None
camera_matrix = None
dist_coeff = None
cap = cv2.VideoCapture(0)
INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [-1.0,-1.0,-1.0,-1.0],
                           [ 1.0, 1.0, 1.0, 1.0]])
##############################################################
def getCameraMatrix():
        global camera_matrix, dist_coeff
        with np.load('System.npz') as X:
                camera_matrix, dist_coeff, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]

spin = 0.0
########################################################################
def spinDisplay():
   global spin
   spin = spin + 8.0
   if(spin > 360.0):
      spin = spin-360.0
   glutPostRedisplay()
###################################################################
     
def main():
        glutInit()
        getCameraMatrix()
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(625, 100)
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        window_id = glutCreateWindow("3D RENDERING")
        init_gl()
        glutDisplayFunc(drawGLScene)
        glutIdleFunc(drawGLScene)
        glutReshapeFunc(resize)
        glutMainLoop()

########################################################### 
def init_gl():
        global texture_object, texture_background
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0) 
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)   
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        texture_background = glGenTextures(1)
        texture_object = glGenTextures(1)
########################################################
def resize(w,h):
        ratio = 1.0* w / h
        glMatrixMode(GL_PROJECTION)
        glViewport(0,0,w,h)
        gluPerspective(45, ratio, 0.1, 100.0)

############################################################
def drawCube(img, ar_list, ar_id, camera_matrix, dist_coeff):
        for x in ar_list:
                if ar_id == x[0]:
                        rvec, tvec = x[2], x[3]
        markerLength = 100
        m = markerLength/2 
        pts = np.float32([[-m,m,0],[m,m,0],[m,-m,0],[-m,-m,0],[-m,m,2*m],[m,m,2*m],[m,-m,2*m],[-m,-m,2*m]])
        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
        imgpts=np.int32(imgpts).reshape(-1,2)
        img=cv2.drawContours(img,[imgpts[:4]],-1,(0,0,255),2)
        for i,j in zip(range(4),range(4,8)):
                img=cv2.line(img,tuple(imgpts[i]),tuple(imgpts[j]),(0,0,255),2)
        img=cv2.drawContours(img,[imgpts[4:]],-1,(0,0,255),2) 
        return img
##################################################################

def drawCylinder(img, ar_list, ar_id, camera_matrix, dist_coeff):
        for x in ar_list:
                if ar_id == x[0]:
                        rvec, tvec = x[2], x[3]
        markerLength = 100
        radius = markerLength/2; height = markerLength*1.5
        m=int(radius)
        h=height
        pts=np.float32([[0,-m,0],[-0.5*m,-0.85*m,0],[-0.85*m,-0.5*m,0],[-m,0,0],[-0.85*m,0.5*m,0],[-0.5*m,0.85*m,0],
                        [0,m,0],[0.5*m,0.85*m,0],[0.85*m,0.5*m,0],[m,0,0],[0.85*m,-0.5*m,0],[0.5*m,-0.85*m,0],
                        [0,-m,h],[-0.5*m,-0.85*m,h],[-0.85*m,-0.5*m,h],[-m,0,h],[-0.85*m,0.5*m,h],[-0.5*m,0.85*m,h],
                        [0,m,h],[0.5*m,0.85*m,h],[0.85*m,0.5*m,h],[m,0,h],[0.85*m,-0.5*m,h],[0.5*m,-0.85*m,h]])
        imgpts, _ = cv2.projectPoints(pts, rvec, tvec, camera_matrix, dist_coeff)
        imgpts=np.int32(imgpts).reshape(-1,2)
        for i,j in zip(range(6),range(6,12)):
            img=cv2.line(img,tuple(imgpts[i]),tuple(imgpts[j]),(255,0,0),2)
        for i,j in zip(range(12,18),range(18,24)):
            img=cv2.line(img,tuple(imgpts[i]),tuple(imgpts[j]),(255,0,0),2)
        for i,j in zip(range(12),range(12,24)):
            img=cv2.line(img,tuple(imgpts[i]),tuple(imgpts[j]),(255,0,0),2)
        cord=[]
        cord1=[]
        for angle in range(0,360):
            theta=math.radians(angle)
            x=m*math.cos(theta)
            y=m*math.sin(theta)
            cord.append([x,y,0])
            cord1.append([x,y,h])
        imgpts, _ = cv2.projectPoints(np.float32([cord]), rvec, tvec, camera_matrix, dist_coeff)
        imgpts=np.int32(imgpts).reshape(-1,2)
        img=cv2.drawContours(img,[imgpts[:len(imgpts)]],-1,(255,0,0),2)
        imgpts, _ = cv2.projectPoints(np.float32([cord1]), rvec, tvec, camera_matrix, dist_coeff)
        imgpts=np.int32(imgpts).reshape(-1,2)
        img=cv2.drawContours(img,[imgpts[:len(imgpts)]],-1,(255,0,0),2)
        return img
 ##################################################################
def drawGLScene():
        global pyimg
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ar_list = []
        ret, frame = cap.read()
        if ret == True:
                draw_background(frame)
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                ar_list = detect_markers(frame)
                for i in ar_list:
                        if i[0] == 8:
                                pyimg = pygame.image.load("download.png")
                                pyimg=pygame.transform.scale(pyimg,(200,200))
                                overlay(frame, ar_list, i[0],"texture_1.png")
                                drawCube(frame, ar_list, i[0],camera_matrix, dist_coeff)
                                drawCylinder(frame, ar_list, i[0],camera_matrix, dist_coeff)
                                
                        if i[0] == 2:
                                pyimg = pygame.image.load("download1.png")
                                pyimg=pygame.transform.scale(pyimg,(200,200))
                                overlay(frame, ar_list, i[0],"texture_2.png")
                                drawCube(frame, ar_list, i[0],camera_matrix, dist_coeff)
                                drawCylinder(frame, ar_list, i[0],camera_matrix, dist_coeff)
                        if i[0] == 7:
                                pyimg = pygame.image.load("download2.jpg")
                                pyimg=pygame.transform.scale(pyimg,(200,200))
                                overlay(frame, ar_list, i[0],"texture_3.png")
                                drawCube(frame, ar_list, i[0],camera_matrix, dist_coeff)
                                drawCylinder(frame, ar_list, i[0],camera_matrix, dist_coeff)
                        if i[0] == 6:
                                pyimg = pygame.image.load("download3.png")
                                pyimg=pygame.transform.scale(pyimg,(200,200))
                                overlay(frame, ar_list, i[0],"texture_4.png")
                                drawCube(frame, ar_list, i[0],camera_matrix, dist_coeff)
                                drawCylinder(frame, ar_list, i[0],camera_matrix, dist_coeff)
                cv2.putText(frame,'###CREATED BY ROHAN AND MANOJ###',(10,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
                cv2.imshow('frame',ig)
                cv2.waitKey(1)
        glutSwapBuffers()

##########################################################
def detect_markers(img):
        aruco_list = []
        global ig
        global l
        l=[]
        aruco_dict=aruco.Dictionary_get(aruco.DICT_5X5_250)
        parameters=aruco.DetectorParameters_create()
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        corners,ids,_=aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
        ig=aruco.drawDetectedMarkers(img,corners,ids)
        if(np.all(ids!=None)):
            for idn in ids:
                for cor in corners:
                        M=cv2.moments(cor)
                        cx=math.ceil(int(M['m10']/M['m00']))
                        cy=math.ceil(int(M['m01']/M['m00']))
                        l=[cx,cy]
                rvec,tvec,_=aruco.estimatePoseSingleMarkers(corners,100,camera_matrix,dist_coeff)
                aruco_list.append([idn,l,rvec,tvec])
        return aruco_list

################# #######################################

def draw_background(img):
        glEnable(GL_TEXTURE_2D)
        bg_image = cv2.flip(img, 0)
        bg_image = Image.fromarray(bg_image)     
        ix = bg_image.size[0]
        iy = bg_image.size[1]
        bg_image = bg_image.tobytes('raw', 'BGRX', 0, -1)
        glBindTexture(GL_TEXTURE_2D, texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)
        glBindTexture(GL_TEXTURE_2D,texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-10.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-6.0, -4.6, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 6.0, -4.6, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 6.0,  4.6, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-6.0,  4.6, 0.0)
        glEnd( )
        glPopMatrix()
        return None
####################################################################

def init_object_texture(image_filepath):
        textureSurface = pygame.image.load(image_filepath)
        textureData = pygame.image.tostring(textureSurface,"RGBA",1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()
        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        return None

######################################################################
def multi(viewmatrix):
        glPushMatrix()
        glLoadMatrixd(viewmatrix)
        glRotatef(spin, 1.0, 1.0, 1.0)
        #glutWireSphere(0.2,100,100)
        #glutSolidTorus(0.1,0.4,100, 100)
        #glRectf(-0.35,-0.35,0.35,0.35)
        gamedisplay.fill(color)
        pygame.display.update()
        gamedisplay.blit(pyimg,(width/4+50,height/4))
        pygame.display.update()
        #glutSolidCube(0.25)
        glutSolidTeapot(0.28)
        spinDisplay()
        glPopMatrix()
        
def overlay(img, ar_list, ar_id, texture_file):
        for x in ar_list:
                if ar_id == x[0]:
                        centre, rvec, tvec = x[1], x[2], x[3]
        for r in rvec:
                rmtx = cv2.Rodrigues(r)[0]
                view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvec[0][0][0]/250],
                                [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvec[0][0][1]/250-0.45],  ##800-0.45
                                [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvec[0][0][2]/500+0.8],
                                [0.0       ,0.0       ,0.0       ,1.0]])
                view_matrix = view_matrix * INVERSE_MATRIX
                view_matrix = np.transpose(view_matrix)
                init_object_texture(texture_file)
                multi(view_matrix)


########################################################################

if __name__ == "__main__":
        main()

        
