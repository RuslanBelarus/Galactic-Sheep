#module imports
import random
import pygame
import keyboard

#initializating
pygame.init()
pygame.font.init()

#systrem global variables
screen = pygame.display.set_mode((18*32, 20*32))
clock = pygame.time.Clock()
FPS = 60
deltaTime = 1 / FPS
font = pygame.font.Font(None, 36)

#game global variables
best_score = 0
difficult = 1

class Galactic:

    def __init__(self):
        self.texture = pygame.image.load('assets/star.png')
        self.enemy = []
        self.max_enemy = 20

    def __AddStar(self):
        #(NEW) star creating
        self.enemy.append([random.randint(0, 18*32), 0, pygame.transform.rotate(self.texture, random.randint(0, 360))])

    def Start(self):
        #start star's crrating
        for i in range(self.max_enemy):
            self.enemy.append([random.randint(0, 18*32), random.randint(0, 20*32), pygame.transform.rotate(self.texture, random.randint(0, 360))])

    def Update(self, screen):
        #star's logic
        for i in range(self.max_enemy):
            if self.enemy[i][1] > 20*32:
                del self.enemy[i]
                self.__AddStar()
            else:
                self.enemy[i][1] += 128*deltaTime
                screen.blit(self.enemy[i][2], (self.enemy[i][0], self.enemy[i][1]))

class Entity:

    def __init__(self, x : int, y : int, texture):
        self.texture = texture
        self.x = x
        self.y = y

    def Draw(self, screen : pygame.Surface) -> None:
        #Draw Entity
        if self.texture != None: screen.blit(self.texture, (self.x, self.y))

class SlikeBullet(Entity):

    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.hitbox = pygame.Rect(self.x, self.y, 16, 24)

    def Draw(self, screen):
        #Draw bullet
        pygame.draw.rect(screen, (0, 255, 0), self.hitbox)

    def Controll(self, screen):
        #bulet logic
        self.hitbox = pygame.Rect(self.x, self.y, 16, 24)
        self.Draw(screen)
        self.y += 256*deltaTime

class Slike(Entity):

    def __init__(self, x, y):
        super().__init__(x, y, pygame.transform.scale(pygame.image.load('assets/slike.png'), (64, 64)))
        self.hitbox = pygame.Rect(self.x, self.y, 64, 64)
        self.velocity = 1
        self.delay = 0

    def Controll(self, screen, enemy):
        #hitbox reject
        self.hitbox = pygame.Rect(self.x, self.y, 64, 64)

        #Draw
        self.Draw(screen)

        #velocity reject
        if self.x < 0:
            self.velocity = 1
        elif self.x > 18*32:
            self.velocity = -1

        #FirstPersonController
        self.x +=  difficult * self.velocity * 128 * deltaTime
        self.y += 0.2

        #SlimeBullet pull delay3
        if self.delay > 0: self.delay -= 1
        if self.delay == 0:
            enemy[2].append(SlikeBullet(self.x+23, self.y))
            self.delay = 2/difficult * FPS



class Bullet(Entity):

    def __init__(self, x, y):
        super().__init__(x, y, None)
        self.hitbox = pygame.Rect(self.x, self.y, 16, 24)

    def Draw(self, screen):

        #drawing of bullet
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox)

    def Controll(self, screen):

        #no comments :)
        self.hitbox = pygame.Rect(self.x, self.y, 16, 24)
        self.Draw(screen)
        self.y -= 528*deltaTime

class Player(Entity):

    def __init__(self, x, y, texture):
        super().__init__(x, y, texture)
        self.hitbox = pygame.Rect(self.x, self.y, 64, 64)
        self.score = 0
        self.delay = 0

    def Controll(self, screen, enemy):

        #retype of hitbox & draw Entity
        self.hitbox = pygame.Rect(self.x, self.y, 64, 64)
        self.Draw(screen)

        #FirstPersonController
        if keyboard.is_pressed('a') and self.x > 0: self.x -= 200*deltaTime
        if keyboard.is_pressed('d') and self.x < 17*32: self.x += 200*deltaTime
        if keyboard.is_pressed('w') and self.y > 10*32: self.y -= 200*deltaTime
        if keyboard.is_pressed('s') and self.y < 18*32-10: self.y += 200*deltaTime

        #Bullet pull delay
        if self.delay > 0: self.delay -= 1
        if pygame.mouse.get_pressed()[0] and self.delay <= 0:
            enemy[1].append(Bullet(self.x+23, self.y))
            self.delay = difficult*FPS

