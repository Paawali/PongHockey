import pygame
import math


pygame.init()


pygame.joystick.init()

joystick_count = pygame.joystick.get_count()

for i in range(joystick_count):
    pygame.joystick.Joystick(i).init()

    if joystick_count == 0:
        pygame.joystick.quit()


dead_zone = .25
FONT = pygame.font.Font("data_c/FreeSerif.ttf", 30)
font3 = pygame.font.Font("data_c/freesansbold.ttf", 15)

GREEN = (0, 200, 0, 0)
REDLine = (240, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255, 128)
WIDTH, HEIGHT = 1600, 900
WIDTH2, HEIGHT2 = 1024, 576

screen = pygame.display.set_mode((WIDTH2, HEIGHT2))
image_menu = pygame.image.load("data_c/main_new.png").convert()

key_map1 = {'Move Up': pygame.K_w,
            'Move Down': pygame.K_s,
            'Move Left': pygame.K_a,
            'Move Right': pygame.K_d,
            'Rotate Stick L': pygame.K_COMMA,
            'Rotate Stick R': pygame.K_PERIOD,
            'Pause': pygame.K_SPACE,
            }

joy_map1 = {''}

key_map1_order = ['Move Up', 'Move Down', 'Move Left', 'Move Right', 'Rotate Stick L', 'Rotate Stick R', 'Pause']


def create_list1(key_map1):
    keys_list1 = []
    for a, (action1, value1) in enumerate(sorted(key_map1.items(), key=lambda x:key_map1_order.index(x[0]))):
        surf1 = FONT.render('{}: {}'.format(action1, pygame.key.name(value1)), True, BLACK)
        rect1 = surf1.get_rect(center=(0, a*40+40))
        rect1.move_ip(WIDTH2 / 2 - 300, HEIGHT2 / 3 - 10)
        keys_list1.append([surf1, rect1, action1])
    return keys_list1


def edit_keys1(key_map1):
    keys_list1 = create_list1(key_map1)
    selected1 = None
    name="Munapää"
    axes=0;
    buttons=0;
    dpad=0;
    
    if joystick_count != 0:
        name = pygame.joystick.Joystick(0).get_name()
        axes = pygame.joystick.Joystick(0).get_numaxes()
        buttons = pygame.joystick.Joystick(0).get_numbuttons()
        dpad = pygame.joystick.Joystick(0).get_numhats()
    
    print(name, axes, buttons, dpad)

    for i in range(axes):
        axis = pygame.joystick.Joystick(0).get_axis(i)
        print(screen, "Axis {:>2} value: {}".format(i, axis))

    for i in range(buttons):
        button = pygame.joystick.Joystick(0).get_button(i)
        print(screen, "Button {:>2} value: {}".format(i, button))

    while True:
        for e1 in pygame.event.get():
            screen.blit(image_menu, [0, 0])


            if e1.type == pygame.KEYDOWN and e1.key == pygame.K_ESCAPE:
                return key_map1

            if e1.type == pygame.KEYDOWN:
                if selected1 is not None:
                    key_map1[selected1] = e1.key
                    selected1 = None
                    keys_list1 = create_list1(key_map1)
                    
            if joystick_count != 0:
                if e1.type == pygame.JOYAXISMOTION or pygame.JOYBUTTONDOWN:
                    if selected1 is not None:
                        key_map1[selected1] = e1.joy
                        selected1 = None
                        keys_list1 = create_list1(key_map1)

            if e1.type == pygame.MOUSEBUTTONDOWN:
                selected1 = None
                for surf1, rect1, action1 in keys_list1:
                    # See if the user clicked on one of the rects.
                    if rect1.collidepoint(e1.pos):
                        pygame.draw.rect(screen, WHITE, (WIDTH2 / 2 - 450, HEIGHT2 / 3, 300, 300))
                        pygame.draw.rect(screen, BLACK, (WIDTH2 / 2 - 450, HEIGHT2 / 3, 300, 300), 4)
                        selected1 = action1

            else:
                pygame.draw.rect(screen, WHITE, (WIDTH2 / 2 - 450, HEIGHT2 / 3, 300, 300))
                pygame.draw.rect(screen, BLACK, (WIDTH2 / 2 - 450, HEIGHT2 / 3, 300, 300), 4)

        for surf1, rect1, action1 in keys_list1:
            screen.blit(surf1, rect1)
            if selected1 == action1:
                pygame.draw.rect(screen, REDLine, rect1, 4)

        pygame.display.flip()


key_map2 = {'Move Up': pygame.K_UP,
            'Move Down': pygame.K_DOWN,
            'Move Left': pygame.K_LEFT,
            'Move Right': pygame.K_RIGHT,
            'Rotate Stick L': pygame.K_KP0,
            'Rotate Stick R': pygame.K_KP_PERIOD
            }

key_map2_order = ['Move Up', 'Move Down', 'Move Left', 'Move Right', 'Rotate Stick L', 'Rotate Stick R', 'Pause']


def create_list2(key_map2):
    keys_list2 = []
    for a, (action2, value2) in enumerate(sorted(key_map2.items(), key=lambda y:key_map2_order.index(y[0]))):
        surf2 = FONT.render('{}: {}'.format(action2, pygame.key.name(value2)), True, BLACK)
        rect2 = surf2.get_rect(center=(0, a*40+40))
        rect2.move_ip(WIDTH2 / 2 + 300, HEIGHT2 / 3 - 10)
        keys_list2.append([surf2, rect2, action2])
    return keys_list2


def edit_keys2(key_map2):
    keys_list2 = create_list2(key_map2)
    selected2 = None

    while True:
        for e2 in pygame.event.get():
            mpos = pygame.mouse.get_pos()
            screen.blit(image_menu, [0, 0])

            if e2.type == pygame.KEYDOWN and e2.key == pygame.K_ESCAPE:
                return key_map2

            if e2.type == pygame.KEYDOWN:
                if selected2 is not None:
                    key_map2[selected2] = e2.key
                    selected2 = None
                    keys_list2 = create_list2(key_map2)

            if e2.type == pygame.MOUSEBUTTONDOWN:
                selected2 = None
                for surf2, rect2, action2 in keys_list2:
                    # See if the user clicked on one of the rects.
                    if rect2.collidepoint(e2.pos):
                        pygame.draw.rect(screen, WHITE, (WIDTH2 - 365, HEIGHT2 / 3, 300, 300))
                        pygame.draw.rect(screen, BLACK, (WIDTH2 - 365, HEIGHT2 / 3, 300, 300), 4)
                        selected2 = action2

            else:
                pygame.draw.rect(screen, WHITE, (WIDTH2 - 365, HEIGHT2 / 3, 300, 300))
                pygame.draw.rect(screen, BLACK, (WIDTH2 - 365, HEIGHT2 / 3, 300, 300), 4)

        for surf2, rect2, action2 in keys_list2:
            screen.blit(surf2, rect2)
            if selected2 == action2:
                pygame.draw.rect(screen, REDLine, rect2, 4)

        pygame.display.flip()

