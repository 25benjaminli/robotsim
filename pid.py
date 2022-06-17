import matplotlib.pyplot as plt
import time
import numpy as np
import pygame
import math
import threading

init_time = time.time()
WIDTH = 360
HEIGHT = 480
FPS = 30


# all_sprites = pygame.sprite.group()


class Motor: 
    def __init__(self, port):
        self.port = port
        self.pos = 0

    def move(self, amount):
        self.pos += amount

    def tare_position(self):
        self.pos = 0

    def get(self):
        return self.pos

class IMU:
    def __init__(self, port):
        self.port = port
        self.deg = 0
    
    def get(self):
        return self.deg

    

class PD:
    def __init__(self, kp, kd, minspeed):
        self.kp = kp
        self.kd = kd
        self.minspeed = minspeed
        self.prev_time = 0
        self.prev_error = 0
        self.dT = 20
        

    def get_value(self, error):
        print("error ", error)
        # t = time.time()
        
        print("dt", self.dT)
        deriv = (error - self.prev_error)/self.dT

        self.prev_error = error
        # self.prev_time = t

        speed = round((self.kp * error) + (self.kd * deriv), 2)

        if (abs(speed) < self.minspeed):
            return self.minspeed if speed > 0 else -1 * self.minspeed
        
        time.sleep(round(self.dT/1000, 3))
        return speed



class RobotSprite(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)

        self.rect = pygame.Rect(location[0], location[1], 50, 50)
        self.rect.center = location
        self.image = pygame.Surface(location)
        self.image.fill((0, 0, 0))

        

    def set_location(self, new_location):
        self.rect.center = new_location

class Button(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)


        self.rect = self.image.get_rect()
        self.rect.center = location

    

        
class Robot:
    
    def __init__(self):
        self.devices = {
            "FL": Motor(1), "FR": Motor(2), "BL": Motor(3), "BR": Motor(4),
            "IMU": IMU(5)
            
        }
        self.x = 0
        self.y = 0
        self.xGraph = np.array([]) # time, pos
        self.yGraph = np.array([])
        self.allPositions = []
        self.mode = "driver"

    def run(self):
        fps = threading.Thread(target=self.fps)
        fps.start()
    
    def fps(self):
        prev_left = 0
        prev_right = 0
        prev_phi = 0
        width = 5 # width from wheel to middle
        while(True):
            print(self.x, self.y)

            heading = self.devices["IMU"].get()
            deltaL = self.devices["FL"].get() - prev_left
            deltaR = self.devices["FR"].get() - prev_right
            middleTravelled = (deltaL + deltaR)/2
            
            phi_change = heading - prev_phi
            phi_change_rad = math.radians(heading - prev_phi)

            radiusToMiddle = middleTravelled / ((2*math.pi*phi_change)/360)

            deltaD = 2 * (math.sin(phi_change_rad) * (radiusToMiddle))

            self.x += (math.cos(heading + (phi_change / 2)) * deltaD)
            self.y += (math.sin(heading + (phi_change / 2)) * deltaD)

            prev_phi = self.devices["IMU"].get()
            prev_left = self.devices["FL"].get()



    
    def moveTrans(self, target):
        pd = PD(0.7, 0.7, 2)
        bound = 0
        startTime = 0
        while(bound < 5):
            self.yGraph = np.append(self.yGraph, self.devices["FL"].get())
            self.xGraph = np.append(self.xGraph, startTime + pd.dT)
            startTime += pd.dT
            print("hi")
            speed = pd.get_value(target - self.devices["FL"].get())
            # if abs(target - self.devices["FL"].get()) < 3:
            #     break
            if speed == pd.minspeed and abs(target - self.devices["FL"].get()) < 3:
                bound+=1
                
            self.allPositions.append(self.devices["FL"])
            print("speed", speed)
            self.devices["FL"].move(speed)
            self.devices["BL"].move(speed)
            self.devices["FR"].move(-speed)
            self.devices["BR"].move(-speed)


    def moveRot(self, deg):
        pd = PD(0.7, 0.7, 2)
        bound = 0
        startTime = 0
        while(bound < 5):
            self.yGraph = np.append(self.yGraph, self.devices["FL"].get())
            self.xGraph = np.append(self.xGraph, startTime + 0.02)

            if abs(deg - self.devices["IMU"].get() < 3): bound += 1


            speed = pd.get_value(deg - self.devices["IMU"].get()) # imu increases to the right

            self.yGraph = np.append(self.yGraph, self.devices["FL"].get())
            self.xGraph = np.append(self.xGraph, startTime + 0.02)
            startTime += 0.02
            
    def plotPID(self):
        print("hi")
        print(self.xGraph)
        
        print(self.yGraph)
        try:
            # plt.plot(np.array([1, 2]), np.array([1,]))
            plt.plot(self.xGraph, self.yGraph)
            plt.show()
        except:
            print("failed plot")
        print("hiagain")
        self.clearMovements()

    def switchMode(self, new_mode):
        self.mode = new_mode
    def plotField(self):
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Robot Visualizer")
        clock = pygame.time.Clock()

        background = pygame.Surface((WIDTH, HEIGHT)) # for drawing items
        background.fill((255, 255, 255))
        running = True
        robot = RobotSprite([0, 0])
        turnLeftButton = pygame.Rect(100, 0, 30, 30)
        turnRightButton = pygame.Rect(100, 100, 30, 30)
        print("plotting field...")
        if self.mode == "driver":
            while running:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            print("w")
                        elif event.key == pygame.K_a:
                            print("a")
                        elif event.key == pygame.K_s:
                            print("s")
                        elif event.key == pygame.K_d:
                            print("d")
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if turnLeftButton.collidepoint(event.pos):
                                print("left clicked")
                            elif turnRightButton.collidepoint(event.pos):
                                print("right clicked")
                        # print(event.key)
                screen.blit(background, robot)
                # all_sprites.draw(screen)

                pygame.display.update()
        # else: 
    


    def clearMovements(self):
        self.xGraph = np.array([])
        self.yGraph = np.array([]) 


robot = Robot()

robot.moveTrans(100)

robot.plotPID()

# robot.plotField()