import pygame, pymunk, pymunk.pygame_util
from pymunk import Vec2d
from itertools import cycle
import InputManager

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.quit()  # somehow sound lags behind, if this ain't here
pygame.mixer.init(44100, -16, 2, 512)

fps = 60
clock = pygame.time.Clock()
inputmanager = InputManager

WIDTH, HEIGHT = 1024, 576

# colors
PUCK = (0, 0, 0, 0)
PLAYERc = (0, 0, 200, 0)
PLAYER2c = (200, 200, 0, 0)
STICK = (25, 100, 100, 0)
REDLine = (240, 0, 0)
GOALPOSTS = (150, 0, 0, 0)
RINK = (100, 100, 100, 0)
WHITE = (255, 255, 255, 128)
ICE = (0, 100, 255)
TRANSPARENT = (255, 255, 255, 255)
BLACK = (0, 0, 0)
GREY = (175, 175, 175, 0)
GREEN = (0, 200, 0, 0)

seg_width = 10  # segment (wall) width
post_width = 7

counter_1, text_1 = 4, ''.rjust(3)
counter_2, text_2 = 4, ''.rjust(3)
counter_3, text_3 = 4, ''.rjust(3)

counter_4, text_6 = 4, ''.rjust(3)
counter_5, text_7 = 4, ''.rjust(3)

COUNTDOWN1 = pygame.USEREVENT + 1
COUNTDOWN2 = pygame.USEREVENT + 2
COUNTDOWN3 = pygame.USEREVENT + 3

blink = pygame.USEREVENT + 4
start = pygame.USEREVENT + 5
p1controls = pygame.USEREVENT + 6
p2controls = pygame.USEREVENT + 7


def scoretrigger1(arbiter, space, data):
    global counter_1, p2scores
    counter_1 = 4  # reset countdown counter
    p2scores = False  # disable ping-pong effect scoring, coast to coast misshaps...

    if arbiter.is_first_contact:
        pygame.mixer.Sound.play(goalhorn)

        pygame.time.set_timer(COUNTDOWN1, 500)

        return True


def scoretrigger2(arbiter, space, data):
    global counter_2, p1scores
    counter_2 = 4
    p1scores = False

    if arbiter.is_first_contact:
        pygame.mixer.Sound.play(goalhorn)

        pygame.time.set_timer(COUNTDOWN2, 500)

        return True


def out_of_bounds(arbiter, space, data):
    global counter_3, p1scores, p2scores
    counter_3 = 4
    p1scores = False
    p2scores = False

    if arbiter.is_first_contact:
        pygame.mixer.Sound.play(whistle)

        pygame.time.set_timer(COUNTDOWN3, 500)

        return True