#start round function
def start():
    global best_score

    #standart setting
    sheep = Player(18*32/2, 18*32-10, pygame.transform.scale(pygame.image.load('assets/player.png'), (64, 64)))
    galactic = Galactic()
    enemy = [[], [], []]
    spawn_delay = 5 * FPS
    
    #Round end
    WASTED = False

    #galactic star creating
    galactic.Start()

    #main loop
    while not WASTED:
        
        #frame per tick
        clock.tick(FPS)

        #window updating
        screen.fill((0, 0, 0))

        #score render
        screen.blit(font.render(f'Score {sheep.score}', False, (255, 255, 255)), (0, 0))

        #Colliding controlling
        for i in range(len(enemy[0])):
            for j in range(len(enemy[1])):
                try:
                    if enemy[0][i].hitbox.colliderect(enemy[1][j].hitbox):
                        del enemy[0][i]
                        del enemy[1][j]
                        sheep.score += 20*0.5*difficult
                        break
                except: pass

        #player death controll
        for i in range(len(enemy[2])):
            if enemy[2][i].hitbox.colliderect(sheep.hitbox):
                WASTED = True

        #spawn of slime's
        spawn_delay -= 1
        if spawn_delay == 0:
            enemy[0].append(Slike(random.randint(0, 18*32), 0))
            spawn_delay = 1.5 * FPS

        #events pygame.QUIT
        for event in pygame.event.get():
            if event == pygame.QUIT:
                exit()

        #Controll update of enemy's
        galactic.Update(screen)
        sheep.Controll(screen, enemy)

        for i in range(len(enemy[1])):
            enemy[1][i].Controll(screen)
        for i in range(len(enemy[0])):
            enemy[0][i].Controll(screen, enemy)
        for i in range(len(enemy[2])):
            enemy[2][i].Controll(screen)

        pygame.display.flip()

    #Death'd menu
    if WASTED:
        deathScreenLoop = True
        while deathScreenLoop:

            #frame per second
            clock.tick(FPS)

            #screen clear
            screen.fill((0, 0, 0))

            #quit tracker
            for event in pygame.event.get():
                if event == pygame.QUIT:
                    exit()

            #text render
            screen.blit(font.render(f'Best score: {best_score}', False, (255, 255, 225)), (18*32/2-18*32/2/4-25, 20*32/3-160))
            screen.blit(font.render(f'Score: {sheep.score}', False, (255, 255, 200)), (18*32/2-18*32/2/4, 20*32/3-120))
            screen.blit(font.render('You dead', False, (255, 255, 255)), (18*32/2-18*32/2/4, 20*32/3))
            screen.blit(font.render('PRESS [T] TO RETURN', False, (255, 255, 255)), (18*32/2-18*32/4, 20*32/3+40))

            #infinity waiting loop
            if keyboard.is_pressed('t'):
                deathScreenLoop = False
                break

            #best score system
            if sheep.score > best_score:
                best_score = sheep.score
            
            pygame.display.flip()

class Button:

    def __init__(self, x, y, text, color=(0, 0, 0), dx=0, dy=0, hitbox_color=(0, 0, 0)):

        #button text
        self.text = font.render(text, False, color)

        #coords
        self.x = x
        self.y = y

        #hitbox_sizes & color
        self.hitbox_sx = self.text.get_width()
        self.hitbox_sy = self.text.get_height()
        self.hitbox_color = hitbox_color

        #buffers
        self.dx = dx
        self.dy = dy

        #hitbox
        self.hitbox = pygame.Rect(self.x-self.dx, self.y-self.dy, self.hitbox_sx+self.dx*2, self.hitbox_sy+self.dy*2)

    def Draw(self, screen):

        #drawing of hitbox
        pygame.draw.rect(screen, self.hitbox_color, self.hitbox)

        #text overlay
        screen.blit(self.text, (self.x, self.y))

    def IsPressed(self):

        #get values
        is_mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        mouse_hitbox = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)

        #condition
        if self.hitbox.colliderect(mouse_hitbox) and is_mouse_pressed:
            return True
        else:
            return False

#menu
def menu():
    global difficult, best_score

    #Loop variable
    inMenu = True

    #create exemple of Galactic class
    galactic = Galactic()

    #summon start stars enum
    galactic.Start()

    #difficult set cooldown
    dif_set_cooldown = 0

    while inMenu:
        #frame per second
        clock.tick(FPS)

        #screen clear
        screen.fill((0, 0, 0))

        #Star's update
        galactic.Update(screen)

        #quit tracker
        for event in pygame.event.get():
            if event == pygame.QUIT:
                exit()
        
        #label
        screen.blit(pygame.font.Font(None, 100).render('Galactic Sheep', False, (255, 255, 225)), (18*32/2-255, 20*32/2-255))

        #best score label render
        screen.blit(font.render(f'Best score: {best_score}', False, (255, 255, 200)), (18*32/2-80, 20*32/2-190))

        #buttons init
        button_play = Button(18*32/2-40, 20*32/2-100, 'Play', dx=10, dy=10, color=(225, 225, 225), hitbox_color=(150, 150, 150))
        if difficult == 1: button_difficult = Button(18*32/2-60, 20*32/2-30, 'Difficult', dx=10, dy=10, color=(0, 225, 0), hitbox_color=(150, 150, 150))
        elif difficult == 2: button_difficult = Button(18*32/2-60, 20*32/2-30, 'Difficult', dx=10, dy=10, color=(225, 225, 0), hitbox_color=(150, 150, 150))
        else: button_difficult = Button(18*32/2-60, 20*32/2-30, 'Difficult', dx=10, dy=10, color=(225, 0, 0), hitbox_color=(150, 150, 150))
        button_exit = Button(18*32/2-40, 20*32/2+40, 'Exit', dx=10, dy=10, color=(225, 225, 225), hitbox_color=(150, 150, 150))

        #buttons draw
        button_play.Draw(screen)
        button_difficult.Draw(screen)
        button_exit.Draw(screen)

        #buttons logic

        #start game
        if button_play.IsPressed():
            start()
        
        #set difficult (hormal, hard, extreme)
        if button_difficult.IsPressed():
            if dif_set_cooldown == 0:
                dif_set_cooldown = 1.5 * FPS
                if difficult < 3: difficult += 1
                else: difficult == 1

        #quit menu -> exit from app (.exe | .py)
        if button_exit.IsPressed():
            inMenu = False

        #set difficult cooldown set to 0
        if dif_set_cooldown > 0: dif_set_cooldown -= 1
    
        pygame.display.flip()

#protection
if __name__ == '__main__':
    #menu activation
    menu()