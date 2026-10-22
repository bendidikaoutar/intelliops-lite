from src.contrat import Analyse, Evenement


def est_doublon(evt: Evenement, vus: set) -> bool:
    cle = (evt.timestamp, evt.source, evt.component, evt.event_type, evt.message)
    if cle in vus:
        return True
    vus.add(cle)
    return False


def compter_erreurs(evt: Evenement, compteur: dict) -> int:
    raise NotImplementedError


def chercher_procedures(evt: Evenement, base: dict) -> list:
    raise NotImplementedError


def classifier(evt: Evenement, nb_erreurs: int = 0) -> str:
    raise NotImplementedError


def analyser(evt: Evenement, base: dict, nb_erreurs: int = 0) -> Analyse:
    raise NotImplementedError