import numpy as np
class Game:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def ready(self):
        board = Board()
        board.print_state()

    def switch_p(self):
        temp = self.sub_p
        self.sub_p = self.main_p
        self.main_p = temp
    def play(self):
        self.main_p = p1
        self.sub_p = p2
        for i in range(N*N):
            position = self.main_p.move()
            print (position)
            self.switch_p()

class Board:
    def __init__(self):
        self.state = np.zeros((N,N))
    def print_state(self):
        MAX_DIGITS = 2#盤のサイズの桁数がこの数を超えると表示がずれる
        print(" " * (MAX_DIGITS + 2) + " ".join([chr(ord('a') + i) for i in range(N)]))
        for i,line in enumerate(self.state):
            ls = list(map(self.convert, line))
            space = " " * (MAX_DIGITS-len(str(i)))#行番号の桁数による列表示ずれの補正
            print (i,space," ".join(ls))

    def convert(self,stone):
        if stone == 0:
            return "-"
        elif stone == 1:
            return "o"
        else:
            return "x"



class Player:
    def __init__(self):
        pass
    def move(self):
        pass
        """
        moveは座標をリストで表現し、返却する
        """

class RandomPlayer(Player):
    def __init__(self):
        super().__init__()
    def move(self):
        position = np.random.randint(0,N,(2))
        return position#座標のリストを返却


if __name__=="__main__":
    N = 19
    p1 = RandomPlayer()
    p2 = RandomPlayer()
    game = Game(p1,p2)
    game.ready()
    game.play()
