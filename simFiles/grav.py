from cmath import cos, sin
import math
import pygame
import random
from vector import Vector, random_vector

pygame.init()


class Cursor:
    def __init__(
        self,
        position: Vector,
    ):
        self.position = position


class Body:
    def __init__(
        self,
        position: Vector,
        newPos: Vector,
        angle: float,
        sight: float,
        minDist: float,
        dx: float,
        dy: float,
        size: float,
        color: float,
        grav: float,
        mass: float,
        momentumX: float,
        momentumY: float
    ):
        self.position = position
        self.angle = angle
        self.sight = sight
        self.minDist = minDist
        self.newPos = newPos
        self.dx = dx
        self.dy = dy
        self.size = size
        self.color = color
        self.g = grav
        self.mass = mass
        self.momentum_x = momentumX
        self.momentum_y = momentumY
        self.locked = False
        self.blhole = False
        self.killing = False


delta_time = 0.0
clock = pygame.time.Clock()


# changeable variables ( for customization )
screenSizeX = 1600
screenSizeY = 800
maxSpeed = 4
backgroundAlpha = 50
drawGravLines = True
gravLineDist = 500


middlePlanet = Body(
    Vector(screenSizeX / 2, screenSizeY / 2),
    Vector(0, 0),
    0,
    100,
    20.0,  # TEMP
    0,
    0,
    40,
    random.random() * 100,
    0.2,
    4,
    500,
    500
)


screen = pygame.display.set_mode((screenSizeX, screenSizeY))
ArrayBodies = [middlePlanet]
BodyStartingAngle = random.random() * 180  # redundant
direction = Vector(0, 0)
makeBody = False

currentBodies = 0

WIPBodyIndex = -1  # Work in progress body index
WIPmouseStartX = 0
WIPmouseStartY = 0


mouseCursor = Cursor(Vector(pygame.mouse.get_pos()[
                     0], pygame.mouse.get_pos()[1]))

kill = True
mouseKillTrigger = False


pygame.mouse.set_visible(False)
backgroundPic = pygame.transform.scale(pygame.image.load(
    "background.png").convert_alpha(), (screenSizeX, screenSizeY))
backgroundRect = backgroundPic.get_rect(
    center=(screenSizeX / 2, screenSizeY / 2))


# make Bodies
# for n in range(numOfBodies):

#     ArrayBodies[n] = Body(
#         Vector(
#             random.random() * screenSizeX, random.random() * screenSizeY),
#         Vector(0, 0),
#         BodyStartingAngle,
#         100,
#         20.0,  # TEMP
#         random.random(),
#         random.random(),
#         10,
#         random.random() * 100
#     )

simRunning = True
BodyStart = True


# ---------------------------------------------------------------------------------------------------
# Body Functions ------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------

def distance(body1: Body, body2: Body):
    return math.sqrt((body1.position.x - body2.position.x) ** 2 + (body1.position.y - body2.position.y) ** 2)


def vecDistance(v1: Vector, v2: Vector):
    return math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2)


def flyTowardsCenter(boid):
    centeringFactor = 0.005

    centerX = 0
    centerY = 0
    numNeighbors = 0

    for otherBoid in ArrayBodies:
        if (distance(boid, otherBoid) < boid.sight):
            centerX += otherBoid.position.x
            centerY += otherBoid.position.y
            numNeighbors += 1

    if (numNeighbors):
        centerX = centerX / numNeighbors
        centerY = centerY / numNeighbors

        boid.dx += (centerX - boid.x) * centeringFactor
        boid.dy += (centerY - boid.y) * centeringFactor


def limitSpeed(boid):

    speedLimit = maxSpeed

    speed = math.sqrt(boid.dx * boid.dx + boid.dy * boid.dy)

    if (speed > speedLimit):
        boid.dx = (boid.dx / speed) * speedLimit
        boid.dy = (boid.dy / speed) * speedLimit


indexChange = 0


