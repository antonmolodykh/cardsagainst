class Judgement:
    def __init__(self, lobby):
        self.lobby = lobby

    def lead_choose_punchline_card(self, card) -> None:
        card_on_table = self.lobby.get_card_from_table(card=card)
        card_on_table.player.score += 1

        for pl in self.lobby.all_players:
            pl.observer.turn_ended(card_on_table.player, card)