# code for a game of solitaire
from random import shuffle

class Card:
    def __init__(self, value, suit, color, facing=False):
        self.value = value # 1 - 13
        self.suit = suit # 0 - 3 spades, diamonds, clubs, hearts
        self.color = color # 0 - 1 black, red
        self.facing = facing # False for face down, True for face up

    def __init__(self, number, facing=False): # placement in 52 card set number should be between 0 and 51
        self.value = (number % 13) + 1
        self.suit = number // 13
        self.color = self.suit % 2
        self.facing = facing # False for face down, True for face up

    def __str__(self):
        return f"\033[3{(7,1)[self.color]}m"+ chr(0x1F0A0 + (self.suit * 16) + self.value + (self.value > 11)) + "\033[0m" if self.facing else chr(0x1F0A0)

    def up(self): # set a card to face up
        self.facing = True

    def down(self): # set a card to face down
        self.facing = False


class Solitaire:
    def __init__(self, batch=1):
        self.batch = batch # usually 1 or 3 for standard or 3 card draw

        self.clear()

    def __str__(self):
        out = f"{len(self.stock):02d}{str(self.waste[-1]) if self.waste else ' '}   {' '.join(str(i[-1]) if i else ' ' for i in self.foundation)}"
        max_len = max(map(len, self.tableau))
        for i in range(max_len):
            out = out + '\n' + ' '.join(str(j[i]) if len(j) > i else " " for j in self.tableau)
        return out


    def clear(self): # clear the board and reset to empty
        self.stock = []
        self.waste = []
        self.foundation = [[], [], [], []]
        self.tableau = [[], [], [], [], [], [], []]


    def deal(self):
        # make a deck
        cards = [Card(i, facing=False) for i in range(52)]
        shuffle(cards)

        # deal to tableau
        for i in range(7):
            for j in range(i+1):
                self.tableau[i].append(cards.pop())
            self.tableau[i][-1].up() # flip top card

        self.stock = cards


    def discard(self): # draw to waste
        for i in range(self.batch): # TODO: do this better
            if len(self.stock) == 0:
                break
            self.waste.append(self.stock.pop())
            self.waste[-1].up()

        return len(self.waste) > 0


    def restock(self): # when the stock is empty and you try to discard again
        if len(self.waste) > 0:
            return False

        self.stock = [i.down() for i in self.waste[::-1]]
        self.waste = []

        return len(self.stock) > 0


    def build(self, stack): # move a card from the given stack to its proper foundation
        # stack 0 - 6 for tableau stack 7 for waste
        if stack < 0 or stack > 7:
            return False

        if stack == 7: # draw from waste
            if len(self.waste) == 0:
                return False

            if len(self.foundation[self.waste[-1].suit]) == self.waste[-1].value - 1:
                self.foundation[self.waste[-1].suit].append(self.waste.pop())
                return True

            return False

        # draw from tableau
        if len(self.tableau[stack]) == 0:
            return False

        if len(self.foundation[self.tableau[stack][-1].suit]) == self.tableau[stack][-1].value - 1:
            self.foundation[self.tableau[stack][-1].suit].append(self.tableau[stack].pop())

            # flip card if needed
            if len(self.tableau[stack]) > 0:
                self.tableau[stack][-1].up()

            return True

        return False


    def play(self, stack, destination):
        # move a card from the foundation (0 - 3) or the waste (4) to a tableau column
        # stack 0 - 3 are foundation, stack 4 is waste
        # destination is 0 - 6 for tableau column

        if stack < 0 or stack > 4 or destination < 0 or destination > 6:
            return False

        if stack == 4:
            # draw from waste
            if len(self.waste) == 0:
                return False

            if len(self.tableau[destination]) == 0 or (self.tableau[destination][-1].value == self.waste[-1].value + 1 and self.tableau[destination][-1].color != self.waste[-1].color):
                self.tableau[destination].append(self.waste.pop())
                return True

            return False

        # draw from foundation
        if len(self.foundation[stack]) == 0:
            return False

        if len(self.tableau[destination]) == 0 or (self.tableau[destination][-1].value == self.foundation[stack][-1].value + 1 and self.tableau[destination][-1].color != self.foundation[stack][-1].color):
            self.tableau[destination].append(self.foundation[stack].pop())
            return True

        return False


    def move(self, stack, destination, depth):
        # stack and destination are 0 - 6 for tableau
        # depth is number of cards to pick up
        # returns True if successful

        if stack < 0 or stack > 6 or destination < 0 or destination > 6 or depth < 1:
            return False

        if depth > len(self.tableau[stack]):
            return False

        if len(self.tableau[destination]) == 0 or (self.tableau[destination][-1].value == self.tableau[stack][-depth].value + 1 and self.tableau[destination][-1].color != self.tableau[stack][-depth].color):
            self.tableau[destination] += self.tableau[stack][-depth:]
            self.tableau[stack] = self.tableau[stack][:-depth]

            # flip card if needed
            if len(self.tableau[stack]) > 0:
                self.tableau[stack][-1].up()

            return True

        return False


    def move_string(self, string):
        if string[0] == "d":
            return self.discard()
        elif string[0] == "r":
            return self.restock()
        elif string[0] == "b":
            return self.build(int(string[1]))
        elif string[0] == "p":
            return self.play(int(string[1]), int(string[2]))
        elif string[0] == "m":
            return self.move(int(string[1]), int(string[2]), int(string[3],16))

        return False


    def won(self):
        return self.foundation[0][-1].value == 13 and self.foundation[1][-1].value == 13 and self.foundation[2][-1].value == 13 and self.foundation[3][-1].value == 13


if __name__ == "__main__":
    # cards = [Card(i, facing=True) for i in range(52)]
    # print(*map(str, cards),)

    game = Solitaire()
    game.deal()

    while True:
        print(game)
        game.move_string(input(">"))

