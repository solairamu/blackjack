class Dealer:
    
    def __init__(self):
        self.hand = []
        self.splitHolding = []
            
    def draw(self,deck):
        card = deck.draw()
        self.hand.append(card)       
        
    def getSuit(self):
        c = self.hand[len(self.hand)-1]
        return c.suit
    
    def getVal(self):
        c = self.hand[len(self.hand)-1]
        return c.val

    def holdingDraw(self):
        if not self.splitHolding:
            return
        self.hand.append(self.splitHolding.pop(0))

    def reset(self):
        self.hand = [] 

    def splitHoldReset(self):
        self.splitHolding.clear() 

    def splitToHolding(self):
        self.splitHolding.append(self.hand.pop(0))

    def score(self):
        aceHand = False
        sum = 0
        count = 0
        for c in self.hand:
            if (c.val ==1):
                aceCard = self.hand.pop(count)
                aceHand = True 
            count+=1
        if(aceHand == False):
            for c in self.hand: 
                if(c.val == 1):
                    sum += 11
                elif(c.val >= 10):
                    sum += 10
                else:
                    sum += c.val
        else:
            self.hand.append(aceCard)
            for c in self.hand: 
             if(c.val == 1):
                 if(sum < 11):
                     sum += 11
                 else:
                     sum+=1                                     
             elif(c.val >= 10):
                 sum += 10
             else:
                 sum += c.val
        return sum     