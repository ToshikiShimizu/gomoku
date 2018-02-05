import numpy as np
from scipy import signal
import chainer
from chainer import functions as F
from chainer import links as L
from chainer import Variable
from chainer import optimizers
from chainer import cuda
from policy_net import CNN
import copy
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
        self.main_p = self.p1
        self.sub_p = self.p2
        for i in range(N*N):
            position = self.main_p.move(self.board)
            if self.is_legal_move(position) == False:
                self.main_p.lose()
                self.sub_p.win()
                break
            self.move(position,self.main_p.color)
            if self.judge(self.board.state,position):
                self.main_p.win()
                self.sub_p.lose()
                #self.board.print_state()
                break
            self.switch_p()
            #self.board.print_state()
        else:
            self.main_p.draw()
            self.sub_p.draw()
    def move(self,position,color):
        self.board.state[position[0], position[1]] = color

    def is_legal_move(self,position):
        return self.board.state[position[0], position[1]] == 0
    def judge(self,state,position):
        filters = np.ones((1,K)),np.ones((K,1)),np.identity(K),np.identity(K)[::-1]
        for fil in filters:
            temp = signal.convolve2d(state,fil,mode="valid")#判定に必要な分だけ(valid)取得。その方が速い
            if(abs(temp).max()==K):

                return True
        return False


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
        self.clear_result()
    def clear_result(self):
        self.n_win = 0
        self.n_lose = 0
        self.n_draw = 0
    def move(self,board):
        pass
        """
        moveは座標をリストで表現し、返却する
        """
    def end_process(self,result):
        pass
    def win(self):
        self.n_win += 1
        self.end_process(1)
    def lose(self):
        self.n_lose += 1
        self.end_process(-1)
    def draw(self):
        self.n_draw += 1
        self.end_process(0)

    def show_result(self):
        print (self.name,"WIN:",self.n_win)
        print (self.name,"DRAW:",self.n_draw)
        print (self.name,"LOSE:",self.n_lose)
        print ()

class RandomPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,board):
        position = np.random.randint(0,board.state.shape[0],(2))
        return position#座標のリストを返却

class LegalPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,board):
        state = board.state
        prob = (state==0).astype(np.int)
        s = prob.sum()
        prob = (prob / s).flatten()
        idx = np.random.choice(len(prob),1,p=prob)[0]
        position = [idx//N, idx%N]
        return position#座標のリストを返却

class UpperLeftPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,board):
        for i in range(board.state.shape[0]):
            for j in range(board.state.shape[0]):
                if board.state[i,j] == 0:
                    position = [i,j]
                    return position#座標のリストを返却

class PolicyGradientPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
        n_channel = 2
        self.train_mode = True
        self.policy_net = CNN(n_channel, N , K)
        self.optimizer = optimizers.Adam(alpha=1e-5)#best
        self.optimizer.setup(self.policy_net)
        self.optimizer.add_hook(chainer.optimizer.WeightDecay(1e-4))
        self.history_idx = []
        self.history_x = []
        self.history_mask = []
        self.history_result = []

    def move(self,board):
        state = board.state

        x = np.array([state == self.color,state == -self.color]).astype(np.float32)#自分の石を0チャネル目、相手の石を1チャネル目
        #mask = (state==0).astype(np.float32).reshape(1,-1)#合法手マスク
        mask = (state != 0)*(1e+8)
        prob = self.policy_net.predict(x, mask).data.flatten()
        #print (prob)
        #print (prob.sum())
        idx = np.random.choice(len(prob),1,p=prob)[0]
        position = [idx//N, idx%N]
        self.history_x.append(x)
        self.history_mask.append(mask)
        self.history_idx.append(idx)

        return position#座標のリストを返却
    def end_process(self,result):#パラメータ更新、historyの初期化
        if self.train_mode:
            self.history_result.extend([result for i in range(len(self.history_x))])
            self.update()
            self.history_x = []
            self.history_idx = []
            self.history_mask = []
            self.history_result = []
        else:
            pass

    def update(self):
        self.policy_net.cleargrads()
        x = np.array(self.history_x)
        mask = np.array(self.history_mask)
        result = np.array(self.history_result)
        target = np.array(self.history_idx).astype(np.int32)

        loss = self.policy_net(x, mask, target)
        loss = F.mean(loss*result)
        loss.backward()
        self.optimizer.update()




class HumanPlayer(Player):
    def __init__(self,name):
        super().__init__(name)
    def move(self,board):
        board.print_state()
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

def evaluate(p1,p2):
    d1 = copy.deepcopy(p1)
    d2 = copy.deepcopy(p2)


    d1.train_mode = False
    d2.train_mode = False
    d1.clear_result()
    d2.clear_result()
    for i in range(N_test):
        eval_game = Game(d1,d2)
        eval_game.ready()
        eval_game.play()
    print ("TEST")
    d1.show_result()
    d2.show_result()

if __name__=="__main__":
    N = 19
    K = 5
    N_test = 1000
    eval_freq = 1000
    show_freq = 100
    #p1 = LegalPlayer("l1")
    #p1 = RandomPlayer("r1")
    p1 = PolicyGradientPlayer("p1")
    #p1 = UpperLeftPlayer("p2")
    #p1.train_mode = False

    p2 = PolicyGradientPlayer("p2")
    #p2 = LegalPlayer("l2")
    #p2 = RandomPlayer("r2")
    #p2 = UpperLeftPlayer("p2")
    #p2 = HumanPlayer("h2")
    for i in range(1000000):
        game = Game(p1,p2)
        game.ready()
        game.play()
        if (i+1) % show_freq == 0:
            print ("TRAIN")
            p1.show_result()
            p2.show_result()
        if (i+1) % eval_freq == 0:
            #evaluate(p1,p2)
            #new_p2 = UpperLeftPlayer("l2")
            new_p2 = LegalPlayer("l2")
            evaluate(p1,new_p2)
