import math
import time
from copy import deepcopy

yellow = "\033[93m"
red = "\033[31m"
green = "\033[92m"
magenta = "\033[95m"
dark_blue = "\033[34m"
ansi_reset = "\033[0m"


def check_color(cell, i, j):
    if cell.startswith(yellow + "king"):
        return "yellow"
    if cell.startswith(green + "king"):
        return "green"
    return None


"""
    if cell == yellow + "king" + to_superscript(i) + to_superscript(j) + ansi_reset:
        return "yellow"
    if cell == green + "king" + to_superscript(i) + to_superscript(j) + ansi_reset:
        return "green"
    return None
    """



superscript = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
}


def to_superscript(num):
    return ''.join(superscript[digit] for digit in str(num))


def clean_cell_value(cell):
    return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')


class NewGameState:
    def __init__(self, board, move=None, parent=None, value=None):
        self.board = board
        self.move = move  # [oldI oldJ newI newJ]
        self.parent = parent
        self.value = value

    # vo ovaa igra minimizinj_player e computer a, maximizing player e #men
    # zosto e toa taka?
    # zatoa sto prviot poteg go pravi #men, vtoriot comp, tretiot #men, cetvrtiot comp ....
    # covekot se obiduva da ja maksimizira svojata prednost so izbor na najdobriot poteg koj ke mu donese najvisok rezultat
    # kompjuterot se obiduva da ja minimizira moznata prednost ili rezultat na covekot, kompjuterot samo saka da ja minimizira svojata steta
    # dokolku prviot poteg go pravese kompjuterot togash toj ke bese maksimiziracki igrac a, covekot minimiziracki
    # bez razlika koj e maksimiziracki a, koj minimiziracki igrac i dvajcata se obiduvaat da go dadat najdobroto od sebe, DA POBEDAT
    def get_children(self, minimizing_player):
        current_state = deepcopy(self.board)
        children_states = []
        available_moves = []
        if minimizing_player is True:  # ako kompjuterot e na red
            available_moves = GameCheckers.getCompAvailableMoves(current_state)
        else:  # ako #men e na red
            available_moves = GameCheckers.getMensAvailableMoves(current_state)

        # possibleMoves.append([i, j, i - 1, j - 1, 100, 100, 100, 100])
        for i in range(len(available_moves)):
            old_I = available_moves[i][0]
            old_J = available_moves[i][1]
            new_I = available_moves[i][2]
            new_J = available_moves[i][3]
            opp1_I = available_moves[i][4]
            opp1_J = available_moves[i][5]
            opp2_I = available_moves[i][6]
            opp2_J = available_moves[i][7]
            state = deepcopy(current_state)
            if minimizing_player is True:
                GameCheckers.MakeAMoveForComputer(state, old_I, old_J, new_I, new_J, opp1_I, opp1_J, opp2_I, opp2_J)
            else:
                GameCheckers.MakeAMoveForMen(state, old_I, old_J, new_I, new_J, opp1_I, opp1_J, opp2_I, opp2_J)
            children_states.append(NewGameState(state, [old_I, old_J, new_I, new_J, opp1_I, opp1_J, opp2_I, opp2_J]))

        return children_states

    def get_board(self):
        return self.board

    def get_parent(self):
        return self.parent

    def get_value(self):
        return self.value

    def set_parent(self, parent):
        self.parent = parent

    def set_value(self, value):
        self.value = value


