import pygame, sys
import pygame.freetype
import pygame.sysfont
from pygame import Rect

tilesize = 128
fontsize = 15

sprite_height = tilesize
sprite_width = tilesize
screen_height = 768
screen_width = 640

tiles_per_row = screen_width / tilesize
tiles_per_col = screen_height / tilesize

left = 0
front = 1
back = 2
right = 3

player_health_index = 0
player_attack_index = 1
monster_health_index = 2

class Game:
    def __init__(self):
        self.screen = MainMenu(self)
        self.fonter = FontManager("cousine", fontsize, bold=True)

    def key_pressed(self, key_char):
        self.screen.key_pressed(key_char)

    def switch_screen(self, screen):
        self.screen = screen

    def draw(self, surface):
        self.screen.draw(surface)

class FontManager:
    def __init__(self, name, size, **kwargs):
        self.font = self.get_font(name, size, **kwargs)

    def get_font(self, name, size, **kwargs):
        return pygame.freetype.SysFont(name, size, **kwargs)

    def draw(self, surface, pos, text, color):
        self.font.render_to(surface, pos, text, color)

class Screen:
    def __init__(self, game):
        self.game = game

    def key_pressed(self, key_char):
        pass

    def draw(self, surface):
        pass

    def update(self, delta):
        pass

class WorldObject:
    def __init__(self, world):
        self.world = world

class MenuItem:
    def __init__(self, text):
        self.text = text

class DisplayItem:
    def __init__(self, text, data):
        self.text = text
        self.data = data

    def update(self, new_data):
        self.data = new_data

    def output(self):
        return self.text + str(self.data)

class MenuItem:
    def __init__(self, text, action):
        self.text = text
        self.action = action

class Menu(Screen):
    def __init__(self, game, items):
        Screen.__init__(self, game)
        self.items = items
        self.selected = 0

    def key_pressed(self, key_char):
        i = 0
        if key_char == pygame.K_w or key_char == pygame.K_UP:
            i -= 1
        if key_char == pygame.K_s or key_char == pygame.K_DOWN:
            i += 1

        self.selected += i

        if self.selected < 0:
            self.selected = len(self.items)-1
        if self.selected >= len(self.items):
            self.selected = 0

        if key_char == pygame.K_RETURN:
            self.items[self.selected].action()

    def draw(self, surface):
        for (i, item) in enumerate(self.items):
            color = pygame.Color(255, 255, 255)
            if i == self.selected:
                color = pygame.Color(255, 0, 100)
            rect = self.game.fonter.font.get_rect(item.text, size = fontsize)
            self.game.fonter.draw(surface, ((screen_width/2) - ((rect.right - rect.left)/2), (screen_height/2)+(((rect.bottom - rect.top)+5)*i)), item.text, color)

class MainMenu(Menu):
    def __init__(self, game):
        items = []
        items.append(MenuItem("NEW GAME", lambda: self.game.switch_screen(World(self.game))))
        items.append(MenuItem("CREDITS", lambda: self.game.switch_screen(CreditsMenu(self.game))))
        items.append(MenuItem("EXIT", lambda: sys.exit()))
        Menu.__init__(self, game, items)

    def key_pressed(self, key_char):
        if key_char == pygame.K_q:
            sys.exit()

        Menu.key_pressed(self, key_char)

class CreditsMenu(Menu):
    def __init__(self, game):
        items = []
        items.append(MenuItem("Rougelike: Hand-Carved by Cloin", lambda: None))
        Menu.__init__(self, game, items)
        self.selected = -1

    def key_pressed(self, key_char):
        if key_char == pygame.K_q:
            self.game.switch_screen(MainMenu(self.game))

        Menu.key_pressed(self, key_char)
        self.selected = -1

