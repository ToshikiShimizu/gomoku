import numpy as np
class Game:
    def __init__(self,p1,p2):
        self.p1 = p1
        self.p1.color = 1
        self.p2 = p2
        self.p2.color = -1

    def ready(self):
        self.board = Board()

    def switch_p(self):
        temp = self.sub_p
        self.sub_p = self.main_p
        self.main_p = temp
    def play(self):
        self.main_p = p1
        self.sub_p = p2
        for i in range(N*N):
            position = self.main_p.move(self.board.state)
            if self.is_legal_move(position) == False:
                self.main_p.lose()
                self.sub_p.win()
                break
            self.move(position,self.main_p.color)
            self.judge(self.board.state,position)
            #if i % 10 == 0:
            #self.board.print_state()
            self.switch_p()
        else:
            self.main_p.draw()
            self.sub_p.draw()
    def move(self,position,color):
        self.board.state[position[0], position[1]] = color

    def is_legal_move(self,position):
        return self.board.state[position[0], position[1]] == 0
    def judge(self,state,position):
        #print (state[position[0],position[1]])
        big_board = np.zeros((N+2*(K-1),N+2*(K-1)))
        #print (position)
        big_position = np.array(position) + K - 1
        print (big_position)
        big_board[K-1:N+K-1,K-1:N+K-1] = state

        ls = [[0,1],[0,-1],[1,0],[1,1]]
        for a,b in ls:
            print (a,b)

class Board:
    def __init__(self):
        self.state = np.zeros((N,N))
    def print_state(self):
        MAX_DIGITS = 2#盤のサイズの桁数がこの数を超えると表示がずれる
        print(" " * (MAX_DIGITS + 2) + " ".join([chr(ord('a') + i) for i in range(N)]))
        for i,line in enumerate(self.state):
            ls = list(map(self.convert, line))
            space = " " * (MAX_DIGITS-len(str(i+1)))#行番号の桁数による列表示ずれの補正
            print (i+1,space," ".join(ls))

    def convert(self,stone):
        if stone == 0:
            return "-"
        elif stone == 1:
            return "o"
        else:
            return "x"



class Player:
    def __init__(self, name):
        self.name = name
        self.n_win = 0
        self.n_lose = 0
        self.n_draw = 0
    def move(self,state):
        pass
        """
        moveは座標をリストで表現し、返却する
        """
    def win(self):
        self.n_win += 1
        print (self.name,"win",self.n_win)
    def lose(self):
        self.n_lose += 1
    def draw(self):
        self.n_draw += 1
class RandomPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,state):
        position = np.random.randint(0,state.shape[0],(2))
        return position#座標のリストを返却

class LegalPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,state):
        prob = (state==0).astype(np.int)
        s = prob.sum()
        prob = (prob / s).flatten()
        idx = np.random.choice(len(prob),1,p=prob)[0]
        position = [idx//N, idx%N]
        return position#座標のリストを返却

class HumanPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,state):
        #position = np.random.randint(0,N,(2))
        idx2 = ord(input("col(alphabet):"))-97
        idx1 = int(input("row(number):"))-1
        position = [idx1,idx2]
        return position#座標のリストを返却
    def win(self):
        print (self.name,"win")
    def lose(self):
        print (self.name,"lose")
    def draw(self):
        print (self.name,"draw")
if __name__=="__main__":
    N = 19
    K = 5
    p1 = LegalPlayer("l1")
    p2 = LegalPlayer("l2")
    #p2 = RandomPlayer("r2")
    #p2 = HumanPlayer("h2")
    for i in range(1):
        game = Game(p1,p2)
        game.ready()
        game.play()
