import pygame, sys

screen_height = 1024
screen_width = 720
world_height = 100
world_width = 100

class Game:
    def __init__(self):
        self.screen = World(self, world_width, world_height)

    def key_pressed(self, key_char):
        print(key_char)

    def draw(self, surface):
        self.screen.draw(surface)

class Screen:
    def __init__(self, game):
        self.game = game

    def key_pressed(self, key_char):
        pass

    def draw(self, surface):
        pass

    def update(self, delta):
        pass

class World:
    def __init__(self, game, width, height):
        Screen.__init__(self, game)

    def draw(self, surface):
        print("blit")

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.DOUBLEBUF)
    clock = pygame.time.Clock()

    game = Game()
    pygame.key.set_repeat(500, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                game.key_pressed(event.key)

        screen.fill((0,0,0,0))

        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