class Tile(WorldObject):
    def __init__(self, world, sprite, is_solid):
        WorldObject.__init__(self, world)
        self.sprite = sprite
        self.is_solid = is_solid
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)

    def is_collidable(self):
        if self.is_solid:
            return True
        for entity in self.entities:
            if entity.is_collidable():
                return True
        return False

    def collide(self, collider):
        if self.is_solid:
            return

        for entity in self.entities:
            entity.collide(collider)

    def draw(self, surface, x, y):
        surface.blit(self.sprite, (x, y))

        for entity in self.entities:
            entity.draw(surface, x, y-(sprite_height/2))

class Entity(WorldObject):
    def __init__(self, world, sprites, loc):
        WorldObject.__init__(self, world)
        world.game_map[loc[0]][loc[1]].add_entity(self)

        self.sprites = sprites
        self.x = loc[0]
        self.y = loc[1]
        self.anim_state = 0

    def move(self, x, y):
        self.move_to(self.x + x, self.y + y)

    def remove(self):
        self.world.game_map[self.x][self.y].remove_entity(self)

    def is_collidable(self):
        return True

    def collide(self, collider):
        pass

    def move_to(self, x, y):
        self.world.game_map[self.x][self.y].remove_entity(self)
        self.world.game_map[x][y].add_entity(self)

        self.x = x
        self.y = y

    def turn(self, direction):
        if len(self.sprites) < direction:
            return
        self.anim_state = direction

    def draw(self, surface, x, y):
        surface.blit(self.sprites[self.anim_state], (x, y))

class Player(Entity):
    skin_color = pygame.Color(203, 203, 203)
    bag_color = pygame.Color(152, 152, 152)
    shirt_color = pygame.Color(136, 136, 136)
    hat_rim_color = pygame.Color(123, 123, 123)
    hat_color = pygame.Color(94, 94, 94)
    boots_color = pygame.Color(84, 84, 84)

    def __init__(self, world, sprites, loc):
        Entity.__init__(self, world, [], loc)

        self.x = loc[0]
        self.y = loc[1]
        self.health = 100
        self.attack = 10

        self.original = sprites
        for sprite in sprites:
            sprite = sprite.copy()
            px = pygame.PixelArray(sprite)
            px.replace(self.skin_color, pygame.Color(105, 0, 0))
            px.replace(self.bag_color, pygame.Color(155, 0, 0))
            px.replace(self.shirt_color, pygame.Color(255, 0, 0))
            px.replace(self.hat_rim_color, pygame.Color(155, 0, 0))
            px.replace(self.hat_color, pygame.Color(255, 0, 0))
            px.replace(self.boots_color, pygame.Color(55, 0, 0))
            self.sprites.append(sprite)

    def update_displays(self):
        self.world.items[player_health_index].data = self.health
        self.world.items[player_attack_index].data = self.attack

    def move_to(self, x, y):
        if self.x > x:
            self.turn(left)
        elif self.x < x:
            self.turn(right)
        if self.y > y:
            self.turn(back)
        elif self.y < y:
            self.turn(front)

        if x >= self.world.width:
            return
        if x < 0:
            return
        if y >= self.world.height:
            return
        if y < 0:
            return

        if not self.world.game_map[x][y].is_collidable():
            Entity.move_to(self, x, y)
            self.world.center()
        else:
            self.world.game_map[x][y].collide(self)

class Monster(Entity):
    body_color = pygame.Color(136, 136, 136)

    def __init__(self, game, sprites, loc):
        Entity.__init__(self, game, [], loc)

        self.health = 20

        self.original = sprites
        for sprite in sprites:
            sprite = sprite.copy()
            px = pygame.PixelArray(sprite)
            px.replace(self.body_color, pygame.Color(40, 0, 0))
            self.sprites.append(sprite)

    def collide(self, collider):
        self.health -= collider.attack

        collider.health -= 10
        collider.update_displays()

        if self.health <= 0:
            self.remove()

        if collider.health <= 0:
            collider.remove()

    def move_to(self, x, y):
        if self.x > x:
            self.turn(left)
        elif self.x < x:
            self.turn(right)
        if self.y > y:
            self.turn(back)
        elif self.y > y:
            self.turn(front)

        if x >= self.world.width:
            return
        if x < 0:
            return
        if y >= self.world.height:
            return
        if y > 0:
            return

        if not self.world.game_map[x][y].is_collidable():
            Entity.move_to(self, x, y)
            self.world.center()
        else:
            self.world.game_map[x][y].collide(self)

