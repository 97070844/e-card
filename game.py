import pygame,sys,os,re,random

EMPEROR = "emperor"
CITIZEN = "citizen"
SLAVE = "slave"

assetsfolder = "E:\\Python\\E-Card\\assets"

class Card:
    def __init__(self,name):
        self.name = name        
        self.image = pygame.image.load(os.path.join(assetsfolder,f"{name}.jpg"))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return self.name  
    
    def move(self,dest):
        self.rect.topleft = dest
            
    def setPosition(self,pos):
        self.rect.topleft = pos

    def facedown(self):
        self.image = pygame.image.load(os.path.join(assetsfolder,"facedown.jpg"))
    
    def faceturn(self):
        self.image = pygame.image.load(os.path.join(assetsfolder,f"{self.name}.jpg"))

    def draw(self,screen):
        screen.blit(self.image,self.rect)
        
class Player:
    def __init__(self,id,has_emperor):
        self.id = id
        self.cards = [Card(CITIZEN) for _ in range(4)]
        self.dealtcards = list()
        self.has_emperor = has_emperor

        if self.has_emperor:
            self.cards.append(Card(EMPEROR))
            self.turn = True
        else:
            self.cards.append(Card(SLAVE))
            self.turn = False
        
        if self.id == 2: #player2 is pc that means cards will hide
            for card in self.cards:
                card.facedown()

        self.shuffle()
    
    def __repr__(self):
        return "Player{}".format(self.id)

    def __str__(self):
        return "Player{}".format(self.id)    

    def dealt(self,card):      
        self.dealtcards.append(card)
        dealtcard = self.cards.pop(card)       
        return dealtcard
    
    def reset(self):
        self.cards.extend(self.dealtcards)
        self.dealtcards.clear()
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
  
