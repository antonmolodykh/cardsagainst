from uuid import uuid4

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
            text="Это я почему злой был?\nА потому что у меня\n_________ не было!",
            case="gen",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="50% всех браков\nзаканчиваются _________.",
            case="inst",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="_________ — лучшее средство от запора.",
            case="nom",
            starts_with_punchline=True,
        ),
        SetupCard(
            text="Я напиваюсь, чтобы не помнить о _________",
            case="prep",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Я видел своего отца в слезах всего дважды: после смерти мамы и после _________",
            case="gen",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Зацените! Я назвал(а) это движение «_________»",
            case="nom",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Перед тем как я убью вас, мистер Бонд, я хочу показать вам _________.",
            case="nom",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Фу, серьезно?! Сендвич с ветчиной и _________?!",
            case="inst",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Чувствуете? Что это за запах?!",
            case="nom",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Своими самыми счастливыми воспоминаниями я обязан(а) _________",
            case="dat",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Как говорил мой дед: «Я твой _________.»",
            case="nom",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="В детстве я, конечно, мечтал(а) стать _________",
            case="inst",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="Читали новую книгу Джоан Роулинг? «Гарри Поттер и _________»",
            case="nom",
            starts_with_punchline=True,
        ),
        SetupCard(
            text="Пять стадий горя: отрицание, гнев, торг, _________, принятие.",
            case="nom",
            starts_with_punchline=False,
        ),
        SetupCard(
            text="В 2150 году предизентом России будет _________",
            case="nom",
            starts_with_punchline=False,
        ),
    ]
)

punchlines_deck = Deck(
    cards=[
        PunchlineCard(
            text={
                "nom": "говно",
                "gen": "говна",
                "dat": "говну",
                "acc": "говно",
                "inst": "говном",
                "prep": "говне",
            },
        ),
        PunchlineCard(
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
            text={
                "nom": "Владимир Путин",
                "gen": "Владимира Путина",
                "dat": "Владимиру Путину",
                "acc": "Владимира Путина",
                "inst": "Владимиром Путиным",
                "prep": "Владимире Путине",
            },
        ),
        PunchlineCard(
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
            text={
                "nom": "мертвые родители",
                "gen": "мертвых родителей",
                "dat": "мертвым родителям",
                "acc": "мертвыз родителей",
                "inst": "мертвыми родителями",
                "prep": "мертвых родителях",
            },
        ),
        PunchlineCard(
            text={
                "nom": "инцест",
                "gen": "инцеста",
                "dat": "инцесту",
                "acc": "инцест",
                "inst": "инцестом",
                "prep": "инцесте",
            },
        ),
        PunchlineCard(
            text={
                "nom": "целый день без дрочки",
                "gen": "целого дня без дрочки",
                "dat": "целому дню без дрочки",
                "acc": "целый день без дрочки",
                "inst": "целым днем без дрочки",
                "prep": "целом дне без дрочки",
            },
        ),
        PunchlineCard(
            text={
                "nom": "твоя мать",
                "gen": "твоей матери",
                "dat": "твоей матери",
                "acc": "твою мать",
                "inst": "твоей матерью",
                "prep": "твоей матери",
            },
        ),
        PunchlineCard(
            text={
                "nom": "порно с детьми",
                "gen": "порно с детьми",
                "dat": "порно с детьми",
                "acc": "порно с детьми",
                "inst": "порно с детьми",
                "prep": "порно с детьми",
            },
        ),
        PunchlineCard(
            text={
                "nom": "шарик ушной серы, сперма и кусачки для ногтей",
                "gen": "шарика ушной серы, спермы и кусачек для ногтей",
                "dat": "шарику ушной серы, сперме и кусачкам для ногтей",
                "acc": "шарик ушной серы, сперму и кусачки для ногтей",
                "inst": "шариком ушной серы, спермой и кусачками для ногтей",
                "prep": "шарике ушной серы, сперме и кусачках для ногтей",
            },
        ),
        PunchlineCard(
            text={
                "nom": "дилдо",
                "gen": "дилдо",
                "dat": "дилдо",
                "acc": "дилдо",
                "inst": "дилдо",
                "prep": "дилдо",
            },
        ),
        PunchlineCard(
            text={
                "nom": "принятие ислама",
                "gen": "принятия ислама",
                "dat": "принятию ислама",
                "acc": "принятие ислама",
                "inst": "принятием ислама",
                "prep": "принятии ислама",
            },
        ),
        PunchlineCard(
            text={
                "nom": "уничтожение улик",
                "gen": "уничтожения улик",
                "dat": "уничтожению улик",
                "acc": "уничтожение улик",
                "inst": "уничтожением улик",
                "prep": "уничтожении улик",
            },
        ),
        PunchlineCard(
            text={
                "nom": "соло на саксофоне",
                "gen": "соло на саксофоне",
                "dat": "соло на саксофоне",
                "acc": "соло на саксофоне",
                "inst": "солом на саксофоне",
                "prep": "соло на саксофоне",
            }
        ),
        PunchlineCard(
            text={
                "nom": "наличие члена",
                "gen": "наличия члена",
                "dat": "наличию члена",
                "acc": "наличие члена",
                "inst": "наличием члена",
                "prep": "наличии члена",
            }
        ),
        PunchlineCard(
            text={
                "nom": "плотоядная бактерия",
                "gen": "плотоядной бактерии",
                "dat": "плотоядной бактерии",
                "acc": "плотоядную бактерию",
                "inst": "плотоядной бактерией",
                "prep": "плотоядной бактерии",
            },
        ),
    ]
)
