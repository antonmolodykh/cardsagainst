from lobby import Deck, PunchlineCard, SetupCard


class CardsDAO:
    def get_setups(self, deck_id: str) -> Deck[SetupCard]:
        return setups_deck

    def get_punchlines(self, deck_id: str) -> Deck[PunchlineCard]:
        return punchlines_deck


cards_dao = CardsDAO()

setups_deck = Deck(
    cards=[
        SetupCard(
            uuid="1",
            text="Это я почему злой был? А потому что у меня _______ не было!",
            case="gen",
            starts_from_punchline=False,
        ),
        SetupCard(
            uuid="2",
            text="50% всех браков заканчиваются _______.",
            case="inst",
            starts_with_punchline=False,
        ),
        SetupCard(
            uuid="3",
            text="_______ — лучшее средство от запора.",
            case="nom",
            starts_with_punchline=True,
        ),
        SetupCard(
            uuid="4",
            text="Я напиваюсь, чтобы не помнить о _______",
            case="prep",
            starts_with_punchline=False,
        ),
        SetupCard(
            uuid="5",
            text="Я видел своего отца в слезах всего дважды: после смерти мамы и после _______",
            text="gen",
            starts_with_punchline=False,
        ),
        SetupCard(
            uuid="6",
            text="Зацените! я называю это движение «_______»",
            text="nom",
            starts_with_punchline=False,
        ),
    ]
)

punchlines_deck = Deck(
    cards=[
        PunchlineCard(
            uuid="1",
            text={
                "nom": "говно",
                "gen": "говна",
                "dat": "говну",
                "acc": "говно",
                "inst": "говном",
                "pre": "говне",
            },
        ),
        PunchlineCard(
            uuid="2",
            text={
                "nom": "Гитлер",
                "gen": "Гитлера",
                "dat": "Гитлеру",
                "acc": "Гитлера",
                "inst": "Гитлером",
                "prep": "Гитлере",
            },
        ),
        PunchlineCard(
            uuid="3",
            text={
                "nom": "президент Татарстана",
                "gen": "президента Татарстана",
                "dat": "президену Татарстана",
                "acc": "президента Татарстана",
                "inst": "президентом Татарстана",
                "prep": "президенте Татарстана",
            },
        ),
        PunchlineCard(
            uuid="4",
            text={
                "nom": "мои яйца на твоем лице",
                "gen": "моих яиц на твоем лице",
                "dat": "моим яйцам на твоем лице",
                "acc": "мои яйца на твоем лице",
                "inst": "моими яйцами на твоем лице",
                "prep": "моих яйцах на твоем лице",
            },
        ),
        PunchlineCard(
            uuid="5",
            text={
                "nom": "евреи",
                "gen": "евреев",
                "dat": "евреям",
                "acc": "евреев",
                "inst": "евреями",
                "prep": "евреях",
            },
        ),
        PunchlineCard(
            uuid="6",
            text={
                "nom": "секс с животными",
                "gen": "секса с животными",
                "dat": "сексу с животными",
                "acc": "секс с животными",
                "inst": "сексом с животными",
                "prep": "сексе с животными",
            },
        ),
        PunchlineCard(
            uuid="7",
            text={
                "nom": "распад Югославии",
                "gen": "распада Югославии",
                "dat": "распаду Бгославии",
                "acc": "распад Югославии",
                "inst": "распадом Югославии",
                "prep": "распаде Югославии",
            },
        ),
        PunchlineCard(
            uuid="8",
            text={
                "nom": "настаящая работа с ДМС и соц. пакетом",
                "gen": "настоящей работы с ДМС и соц. пакетом",
                "dat": "настящей работе с ДМС и соц. пакетом",
                "acc": "настоящую работу с ДМС и соц. пакетом",
                "inst": "настоящей работой с ДМС и соц. пакетом",
                "prep": "настоящей работе с ДМС и соц. пакетом",
            },
        ),
        PunchlineCard(
            uuid="9",
            text={
                "nom": "Илон Маск",
                "gen": "Илона Маска",
                "dat": "Илону Маску",
                "acc": "Илона Маска",
                "inst": "Илоном Маском",
                "prep": "Илоне Маске",
            },
        ),
        PunchlineCard(
            uuid="10",
            text={
                "nom": "Библия",
                "gen": "Библии",
                "dat": "Библии",
                "acc": "Библию",
                "inst": "Библией",
                "prep": "Библии",
            },
        ),
        PunchlineCard(
            uuid="11",
            text={
                "nom": "массовые убийства",
                "gen": "массовых убийств",
                "dat": "массовым убийствам",
                "acc": "массовые убийства",
                "inst": "массовыми убийствами",
                "prep": "масовых убйиствах",
            },
        ),
        PunchlineCard(
            uuid="12",
            text={
                "nom": "Путин",
                "gen": "Путина",
                "dat": "Путину",
                "acc": "Путина",
                "inst": "Путиным",
                "prep": "Путине",
            },
        ),
        PunchlineCard(
            uuid="13",
            text={
                "nom": "мужчины",
                "gen": "мужчин",
                "dat": "мужчинам",
                "acc": "мужчин",
                "inst": "мужчинами",
                "prep": "мужчинах",
            },
        ),
        PunchlineCard(
            uuid="14",
            text={
                "nom": "моя бывшая",
                "gen": "моей бывшей",
                "dat": "моей бывшей",
                "acc": "мою бывшую",
                "inst": "моей бывшей",
                "prep": "моей бывшей",
            },
        ),
        PunchlineCard(
            uuid="15",
            text={
                "nom": "алкоголизм",
                "gen": "алкоголизма",
                "dat": "малкоголизму",
                "acc": "алкоголизм",
                "inst": "алкоголизмом",
                "prep": "алкоголизме",
            },
        ),
        PunchlineCard(
            uuid="16",
            text={
                "nom": "роды в тюрьме",
                "gen": "родов в тюрьме",
                "dat": "родам в тюрьме",
                "acc": "роды в тюрьме",
                "inst": "родами в тюрьме",
                "prep": "родах в тюрьме",
            },
        ),
        PunchlineCard(
            uuid="17",
            text={
                "nom": "наука",
                "gen": "науки",
                "dat": "науке",
                "acc": "науку",
                "inst": "наукой",
                "prep": "науке",
            },
        ),
        PunchlineCard(
            uuid="18",
            text={
                "nom": "большой черный член",
                "gen": "большого черного члена",
                "dat": "большому черному члену",
                "acc": "большой черный член",
                "inst": "большим черным членом",
                "prep": "большом черном члене",
            },
        ),
        PunchlineCard(
            uuid="19",
            text={
                "nom": "мертвые родители",
                "gen": "мертвых родителей",
                "dat": "мертвым родителям",
                "acc": "мертвыз родителей",
                "inst": "мертвыми родителями",
                "prep": "о мертвых родителях",
            },
        ),
        PunchlineCard(
            uuid="20",
            text={
                "nom": "инцест",
                "gen": "инцеста",
                "dat": "инцесту",
                "acc": "инцест",
                "inst": "инцестом",
                "prep": "инцесте",
            },
        ),
    ]
)