def checkCollisions(body):
    global currentBodies
    global WIPBodyIndex
    global kill
    for otherBody in ArrayBodies:
        if not otherBody == body:
            if distance(body, otherBody) < (body.size/2) + (otherBody.size/2):

                if otherBody.mass < body.mass:
                    body.momentum_x += otherBody.momentum_x * \
                        (otherBody.mass / otherBody.mass)
                    body.momentum_y += otherBody.momentum_y * \
                        (otherBody.mass / body.mass)
                    if kill:
                        ArrayBodies.remove(otherBody)
                        currentBodies -= 1
                        WIPBodyIndex -= 1
                        kill = False
                    else:
                        body.momentum_x = 0
                        body.momentum_y = 0
                        otherBody.momentum_x = 0
                        otherBody.momentum_y = 0

                elif otherBody.mass == body.mass:
                    currentBodies -= 2
                    WIPBodyIndex -= 2
                    ArrayBodies.append(Body(
                        Vector(
                            (body.position.x + otherBody.position.x) / 2, (body.position.y + otherBody.position.y) / 2),
                        Vector(0, 0),
                        BodyStartingAngle,
                        100,
                        20.0,  # TEMP
                        0,
                        0,
                        body.size + otherBody.size,
                        random.random() * 100,
                        0.2,
                        ((body.size + otherBody.size) ** 2) // 100,
                        (body.momentum_x + otherBody.momentum_x) / 2,
                        (body.momentum_y + otherBody.momentum_y) / 2
                    ))
                    ArrayBodies.remove(body)
                    ArrayBodies.remove(otherBody)
                    currentBodies += 1
                    WIPBodyIndex = currentBodies


def moveBody(body):
    global gravLineDist

    for otherBody in ArrayBodies:
        if not otherBody == body:
            # if (distance(body, ArrayBodies[otherBody]) < body.sight - (ArrayBodies[otherBody].size/2)):
            # if ArrayBodies[otherBody].size > ArrayBodies[biggestNeighborInd].size or biggestNeighborInd == 0:
            # biggestNeighborInd = otherBody
            # foundNeighbor = True

            # if foundNeighbor:
            x2 = otherBody.position.x
            y2 = otherBody.position.y
            hyp = (body.position.x - x2) ** 2 + (body.position.y - y2) ** 2
            theta = math.atan2(y2 - body.position.y, x2 - body.position.x)
            force = (body.g * (otherBody.mass / body.mass)
                     * 10e7) / (hyp/2)  # -----------
            force_x = force * math.cos(theta)
            force_y = force * math.sin(theta)
            body.momentum_x += force_x * 0.001
            body.momentum_y += force_y * 0.001

        # ---------------------------------------------------
            if hyp <= 255 * gravLineDist and drawGravLines:
                pygame.draw.line(screen, (255 - (hyp / gravLineDist), 255 - (hyp / gravLineDist), 255 - (hyp / gravLineDist)), (body.position.x, body.position.y),
                                 (x2, y2))
        # --------------------------------------------------

    if (body.position.x + body.momentum_x / body.mass * 0.001) >= screenSizeX or (
        body.position.x + body.momentum_x / body.mass * 0.001
    ) <= 0:
        body.newPos = Vector(
            screenSizeX - body.position.x, body.position.y)

    elif (body.position.y + body.momentum_y / body.mass * 0.001) >= screenSizeY or (
        body.position.y + body.momentum_y / body.mass * 0.001
    ) <= 0:
        body.newPos = Vector(
            body.position.x, screenSizeY - body.position.y)

    else:
        body.newPos.x = body.position.x + \
            (body.momentum_x / body.mass * 0.001)
        body.newPos.y = body.position.y + \
            (body.momentum_y / body.mass * 0.001)

    body.position = body.newPos


def update():
    global currentBodies
    global WIPBodyIndex
    global kill
    global canReset

    for n in ArrayBodies:
        if n.blhole:
            n.size = 60
            n.locked = True
        if n.size > 300:
            n.blhole = True

        # TODO: if two bodies collide, bigger one survives or grows and little one dies
        # TODO: when making body, hold mouse and drag to change direction and velocity, and click W to make bigger and S to make smaller
        if WIPBodyIndex == -1 and not n.locked:
            moveBody(n)
        elif not n == ArrayBodies[WIPBodyIndex] and not n.locked:
            moveBody(n)
    for n in ArrayBodies:
        checkCollisions(n)
    kill = True
    # limitSpeed(n)
    pass


def draw():

    backgroundPic.set_alpha(backgroundAlpha)
    screen.blit(backgroundPic, backgroundRect)

    for n in ArrayBodies:
        if n.killing and n.blhole:
            pygame.draw.ellipse(
                screen,
                (175, 100, 100),
                pygame.Rect(n.position.x - (n.size/8), n.position.y - (n.size/8), n.size/4, n.size/4))
        elif n.blhole:
            pygame.draw.ellipse(
                screen,
                (50, 0, 50),
                pygame.Rect(n.position.x - (n.size/8), n.position.y - (n.size/8), n.size/4, n.size/4))
        elif n.killing:
            pygame.draw.ellipse(
                screen,
                (175, 100, 100),
                pygame.Rect(n.position.x - (n.size/2), n.position.y - (n.size/2), n.size, n.size))
        elif n.locked:
            pygame.draw.ellipse(
                screen,
                (100 + n.color, 100 + n.color, 155 + n.color),
                pygame.Rect(n.position.x - (n.size/2), n.position.y - (n.size/2), n.size, n.size))
        else:
            pygame.draw.ellipse(
                screen,
                (155 + n.color, 155 + n.color, 155 + n.color),
                pygame.Rect(n.position.x - (n.size/2), n.position.y - (n.size/2), n.size, n.size))

        # draw mouse
    pygame.draw.ellipse(
        screen,
        (255, 255, 255),
        pygame.Rect(pygame.mouse.get_pos()[0] - 2, pygame.mouse.get_pos()[1] - 2, 4, 4))
    if makeBody:
        pygame.draw.line(screen, (255, 255, 255), (WIPmouseStartX, WIPmouseStartY),
                         (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))