class Puck(pygame.sprite.Sprite):
    def __init__(self, pos, space):
        super().__init__()
        self.image = pygame.Surface((7, 7), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLACK, [3, 4], 4)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=pos)

        puck_mass = 10
        puck_radius = 6

        self.puck_body = pymunk.Body(puck_mass, moment=10)
        self.puck_shape = pymunk.Circle(self.puck_body, puck_radius)
        self.puck_shape.color = PUCK
        self.puck_body.position = pos
        self.puck_shape.elasticity = 0.7
        self.puck_shape.friction = 0.3
        self.puck_shape.collision_type = 3

        self.space = space

        self.space.add(self.puck_body, self.puck_shape)

    def update(self, dt):
        pos = self.puck_body.position

        self.rect.center = pos
        self.rect = self.image.get_rect(center=self.rect.center)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, space):
        super().__init__()
        self.image = pygame.image.load('data_c/player1.png').convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        radius = 20
        body_mass = 100
        self.body = pymunk.Body(body_mass, pymunk.inf)  # infinite moment, overhead 2d cam = body rotation confusing
        self.shape = pymunk.Circle(self.body, radius)
        self.body.position = pos
        self.shape.color = BLACK
        self.shape.collision_type = 1
        self.shape.friction = .01
        self.shape.elasticity = .2
        self.space = space

        """player1's stick"""

        stick_mass = 100
        stick_ps = [(0, 3), (0, -3), (-50, 3), (-50, -3)]

        self.stick_body = pymunk.Body(stick_mass, pymunk.inf)
        self.stick_body.position = pos
        self.stick_shape = pymunk.Poly(self.stick_body, stick_ps)
        self.stick_shape.color = STICK
        self.stick_shape.friction = 0.1
        self.stick_shape.elasticity = 0.5
        self.stick_shape.collision_type = 7
        self.stick_body.angle = 1.6

        self.stick_to_body_joint = pymunk.constraint.PinJoint(self.stick_body, self.body, (0, 0), (0, 0))

        self.space.add(self.body, self.stick_body, self.shape, self.stick_shape, self.stick_to_body_joint)
        self.space.add_collision_handler(1, 7).begin = self.ignore_collision

    def update(self, dt):
        pos = self.body.position
        self.rect.center = pos
        self.rect = self.image.get_rect(center=self.rect.center)

        pressed = pygame.key.get_pressed()

        if pressed[InputManager.key_map1['Move Up']]:
            self.body.apply_impulse_at_local_point(Vec2d(0, -400))

        if pressed[InputManager.key_map1['Move Down']]:
            self.body.apply_impulse_at_local_point(Vec2d(0, 400))

        if pressed[InputManager.key_map1['Move Left']]:
            self.body.apply_impulse_at_local_point(Vec2d(-400, 0))

        if pressed[InputManager.key_map1['Move Right']]:
            self.body.apply_impulse_at_local_point(Vec2d(400, 0))

        if pressed[InputManager.key_map1['Rotate Stick L']]:
            self.stick_body.angle -= 0.07

        if pressed[InputManager.key_map1['Rotate Stick R']]:
            self.stick_body.angle += 0.07

    def ignore_collision(self, arbiter, space, data):  # disable own stick-to body collision.

        return False


class Player2(pygame.sprite.Sprite):
    def __init__(self, pos, space):
        super().__init__()
        self.image = pygame.image.load('data_c/player2.png').convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        radius = 20
        body_mass = 100
        self.body = pymunk.Body(body_mass, pymunk.inf)
        self.shape = pymunk.Circle(self.body, radius)
        self.body.position = pos
        self.shape.color = BLACK
        self.shape.collision_type = 2
        self.shape.friction = .2
        self.shape.elasticity = .2
        self.space = space

        """player2's stick"""

        stick_mass = 100
        stick_ps = [(0, 3), (0, -3), (-50, 3), (-50, -3)]

        self.stick_body = pymunk.Body(stick_mass, pymunk.inf)
        self.stick_body.position = pos
        self.stick_shape = pymunk.Poly(self.stick_body, stick_ps)
        self.stick_shape.color = STICK
        self.stick_shape.friction = 0.1
        self.stick_shape.elasticity = 0.5
        self.stick_shape.collision_type = 8
        self.stick_body.angle = 4.7
        self.stick_to_body_joint = pymunk.constraint.PinJoint(self.stick_body, self.body, (0, 0), (0, 0))

        self.space.add(self.body, self.stick_body, self.shape, self.stick_shape, self.stick_to_body_joint)
        self.space.add_collision_handler(2, 8).begin = self.ignore_collision

    def update(self, dt):
        pos = self.body.position
        self.rect.center = pos
        self.rect = self.image.get_rect(center=self.rect.center)

        pressed = pygame.key.get_pressed()

        if pressed[InputManager.key_map2['Move Up']]:
            self.body.apply_impulse_at_local_point(Vec2d(0, -400))

        if pressed[InputManager.key_map2['Move Down']]:
            self.body.apply_impulse_at_local_point(Vec2d(0, 400))

        if pressed[InputManager.key_map2['Move Left']]:
            self.body.apply_impulse_at_local_point(Vec2d(-400, 0))

        if pressed[InputManager.key_map2['Move Right']]:
            self.body.apply_impulse_at_local_point(Vec2d(400, 0))

        if pressed[InputManager.key_map2['Rotate Stick L']]:
            self.stick_body.angle -= 0.07

        if pressed[InputManager.key_map2['Rotate Stick R']]:
            self.stick_body.angle += 0.07

        # if joystick_count > 0:
        #
        #     pygame.joystick.Joystick(0).get_numaxes()
        #
        #     """Controls"""
        #     gamepad0 = pygame.joystick.Joystick(0).get_axis(0)
        #     gamepad1 = pygame.joystick.Joystick(0).get_axis(1)
        #     gamepad2 = pygame.joystick.Joystick(0).get_axis(3)
        #
        #     if gamepad1 >= 0.15:
        #         self.body.apply_impulse_at_local_point(Vec2d(0, 400))
        #     if gamepad1 < -0.15:
        #         self.body.apply_impulse_at_local_point(Vec2d(0, -400))
        #     if gamepad0 > 0.15:
        #         self.body.apply_impulse_at_local_point(Vec2d(400, 0))
        #     if gamepad0 < -0.15:
        #         self.body.apply_impulse_at_local_point(Vec2d(-400, 0))
        #
        #     if gamepad2 > 0.15:
        #         self.stick_body.angle += 0.07
        #
        #     if gamepad2 < -0.15:
        #         self.stick_body.angle -= 0.07

    def ignore_collision(self, arbiter, space, data):  # disable own stick-to body collision.

        return False


