# Сards Against

This is our online game inspired by «[Cards Against Humanity](https://cardsagainsthumanity.com)»

You can play it on https://cardsagainst.fun

## About

During development, we adhered to the principles of TDD and DDD.
The main engineering idea was to separate domain logic from infrastructure code and integrations.

As a result, we have a convenient object-oriented API that is easy to test.

```python
@pytest.mark.usefixtures("yura_connected", "game_started")
async def test_refresh_hand(yura: Player) -> None:
    yura.score = 1
    prev_hand = yura.hand.copy()
    yura.refresh_hand()
    assert prev_hand != yura.hand
    assert yura.score == 0
```

The domain entities is a comprehensive mental model of the game.

The integration layer provides an asynchronous API over WebSockets using FastAPI.
Currently, all state is kept in memory.

At this point, we do not test integration because it is unnecessary: running the game with the current backend
is sufficient to reveal integration bugs, and all game logic is covered by tests.
