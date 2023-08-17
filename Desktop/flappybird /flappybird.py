import pygame
from pygame.locals import *
import random
import neat
import os


pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 514
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

gen = 0

#image loading
bg = pygame.image.load('img/bg.png')
ground = pygame.image.load('img/ground copy.png')
button = pygame.image.load('img/restart.png')

#font
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)

#game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
pass_pipe = False
score = 0

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 50
    flappy.rect.y = int(screen_height/2)
    score = 0
    return score 

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img) 
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.velocity = 0
        self.jumped = False

    #animation function
    def update(self):
        global flying
        if flying == True:
            #gravity
            self.velocity += 0.2
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom <= 500:
                self.rect.y += int(self.velocity)

        if game_over == False:
            #jumping
            keys = pygame.key.get_pressed()
            if keys[K_SPACE]:
                self.jumped = True
                self.velocity = -7
                flying = True
            else:
                self.jumped = False

            #flapping animation
            self.counter += 1
            flap_cooldown = 15
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

        #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2 )
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self,x, y, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        #pos 1 is from the top, -1 is the bottom
        if pos == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if pos == -1:
            self.rect.topleft = [x,y + int(pipe_gap/2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
              #  pygame.transform.scale2x(self.image)

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(50, int(screen_height / 2))
bird_group.add(flappy)

button = Button(screen_width//2 -50, screen_height//2 - 100, button)

"""
def eval_nodes(nodes, config):
    #evaluates the current population
    #and sets fitness based on how 
    #good they do
    global screen, gen, ground_scroll
    s = screen 
    gen += 1
    
    nets = []
    birds = []
    n = []
    screen.blit(bg, (0, 0))
    pipe_group.draw(screen)
    screen.blit(ground, (ground_scroll, 500))

    for node_id, node in nodes:
        node.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(node, config)
        nets.append(net)
        birds.append(flappy)
        n.append(node)
    run = True
    while run and len(birds) > 0:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                game_over = True
                pygame.quit()
                quit()
        pipe_ind = 0
        if len(pipe_group) > 1 and birds[0].x > pipe_group[0].x +\
            pipe_group[0].rect.topleft:
            pipe_ind = 1
        for x, bird in enumerate(birds):
            n[x].fitness += 0.1
            global flying
            if flying == True:
                #gravity
                bird.velocity += 0.2
                if bird.velocity > 8:
                    bird.velocity = 8
                if bird.rect.bottom <= 500:
                    bird.rect.y += int(bird.velocity)

            output = nets[birds.index(bird)].activate((bird.rect.y, abs(bird.rect.y - pipe_group.rect.y),abs(bird.y - pipe_group.sprites()[0].height)))
            if output[0] > 0.5:
                bird.jumped = True
                bird.velocity = -7
                flying = True
            else: 
                bird.flying = False
            
            rem = []
            for pipe in pipe_group:
                if game_over == False:
                    ground_scroll -= scroll_speed
                    if abs(ground_scroll) > 35:
                        ground_scroll = -0
                # check for collision
                for bird in birds:
                    if pipe.collide(bird, screen):
                        n[birds.index(bird)].fitness -= 1
                        nets.pop(birds.index(bird))
                        n.pop(birds.index(bird))
                        birds.pop(birds.index(bird))

                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if add_pipe:
                score += 1
            for node in n:
                node.fitness += 5
            pipe_group.append(Pipe(screen_width))
            for r in rem:
                pipe_group.remove(r)
            for bird in birds:
                if bird.y + bird.img.get_height() - 10 >= 100 or bird.y < -50:
                    nets.pop(birds.index(bird))
                    n.pop(birds.index(bird))
                    birds.pop(birds.index(bird))
            
           # screen.blit(bg, (0, 0))
           # pipe_group.draw(screen)
            birds.draw(screen)
           # screen.blit(ground, (ground_scroll, 500))
            if len(pipe_group) > 0:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                    pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
            draw_text(str(score), font, white, int(screen_width/2), 20)
        


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                              neat.DefaultSpeciesSet, neat.DefaultStagnation,
                              config_file)
    p = neat.Population(config)

    p.add_reporter
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_nodes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

        





"""

run = True
while run:

    clock.tick(fps)

    #draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)

    #draw the ground
    screen.blit(ground, (ground_scroll, 500))

    #check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width/2), 20)

    #look for pipe collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    #checking if bird has hit ground
    if flappy.rect.bottom >= 500:
        game_over = True
        flying = False

    #draw ground scrolling
    if game_over == False and flying == True:

        #generate continuous pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            b_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            t_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(b_pipe)
            pipe_group.add(t_pipe)
            last_pipe = time_now

        #draw ground movement
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = -0

        pipe_group.update()


    if game_over == True:
        if button.draw():
            game_over = False
            score = reset_game()
            flying = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and flying == False and game_over == False:
            if event.key == pygame.K_SPACE:
                flying = True

    pygame.display.update()

pygame.QUIT()