class Goal1(pygame.sprite.Sprite):
    def __init__(self, pos, space):
        super().__init__()
        self.image = pygame.Surface((50, 100), pygame.SRCALPHA)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=pos)

        goal1_ps = [(-16, 35), (20, 35), (20, -35), (-16, -35)]

        self.goal1_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.goal1_body.position = pos
        self.goal1_shape = pymunk.Poly(self.goal1_body, goal1_ps)
        self.goal1_shape.color = WHITE
        self.goal1_shape.collision_type = 5

        self.space = space

        self.space.add(self.goal1_body, self.goal1_shape)
        self.space.add_collision_handler(3, 5).begin = self.score_player1

    def score_player1(self, arbiter, space, data):  # disable puck to goal collision.ue
        if p1scores is True:

            scoretrigger1(arbiter, space, data)

        return False


class Goal2(pygame.sprite.Sprite):
    def __init__(self, pos, space):
        super().__init__()
        self.image = pygame.Surface((50, 100), pygame.SRCALPHA)
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=pos)

        goal2_ps = [(-20, 35), (16, 35), (16, -35), (-20, -35)]

        self.goal2_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.goal2_body.position = pos
        self.goal2_shape = pymunk.Poly(self.goal2_body, goal2_ps)
        self.goal2_shape.color = WHITE
        self.goal2_shape.collision_type = 6

        self.space = space

        self.space.add(self.goal2_body, self.goal2_shape)
        self.space.add_collision_handler(3, 6).begin = self.score_player2

    def score_player2(self, arbiter, space, data):  # disable puck to goal collision.
        if p2scores is True:

            scoretrigger2(arbiter, space, data)

        return False


