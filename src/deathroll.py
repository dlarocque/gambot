import time
import random
import discord

expire_time = 300.0  # seconds


class DeathrollGame:
    """An Instance of a deathroll game"""

    def __init__(
            self,
            player1: discord.User,
            player2: discord.User,
            bet,
            channel):
        self.player1 = player1  # id of the player that send the invite to the DeathrollGame
        self.player2 = player2  # id of the player that accepted the DeathrollGame
        self.p1_last_activity = time.mktime(
            time.localtime())
        self.p2_last_activity = time.mktime(time.localtime())
        self.bet = bet
        self.channel = channel
        self.turn = player1
        self.next_roll = bet

    def __str__(self):
        return f'(deathroll DeathrollGame) {self.player1.display_name} vs {self.player2.display_name}, for {self.bet} gold\n'

    def roll(self):
        """Plays the next players turn in the DeathrollGame

        Returns:
            roll (int): The value of the players roll
        """
        roll = random.randint(0, self.next_roll)

        # Adjust fields for the next roll
        if self.turn is self.player1:
            self.turn = self.player2
            self.next_roll = roll
            self.p1_last_activity = time.mktime(time.localtime())
        elif self.turn is self.player2:
            self.turn = self.player1
            self.next_roll = roll
            self.p2_last_activity = time.mktime(time.localtime())

        return roll

    def get_opponent(self, player: discord.User):
        """Returns the player that the player is playing against

        Throws a ValueError if player is not in this game.

        Keyword Arguments:
            player (discord.User): One of the two players

        Returns:
            self.player1 (discord.User): player2's opponent
            self.player2 (discord.User): player1's opponent
        """
        if player.id == self.player1.id:
            return self.player2
        elif player.id == self.player2.id:
            return self.player1
        else:
            raise ValueError(
                f'Player {player} is not part of this DeathrollGame.')

    def t_since_roll(self, player: discord.User):
        """Time since the players last roll

        Keyword Arguments:
            player (discord.User): The player who's time since last activity is returned

        Returns:
            t_since_roll: time since the players last roll
        """
        if player is self.player1:
            t_since_roll = time.mktime(time.localtime) - self.p1_last_activity
        elif player is self.player2:
            t_since_roll = time.mktime(time.localtime) - self.p2_last_activity
        else:
            raise ValueError(
                f'Player {player} is not part of this DeathrollGame.')

        return t_since_roll


class DeathrollInvite:
    """An invitation to a deathroll game from a player with a given bet"""

    def __init__(self, player: discord.User, bet, channel):
        self.player = player
        self.bet = bet
        self.channel = channel
        self.DeathrollInvite_time = time.mktime(time.localtime())

    def is_expired(self):
        """Returns whether or not an invite has expired

        An invitation has expired if 'expire_time' seconds have passed
        since the invitation was sent.

        Returns:
            True: invitation has expired
            False: invitation has not expired
        """
        global expire_time

        time_since_inv = time.mktime(
            time.localtime()) - self.DeathrollInvite_time
        return time_since_inv > expire_time

    def __str__(self):
        if self.is_expired():
            output = f'[EXPIRED] Deathroll DeathrollInvite: {self.player.display_name} sent an DeathrollInvite for {self.bet} gold.'
        else:
            output = f'Deathroll DeathrollInvite: {self.player.display_name} sent an DeathrollInvite for {self.bet} gold.'
        return output