class GameScreen:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("E Card")
        pygame.display.set_icon(pygame.image.load(os.path.join(assetsfolder,"logo.png")))
        
        #cards positons on screen
        self.WIDTH = 800
        self.HEIGHT = 600
        self.P1_POSITIONS = [(150,460),(250,460),(350,460),(450,460),(550,460)]
        self.P2_POSITIONS = [(150,20),(250,20),(350,20),(450,20),(550,20)]
        self.P1_DEAL_POS = (400,280)
        self.P2_DEAL_POS = (300,200)
        self.CARDWIDTH = 90
        self.CARDHEIGHT = 120
        
        #game variables
        self.number_of_cards = 5
        self.p1_dealtcard = None
        self.p2_dealtcard = None
        self.winner = None
        self.clicked = False
        self.mousepos = None
        self.player1_score = 0
        self.player2_score = 0
        self.time = 0
        self.rounds = 0
        self.dealtflag = False

        #initialize player & cards
        self.player1 = Player(1,has_emperor=True)
        self.player2 = Player(2,has_emperor=False)

        #set game screen and font
        self.screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT))
        self.gamefont = os.path.join(assetsfolder,"BebasNeue.ttf")
        self.gamefont1 = os.path.join(assetsfolder,"AGENCYR.ttf")
        #self.backgound = pygame.image.load(os.path.join(assetsfolder,"bg.jpg")).convert()
        
        #set position for cards to diplay in screen
        self.setCardsPosition(self.P1_POSITIONS,self.player1.cards)
        self.setCardsPosition(self.P2_POSITIONS,self.player2.cards)

    def run(self): 
        time = pygame.time.Clock()    
        playing = True 
        gameover = False

        while playing:
            if not gameover:
                self.current_time = pygame.time.get_ticks()

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        playing = False
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self.clicked = True                       
                        self.mousepos = e.pos

                if not self.winner:
                    if self.player1.turn:
                        #check if player1 have already dealt
                        if self.p1_dealtcard:
                            if self.current_time > self.time + 500:
                                p2chosen = random.randrange(self.number_of_cards)
                                self.player2.cards[p2chosen].move(self.P2_DEAL_POS)
                                self.p2_dealtcard = self.player2.cards[p2chosen]
                                self.time = 0

                        #check if player1 clicked a card
                        if self.clicked:
                            for card in self.player1.cards:
                                if card.rect.collidepoint(self.mousepos):
                                    p1chosen = self.player1.cards.index(card)
                                    card.move(self.P1_DEAL_POS) #card animation
                                    self.p1_dealtcard = self.player1.cards[p1chosen]                        
                                    self.time = pygame.time.get_ticks()
                                
                            self.clicked = False               
                        self.drawWindow()
                                        
                    if self.player2.turn:
                        #player2 deals first
                        #check if player2 have already dealt
                        if not self.p2_dealtcard:
                            if self.current_time > self.time + 2000:
                                chosen = random.randrange(self.number_of_cards)
                                self.player2.cards[chosen].move(self.P2_DEAL_POS)
                                self.p2_dealtcard = self.player2.cards[chosen]
                                self.time = 0
                                            
                        if self.clicked:
                            for card in self.player1.cards:
                                if card.rect.collidepoint(self.mousepos):
                                    p1chosen = self.player1.cards.index(card)
                                    card.move(self.P1_DEAL_POS)
                                    self.p1_dealtcard = self.player1.cards[p1chosen]
                            
                            self.clicked = False                                            
                        self.drawWindow()
                        
                if self.p1_dealtcard and self.p2_dealtcard and not self.winner:
                    self.winner = self.getWinner(self.p1_dealtcard,self.p2_dealtcard)
                    self.time = pygame.time.get_ticks()
                    
                if self.winner:
                    if self.current_time > self.time + 500:
                        if self.current_time < self.time + 1500:
                            self.diplayWinner(self.winner)
                        else:
                            if not self.winner == "No one":
                                self.rounds +=1 
                                
                                if self.dealtflag:
                                    self.number_of_cards = 5
                                    self.player1.cards.extend(self.player1.dealtcards)
                                    self.player2.cards.extend(self.player2.dealtcards)
                                    self.player1.dealtcards.clear()
                                    self.player2.dealtcards.clear()
                                    self.dealtflag = False
                                    
                                if self.winner == self.player1:
                                    self.player1_score += 1

                                if self.winner == self.player2:
                                    self.player2_score += 1

                                if self.rounds == 12:
                                    gameover = True
                                
                                if self.rounds%3 ==0:
                                    self.exchangeCards()
                            else:
                                self.number_of_cards -= 1
                                self.player1.dealtcards.append(self.p1_dealtcard)
                                self.player1.cards.remove(self.p1_dealtcard)
                                self.player2.dealtcards.append(self.p2_dealtcard)
                                self.player2.cards.remove(self.p2_dealtcard)
                                self.dealtflag = True
                                
                            
                            self.winner = None
                            self.p1_dealtcard = None
                            self.p2_dealtcard = None
                            self.changeTurn()
                            self.resetCards()
                
                time.tick(60)
            else:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        playing = False
                    if e.type == pygame.KEYDOWN:
                        gameover = False
                
                self.screen.fill((80,0,0))
                gamefont = pygame.font.Font(self.gamefont, 50)
                self.font_surface = gamefont.render("{} win!".format(self.getFinalWinner()),True,(255,255,255))
                self.font_rect = self.font_surface.get_rect(center=(self.WIDTH//2,self.HEIGHT//2))
                self.font_surface1 = gamefont.render("Press any key to continue!",True,(255,255,255))
                self.font_rect1 = self.font_surface1.get_rect(center=(self.WIDTH//2,self.HEIGHT//4))
                self.screen.blit(self.font_surface,self.font_rect)
                self.screen.blit(self.font_surface1,self.font_rect1)
                pygame.display.update()

        pygame.quit()
        sys.exit()

    def getWinner(self,card1: Card,card2: Card):    
        if card1.name == EMPEROR and card2.name == CITIZEN:
            return self.player1
        if card1.name == EMPEROR and card2.name == SLAVE:
            return self.player2
        if card1.name == CITIZEN and card2.name == CITIZEN:
            return "No one"
        if card1.name == CITIZEN and card2.name == SLAVE:
            return self.player1           
        if card1.name == CITIZEN and card2.name == EMPEROR:
            return self.player2      
        if card1.name == SLAVE and card2.name == CITIZEN:
            return self.player2
        if card1.name == SLAVE and card2.name == EMPEROR:
            return self.player1

    def changeTurn(self):
        self.player1.turn, self.player2.turn = self.player2.turn, self.player1.turn

    def exchangeCards(self):
        self.player1.cards, self.player2.cards = self.player2.cards, self.player1.cards             
        for card in self.player2.cards:
            card.facedown()
        
        for card in self.player1.cards:
            card.faceturn()

    def diplayWinner(self,winner):
        gamefont = pygame.font.Font(self.gamefont, 100)
        self.font_surface = gamefont.render("{} win!".format(winner),True,(255,255,255))
        self.font_rect = self.font_surface.get_rect(center=(self.WIDTH//2,self.HEIGHT//2))
        self.p2_dealtcard.faceturn()
        self.screen.blit(self.p2_dealtcard.image,self.p2_dealtcard.rect)
        self.screen.blit(self.font_surface,self.font_rect)
        pygame.display.update(self.font_rect)
        self.p2_dealtcard.facedown()
   
    def setCardsPosition(self,position,cards):
        for pos,card in zip(position,cards):
            card.setPosition(pos)
    
    def _drawCards(self,cards):
        for card in cards:
            card.draw(self.screen)
    
    def _drawGameStatus(self,rounds,score1,score2):
        gamefont = pygame.font.Font(self.gamefont1, 15)
        info = gamefont.render("[ GAME INFO ]",True,(255,255,255))
        info_rect = info.get_rect(topleft=(30,220))

        rounds = gamefont.render("Rounds:{:6}".format(rounds),True,(255,255,255))
        rounds_rect = rounds.get_rect(topleft=(30,250))
        
        p1score = gamefont.render("Player1:{:6} win".format(score1),True,(255,255,255))
        p1score_rect = p1score.get_rect(topleft=(30,280))
 
        p2score = gamefont.render("Player2:{:5} win".format(score2),True,(255,255,255))
        p2score_rect = p2score.get_rect(topleft=(30,310))
        
        self.screen.blit(info,info_rect)
        self.screen.blit(rounds,rounds_rect)
        self.screen.blit(p1score,p1score_rect)
        self.screen.blit(p2score,p2score_rect)
    
    def drawWindow(self):
        #self.screen.blit(pygame.transform.scale2x(self.backgound),(0,0))
        self.screen.fill((80,0,0))
        self._drawCards(self.player1.cards)
        self._drawCards(self.player2.cards)
        self._drawGameStatus(self.rounds,self.player1_score,self.player2_score)
        pygame.display.update()

    def resetCards(self):
        self.setCardsPosition(self.P1_POSITIONS,self.player1.cards)
        self.setCardsPosition(self.P2_POSITIONS,self.player2.cards)
        self.drawWindow()

    def getFinalWinner(self):
        if self.player1_score > self.player2_score:
            return self.player1
        else:
            return self.player2

if __name__ == "__main__":
    game = GameScreen()
    game.run()