def player1wins():
    text_6_rect = (WIDTH / 2, 150)
    player1wins = True
    image_p1wins = pygame.image.load("data_c/p1wins.png").convert_alpha()
    pygame.mixer.music.load("data_c/A_Jubilant_Sport.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1, start=0.0)
    text_6 = font2.render("Player1 WINS!!!", True, BLACK)
    blink_rect = text_6.get_rect()
    blink_rect.center = text_6_rect
    off_text_6 = font2.render("", True, TRANSPARENT)
    blink_surfaces = cycle([text_6, off_text_6])
    blink_surface = next(blink_surfaces)
    pygame.time.set_timer(blink, 180)
    text_7 = font2.render(str(score1) +" - " +str(score2), True, BLACK)
    text_8 = font_5.render('"WOOHOO"', True, BLACK)
    text_9 = font3.render("[UP]", True, BLACK)
    text_10 = font_5.render('"WHIMPER"', True, BLACK)
    text_11 = font3.render("[DOWN]", True, BLACK)
    text_12 = font3.render("ESC to menu", True, BLACK)
    woohoo1 = pygame.mixer.Sound("data_c/woohoo1.ogg")
    pygame.mixer.Sound.set_volume(woohoo1, 0.6)
    cry = pygame.mixer.Sound("data_c/cryingmale.ogg")
    pygame.mixer.Sound.set_volume(cry, 0.3)

    while player1wins:
        for e in pygame.event.get():
            pressed = pygame.key.get_pressed()

            if e.type == blink:
                blink_surface = next(blink_surfaces)

            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                player1wins = False
                menu()

            if pressed[InputManager.key_map1['Move Up']]:
                pygame.mixer.Sound.play(woohoo1)

            if pressed[InputManager.key_map2['Move Down']]:
                pygame.mixer.Sound.play(cry)

        screen.blit(image_p1wins, [0, 0])
        screen.blit(blink_surface, blink_rect)
        screen.blit(text_7, [WIDTH / 2 - 70, 200])
        screen.blit(text_8, [WIDTH / 2 - 400, 500])
        screen.blit(text_9, [WIDTH / 2 - 330, 530])
        screen.blit(text_10, [WIDTH / 2 + 200, 500])
        screen.blit(text_11, [WIDTH / 2 + 250, 530])
        screen.blit(text_12, [900, 5])
        pygame.display.flip()


def player2wins():
    text_6_rect = (WIDTH / 2, 150)
    player2wins = True
    image_p2wins = pygame.image.load("data_c/p2wins.png").convert()
    pygame.mixer.music.load("data_c/A_Jubilant_Sport.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1, start=0.0)
    text_6 = font2.render("Player2 WINS!!!", True, BLACK)
    blink_rect = text_6.get_rect()
    blink_rect.center = text_6_rect
    off_text_6 = font2.render("", True, TRANSPARENT)
    blink_surfaces = cycle([text_6, off_text_6])
    blink_surface = next(blink_surfaces)
    pygame.time.set_timer(blink, 180)
    text_7 = font2.render(str(score1) +" - " +str(score2), True, BLACK)
    text_8 = font_5.render('"WHIMPER"', True, BLACK)
    text_9 = font3.render("[DOWN]", True, BLACK)
    text_10 = font_5.render('"WOOHOO"', True, BLACK)
    text_11 = font3.render("[UP]", True, BLACK)
    text_12 = font3.render("ESC to menu", True, BLACK)
    woohoo2 = pygame.mixer.Sound("data_c/woohoo2.ogg")
    pygame.mixer.Sound.set_volume(woohoo2, 0.7)
    cry = pygame.mixer.Sound("data_c/cryingmale.ogg")
    pygame.mixer.Sound.set_volume(cry, 0.3)

    while player2wins:
        for e in pygame.event.get():
            pressed = pygame.key.get_pressed()

            if e.type == blink:
                blink_surface = next(blink_surfaces)

            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                player2wins = False
                menu()

            if pressed[InputManager.key_map1['Move Down']]:
                pygame.mixer.Sound.play(cry)

            if pressed[InputManager.key_map2['Move Up']]:
                pygame.mixer.Sound.play(woohoo2)

        screen.blit(image_p2wins, [0, 0])
        screen.blit(blink_surface, blink_rect)
        screen.blit(text_7, [WIDTH / 2 - 70, 200])
        screen.blit(text_8, [WIDTH / 2 - 400, 500])
        screen.blit(text_9, [WIDTH / 2 - 330, 530])
        screen.blit(text_10, [WIDTH / 2 + 200, 500])
        screen.blit(text_11, [WIDTH / 2 + 270, 530])
        screen.blit(text_12, [900, 5])
        pygame.display.flip()


def menu():
    pygame.mixer.music.load("data_c/menu.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1, start=0.0)

    pygame.display.set_caption("Pong Hockey")

    global screen, font, font2, font3, font_4, font_5

    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # , pygame.FULLSCREEN)
    pygame.mouse.set_visible(True)

    font = pygame.font.Font("data_c/freesansbold.ttf", 100)
    font2 = pygame.font.Font("data_c/freesansbold.ttf", 60)
    font3 = pygame.font.Font("data_c/freesansbold.ttf", 15)

    font_4 = pygame.font.Font("data_c/freesansbold.ttf", 20)
    font_5 = pygame.font.Font("data_c/freesansbold.ttf", 30)

    option_list = {'START': start,
                   'P1 CONTROLS': p1controls,
                   'P2 CONTROLS': p2controls
                   }

    def create_list(option_list):
        list_options = []
        for c, (choice, value) in enumerate(sorted(option_list.items(), key=lambda x: x[1])):
            surf_o = font_4.render('{}'.format(choice), True, GREY)
            rect_o = surf_o.get_rect(center =(0, c*30+40))
            rect_o.move_ip(WIDTH / 2, HEIGHT / 2 - 125)
            list_options.append([surf_o, rect_o, choice])
        return  list_options

    image_menu = pygame.image.load("data_c/main_new.png").convert()

    pygame.joystick.init()

    global joystick_count

    joystick_count = pygame.joystick.get_count()

    for i in range (joystick_count):
        pygame.joystick.Joystick(i).init()

        if joystick_count == 0:

            pygame.joystick.quit()

    list_options = create_list(option_list)
    menu = True
    while menu:
        for e in pygame.event.get():
            screen.fill(WHITE)
            screen.blit(image_menu, [0, 0])

            mpos = pygame.mouse.get_pos()

            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

            for surf_o, rect_o, choice in list_options:
                screen.blit(surf_o, rect_o)
                if rect_o.collidepoint(mpos):
                    pygame.draw.rect(screen, WHITE, rect_o, 0)
                    surf_o = font_4.render('{}'.format(choice), True, BLACK)
                    screen.blit(surf_o, rect_o)

                    if e.type == pygame.MOUSEBUTTONDOWN:
                            # See if the user clicked on one of the rects.
                            if rect_o.collidepoint(e.pos):
                                #print(e, choice)

                                if choice == 'START':
                                    game()

                                if choice == 'P1 CONTROLS':
                                    InputManager.edit_keys1(InputManager.key_map1)

                                if choice == 'P2 CONTROLS':
                                    InputManager.edit_keys2(InputManager.key_map2)

        pygame.display.flip()  # Pygame draw updates, flip for all, /.update for separate things if needed


def game():

    pygame.mixer.music.load("data_c/Space_Blocks.mp3")
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(loops=-1, start=0.0)

    global goalhorn, whistle, image_ice, space, players, font_4\
    , counter_1, counter_2, counter_3, counter_4, text_1, text_2, text_3, text_6, score1, score2, p1scores, p2scores

    score1 = 0
    score2 = 0

    space = pymunk.Space(threaded=True)
    space.threads = 2
    space.damping = 0.995
    space.gravity = 0, 0  # not necessary
    steps = 10

    image_ice = pygame.image.load("data_c/ICE.png").convert()

    # sound effects load
    puck_stick = pygame.mixer.Sound("data_c/hockey2.ogg")
    click = pygame.mixer.Sound("data_c/click.ogg")
    goalhorn = pygame.mixer.Sound("data_c/Goalhorn.ogg")
    pygame.mixer.Sound.set_volume(goalhorn, 0.3)

    ughhh = pygame.mixer.Sound("data_c/ughhh.ogg")
    pygame.mixer.Sound.set_volume(ughhh, 0.5)

    ughh2 = pygame.mixer.Sound("data_c/ughhh2.ogg")
    pygame.mixer.Sound.set_volume(ughh2, 0.7)

    puckb = pygame.mixer.Sound("data_c/puckboardhit.ogg")
    whistle = pygame.mixer.Sound("data_c/whistle.ogg")
    grunt = pygame.mixer.Sound("data_c/grunt.ogg")
    pygame.mixer.Sound.set_volume(grunt, 0.6)

    grunt2 = pygame.mixer.Sound("data_c/grunt2.ogg")
    pygame.mixer.Sound.set_volume(grunt2, 0.5)

    puck_post = pygame.mixer.Sound("data_c/post.ogg")
    pygame.mixer.Sound.set_volume(puck_post, 0.5)

    font10 = pygame.font.Font("data_c/CursedTimer.ttf", 14)
    font11 = pygame.font.Font("data_c/CursedTimer.ttf", 30)

    doptions = pymunk.pygame_util.DrawOptions(screen)
    pymunk.pygame_util.positive_y_is_up = False  # no need to flip y axis to fit pygame's coordinates, cool!
    # pygame.mouse.set_visible(False)

    #  RINK
    """vas-vas, yla, oik-oik, ala"""

    static_lines1 = \
        [pymunk.Segment(space.static_body, (73, 37), (73, 265), seg_width)
         , pymunk.Segment(space.static_body, (73, 345), (73, 565), seg_width)

         , pymunk.Segment(space.static_body, (73, 46), (960, 46), seg_width)

         , pymunk.Segment(space.static_body, (950, 37), (950, 265), seg_width)
         , pymunk.Segment(space.static_body, (950, 345), (950, 565), seg_width)

         , pymunk.Segment(space.static_body, (73, 555), (950, 555), seg_width)
                ]

    for line in static_lines1:
        line.color = RINK
        line.elasticity = .5
        line.friction = .5
        line.collision_type = 4

    # OUT of bounds sensors
    static_lines2 = \
        [pymunk.Segment(space.static_body, (0, 0), (0, HEIGHT), seg_width)
         , pymunk.Segment(space.static_body, (0, 0), (WIDTH, 0), seg_width * 2)
         , pymunk.Segment(space.static_body, (WIDTH, 0), (WIDTH, HEIGHT)
                          , seg_width)
         , pymunk.Segment(space.static_body, (0, HEIGHT + 5), (WIDTH, HEIGHT + 5), seg_width)
         , pymunk.Segment(space.static_body, (seg_width * 2, 0), (seg_width * 2, 240), seg_width * 3 + 5)
         , pymunk.Segment(space.static_body, (seg_width * 2, 370), (seg_width * 2, HEIGHT), seg_width * 3 + 5)
         , pymunk.Segment(space.static_body, (WIDTH - seg_width*2, 0), (WIDTH - seg_width * 2, 240), seg_width * 3 + 5)
         , pymunk.Segment(space.static_body, (WIDTH - seg_width*2, 370), (WIDTH - seg_width * 2, HEIGHT), seg_width * 3
                          + 5)]

    for line2 in static_lines2:
        line2.color = BLACK
        line2.sensor = True
        line2.collision_type = 9
        line2.sensor = True

    # GoalPosts, for the "spling" sound...vas maali (3), oik maali (3)
    static_lines3 = \
        [pymunk.Segment(space.static_body, (33, 265), (84, 265), post_width)
         , pymunk.Segment(space.static_body, (33, 259), (33, 352), post_width)
         , pymunk.Segment(space.static_body, (33, 345), (84, 345), post_width)

         , pymunk.Segment(space.static_body, (940, 265), (991, 265), post_width)
         , pymunk.Segment(space.static_body, (991, 259), (991, 352), post_width)
         , pymunk.Segment(space.static_body, (940, 345), (991, 345), post_width)]

    for line in static_lines3:
        line.color = GOALPOSTS
        line.elasticity = .1
        line.friction = .7
        line.collision_type = 10

    def statics(arbiter, space, data):

        return False

    def score(score1, score2):
        text = font11.render(str(score1), True, WHITE)
        text2 = font_5.render("-", True, WHITE)
        text3 = font11.render(str(score2), True, WHITE)

        pygame.draw.rect(screen, BLACK, (450, 0, 120, 55))
        pygame.draw.rect(screen, WHITE, (450, 0, 120, 56), 1)

        screen.blit(text, [WIDTH / 2 - 30, 5])
        screen.blit(text2, [WIDTH / 2 - 5, 5])
        screen.blit(text3, [WIDTH / 2 + 13, 5])

    """ add everything above to the physics simulation"""
    space.add(static_lines1, static_lines2, static_lines3)

    puck = Puck((WIDTH / 2, HEIGHT /2 + 10), space)
    player1 = Player((WIDTH / 2 - 60, HEIGHT / 2 + 17), space)
    goal1 = Goal1((WIDTH / 2 + 450, HEIGHT / 2 + 17), space)
    goal2 = Goal2((WIDTH / 2 - 450, HEIGHT / 2 + 17), space)
    player2 = Player2((WIDTH / 2 + 60, HEIGHT / 2 + 17), space)
    players = pygame.sprite.Group()  # add pygame stuff, e.g. if adding sprites
    players.add(player1, player2, puck, goal1, goal2)

    def smooth_hands1(arbiter, space, data):  # NOT so smooth hands, hah!
        pygame.mixer.Sound.play(puck_stick)
        arbiter.restitution *= 9
        return True

    def smooth_hands2(arbiter, space, data):  # NOT so smooth hands, hah!
        pygame.mixer.Sound.play(puck_stick)
        arbiter.restitution *= 9
        return True

    def collision(arbiter, space, data):  # Player Collision sounds
        pygame.mixer.Sound.play(ughh2)
        pygame.mixer.Sound.play(ughhh)
        return True

    def boardsound(arbiter, space, data):  # Puck hit boards sound
        pygame.mixer.Sound.play(puckb)
        return True

    def stickhit1(arbiter, space, data):  # Plr1 stick hits Plr2
        pygame.mixer.Sound.play(grunt)
        arbiter.restitution *= 10
        return True

    def stickhit2(arbiter, space, data):  # Plr2 stick hits Plr1
        pygame.mixer.Sound.play(grunt2)
        arbiter.restitution *= 10
        return True

    def spling(arbiter, space, data):
        pygame.mixer.Sound.play(puck_post)
        return True

    # add collisions
    space.add_collision_handler(7, 3).pre_solve = smooth_hands1
    space.add_collision_handler(8, 3).pre_solve = smooth_hands2
    space.add_collision_handler(1, 2).begin = collision
    space.add_collision_handler(3, 4).begin = boardsound
    space.add_collision_handler(7, 2).begin = stickhit1
    space.add_collision_handler(8, 1).begin = stickhit2
    space.add_collision_handler(3, 9).begin = out_of_bounds
    space.add_collision_handler(4, 10).begin = statics
    space.add_collision_handler(3, 10).begin = spling

    minutes = 3  # 6000 per minute, not 100% accurate, but who gives a F"#k, also fpsclock dependable
    seconds = 0
    milliseconds = 0
    timer1 = 18000

    p1scores = True
    p2scores = True
    running = True

    def pause():
        text_6_rect = (WIDTH / 2, HEIGHT / 2)
        text_6 = font2.render("PAUSED", True, BLACK)
        blink_rect = text_6.get_rect()
        blink_rect.center = text_6_rect
        off_text_6 = font2.render("", True, TRANSPARENT)
        blink_surfaces = cycle([text_6, off_text_6])
        blink_surface = next(blink_surfaces)
        pygame.time.set_timer(blink, 240)
        pause = True

        while pause:
            for e in pygame.event.get():
                pressed = pygame.key.get_pressed()

                if e.type == blink:
                    blink_surface = next(blink_surfaces)

                if e.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if pressed[InputManager.key_map1['Pause']]:
                    pygame.mixer.music.unpause()

                    pause = False

            screen.fill(BLACK)
            screen.blit(image_ice, [83, 55])
            space.debug_draw(doptions)
            players.draw(screen)
            screen.blit(blink_surface, blink_rect)
            score(score1, score2)
            screen.blit(font10.render("{:02.0f}:{:02.0f}".format(minutes, seconds), True, (255, 255, 255)), (490, 37))
            screen.blit(font3.render("fps: " + str(clock.get_fps()), 1, WHITE), (950, 0))  # to see how rasbpi handles this
            pygame.display.flip()

    while running:
        # keep loop running at the right speed, busy loop is better for various cpu-speeds aka "frame_cap aka lock"
        clock.tick_busy_loop(fps)

        for e in pygame.event.get():
            pressed = pygame.key.get_pressed()
            #print(e)

            if e.type == COUNTDOWN1:
                counter_1 -= 1
                text_1 = str(counter_1).rjust(3) if counter_1 > 0 else ''

                if counter_1 == 0:
                    pygame.mixer.Sound.play(click)
                    score1 += 1
                    puck.puck_body.position = (WIDTH / 2), (HEIGHT / 2 + 10)
                    puck.puck_body.velocity = (Vec2d(0, 0))
                    p2scores = True

                    if score1 > 9:
                        space.remove(player1.body, player1.shape, player1.stick_body, player1.stick_shape
                                     , player2.body, player2.shape, player2.stick_body, player2.stick_shape
                                     , puck.puck_body, puck.puck_shape)
                        player1wins()

            if e.type == COUNTDOWN2:
                counter_2 -= 1
                text_2 = str(counter_2).rjust(3) if counter_2 > 0 else ''

                if counter_2 == 0:
                    pygame.mixer.Sound.play(click)
                    score2 += 1
                    puck.puck_body.position = (WIDTH / 2), (HEIGHT / 2 + 10)
                    puck.puck_body.velocity = (Vec2d(0, 0))
                    p1scores = True

                    if score2 > 9:
                        space.remove(player1.body, player1.shape, player1.stick_body, player1.stick_shape
                                     , player2.body, player2.shape, player2.stick_body, player2.stick_shape
                                     , puck.puck_body, puck.puck_shape)
                        player2wins()

            if e.type == COUNTDOWN3:
                counter_3 -= 1
                text_3 = str(counter_3).rjust(3) if counter_3 > 0 else ''
                p1scores = True
                p2scores = True

                if counter_3 == 0:
                    puck.puck_body.position = (WIDTH / 2), (HEIGHT / 2 + 10)
                    puck.puck_body.velocity = (Vec2d(0, 0))

            elif e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                space.remove(player1.body, player1.shape, player1.stick_body, player1.stick_shape
                             , player2.body, player2.shape, player2.stick_body, player2.stick_shape
                             , puck.puck_body, puck.puck_shape)
                running = False
                menu()

            elif pressed[InputManager.key_map1['Pause']]:
                pygame.mixer.music.pause()

                pause()

        #  Draw / render
        screen.fill(BLACK)
        screen.blit(image_ice, [83, 55])
        space.debug_draw(doptions)
        players.draw(screen)
        score(score1, score2)

        screen.blit(font.render(text_1, True, (0, 0, 0)), (WIDTH / 2 - 84, HEIGHT / 2 - 30))
        screen.blit(font.render(text_2, True, (0, 0, 0)), (WIDTH / 2 - 84, HEIGHT / 2 - 30))
        screen.blit(font.render(text_3, True, (0, 0, 0)), (WIDTH / 2 - 84, HEIGHT / 2 - 30))
        screen.blit(font3.render("fps: " + str(clock.get_fps()), 1, WHITE), (950, 0))  # to see how rasbpi handles this

        if timer1 >= 0:
            screen.blit(font10.render("{:02.0f}:{:02.0f}".format(minutes, seconds), True, (255, 255, 255)), (490, 37))
            milliseconds -= 1
            timer1 -= 1

        if milliseconds < 0:
            seconds -= 1
            milliseconds += 100

        if seconds < 0:
            minutes -= 1
            seconds += 60

        if timer1 <= 0 and score1 > score2:
            space.remove(player1.body, player1.shape, player1.stick_body, player1.stick_shape
                         , player2.body, player2.shape, player2.stick_body, player2.stick_shape
                         , puck.puck_body, puck.puck_shape)
            player1wins()

        if timer1 <= 0 and score2 > score1:
            space.remove(player1.body, player1.shape, player1.stick_body, player1.stick_shape
                         , player2.body, player2.shape, player2.stick_body, player2.stick_shape
                         , puck.puck_body, puck.puck_shape)
            player2wins()

        if timer1 <= 0:
            screen.blit(font3.render("OT", True, (255, 255, 255)),
                        (WIDTH / 2 - 10, 37))

        # Update

        for x in range(steps):              # "tuhat" kertaa tarkempi collision detectioni for loopin kanssa
            space.step(0.05 / steps)

        players.update(.1)
        pygame.display.flip()  # Pygame draw updates, flip for all, /.update for separate things if needed

    pygame.quit()
    quit()

menu()