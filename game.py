import pygame, sys
from pygame.locals import *
from cards import Deck, Hand

# Constants for screen dimensions and card sizes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_MARGIN = 20

# Color definitions
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (200, 0, 0)

class Button:
    def __init__(self, text, rect, callback):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.font = pygame.font.SysFont(None, 30)
    
    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        txt_surface = self.font.render(self.text, True, BLACK)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, txt_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class BlackjackGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        # Game states: "betting", "playing", "dealer_turn", "round_over"
        self.state = "betting"
        self.bankroll = 1000
        self.current_bet = 0   # Accumulates while betting
        self.base_bet = 0      # The confirmed bet for the round
        self.hands_bets = []   # One bet per hand (if split)

        # Buttons for betting state
        self.bet_buttons = [
            Button("Bet $10", (50, SCREEN_HEIGHT - 100, 100, 50), lambda: self.place_bet(10)),
            Button("Bet $50", (170, SCREEN_HEIGHT - 100, 100, 50), lambda: self.place_bet(50)),
            Button("Bet $100", (290, SCREEN_HEIGHT - 100, 100, 50), lambda: self.place_bet(100)),
            Button("Clear Bet", (410, SCREEN_HEIGHT - 100, 100, 50), self.clear_bet),
            Button("Confirm Bet", (530, SCREEN_HEIGHT - 100, 120, 50), self.confirm_bet)
        ]
        
        # Action buttons for playing state
        self.action_buttons = [
            Button("Hit", (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 80, 100, 50), self.player_hit),
            Button("Stand", (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT - 80, 100, 50), self.player_stand),
            Button("Double Down", (SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT - 80, 130, 50), self.double_down)
        ]
        self.split_button = Button("Split", (SCREEN_WIDTH//2 + 240, SCREEN_HEIGHT - 80, 100, 50), self.split_hand)
        
        # For displaying messages during the round (e.g., bust messages)
        self.message = ""

        # For end-of-round results, store multiple lines to avoid overlap
        self.round_results = []

        # Deck/Hands data
        self.deck = None
        self.dealer_hand = None
        self.player_hands = []
        self.active_hand_index = 0

    def place_bet(self, amount):
        if self.state == "betting":
            if self.current_bet + amount <= self.bankroll:
                self.current_bet += amount

    def clear_bet(self):
        if self.state == "betting":
            self.current_bet = 0

    def confirm_bet(self):
        if self.state == "betting" and self.current_bet > 0:
            self.base_bet = self.current_bet
            self.start_round()

    def start_round(self):
        self.state = "playing"
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer_hand = Hand()
        self.dealer_hand.add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())

        # Create initial player hand
        hand = Hand()
        hand.add_card(self.deck.deal_card())
        hand.add_card(self.deck.deal_card())
        self.player_hands = [hand]
        self.hands_bets = [self.base_bet]
        self.active_hand_index = 0

        self.message = ""
        self.round_results = []  # Clear old round results

    def current_player_hand(self):
        return self.player_hands[self.active_hand_index]

    def player_hit(self):
        if self.state != "playing":
            return
        hand = self.current_player_hand()
        hand.add_card(self.deck.deal_card())
        if hand.value > 21:
            self.message = f"Hand {self.active_hand_index+1} busted!"
            self.next_hand_or_dealer()

    def player_stand(self):
        if self.state == "playing":
            self.next_hand_or_dealer()

    def double_down(self):
        if self.state != "playing":
            return
        hand = self.current_player_hand()
        current_bet = self.hands_bets[self.active_hand_index]
        # Double down allowed only on a two-card hand, and must have enough bankroll
        if len(hand.cards) == 2 and current_bet <= (self.bankroll - current_bet):
            self.hands_bets[self.active_hand_index] *= 2
            hand.add_card(self.deck.deal_card())
            if hand.value > 21:
                self.message = f"Hand {self.active_hand_index+1} busted!"
            self.next_hand_or_dealer()

    def split_hand(self):
        if self.state != "playing":
            return
        hand = self.current_player_hand()
        # Splitting allowed if two cards match in rank and there's enough bankroll for another bet
        if len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank:
            if self.bankroll >= self.base_bet:
                card1 = hand.cards[0]
                card2 = hand.cards[1]
                new_hand1 = Hand()
                new_hand1.add_card(card1)
                new_hand1.add_card(self.deck.deal_card())
                new_hand2 = Hand()
                new_hand2.add_card(card2)
                new_hand2.add_card(self.deck.deal_card())
                self.player_hands[self.active_hand_index] = new_hand1
                self.player_hands.insert(self.active_hand_index+1, new_hand2)
                # Keep the existing bet on the first hand; add a new bet for the second
                self.hands_bets.insert(self.active_hand_index+1, self.base_bet)
                self.message = "Hand split! Playing first split hand."

    def next_hand_or_dealer(self):
        # Move to next hand, or if none left, dealer turn
        if self.active_hand_index < len(self.player_hands) - 1:
            self.active_hand_index += 1
            self.message = f"Playing hand {self.active_hand_index+1}."
        else:
            self.state = "dealer_turn"
            self.dealer_play()

    def dealer_play(self):
        # Dealer hits until reaching at least 17
        while self.dealer_hand.value < 17:
            self.dealer_hand.add_card(self.deck.deal_card())
        self.state = "round_over"
        self.evaluate_round()

    def evaluate_round(self):
        dealer_value = self.dealer_hand.value
        results = []
        for i, hand in enumerate(self.player_hands):
            bet = self.hands_bets[i]
            if hand.value > 21:
                results.append(f"Hand {i+1}: Busted! You lose ${bet}.")
                self.bankroll -= bet
            elif dealer_value > 21:
                results.append(f"Hand {i+1}: Dealer busted! You win ${bet}!")
                self.bankroll += bet
            elif hand.value > dealer_value:
                results.append(f"Hand {i+1}: You win ${bet}!")
                self.bankroll += bet
            elif hand.value < dealer_value:
                results.append(f"Hand {i+1}: You lose ${bet}.")
                self.bankroll -= bet
            else:
                results.append(f"Hand {i+1}: Push.")

        # Store final round results in a list so we can draw them line by line
        self.round_results = results

    def draw_card(self, card, pos, hidden=False):
        rect = pygame.Rect(pos[0], pos[1], CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        if hidden:
            pygame.draw.rect(self.screen, RED, rect.inflate(-10, -10))
        else:
            text = f"{card.rank} {card.suit[0]}"
            txt_surface = self.font.render(text, True, BLACK)
            txt_rect = txt_surface.get_rect(center=rect.center)
            self.screen.blit(txt_surface, txt_rect)

    def draw_hands(self):
        # Draw dealer's hand (first card hidden if still playing/betting)
        dealer_x = CARD_MARGIN
        dealer_y = CARD_MARGIN + 50
        for i, card in enumerate(self.dealer_hand.cards):
            if self.state in ["playing", "betting"] and i == 0:
                self.draw_card(card, (dealer_x, dealer_y), hidden=True)
            else:
                self.draw_card(card, (dealer_x, dealer_y))
            dealer_x += CARD_WIDTH + CARD_MARGIN

        # Draw player's hands
        for index, hand in enumerate(self.player_hands):
            player_x = CARD_MARGIN
            # Stagger each hand vertically if multiple
            player_y = SCREEN_HEIGHT - CARD_HEIGHT - CARD_MARGIN - 150 - (index * (CARD_HEIGHT + 20))
            for card in hand.cards:
                self.draw_card(card, (player_x, player_y))
                player_x += CARD_WIDTH + CARD_MARGIN

            # Display hand value and bet above each hand
            hand_text = f"Hand {index+1}: {hand.value} | Bet: ${self.hands_bets[index]}"
            txt_surface = self.font.render(hand_text, True, WHITE)
            self.screen.blit(txt_surface, (CARD_MARGIN, player_y - 30))

    def draw_text(self, text, pos):
        txt_surface = self.font.render(text, True, WHITE)
        self.screen.blit(txt_surface, pos)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.state == "betting":
                        for button in self.bet_buttons:
                            if button.is_clicked(pos):
                                button.callback()
                    elif self.state == "playing":
                        for button in self.action_buttons:
                            if button.is_clicked(pos):
                                button.callback()
                        # Draw Split button only if eligible
                        current_hand = self.current_player_hand()
                        if (len(current_hand.cards) == 2 and 
                            current_hand.cards[0].rank == current_hand.cards[1].rank):
                            if self.split_button.is_clicked(pos):
                                self.split_button.callback()
                    elif self.state == "round_over":
                        # Click anywhere to go back to betting
                        self.state = "betting"
                        self.current_bet = 0
                        self.message = ""

            self.screen.fill(GREEN)

            if self.state == "betting":
                # Betting interface
                self.draw_text(f"Bankroll: ${self.bankroll}", (CARD_MARGIN, 20))
                self.draw_text(f"Current Bet: ${self.current_bet}", (CARD_MARGIN, 60))
                for button in self.bet_buttons:
                    button.draw(self.screen)
                self.draw_text("Place your bet and click Confirm Bet", (CARD_MARGIN, SCREEN_HEIGHT - 140))

            else:
                # Draw dealer and player hands
                if self.dealer_hand:
                    self.draw_hands()

                if self.state == "playing":
                    # Action buttons
                    for button in self.action_buttons:
                        button.draw(self.screen)
                    # Split button if eligible
                    current_hand = self.current_player_hand()
                    if len(current_hand.cards) == 2 and current_hand.cards[0].rank == current_hand.cards[1].rank:
                        self.split_button.draw(self.screen)

                    self.draw_text(f"Bankroll: ${self.bankroll}", (SCREEN_WIDTH - 220, 20))
                    self.draw_text(f"Base Bet: ${self.base_bet}", (SCREEN_WIDTH - 220, 60))
                    self.draw_text(f"Playing Hand {self.active_hand_index+1}", 
                                   (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 140))
                    # Mid-round message (e.g. "Hand busted!")
                    if self.message:
                        self.draw_text(self.message, (CARD_MARGIN, SCREEN_HEIGHT//2))

                elif self.state == "dealer_turn":
                    self.draw_text("Dealer's turn...", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))

                elif self.state == "round_over":
                    # Show final results, each on its own line
                    self.draw_text(f"Bankroll: ${self.bankroll}", (SCREEN_WIDTH - 220, 20))
                    
                    # Draw each result line with some spacing
                    message_y = SCREEN_HEIGHT // 2 - (len(self.round_results) * 20) // 2
                    for i, line in enumerate(self.round_results):
                        self.draw_text(line, (CARD_MARGIN, message_y + i * 30))

                    # Instruction to continue
                    self.draw_text("Click anywhere to continue", 
                                   (CARD_MARGIN, message_y + len(self.round_results)*30 + 40))

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()
