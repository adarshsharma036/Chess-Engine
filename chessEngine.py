class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'N': self.getKnightMoves, 'K': self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # coordinates of squares where enpassant is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastleRight = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                            self.currentCastleRight.wqs, self.currentCastleRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # Updating the King's Location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.pawnPromotion:
            # promotedPiece = input("promote to Q, R, B or N : ")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+'Q'

        # update enpassantpossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow+move.endRow)//2, move.endCol)
        else:
            self.enpassantPossible = ()

        # enpassant move
        if move.enpassant:
            # capturing the pawn
            self.board[move.startRow][move.endCol] = "--"

        # castle move
        if move.isCastleMove:
            if (move.endCol-move.startCol) == 2:  # king side castle
                # moves the rook
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else:  # queen side castle
                # moves the rook
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update Castling rights- whenever there is a kin or rook move
        self.updateCastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                                self.currentCastleRight.wqs, self.currentCastleRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()  # no piece to UNDO
            # current square undo
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # black's turn
            # Updating the King's Location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant
            if move.enpassant:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo Castling rights
            self.castleRightLog.pop()
            newRights = self.castleRightLog[-1]
            self.currentCastleRight = CastleRights(newRights.wks, newRights.bks,
                                                   newRights.wqs, newRights.bqs)

            # undo castle move
            if move.isCastleMove:
                if move.endCol-move.startCol == 2:
                    self.board[move.endRow][move.endCol +
                                            1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol -
                                            2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastleRight.wks = False
            self.currentCastleRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastleRight.bks = False
            self.currentCastleRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastleRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastleRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastleRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastleRight.bks = False

        # if rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastleRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastleRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastleRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastleRight.bks = False

    def getValidMoves(self):
        moves = []
        tempCastleRights = CastleRights(self.currentCastleRight.wks, self.currentCastleRight.bks,
                                        self.currentCastleRight.wqs, self.currentCastleRight.bqs)
        self.inCheck, self.pins, self.checks = self.checkForPinsandChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                if self.whiteToMove:
                    self.getCastleMoves(
                        self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
                else:
                    self.getCastleMoves(
                        self.blackKingLocation[0], self.blackKingLocation[1], moves)
                # to block a check move one piece between enemy and king
                check = self.checks[0]  # checks information
                checkRow = check[0]
                checkCol = check[1]
                # enemy piece causing check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares the piece can move to

                # if Knight, must capture knight or move king else, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        # check[2] and check[3] are check directions
                        validSquare = (kingRow+check[2]*i, kingCol+check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # no checks, all moves are valid
            moves = self.getAllPossibleMoves()

        print(len(moves))

        if len(moves) == 0:
            if self.CheckCheck:
                self.checkMate = True
                # print("CHECKMATE")
            else:
                print("STALEMATE")
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.currentCastleRight = tempCastleRights

        return moves

    def CheckCheck(self):
        print("aaaaaaaaaaa")
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board)):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # Call appropriate move Functions of the Piece
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

            # if self.whiteToMove:
            #     moveAmount = -1
            #     startRow = 6
            #     backRow = 0
            #     enemyColor = 'b'
            # else:
            #     moveAmount = 1
            #     startRow = 1
            #     backRow = 7
            #     enemyColor = 'w'
            # pawnPromotion = False

            # if self.board[r+moveAmount][c] == "--":
            #     if not piecePinned or pinDirection == (moveAmount, 0):
            #         if r+moveAmount == backRow:
            #             pawnPromotion = True
            #         moves.append(Move((r, c), (r+moveAmount, c),
            #                           self.board, pawnPromotion=pawnPromotion))
            #         if r == startRow and self.board[r+2*moveAmount][c] == "--":
            #             moves.append(
            #                 Move((r, c), (r+2*moveAmount, c), self.board))
            # if c-1 >= 0:
            #     if self.board[r+moveAmount][c-1][0] == enemyColor:
            #         if not piecePinned or pinDirection == (moveAmount, -1):
            #             if r+moveAmount == backRow:
            #                 pawnPromotion = True
            #             moves.append(Move((r, c), (r+moveAmount, c-1),
            #                               self.board, pawnPromotion=pawnPromotion))
            #         if (r+moveAmount, c-1) == self.enpassantPossible:
            #             moves.append(
            #                 Move((r, c), (r+moveAmount, c-1), self.board, enpassant=True))
            # if c+1 <= 7:
            #     if self.board[r+moveAmount][c+1][0] == enemyColor:
            #         if not piecePinned or pinDirection == (moveAmount, 1):
            #             if r+moveAmount == backRow:
            #                 pawnPromotion = True
            #             moves.append(Move((r, c), (r+moveAmount, c+1),
            #                               self.board, pawnPromotion=pawnPromotion))
            #         if (r+moveAmount, c+1) == self.enpassantPossible:
            #             moves.append(
            #                 Move((r, c), (r+moveAmount, c+1), self.board, enpassant=True))

        if self.whiteToMove:  # White PAwn Moves
            if self.board[r-1][c] == "--":   # 1 move pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":  # 2 move pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:   # pawn captures to left
                if not piecePinned or pinDirection == (-1, -1):
                    if self.board[r-1][c-1][0] == 'b':
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                    elif (r-1, c-1) == self.enpassantPossible:
                        moves.append(
                            Move((r, c), (r-1, c-1), self.board, enpassant=True))
            if c+1 <= 7:   # pawn captures to right
                if not piecePinned or pinDirection == (-1, 1):
                    if self.board[r-1][c+1][0] == 'b':
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1, c+1) == self.enpassantPossible:
                        moves.append(
                            Move((r, c), (r-1, c+1), self.board, enpassant=True))
        else:  # Black Pawn Moves
            if self.board[r+1][c] == "--":   # 1 move pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  # 2 move pawn advance
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:   # pawn captures to left
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[r+1][c-1][0] == 'w':
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                    elif (r+1, c-1) == self.enpassantPossible:
                        moves.append(
                            Move((r, c), (r+1, c-1), self.board, enpassant=True))
            if c+1 <= 7:   # pawn captures to right
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[r+1][c+1][0] == 'w':
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                    elif (r+1, c+1) == self.enpassantPossible:
                        moves.append(
                            Move((r, c), (r+1, c+1), self.board, enpassant=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r+d[0]*i
                endCol = c+d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":   # Empty Space
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:   # Enemy Piece
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break
                        else:    # Own color Piece
                            break
                else:   # Not in the board MOVE
                    break

    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r+m[0]
            endCol = c+m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r+d[0]*i
                endCol = c+d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":   # Empty Space
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:   # Enemy Piece
                            moves.append(
                                Move((r, c), (endRow, endCol), self.board))
                            break
                        else:    # Own color Piece
                            break
                else:   # Not in the board MOVE
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r+rowMoves[i]
            endCol = c+colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # not an ally piece(empty or enemy piece)
                if endPiece[0] != allyColor:
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsandChecks()
                    if not inCheck:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    # if king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # self.getCastleMoves(r, c, moves, allyColor)

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastleRight.wks) or (not self.whiteToMove and self.currentCastleRight.bks):
            self.getKingsSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastleRight.wqs) or (not self.whiteToMove and self.currentCastleRight.bqs):
            self.getQueensSideCastleMoves(r, c, moves)

    def getKingsSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(
                    Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(
                    Move((r, c), (r, c-2), self.board, isCastleMove=True))

    def checkForPinsandChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow+d[0]*i
                endCol = startCol+d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no check possible
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:   # enemy piece not applying check
                            break
                else:
                    break  # off the board

        # check for knigh checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow+m[0]
            endCol = startCol+m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassant=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.pawnPromotion = False
        # self.promotionChoice = 'Q'
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.pawnPromotion = True

        self.enpassant = enpassant
        if enpassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'

        # castle
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol
        # print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol)+self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # overriding the str() function

    def __str__(self):
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + 'x' + endSquare
            else:
                return endSquare

        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString+endSquare