while simRunning:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simRunning = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                simRunning = False
            if event.key == pygame.K_1:
                maxSpeed += 0.5
            if event.key == pygame.K_2:
                maxSpeed -= 0.5

            # change streak lengths
            if event.key == pygame.K_5:
                if backgroundAlpha > 10:
                    backgroundAlpha -= 10
                else:
                    backgroundAlpha = 0

            if event.key == pygame.K_6:
                if backgroundAlpha < 245:
                    backgroundAlpha += 10
                else:
                    backgroundAlpha = 255
            if event.key == pygame.K_w and makeBody and not ArrayBodies[WIPBodyIndex].blhole:
                ArrayBodies[WIPBodyIndex].size += 10
                ArrayBodies[WIPBodyIndex].mass = (
                    ArrayBodies[WIPBodyIndex].size ** 2) / 100
            if event.key == pygame.K_s and makeBody and not ArrayBodies[WIPBodyIndex].blhole:
                if ArrayBodies[WIPBodyIndex].mass > 1 and ArrayBodies[WIPBodyIndex].size > 10:
                    ArrayBodies[WIPBodyIndex].size -= 10
                    ArrayBodies[WIPBodyIndex].mass = (
                        ArrayBodies[WIPBodyIndex].size ** 2) / 100
            if event.key == pygame.K_e and makeBody:
                ArrayBodies[WIPBodyIndex].locked = not ArrayBodies[WIPBodyIndex].locked
            if event.key == pygame.K_SPACE:
                for n in ArrayBodies:
                    n.locked = False
            if event.key == pygame.K_g:
                drawGravLines = not drawGravLines

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]:
        if makeBody:
            ArrayBodies[WIPBodyIndex].dx = ArrayBodies[WIPBodyIndex].position.x - \
                pygame.mouse.get_pos()[0]
            ArrayBodies[WIPBodyIndex].dy = ArrayBodies[WIPBodyIndex].position.y - \
                pygame.mouse.get_pos()[1]
            ArrayBodies[WIPBodyIndex].momentum_x = 15 * (
                WIPmouseStartX - pygame.mouse.get_pos()[0])
            ArrayBodies[WIPBodyIndex].momentum_y = 15 * (
                WIPmouseStartY - pygame.mouse.get_pos()[1])
        else:
            WIPmouseStartX = pygame.mouse.get_pos()[0]
            WIPmouseStartY = pygame.mouse.get_pos()[1]
            makeBody = True
            ArrayBodies.append(Body(
                Vector(
                    pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]),
                Vector(0, 0),
                BodyStartingAngle,
                100,
                20.0,  # TEMP
                0,
                0,
                10,
                random.random() * 100,
                0.2,
                1,
                0,
                0
            ))
            currentBodies += 1
            WIPBodyIndex = currentBodies
    # elif pygame.mouse.get_pressed()[2]:
    #     print("*click*")
    #     if len(ArrayBodies) > 1:
    #         for n in ArrayBodies:
    #             if vecDistance(n.position, Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])) < n.size/2:
    #                 # ArrayBodies.remove(n)
    #                 mouseKillTrigger = True
    #                 n.killing = True
    #                 print("inside")
    #             else:
    #                 mouseKillTrigger = False
    #                 n.killing = False
    # elif mouseKillTrigger:
    #     for n in ArrayBodies:
    #         if len(ArrayBodies) > 1:
    #             if vecDistance(n.position, Vector(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])) < n.size/2:
    #                 ArrayBodies.remove(n)
    #                 currentBodies -= 1
    #                 mouseKillTrigger = False
    #                 print("kill")
    else:
        makeBody = False
        WIPBodyIndex = -1

    update()
    draw()

    pygame.display.flip()

    delta_time = 0.001 * clock.tick(144)


pygame.quit()