class World(Screen):
    def __init__(self, game):
        Screen.__init__(self, game)

        self.entity_map = load_sprite("assets/sprites/entitiesx128.png", sprite_width, sprite_height)
        self.tile_map = load_sprite("assets/sprites/tilesx128.png", sprite_width, sprite_height)

        game_map = load_map('map')
        self.game_map = []
        self.width = len(game_map)
        self.height = len(game_map[0])
        self.items = []

        temp_surf = pygame.Surface((tilesize, tilesize))

        for x in range(0, self.width):
            line = []
            self.game_map.append(line)
            for y in range(0, self.height):
                print(game_map[x][y])
                if game_map[x][y] == '0':
                    line.append(Tile(self, self.tile_map[0][0], False))
                elif game_map[x][y] == '1':
                    line.append(Tile(self, self.tile_map[0][1], True))
                elif game_map[x][y] == 'P':
                    line.append(Tile(self, self.tile_map[0][0], False))
                    player_loc = (x, y)
                elif game_map[x][y] == 'M':
                    line.append(Tile(self, self.tile_map[0][0], False))
                    monster_loc = (x, y)

        self.monsters = []
        self.monsters.append(Monster(self, self.entity_map[1], player_loc))

        self.player = Player(self, self.entity_map[0], monster_loc)
        self.center()

        self.items.append(DisplayItem("Player Health: ", self.player.health))
        self.items.append(DisplayItem("Player Attack: ", self.player.attack))

    def center(self):
        x = self.player.x
        y = self.player.y

        x = x - (tiles_per_row//2)
        y = y - (tiles_per_col//2)

        if x + tiles_per_row > self.width:
            if hasattr(self, "view"):
                x = self.view.left
            else:
                x = 0
        if x < 0:
            x = 0
        if y + tiles_per_col-1 > self.height:
            if hasattr(self, "view"):
                y = self.view.top
            else:
                y = 0
        if y < 0:
            y = 0

        self.view = Rect((x, y),(x+tiles_per_row, y+tiles_per_col-1))

    def key_pressed(self, key_char):
        if key_char == pygame.K_w:
            self.player.move(0, -1)
        if key_char == pygame.K_s:
            self.player.move(0, 1)
        if key_char == pygame.K_a:
            self.player.move(-1, 0)
        if key_char == pygame.K_d:
            self.player.move(1, 0)
        if key_char == pygame.K_q:
            sys.exit()


    def draw(self, surface):
        for x in range(self.view.left, self.view.width):
            for y in range(self.view.top, self.view.height):
                self.game_map[x][y].draw(surface, (x-self.view.left)*tilesize, (y-self.view.top+1)*tilesize)

        self.player.update_displays()
        for (i, item) in enumerate(self.items):
            rect = self.game.fonter.font.get_rect(item.output(), size = fontsize)
            self.game.fonter.draw(surface, (0, (0 + (((rect.bottom - rect.top)+5)*i))), item.output(), pygame.Color(255, 255, 255))

def load_sprite(filename, width, height):
    image = pygame.image.load(filename).convert_alpha()
    image_width, image_height = image.get_size()
    sprite_table = []
    for sprite_y in range(0, int(image_height/height)):
        line = []
        sprite_table.append(line)
        for sprite_x in range(0, int(image_width/width)):
            rect = (sprite_x*width, sprite_y*height, width, height)
            line.append(image.subsurface(rect))
    return sprite_table

def load_map(filename):
    mapfile = open(filename, 'r')
    tilemap = []
    (width, height) = tuple(mapfile.readline().rstrip().split(' '))
    mapfile.readline()
    for x in range(0, int(width)):
        line = []
        tilemap.append(line)
        tmp = mapfile.readline().rstrip().split(' ')
        for y in range(0, int(height)):
            line.append(tmp[y])

    return tilemap

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Rougelike")
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

