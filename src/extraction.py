from src.contrat import Evenement


def masquer_secrets(texte: str) -> str:
    import re

    return re.sub(
        r'(?i)\b(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)[^ &;,]+',
        r'\1\2[SECRET]',
        texte
    )


def normaliser_log(ligne: str, numero: int, source: str = "DOCKER",
                   environment: str = "production") -> Evenement:
    champs = ligne.split(maxsplit=4)

    if len(champs) < 5:
        raise ValueError("Ligne de log invalide")

    date, heure, niveau, composant, message = champs

    niveau = niveau.upper()

    if niveau in ("CRITICAL", "FATAL"):
        severity = "CRITICAL"
    elif niveau == "ERROR":
        severity = "HIGH"
    elif niveau in ("WARN", "WARNING"):
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=f"{date}T{heure}Z",
        source=source,
        component=composant,
        environment=environment,
        event_type="LOG",
        severity=severity,
        message=masquer_secrets(message)
    )

def normaliser_scan(rapport: dict, numero: int,
                    environment: str = "production") -> Evenement:
    raise NotImplementedError


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    raise NotImplementedError