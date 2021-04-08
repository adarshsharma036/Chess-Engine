import pygame as p
import chessEngine
import SmartMoveFinder

WIDTH = HEIGHT = 512
MOVE_LOG_WIDTH = 300
MOVE_LOG_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
p.init()


def LoadImages():
    pieces = ['wp', 'wR', 'wN', 'wQ', 'wK',
              'wB', 'bp', 'bR', 'bN', 'bQ', 'bK', 'bB']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            "images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def MAIN():
    p.init()
    screen = p.display.set_mode((WIDTH+MOVE_LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    # print(gs.board)
    LoadImages()
    running = True
    moveLogFont = p.font.SysFont("Arial", 16, False, False)
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True  # if human is white, then it will be true. If AI , then false
    playerTwo = False  # same as above but for black

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (
            not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = chessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        # print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

                # KEY handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:      # UNDO when Z is hitted on keyboard
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:  # reset
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = 'STALEMATE' if gs.staleMate else 'BLACK WINS BY CHECKMATE' if gs.whiteToMove else 'WHITE WINS BY CHECKMATE'
            drawEndGameText(screen, text)
        clock.tick(MAX_FPS)
        p.display.flip()

# highlight square selected and moves for piece selected


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # square selected is a piece that can be moved
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency-> 0(transparent) 255(opaque)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Animating a move
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow-move.startRow
    dC = move.endCol-move.startCol
    framesperSquare = 10  # frames to move one square
    frameCount = (abs(dR)+abs(dC))*framesperSquare
    for frame in range(frameCount+1):
        r, c = (move.startRow+dR*frame/frameCount,
                move.startCol+dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece from ending square
        color = colors[(move.endRow+move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,
                           move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw Captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.enpassant:
                enpassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow-1
                endSquare = p.Rect(move.endCol*SQ_SIZE,
                                   enpassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2-textObject.get_width()/2, HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2+1)+'. ' + str(moveLog[i])+" "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])+"     "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    textY = padding
    lineSpacing = 2
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('Black'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    MAIN()
