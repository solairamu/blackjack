import random
from card import Card

class SixDeck():
    
    def __init__(self):
        self.cards = []
        self.build()
        
    def build(self):
        for i in range (0,6):
            for s in ["Spades", "Clubs", "Hearts", "Diamonds"]:
                for v in range(1,14):
                    self.cards.append(Card(v,s))

    def shuffle(self):
        for i in range(1,15):
            for i in range(len(self.cards) -1, 0, -1):
                r = random.randint(0, i)
                self.cards[i], self.cards[r] = self.cards[r], self.cards[i]  

    def draw(self):
        return self.cards.pop()

    def length(self):
        return len(self.cards)
        
    def deckReset(self):
        self.cards = []
        self.build()