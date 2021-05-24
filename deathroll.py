# Gambot/deathroll.py

# IMPORTS
import time

import discord

# CLASSES
class Game:
    """An Instance of a Deathroll game

    - Created when a deathroll game starts between two players.
    - We assume that the conditions for a game have been met.
    """

    def __init__(self, p1_id, p2_id, bet):
        self.p1_id = p1_id # id of the player that started the game
        self.p2_id = p2_id # id of the player that accepted the game
        self.p1_last_activity = time.ctime() # time that the last player was active
        self.p2_last_activity = time.ctime()
        self.bet = bet # Amount of gold that was bet
        self.turn = 'p1'# Whos turn it is to roll next
        self.next_roll = bet # What to roll on next turn

    def __str__(self):
        return f'(deathroll game) {self.p1_id} vs {self.p2_id}, for {self.bet}\n'


class Invite:
    """An invitation from a player with a given bet

    - These invitations are generated when an member sends a deathroll invite 
    to another player.
    - These invites are stored in the deathroll_invites[opponent.id] dict.
    """

    def __init__(self, player: discord.User, bet):
        self.player = player
        self.bet = bet

    def __str__(self):
        # not the prettiest __str__ ever
        return f'Deathroll invite: {self.player.display_name} sent an invite for {self.bet} gold'