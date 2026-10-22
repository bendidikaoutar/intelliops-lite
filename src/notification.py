from src.contrat import Analyse, Evenement, Notification


def choisir_canal(niveau: str) -> str:
    canaux = {
        "CRITICAL": "TEAMS",
        "HIGH": "SLACK",
        "MEDIUM": "EMAIL",
        "LOW": "DASHBOARD"
    }

    if niveau not in canaux:
        raise ValueError("Niveau invalide")

    return canaux[niveau]


def rediger(evt: Evenement, analyse: Analyse) -> str:
    return (
        f"[{analyse.level}] Composant : {evt.component}\n"
        f"Evenement : {evt.message}\n"
        f"Explication : {analyse.explanation}\n"
        f"Action proposee : {analyse.action}\n"
        f"Sources : {', '.join(analyse.sources)}"
    )


def notifier(evt: Evenement, analyse: Analyse, historique: list) -> Notification:
    raise NotImplementedError


def valider_action(analyse: Analyse, reponse: str) -> bool:
    raise NotImplementedError


def tracer_decision(analyse: Analyse, approuve: bool, acteur: str,
                    journal: list, horodatage: str) -> dict:
    raise NotImplementedError