# Gambot/deathroll.py

# IMPORTS
import time
import random

import discord

# GLOBAL VARIABLES
expire_time = 300.0  # seconds

# CLASSES


class DeathrollGame:
    """An Instance of a Deathroll DeathrollGame

    - Created when a deathroll DeathrollGame starts between two players.
    - We assume that the conditions for a DeathrollGame have been met.
    """

    def __init__(self, player1: discord.User, player2: discord.User, bet, channel):
        self.player1 = player1  # id of the player that started the DeathrollGame
        self.player2 = player2  # id of the player that accepted the DeathrollGame
        self.p1_last_activity = time.mktime(
            time.localtime())  # seconds since last roll
        self.p2_last_activity = time.mktime(time.localtime())
        self.bet = bet  # Amount of gold that was bet
        self.channel = channel # channel that the invitation was sent in
        self.turn = player1  # Whos turn it is to roll next
        self.next_roll = bet  # What to roll on next turn

    def __str__(self):
        return f'(deathroll DeathrollGame) {self.player1.display_name} vs {self.player2.display_name}, for {self.bet} gold\n'

    def roll(self):
        """Plays the next players turn in the DeathrollGame

        Assumes that self.turn is correctly assigned before the method.
        """
        roll = random.randint(0, self.next_roll)

        if(self.turn is self.player1):
            self.turn = self.player2
            self.next_roll = roll
            self.p1_last_activity = time.mktime(time.localtime())
        elif(self.turn is self.player2):
            self.turn = self.player1
            self.next_roll = roll
            self.p2_last_activity = time.mktime(time.localtime())

        return roll

    def get_opponent(self, player: discord.User):
        """Returns the player that the player is playing against"""
        if(player.id == self.player1.id):
            return self.player2
        elif(player.id == self.player2.id):
            return self.player1
        else:
            raise ValueError(f'Player {player} is not part of this DeathrollGame.')

    def t_since_roll(self, player: discord.User):
        """Returns the time(s) since the players last roll"""
        if(player is self.player1):
            t_since_roll = time.mktime(time.localtime) - self.p1_last_activity
        elif(player is self.player2):
            t_since_roll = time.mktime(time.localtime) - self.p2_last_activity
        else:
            raise ValueError(f'Player {player} is not part of this DeathrollGame.')

        return t_since_roll


class DeathrollInvite:
    """An invitation from a player with a given bet

    - These invitations are generated when an member sends a deathroll DeathrollInvite
    to another player.
    - These DeathrollInvites are stored in the deathroll_DeathrollInvites[opponent.id] dict.
    """

    def __init__(self, player: discord.User, bet, channel):
        self.player = player
        self.bet = bet
        self.channel = channel
        self.DeathrollInvite_time = time.mktime(time.localtime())

    def is_expired(self):
        """Returns True or False based on if the DeathrollInvite has expired

        An invitation has expired if 'expire_time' seconds have passed
        since the invitation was sent.
        """
        global expire_time

        time_since_inv = time.mktime(time.localtime()) - self.DeathrollInvite_time
        print(time_since_inv)
        print(expire_time)
        return time_since_inv > expire_time

    def __str__(self):
        if(self.is_expired()):
            output = f'[EXPIRED] Deathroll DeathrollInvite: {self.player.display_name} sent an DeathrollInvite for {self.bet} gold.'
        else:
            output = f'Deathroll DeathrollInvite: {self.player.display_name} sent an DeathrollInvite for {self.bet} gold.'
        return output
