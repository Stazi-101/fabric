
import pygame
import random
import time
import math
import numpy as np

# Global option thingies

SCREEN_SIZE = (500,500)

MIN_LINK_LEN = 21
X_RANGE = range(0,401,20)
Y_RANGE = range(-200,-199)
Z_RANGE = range(-200,201,20)
STATIC_CONDITION = lambda x,y,z: x==0 

START_ROTATION = [0]
TO_MIDDLE = np.array( (SCREEN_SIZE[0]//2,SCREEN_SIZE[1]//2,0) )
ROTATE_SPEED = math.pi/60

SPRING_K = .2
LINEAR_DRAG = .01
QUADRATIC_DRAG = .005

SNAP = True


class World():

    def __init__(self):

        self.size = SCREEN_SIZE
        self.min = MIN_LINK_LEN

        pygame.init()
        self.screen = pygame.display.set_mode( self.size )

        self.rotation = START_ROTATION
        #self.rotCen = np.array( [0, 0 , 0 ] )

        self.points = []

        for x in X_RANGE:
            for y in Y_RANGE:
                for z in Z_RANGE:
                    
                    pos = np.array( (x, y, z), dtype=np.float64 )
                    static = STATIC_CONDITION(x,y,z)
                    self.points.append( Point(pos,static=static) )
                
        self.genLinks()

        


    def genLinks(self):

        self.links = []

        for p1 in self.points:
            for p2 in self.points:
               
                if p1==p2:
                    next

                if np.linalg.norm(p1.pos-p2.pos) < self.min:
                    self.links.append( Link(p1,p2) )


    def tick(self):


        def spring():
           
            for link in self.links:

                p1,p2 = link.s,link.e

                if  (p1.pos-p2.pos).any() :
                   
                    dis = np.linalg.norm( p1.pos - p2.pos )
                    ext = link.len - dis
                    v = ext * (p1.pos-p2.pos)/dis *SPRING_K

                    p1.vel +=  v
                    p2.vel += -v

        def gravity():
            for point in self.points:
                point.vel += np.array( (0, .3, 0) )

        def drag():

            for point in self.points:

                
                v = point.vel
                modv = np.linalg.norm(v)
                
                drag  = ( modv * LINEAR_DRAG )
                drag += ( modv**2 * QUADRATIC_DRAG )
                
                mult = (modv-drag)/modv
                #if random.random()<1/100:
                #    print(point.vel,modv,drag,mult)
                if mult <0:
                    if SNAP:
                        del point
                        return
                    else:
                        mult = 0

                point.vel *= mult

        def move():

            for point in self.points:
                if not point.static:
                    point.pos += point.vel


        funList = [ spring, gravity, drag, move ]
        for fun in funList:
            fun()

        #self.rotation[0] += math.pi/240

       

    def draw(self):

        self.screen.fill( (0,0,0) )

        self.rot = genRotation( self.rotation[0] )
        
        for link in self.links:

            s = self.getScreen( link.s.pos )
            e = self.getScreen( link.e.pos )
            pygame.draw.line(self.screen, [20,20,20], e,s )

        for point in self.points:

            color = (255, 0 ,255) if point.static else (255,255,255)
            #pygame.draw.circle(self.screen, color, point.getScreen(),1 )
            self.screen.set_at( self.getScreen(point.pos), color )

        pygame.display.update()

    def getScreen( self, pos ):
        npos = np.dot( self.rot, pos )
        npos += TO_MIDDLE
        return  int(npos[0]) , int(npos[1])

    def fromScreen( self, pos ):
        npos = np.array( (pos[0],pos[1],0), dtype = float )
        npos -= TO_MIDDLE

        return npos 
        

class Point():


    def __init__(self, pos, static=False):

        self.pos = pos
        self.static = static
        self.vel = np.array( (0,0,0), dtype = np.float64 )
    '''
    def getScreen(self, rot, centre ):
        rpos = np.dot( rot, self.pos )
        rpos += TO_MIDDLE

        
        return ( int(rpos[0]) , int(rpos[1]) )
    '''



class Link():

    def __init__(self, p1, p2):

        self.s = p1
        self.e = p2
        self.dis = 0
        self.len = np.linalg.norm( p1.pos - p2.pos )



def main():

    world = World()
    print('w')
    
    clock = pygame.time.Clock()
    clicked = None

    print('l')
    while True:

        ms = clock.tick(30)
        #print( 1000/ms )
        world.tick()

        
        endNow, clicked = events(world, clicked)
        if endNow:
            return
        
        
        world.draw()




def events( world, clicked ):

    if clicked:
        mpos = pygame.mouse.get_pos()
        mpos = world.fromScreen( mpos )
        clicked.pos[:2] = mpos[:2]


    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            return True, None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not clicked:
                    mpos = pygame.mouse.get_pos()
                    mpos = world.fromScreen( mpos )
                    clicked = min( world.points, key = lambda p: np.linalg.norm(p.pos-mpos) )
            if event.button == 4:
                world.rotation[0] += ROTATE_SPEED
            if event.button == 5:
                world.rotation[0] +=-ROTATE_SPEED
                
        if event.type == pygame.MOUSEBUTTONUP:
            if clicked:
                clicked.vel = np.array( (0,0,0), dtype=np.float64 )
                clicked = None

    '''
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        world.rotation[0] += math.pi/120
    if keys[pygame.K_d]:
        world.rotation[0] +=-math.pi/120
    '''
    

    return False, clicked


def genRotation( a ):
    return np.array( (( math.cos(a), 0, -math.sin(a) ),
                      (       0    , 1,      0       ),
                      ( math.sin(a), 0,  math.cos(a) )) )


if __name__ == '__main__':
    main()
    pygame.quit()

