from __future__ import annotations


class Judgement:
    def __init__(self, something: Lobby) -> None:
        self.something = something

    def i_can_do_it_in_state_a_only(self):
        self.something._state = StateB(self.something)


class StateB:
    def __init__(self, something: Lobby) -> None:
        self.something = something

    def i_can_do_it_in_state_b_only(self):
        self.something.state = Judgement(self.something)


class Lobby:
    def __init__(self) -> None:
        self._state = Judgement(self)

    def delegate(self) -> None:
        self._state = Judgement(self)
        self._state.i_can_do_it_in_state_a_only()

        # if self._state == "judgement":
        #     self._i_can_do_it_in_state_a_only()

        if isinstance(self._state, Judgement):
            self._state.i_can_do_it_in_state_a_only()

        # if self._state == "StateB":
        #   self.i_can_do_it_in_state_b_only()

        if isinstance(self._state, StateB):
            self._state.i_can_do_it_in_state_b_only()

    def i_can_do_it_in_state_a_only(self):
        pass

    def i_can_do_it_in_state_b_only(self):
        pass


def main() -> None:
    pass


if __name__ == '__main__':
    main()
