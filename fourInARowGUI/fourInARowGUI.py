import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7  # how many spaces wide the board is
BOARDHEIGHT = 6  # how many spaces tall the board is

SPACESIZE = 50  # size of the tokens and individual board spaces in pixels

FPS = 30  # frames per second to update the screen
WINDOWWIDTH = 640  # width of the program's window, in pixels
WINDOWHEIGHT = 480  # height in pixels

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'

# Move counters
human_moves = 0
ai_moves = 0

class Star:
    def __init__(self):
        self.x = random.randint(0, WINDOWWIDTH)
        self.y = random.randint(0, WINDOWHEIGHT)
        self.size = random.randint(1, 1)
        self.speed = random.uniform(0.05, 0.2)

    def move(self):
        self.y += self.speed
        if self.y > WINDOWHEIGHT:
            self.y = 0
            self.x = random.randint(0, WINDOWWIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size)


def run():
    global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
    global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
    global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG

    pygame.init()
    global stars
    stars = [Star() for _ in range(100)]

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Connect Four against AI')

    REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
    REDTOKENIMG = pygame.image.load('images/red_ball.png')
    REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
    BLACKTOKENIMG = pygame.image.load('images/yellow_ball.png')
    BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
    BOARDIMG = pygame.image.load('images/4row_board.png')
    BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

    HUMANWINNERIMG = pygame.image.load('images/4row_humanwinner.png')
    COMPUTERWINNERIMG = pygame.image.load('images/4row_computerwinner.png')
    TIEWINNERIMG = pygame.image.load('images/4row_tie.png')
    WINNERRECT = HUMANWINNERIMG.get_rect()
    WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    ARROWIMG = pygame.image.load('images/4row_arrow.png')
    ARROWRECT = ARROWIMG.get_rect()
    ARROWRECT.left = REDPILERECT.right + 10
    ARROWRECT.centery = REDPILERECT.centery


def processGameOver(winner, board):
    global human_moves, ai_moves  # Add this line
    winnerImg = COMPUTERWINNERIMG if winner == COMPUTER else HUMANWINNERIMG if winner == HUMAN else TIEWINNERIMG
    while True:
        drawBoard(board)
        DISPLAYSURF.blit(winnerImg, WINNERRECT)
        pygame.display.update()
        FPSCLOCK.tick()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                # Reset move counters before returning to start a new game
                human_moves = 0
                ai_moves = 0
                return


def getNewBoard():
    board = []
    for x in range(BOARDWIDTH):
        board.append([EMPTY] * BOARDHEIGHT)
    return board


def makeMove(board, player, column):
    lowest = getLowestEmptySpace(board, column)
    if lowest != -1:
        board[column][lowest] = player


def drawBoard(board, extraToken=None):
    DISPLAYSURF.fill((5, 5, 20))
    for star in stars:
        star.move()
        star.draw(DISPLAYSURF)

    spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            if board[x][y] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
            elif board[x][y] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    if extraToken is not None:
        token_img = REDTOKENIMG if extraToken['color'] == RED else BLACKTOKENIMG
        DISPLAYSURF.blit(token_img, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
            DISPLAYSURF.blit(BOARDIMG, spaceRect)

    DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT)
    DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT)

    # Display move counters
    font = pygame.font.SysFont(None, 30)
    counter_text = font.render(f"Player Moves: {human_moves}    AI Moves: {ai_moves}", True, WHITE)
    DISPLAYSURF.blit(counter_text, (10, 10))


def updateDisplay():
    pygame.display.update()
    FPSCLOCK.tick()


def getHumanInteraction(board):
    global human_moves
    draggingToken = False
    tokenx, tokeny = None, None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                draggingToken = True
                tokenx, tokeny = event.pos
            elif event.type == MOUSEMOTION and draggingToken:
                tokenx, tokeny = event.pos
            elif event.type == MOUSEBUTTONUP and draggingToken:
                if tokeny < YMARGIN and XMARGIN < tokenx < WINDOWWIDTH - XMARGIN:
                    column = int((tokenx - XMARGIN) / SPACESIZE)
                    human_moves += 1
                    return column
                tokenx, tokeny = None, None
                draggingToken = False
        if tokenx is not None and tokeny is not None:
            drawBoard(board, {'x': tokenx - int(SPACESIZE / 2), 'y': tokeny - int(SPACESIZE / 2), 'color': RED})
        else:
            drawBoard(board)

        pygame.display.update()
        FPSCLOCK.tick()


def dropHumanToken(board, column):
    animateDroppingToken(board, column, RED)
    board[column][getLowestEmptySpace(board, column)] = RED
    drawBoard(board)
    pygame.display.update()


def animateDroppingToken(board, column, color):
    x = XMARGIN + column * SPACESIZE
    y = YMARGIN - SPACESIZE
    dropSpeed = 2.0

    lowestEmptySpace = getLowestEmptySpace(board, column)

    while True:
        y += int(dropSpeed)
        dropSpeed += 2
        if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
            return
        drawBoard(board, {'x': x, 'y': y, 'color': color})
        pygame.display.update()
        FPSCLOCK.tick()


def animateComputerMoving(board, column):
    global ai_moves
    ai_moves += 1
    x = BLACKPILERECT.left
    y = BLACKPILERECT.top
    speed = 2.0
    while y > (YMARGIN - SPACESIZE):
        y -= int(speed)
        speed += 1
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    y = YMARGIN - SPACESIZE
    speed = 2.0
    while x > (XMARGIN + column * SPACESIZE):
        x -= int(speed)
        speed += 1.0
        drawBoard(board, {'x': x, 'y': y, 'color': BLACK})
        pygame.display.update()
        FPSCLOCK.tick()
    animateDroppingToken(board, column, BLACK)


def getLowestEmptySpace(board, column):
    for y in range(BOARDHEIGHT - 1, -1, -1):
        if board[column][y] == EMPTY:
            return y
    return -1