class GameCheckers:
    num_h = 1  # eden e najsolzenata i najuspesnata hevristika
    num_h_second = None    #po potreba za expectimax

    def __init__(self):
        self.matrica = [["" for _ in range(8)] for _ in range(8)]
        self.isPlayerTurn = True
        self.computerScore = 0
        self.playerScore = 0
        self.availableMoves = []
        self.compPieces = 12
        self.player_pieces = 12
        self.minimaxAlgorithm = True
        self.makeAInitialMatrix()
        self.totalMinimaxSeconds = 0
        self.totalExpectimaxSeconds = 0

    @staticmethod
    def static_method(instance):
        # Пристап до нестатичката
        return instance.num_h

    def makeAInitialMatrix(self):
        for i in range(8):
            for j in range(8):
                self.matrica[i][j] = "----" + to_superscript(i) + to_superscript(j)

        # vo prvite tri reda e comp
        for i in range(3):
            for j in range(8):
                superscript_indices = to_superscript(i) + to_superscript(j)

                if i == 0 and j % 2 != 0 or i == 2 and j % 2 != 0:
                    self.matrica[i][j] = yellow + "comp" + superscript_indices + ansi_reset

                if i == 1 and j % 2 == 0:
                    self.matrica[i][j] = yellow + "comp" + superscript_indices + ansi_reset

        # vo poslednite tri reda e #men
        for i in range(5, 8):
            for j in range(8):
                superscript_indices = to_superscript(i) + to_superscript(j)

                if i == 5 and j % 2 == 0 or i == 7 and j % 2 == 0:
                    self.matrica[i][j] = green + "#men" + superscript_indices + ansi_reset
                if i == 6 and j % 2 != 0:
                    self.matrica[i][j] = green + "#men" + superscript_indices + ansi_reset

    def printAMatrix(self):
        print("       0       1       2       3       4       5       6       7")
        print()
        for i in range(8):
            print(str(i) + "    ", end="")
            for j in range(8):
                print(self.matrica[i][j] + "  ", end="")
            print()
            print()

        print(red + f"                    SCORE:   comp:{self.computerScore}   #men:{self.playerScore}" + ansi_reset)
        if self.totalMinimaxSeconds != 0:
            print(dark_blue + f"            Total minimax seconds so far: {self.totalMinimaxSeconds:.3f}" + ansi_reset)
        if self.totalExpectimaxSeconds != 0:
            print(dark_blue + f"            Total expectimax seconds so far: {self.totalExpectimaxSeconds:.3f}" + ansi_reset)

    """ 
    POCNUVA OBLAST NA FUNKCII ZA PROVERKA NA VALIDNOST NA PLAYER I COMPUTER
    """

    @staticmethod
    def checkPlayerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ):
        # samo da se pomesti na levo ili na desno
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if newI < 0 or newI > 7:
            return False
        if newJ < 0 or newJ > 7:
            return False
        new_cell = clean_cell_value(tablaZaIgranje[newI][newJ])
        old_cell = clean_cell_value(tablaZaIgranje[oldI][oldJ])
        if new_cell != "----" + to_superscript(newI) + to_superscript(newJ):
            return False
        if (old_cell == "#men" + to_superscript(oldI) + to_superscript(oldJ)) or (
                old_cell == "king" + to_superscript(oldI) + to_superscript(oldJ)):
            return True
        return False

    @staticmethod
    def checkComputerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ):
        # samo da se pomesti na levo ili na desno
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if newI < 0 or newI > 7:
            return False
        if newJ < 0 or newJ > 7:
            return False
        new_cell = clean_cell_value(tablaZaIgranje[newI][newJ])
        old_cell = clean_cell_value(tablaZaIgranje[oldI][oldJ])
        if new_cell != "----" + to_superscript(newI) + to_superscript(newJ):
            return False
        if (old_cell == "comp" + to_superscript(oldI) + to_superscript(oldJ)) or (
                old_cell == "king" + to_superscript(oldI) + to_superscript(oldJ)):
            return True
        return False

    @staticmethod
    def checkPlayerJump(tablaZaIgranje, oldI, oldJ, newI, newJ, opponentX, opponentY):
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if GameCheckers.checkPlayerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ) == False:
            return False

        opponent_cell = clean_cell_value(tablaZaIgranje[opponentX][opponentY])

        if opponent_cell == "comp" + to_superscript(opponentX) + to_superscript(opponentY):
            return True
        if check_color(tablaZaIgranje[opponentX][opponentY], opponentX, opponentY) == "yellow":
            return True

        return False

    @staticmethod
    def checkComputerJump(tablaZaIgranje, oldI, oldJ, newI, newJ, opponentX, opponentY):
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if GameCheckers.checkComputerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ) == False:
            return False

        opponent_cell = clean_cell_value(tablaZaIgranje[opponentX][opponentY])

        if opponent_cell == "#men" + to_superscript(opponentX) + to_superscript(opponentY):
            return True
        if check_color(tablaZaIgranje[opponentX][opponentY], opponentX, opponentY) == "green":   #skoka kral
            return True
        return False

    @staticmethod
    def checkPlayerDoubleJump(tablaZaIgranje, oldI, oldJ, newI, newJ, opponent_One_X, opponent_One_Y, opponent_Two_X,
                              opponent_Two_Y, posrednikX, posrednikY):
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if GameCheckers.checkPlayerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ) == False:
            return False

        protivnik1 = False
        protivnik2 = False
        opp1 = clean_cell_value(tablaZaIgranje[opponent_One_X][opponent_One_Y])
        opp2 = clean_cell_value(tablaZaIgranje[opponent_Two_X][opponent_Two_Y])
        posred = clean_cell_value(tablaZaIgranje[posrednikX][posrednikY])
        if posred != "----" + to_superscript(posrednikX) + to_superscript(posrednikY):     # posrednik poleto mora da e prazno za da ima dvojno skokanje
            return False
        if opp1 == "comp" + to_superscript(opponent_One_X) + to_superscript(opponent_One_Y):
            protivnik1 = True
        if opp2 == "comp" + to_superscript(opponent_Two_X) + to_superscript(opponent_Two_Y):
            protivnik2 = True
        if check_color(tablaZaIgranje[opponent_One_X][opponent_One_Y], opponent_One_X, opponent_One_Y) == "yellow":
            protivnik1 = True
        if check_color(tablaZaIgranje[opponent_Two_X][opponent_Two_Y], opponent_Two_X, opponent_Two_Y) == "yellow":
            protivnik2 = True
        if protivnik1 == True and protivnik2 == True:
            return True
        return False

    @staticmethod
    def checkComputerDoubleJump(tablaZaIgranje, oldI, oldJ, newI, newJ, opponent_One_X, opponent_One_Y, opponent_Two_X,
                                opponent_Two_Y, posrednikX, posrednikY):
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        if GameCheckers.checkComputerMoves(tablaZaIgranje, oldI, oldJ, newI, newJ) == False:
            return False

        protivnik1 = False
        protivnik2 = False
        opp1 = clean_cell_value(tablaZaIgranje[opponent_One_X][opponent_One_Y])
        opp2 = clean_cell_value(tablaZaIgranje[opponent_Two_X][opponent_Two_Y])
        posred = clean_cell_value(tablaZaIgranje[posrednikX][posrednikY])

        if posred != "----" + to_superscript(posrednikX) + to_superscript(posrednikY):
            return False
        if opp1 == "#men" + to_superscript(opponent_One_X) + to_superscript(opponent_One_Y):
            protivnik1 = True
        if opp2 == "#men" + to_superscript(opponent_Two_X) + to_superscript(opponent_Two_Y):
            protivnik2 = True
        # posrednik poleto mora da e prazno za da ima dvojno skokanje
        if check_color(tablaZaIgranje[opponent_One_X][opponent_One_Y], opponent_One_X, opponent_One_Y) == "green":
            protivnik1 = True
        if check_color(tablaZaIgranje[opponent_Two_X][opponent_Two_Y], opponent_Two_X, opponent_Two_Y) == "green":
            protivnik2 = True
        if protivnik1 == True and protivnik2 == True:
            return True
        return False

    """
        ZAVRSUVA OBLAST NA FUNKCII ZA PROVERKA NA VALIDNOST NA PLAYER I COMPUTER
    """

    def startGame(self):
        print(magenta + " *** DOBREDOJDOVTE VO IGRATA DAMA ***" + ansi_reset)
        print(
            "Ova e implementacijata na studentot Dragana Trifunova [223044] za igrata dama i ovde e prikazana amerikanskata verzija od igrata")
        print(
            "Vo Amerikanskata verzija postojat 12 pioncinja na sekoi od protivnicite i vo sekoi red ima po osum kelii")
        print()
        print("PRAVILA NA IGRANJE")
        print("1. Dokolku sakate da zapocnete so igranje napisete 'start'")
        print("2. Dokolku sakate da prekinete so igranje vo bilo koe vreme pritisnete 'Enter'")
        print("3. Dokolku sakate da se predadete napisete 'surrender'")
        print("4. Koordinatite 'i' i 'j' gi vnesuvate so zapirka pomegu niv bez prazno mesto")
        print(red + "Pred da zapocnete so igrata (pred da napisete 'start') najprvin mora da ja napravite nejzinata konfiguracija." + ansi_reset)
        print()
        print(red + "!!! KONFIGURACIJA !!!" + ansi_reset)
        print()
        print("Dali sakate igra covek-algoritam ili pak sakate algoritmite da igraat megu niv 1/2? ")
        numberr = input()
        if numberr == "1":
            print("Vie igrate so pionceto oznaceno kako '#men'")
            print(red  + "Mora da izberete so koj algoritam ke igrate. Napisete go imeto na algoritmot minimax/expectimax? " + ansi_reset)
            algo = input()
            if algo == "expectimax":
                self.minimaxAlgorithm = False
            if algo != "expectimax" and algo != "minimax":
                exit()
            print("So koja hevristika ke igrate 1/2/3?")
            print("1) Best")
            print("2) Almost King")
            print("3) Edge Position")
            nh = input()
            if nh == "2":
                GameCheckers.num_h = 2
            if nh == "3":
                GameCheckers.num_h = 3
            if nh != "1" and nh != "2" and nh != "3":
                print(
                    "Morate da vnesete validen broj za hevristikite. Ima vkupno 3 hevristiki.\n" + red + "Startuvajte ja programata od pocetok i vnesete 1, 2 ili 3" + ansi_reset)
                exit()

            print("Vnesete 'start' koga ke se cuvstvuvate podgotveni da pocnete.")
            started = input()
            if started != "start":
                exit()
            while True:
                self.printAMatrix()
                if self.isPlayerTurn == True:
                    print("\nVie #men ste na red")
                    self.getMensInput()
                else:
                    print("\nComputer e na red")
                    self.artificialIntelligence()
                if self.player_pieces == 0:
                    self.printAMatrix()
                    print(red + "IZGUBIVTE!!!" + ansi_reset)
                    exit()
                elif self.compPieces == 0:
                    self.printAMatrix()
                    print(red + "POBEDIVTE!!!" + ansi_reset)
                    exit()
                self.isPlayerTurn = not self.isPlayerTurn
        elif numberr == "2":
            #ako algoritmite igraat megu sebe, vo toj slucaj prv ke bide expectimax a, vtor minimax
            print("Expectimax igra so pionceto oznaceno kako #men")
            print("Minimax igra so pionceto oznaceno kako comp")
            print("So koja hevristika ke igra minimax 1/2/3?")
            print("1) Best")
            print("2) Almost King")
            print("3) Edge Position")
            nh = input()
            if nh == "2":
                GameCheckers.num_h = 2
            if nh == "3":
                GameCheckers.num_h = 3
            if nh != "1" and nh != "2" and nh != "3":
                print(
                    "Morate da vnesete validen broj za hevristikite. Ima vkupno 3 hevristiki.\n" + red + "Startuvajte ja programata od pocetok i vnesete 1, 2 ili 3" + ansi_reset)
                exit()
            print("So koja hevristika ke igra expectimax 1/2/3?")
            print("1) Best")
            print("2) Almost King")
            print("3) Edge Position")
            nh = input()
            if nh == "1":
                GameCheckers.num_h_second = 1
            if nh == "2":
                GameCheckers.num_h_second = 2
            if nh == "3":
                GameCheckers.num_h_second = 3
            if nh != "1" and nh != "2" and nh != "3":
                print("Morate da vnesete validen broj za hevristikite. Ima vkupno 3 hevristiki.\n" + red + "Startuvajte ja programata od pocetok i vnesete 1, 2 ili 3" + ansi_reset)
                exit()

            print("Vnesete 'start' koga ke se cuvstvuvate podgotveni da pocnete.")
            started = input()
            if started != "start":
                exit()
            while True:
                self.printAMatrix()
                if self.isPlayerTurn == True:   #ako e expectimax e na red
                    print("\nExpectimax e na red")
                    self.expectimaxInsteadOfPerson()
                else:
                    #minimax se povikuva povtorno preku artificialInteligence()
                    print("\nMinimax e na red")
                    self.artificialIntelligence()  #pod defolt vo klasata e minimax algoritam
                if self.player_pieces == 0:
                    self.printAMatrix()
                    print(red + "POBEDI MINIMAX!!!" + ansi_reset)
                    exit()
                elif self.compPieces == 0:
                    self.printAMatrix()
                    print(red + "POBEDI EXPECTIMAX!!!" + ansi_reset)
                    exit()
                self.isPlayerTurn = not self.isPlayerTurn


        else:
            print("Nevaliden vlez! Trebase da vnesete '1' ili '2'. Startuvajte ja programata od pocetokot.")


    @staticmethod
    def getMensAvailableMoves(tabla):
        """
        Za #men
            - 1 pole napred levo
            - 1 pole napred desno
            - da skokne edno pole dijagonalno na levo ako na toa pole ima protivnik
            - da skokne edno pole dijagonalno na desno ako na toa pole ima protivnik
            - da skokne dve polinja dijagonalno na levo ili desno dokolku i na dvete polinja ima protivnik
        """
        possibleMoves = []
        # lista koja sodrzi old_I old_J new_I new_J opponent1_i opponent1_j opponent2_i opponent2_j
        # DOKOLKU '#men' se pomestuva samo na levo ili desno BEZ SKOKANJE togash    opponent1_i=100    opponent1_j=100

        for i in range(8):
            for j in range(8):
                cell = tabla[i][j].replace(ansi_reset, '').replace(green, '').replace(yellow, '')[:4]
                if cell == "#men":
                    if GameCheckers.checkPlayerMoves(tabla, i, j, i - 1, j - 1):  # edno pole napred levo
                        possibleMoves.append([i, j, i - 1, j - 1, 100, 100, 100, 100])  # 4 * 100 bideiki nema opponents
                    if GameCheckers.checkPlayerMoves(tabla, i, j, i - 1, j + 1):  # edno pole napred desno
                        possibleMoves.append([i, j, i - 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkPlayerJump(tabla, i, j, i - 2, j - 2, i - 1, j - 1):  # skoka 1 pole na levo
                        possibleMoves.append([i, j, i - 2, j - 2, i - 1, j - 1, 100,
                                              100])  # 2 * 100 bideiki prviot opponent go ima a, vtoriot go nema
                    if GameCheckers.checkPlayerJump(tabla, i, j, i - 2, j + 2, i - 1,
                                                    j + 1):  # skoka edno pole na desno
                        possibleMoves.append([i, j, i - 2, j + 2, i - 1, j + 1, 100, 100])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3, i - 2,
                                                          j + 2):  # skoka dve polinja na levo   6,1         5,2    3,4
                        possibleMoves.append([i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3, i - 2,
                                                          j - 2):  # skoka dve polinja na desno   6,7      5,6   3,4
                        possibleMoves.append([i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3])

        """
        Za king 
            - 1 pole napred levo
            - 1 pole nazad levo
            - 1 pole napred desno
            - 1 pole nazad desno
            - da skokne edno pole dijagonalno na levo-napred ako na toa pole ima protivnik
            - da skokne edno pole dijagonalno na levo-nazad ako na toa pole ima protivnik
            - da skokne edno pole dijagonalno na desno-napred ako na toa pole ima protivnik
            - da skokne edno pole dijagonalno na desno-nazad ako na toa pole ima protivnik
            - da skokne dve polinja dijagonalno na levo-napred ili desno-napred dokolku i na dvete polinja ima protivnik
            - da skokne dve polinja dijagonalno na levo-nazad ili desno-nazad dokolku i na dvete polinja ima protivnik

        """

        for i in range(8):
            for j in range(8):
                if check_color(tabla[i][j], i,
                               j) == "green":  # tabla[i][j].startswith(green + 'k'):   #Ako king e so zelena boja togash toa e king na #men a, dokolku e so zolta e na computer

                    if GameCheckers.checkPlayerMoves(tabla, i, j, i - 1, j - 1):  # edno pole napred levo
                        possibleMoves.append([i, j, i - 1, j - 1, 100, 100, 100, 100])
                    if GameCheckers.checkPlayerMoves(tabla, i, j, i + 1, j - 1):  # edno pole nazad levo
                        possibleMoves.append([i, j, i + 1, j - 1, 100, 100, 100, 100])
                    if GameCheckers.checkPlayerMoves(tabla, i, j, i - 1, j + 1):  # edno pole napred desno
                        possibleMoves.append([i, j, i - 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkPlayerMoves(tabla, i, j, i + 1, j + 1):  # edno pole nazad desno
                        possibleMoves.append([i, j, i + 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkPlayerJump(tabla, i, j, i - 2, j - 2, i - 1,
                                                    j - 1):  # skoka 1 pole na levo napred
                        possibleMoves.append([i, j, i - 2, j - 2, i - 1, j - 1, 100, 100])
                    if GameCheckers.checkPlayerJump(tabla, i, j, i + 2, j - 2, i + 1,
                                                    j - 1):  # skoka edno pole levo nazad
                        possibleMoves.append([i, j, i + 2, j - 2, i + 1, j - 1, 100, 100])
                    if GameCheckers.checkPlayerJump(tabla, i, j, i - 2, j + 2, i - 1,
                                                    j + 1):  # skoka edno pole na desno napred
                        possibleMoves.append([i, j, i - 2, j + 2, i - 1, j + 1, 100, 100])
                    if GameCheckers.checkPlayerJump(tabla, i, j, i + 2, j + 2, i + 1,
                                                    j + 1):  # skoka edno pole na desno nazad
                        possibleMoves.append([i, j, i + 2, j + 2, i + 1, j + 1, 100, 100])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3, i - 2,
                                                          j + 2):  # skoka dve polinja na levo napred
                        possibleMoves.append([i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3, i + 2,
                                                          j - 2):  # skoka dve polinja na levo nazad
                        possibleMoves.append([i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3, i - 2,
                                                          j - 2):  # skoka dve polinja na desno napred
                        possibleMoves.append([i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3])
                    if GameCheckers.checkPlayerDoubleJump(tabla, i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3, i + 2,
                                                          j + 2):  # skoka dve polinja na desno nazad
                        possibleMoves.append([i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3])

        return possibleMoves

    @staticmethod
    def getCompAvailableMoves(tabla):
        possibleMoves = []

        # ako se raboti za obicno pionce [levo i desno sega se obratno]

        for i in range(8):
            for j in range(8):
                cell = tabla[i][j].replace(ansi_reset, '').replace(green, '').replace(yellow, '')[:4]
                if cell == "comp":
                    if GameCheckers.checkComputerMoves(tabla, i, j, i + 1, j + 1):  # edno pole napred levo  i+1,j+1
                        possibleMoves.append([i, j, i + 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerMoves(tabla, i, j, i + 1, j - 1):  # edno pole napred desno i+1, j-1
                        possibleMoves.append([i, j, i + 1, j - 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i + 2, j + 2, i + 1,
                                                      j + 1):  # skok edno pole na levo i+2, j+2
                        possibleMoves.append([i, j, i + 2, j + 2, i + 1, j + 1, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i + 2, j - 2, i + 1,
                                                      j - 1):  # skok edno pole na desno i+2, j-2
                        possibleMoves.append([i, j, i + 2, j - 2, i + 1, j - 1, 100, 100])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3,
                                                            i + 2,
                                                            j + 2):  # skoka dve polinja na levo  i+4,j+4     4 1 3 2
                        possibleMoves.append([i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3,
                                                            i + 2, j - 2):  # skoka dve polinja na desno  i+4,j-4
                        possibleMoves.append([i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3])

        # ako se raboti za zolt king e sosema istata logika kako i za zelen king
        for i in range(8):
            for j in range(8):
                if check_color(tabla[i][j], i, j) == "yellow":  # tabla[i][j].startswith(yellow + "k"):
                    if GameCheckers.checkComputerMoves(tabla, i, j, i - 1, j - 1):  # edno pole napred levo
                        possibleMoves.append([i, j, i - 1, j - 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerMoves(tabla, i, j, i + 1, j - 1):  # edno pole nazad levo
                        possibleMoves.append([i, j, i + 1, j - 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerMoves(tabla, i, j, i - 1, j + 1):  # edno pole napred desno
                        possibleMoves.append([i, j, i - 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerMoves(tabla, i, j, i + 1, j + 1):  # edno pole nazad desno
                        possibleMoves.append([i, j, i + 1, j + 1, 100, 100, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i - 2, j - 2, i - 1,
                                                      j - 1):  # skoka 1 pole na levo napred
                        possibleMoves.append([i, j, i - 2, j - 2, i - 1, j - 1, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i + 2, j - 2, i + 1,
                                                      j - 1):  # skoka edno pole levo nazad
                        possibleMoves.append([i, j, i + 2, j - 2, i + 1, j - 1, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i - 2, j + 2, i - 1,
                                                      j + 1):  # skoka edno pole na desno napred
                        possibleMoves.append([i, j, i - 2, j + 2, i - 1, j + 1, 100, 100])
                    if GameCheckers.checkComputerJump(tabla, i, j, i + 2, j + 2, i + 1,
                                                      j + 1):  # skoka edno pole na desno nazad
                        possibleMoves.append([i, j, i + 2, j + 2, i + 1, j + 1, 100, 100])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3,
                                                            i - 2, j + 2):  # skoka dve polinja na levo napred
                        possibleMoves.append([i, j, i - 4, j + 4, i - 1, j + 1, i - 3, j + 3])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3,
                                                            i + 2, j - 2):  # skoka dve polinja na levo nazad
                        possibleMoves.append([i, j, i + 4, j - 4, i + 1, j - 1, i + 3, j - 3])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3,
                                                            i - 2, j - 2):  # skoka dve polinja na desno napred
                        possibleMoves.append([i, j, i - 4, j - 4, i - 1, j - 1, i - 3, j - 3])
                    if GameCheckers.checkComputerDoubleJump(tabla, i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3,
                                                            i + 2, j + 2):  # skoka dve polinja na desno nazad
                        possibleMoves.append([i, j, i + 4, j + 4, i + 1, j + 1, i + 3, j + 3])
        return possibleMoves

    def getMensInput(self):
        mensLegalMoves = GameCheckers.getMensAvailableMoves(self.matrica)
        if len(mensLegalMoves) == 0:
            print("Nemate preostanati dozvoleni potezi! JA PREKINUVAME IGRATA!!!")
            exit()

        while True:
            oldPositionCordinates = input("Vnesete na koi koordinati se naoga pionceto: ")
            if oldPositionCordinates == "":  # Enter, znaci se otkazuva od igrata
                print("Igrata zavrsi!")
                exit()
            if oldPositionCordinates == "surrender":
                print("Se predadovte!")
                exit()

            newPositionCordinates = input("Vnesete na koi koordinati sakate da go pomestite pionceto: ")
            if newPositionCordinates == "":
                print("Igrata zavrsi!")
                exit()
            if newPositionCordinates == "surrender":
                print("Se predadovte!")
                exit()
            old = oldPositionCordinates.split(",")
            new = newPositionCordinates.split(",")

            if len(old) != 2 or len(new) != 2:
                print("Nelegalen vlez!")
                continue

            old_I = old[0]
            old_J = old[1]
            new_I = new[0]
            new_J = new[1]
            if not old_I.isdigit() or not old_J.isdigit() or not new_I.isdigit() or not new_J.isdigit():
                print("Nelegalen vlez!")
                continue
            old_I = int(old_I)
            old_J = int(old_J)
            new_I = int(new_I)
            new_J = int(new_J)
            move = []
            if abs(old_I - new_I) == 1:  # se raboti za obicno pomestuvanje
                move = [old_I, old_J, new_I, new_J, 100, 100, 100, 100]
                if move not in mensLegalMoves:
                    print("Ne mozete da napravete takvo dvizenje")
                    continue
                GameCheckers.MakeAMoveForMen(self.matrica, old_I, old_J, new_I, new_J, 100, 100, 100, 100)
                self.calculatePoints()
                break
            elif abs(old_I - new_I) == 2:  # se raboti za preskoknuvanje eden opponent
                move = [old_I, old_J, new_I, new_J, (old_I + new_I) // 2, (old_J + new_J) // 2, 100, 100]
                if move not in mensLegalMoves:
                    print("Ne mozete da napravete takvo dvizenje")
                    continue
                GameCheckers.MakeAMoveForMen(self.matrica, old_I, old_J, new_I, new_J, (old_I + new_I) // 2,
                                             (old_J + new_J) // 2, 100, 100)
                self.calculatePoints()
                break
            elif abs(old_I - new_I) == 4:  # skoknuvanje na 2 protivnici
                move = self.defineAllPosibleOpponents(old_I, old_J, new_I, new_J, mensLegalMoves)
                if move == None:
                    print("Ne mozete da napravete takvo dvizenje")
                    continue
                GameCheckers.MakeAMoveForMen(self.matrica, move[0], move[1], move[2], move[3], move[4], move[5],
                                             move[6], move[7])
                self.calculatePoints()
                break
            else:
                print("Nemozete da napravite takvo dvizenje")
                continue

    def defineAllPosibleOpponents(self, old_I, old_J, new_I, new_J, mensLegalMoves):
        move1_base = [old_I, old_J, new_I, new_J, old_I + 1, old_J + 1]
        for i in [[old_I + 3, old_J + 3], [old_I + 3, old_J - 3], [old_I - 3, old_J + 3], [old_I - 3, old_J - 3]]:
            move = move1_base + i
            if move in mensLegalMoves:
                return move

        move2_base = [old_I, old_J, new_I, new_J, old_I + 1, old_J - 1]
        for i in [[old_I + 3, old_J + 3], [old_I + 3, old_J - 3], [old_I - 3, old_J + 3], [old_I - 3, old_J - 3]]:
            move = move2_base + i
            if move in mensLegalMoves:
                return move

        move3_base = [old_I, old_J, new_I, new_J, old_I - 1, old_J + 1]
        for i in [[old_I + 3, old_J + 3], [old_I + 3, old_J - 3], [old_I - 3, old_J + 3], [old_I - 3, old_J - 3]]:
            move = move3_base + i
            if move in mensLegalMoves:
                return move

        move4_base = [old_I, old_J, new_I, new_J, old_I - 1, old_J - 1]
        for i in [[old_I + 3, old_J + 3], [old_I + 3, old_J - 3], [old_I - 3, old_J + 3], [old_I - 3, old_J - 3]]:
            move = move4_base + i
            if move in mensLegalMoves:
                return move

        return None

    def calculatePoints(self):
        self.player_pieces = 0
        self.compPieces = 0
        for i in range(8):
            for j in range(8):
                if clean_cell_value(self.matrica[i][j])[0] == "#" and clean_cell_value(self.matrica[i][j])[1] == 'm':
                    self.player_pieces += 1
                if check_color(self.matrica[i][j], i, j) == "green":  # self.matrica[i][j].startswith(green + 'k'):
                    self.player_pieces += 1
                if clean_cell_value(self.matrica[i][j])[0] == "c" and clean_cell_value(self.matrica[i][j])[
                    1] == "o":  # proveruvame za sekoj slucaj po dva karakteri
                    self.compPieces += 1
                if check_color(self.matrica[i][j], i, j) == "yellow":  # self.matrica[i][j].startswith(yellow + 'k'):
                    self.compPieces += 1
        self.computerScore = 12 - self.player_pieces
        self.playerScore = 12 - self.compPieces

    # ovaa funkcija navistina pravi pridvizuvanje zatoa sto direktno ja menuva self.matrica
    # najgolem del od drugite funkcii pravat deepcopy odnosno samo isprobuvaat na kopija sto bi bilo koga bilo koe covece pravi poteg
    @staticmethod
    def MakeAMoveForMen(board, old_I, old_J, new_I, new_J, opponent1_I, opponent1_J, opponent2_I, opponent2_J):
        string = "king"
        if not check_color(board[old_I][old_J], old_I,
                           old_J) == "green":  # board[old_I][old_J].startswith(green + "k"):    #dokolku seuste nema stanato king
            if new_I != 0:  # queenRow = 0 za #men
                string = "#men"

        if opponent1_I == 100 and opponent1_J == 100 and opponent2_I == 100 and opponent2_J == 100:  # ako se raboti samo za prosto dvizenje edno pole napred
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = green + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset
        elif opponent2_I == 100 and opponent2_J == 100:  # skoka preku edno
            board[opponent1_I][opponent1_J] = "----" + to_superscript(opponent1_I) + to_superscript(opponent1_J)
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = green + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset
        else:  # dvojno skokanje
            board[opponent1_I][opponent1_J] = "----" + to_superscript(opponent1_I) + to_superscript(opponent1_J)
            board[opponent2_I][opponent2_J] = "----" + to_superscript(opponent2_I) + to_superscript(opponent2_J)
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = green + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset

    @staticmethod
    def MakeAMoveForComputer(board, old_I, old_J, new_I, new_J, opponent1_I, opponent1_J, opponent2_I, opponent2_J):
        string = "king"
        if not check_color(board[old_I][old_J], old_I,
                           old_J) == "yellow":  # board[old_I][old_J].startswith(yellow + "k"):
            if new_I != 7:  # sedmata redica e king redica za comp
                string = "comp"
        if opponent1_I == 100 and opponent1_J == 100 and opponent2_I == 100 and opponent2_J == 100:  # ako se raboti samo za prosto dvizenje edno pole napred
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = yellow + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset
        elif opponent2_I == 100 and opponent2_J == 100:  # skoka preku edno
            board[opponent1_I][opponent1_J] = "----" + to_superscript(opponent1_I) + to_superscript(opponent1_J)
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = yellow + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset
        else:
            board[opponent1_I][opponent1_J] = "----" + to_superscript(opponent1_I) + to_superscript(opponent1_J)
            board[opponent2_I][opponent2_J] = "----" + to_superscript(opponent2_I) + to_superscript(opponent2_J)
            board[old_I][old_J] = "----" + to_superscript(old_I) + to_superscript(old_J)
            board[new_I][new_J] = yellow + string + to_superscript(new_I) + to_superscript(new_J) + ansi_reset

    def artificialIntelligence(self):
        t1 = time.time()
        timeRecord = ""
        current_State = NewGameState(deepcopy(self.matrica))

        first_computer_moves = current_State.get_children(True)
        if len(first_computer_moves) == 0:
            print("Kompjuterot nemoze da najde resenie. Vie pobedivte")
            exit()
        dict = {}

        for i in range(len(first_computer_moves)):
            child = first_computer_moves[i]
            if self.minimaxAlgorithm == True:
                value = GameCheckers.minimax(child.get_board(), 2, -math.inf, math.inf, False)
                timeRecord = "minimax: "
            else:
                value = GameCheckers.expectimax(child.get_board(), 2,  False)
                timeRecord = "expectimax: "
            dict[value] = child

        if len(dict.keys()) == 0:
            print("Kompjuterot ima problemi so presmetkite. Ti pobedi!")
            exit()

        new_board = dict[max(dict)].get_board()
        self.matrica = new_board
        self.calculatePoints()
        t2 = time.time()
        difference = t2-t1
        timeRecord += str(difference)
        timeRecord += " sekundi"
        print(timeRecord)
        if self.minimaxAlgorithm == True:
            self.totalMinimaxSeconds += difference
        else:
            self.totalExpectimaxSeconds += difference

    def expectimaxInsteadOfPerson(self):
        t1 = time.time()
        current_State = NewGameState(deepcopy(self.matrica))

        first_computer_moves = current_State.get_children(False)
        if len(first_computer_moves) == 0:
            print("Expectimax nemoze da najde resenie. Minimax pobedi!")
            exit()
        dict = {}

        for i in range(len(first_computer_moves)):
            child = first_computer_moves[i]
            value = GameCheckers.expectimax(child.get_board(), 2, True)
            dict[value] = child

        if len(dict.keys()) == 0:
            print("Expectimax ima problemi so presmetkite. Ti pobedi!")
            exit()

        new_board = dict[max(dict)].get_board()
        self.matrica = new_board
        self.calculatePoints()
        t2 = time.time()
        difference = t2 - t1
        timeRecord = "expectimax: "
        timeRecord += str(difference)
        timeRecord += " sekundi"
        print(timeRecord)
        self.totalExpectimaxSeconds += difference

    @staticmethod
    def minimax(board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return GameCheckers.calculate_heuristics(board, 'minimax')
        current_state = NewGameState(deepcopy(board))
        if maximizing_player is True:
            max_eval = -math.inf
            for child in current_state.get_children(True):
                ev = GameCheckers.minimax(child.get_board(), depth - 1, alpha, beta, False)
                max_eval = max(max_eval, ev)
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            current_state.set_value(max_eval)
            return max_eval
        else:
            min_eval = math.inf
            for child in current_state.get_children(False):
                ev = GameCheckers.minimax(child.get_board(), depth - 1, alpha, beta, True)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            current_state.set_value(min_eval)
            return min_eval

    # Covekot ja bara najgolemata mozna vrednost
    # Kompjuterot ja bara najmalata mozna vrednost i go izbira potegot sto ke ja minimizira dobivkata na igracot
    # Za da go adaptirame minmax algoritmot na coveckiot igrac,
    # heuristickata funkcija treba da go proceni tekovnioto pozicioniranje na tablata na nacin
    # na koj gi favorizira potezite na covekot
    @staticmethod
    def best_heuristics(board):
        def clean_cell_value(cell):
            return cell.replace(ansi_reset, '').replace(green, '').replace(yellow, '')

        def isTheSame(cell, string, i, j):
            x = clean_cell_value(cell)
            return x == (string + to_superscript(i) + to_superscript(j))

        result = 0
        mine = 0
        opp = 0
        for i in range(8):
            for j in range(8):
                if isTheSame(board[i][j], "comp", i, j) or board[i][j].startswith(yellow + "k"):
                    mine += 1
                    if isTheSame(board[i][j], "comp", i, j):
                        result -= 5
                    if board[i][j].startswith(yellow + "k"):
                        result -= 10
                    if i == 0 or j == 0 or i == 7 or j == 7:
                        result -= 7
                    if i + 1 > 7 or j - 1 < 0 or i - 1 < 0 or j + 1 > 7:
                        continue
                    if (isTheSame(board[i + 1][j - 1], "#men", i + 1, j - 1) or board[i + 1][j - 1].startswith(
                            green + "k")) and isTheSame(board[i - 1][
                                                            j + 1], "----", i - 1, j + 1):
                        result += 3
                    if (isTheSame(board[i + 1][j + 1], "#men", i + 1, j + 1) or board[i + 1][j + 1].startswith(
                            green + "k")) and isTheSame(board[i - 1][j - 1], "----", i - 1, j - 1):
                        result += 3
                    if board[i - 1][j - 1].startswith(green + "k") and isTheSame(board[i + 1][j + 1], "----", i + 1,
                                                                                 j + 1):  # board[i + 1][j + 1] == "---":
                        result += 3

                    if board[i - 1][j + 1].startswith(green + "k") and isTheSame(board[i + 1][j - 1], "----", i + 1,
                                                                                 j - 1):
                        result += 3
                    if i + 2 > 7 or i - 2 < 0 or j - 2 < 0:
                        continue
                    if (isTheSame(board[i + 1][j - 1], "#men", i + 1, j - 1) or board[i + 1][j - 1].startswith(
                            green + "k")) and isTheSame(board[i + 2][j - 2], "----", i + 2, j - 2):
                        result -= 6
                    if i + 2 > 7 or j + 2 > 7:
                        continue
                    if (isTheSame(board[i + 1][j + 1], "#men", i + 1, j + 1) or board[i + 1][j + 1].startswith(
                            green + "k")) and isTheSame(board[i + 2][j + 2], "----", i + 2, j + 2):
                        result -= 6

                elif isTheSame(board[i][j], "#men", i, j) or board[i][j].startswith(green + "k"):
                    opp += 1
        return result + (mine - opp) * 1000

    @staticmethod
    def calculate_heuristics(board, algo):
        if GameCheckers.num_h_second == None:
            if GameCheckers.num_h == 1:
                return GameCheckers.best_heuristics(board)
            if GameCheckers.num_h == 2:
                return GameCheckers.almostKing(board)
            return GameCheckers.edgePosition(board)
        else:
            # algo = minimax
            # algo = expectimax
            if algo == 'minimax':
                if GameCheckers.num_h == 1:
                    return GameCheckers.best_heuristics(board)
                if GameCheckers.num_h == 2:
                    return GameCheckers.almostKing(board)
                return GameCheckers.edgePosition(board)
            if algo == 'expectimax':
                if GameCheckers.num_h_second == 1:
                    return GameCheckers.best_heuristics(board)
                if GameCheckers.num_h_second == 2:
                    return GameCheckers.almostKing(board)
                return GameCheckers.edgePosition(board)


    """Ovaa hevristika 'almostKing' gi potiknuva obicnite figuri da stanat kralevi"""
    @staticmethod
    def almostKing(board):
        result = 0
        def isTheSame(cell, string, i, j):
            x = clean_cell_value(cell)
            return x == (string + to_superscript(i) + to_superscript(j))

        for i in range(8):
            for j in range(8):
                if isTheSame(board[i][j], "comp", i, j):
                    result -= (7 - i)  # Поголема вредност за фигури поблиску до крајната линија
                elif isTheSame(board[i][j], "#men", i, j):
                    result += i  # Противничките фигури добиваат вредност за близина до крајната линија

        #poveke poeni ako protivnickite figuri se vo pogolem broj
        #pomalku poeni ako figurite na kompjuterot se vo pogolem broj
        mine = 0
        opp = 0

        for i in range(8):
            for j in range(8):
                if isTheSame(board[i][j], "comp", i, j) or board[i][j].startswith(yellow + "k"):
                    mine += 1
                elif isTheSame(board[i][j], "#men", i, j) or board[i][j].startswith(green + "k"):
                    opp += 1

        return result + (mine - opp) * 100

    #Ovaa hevristika gi potiknuva figurite da se dvizat po rabovite
    @staticmethod
    def edgePosition(board):
        result = 0
        def isTheSame(cell, string, i, j):
            x = clean_cell_value(cell)
            return x == (string + to_superscript(i) + to_superscript(j))

        for i in range(8):
            for j in range(8):
                if isTheSame(board[i][j], "comp", i, j) or board[i][j].startswith(yellow + "k"):
                    if i == 0 or j == 0 or i == 7 or j == 7:
                        result -= 5  # Kompjuterskite figuri gubat poeni za stabilnost
                elif isTheSame(board[i][j], "#men", i, j) or board[i][j].startswith(green + "k"):
                    if i == 0 or j == 0 or i == 7 or j == 7:
                        result += 5  # Protivnickite figuri dobivaat poeni za stabilnost

        mine = 0
        opp = 0

        for i in range(8):
            for j in range(8):
                if isTheSame(board[i][j], "comp", i, j) or board[i][j].startswith(yellow + "k"):
                    mine += 1
                elif isTheSame(board[i][j], "#men", i, j) or board[i][j].startswith(green + "k"):
                    opp += 1


        return result + (mine - opp) * 40


    @staticmethod
    def expectimax(board, depth, maximizing_player):
        if depth == 0:
            return GameCheckers.calculate_heuristics(board, 'expectimax')

        current_state = NewGameState(deepcopy(board))

        if maximizing_player:
            max_eval = -math.inf
            for child in current_state.get_children(True):
                ev = GameCheckers.expectimax(child.get_board(), depth - 1, False)
                max_eval = max(max_eval, ev)
            current_state.set_value(max_eval)
            return max_eval
        else:
            children = current_state.get_children(False)
            if not children:
                return GameCheckers.calculate_heuristics(board, 'expectimax')

            total_value = 0
            for child in children:
                ev = GameCheckers.expectimax(child.get_board(), depth - 1, True)
                total_value += ev
            expected_value = total_value / len(children)
            current_state.set_value(expected_value)
            return expected_value


    """
    Vo ovaa implementacija na expectimax algoritamot, nema potreba od verojatnosti.
    Site potezi i ishodi se logicki odredeni
    Nesigurnosta bara verojatnost (pr. frlanje na kocka) --> Vo ovaa igra ne postoi nesigurnost  
    ZATOA JA KORISTIME OVAA IMPLEMENTACIJA NA expectimax algoritmot
    """

if __name__ == '__main__':
    gameCheckers = GameCheckers()
    gameCheckers.startGame()
