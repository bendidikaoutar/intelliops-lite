
import re

from src.contrat import Evenement


def masquer_secrets(texte: str) -> str:
    texte = re.sub(
        r'\b(password|passwd|token|secret|api_key|apikey)(\s*[=:]\s*)[^ &;,]+',
        r'\1\2[SECRET]',
        texte,
        flags=re.IGNORECASE
    )
    return re.sub(
        r'\b(Bearer\s+)[^\s&;,]+',
        r'\1[SECRET]',
        texte,
        flags=re.IGNORECASE
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
    for cle in ("cve", "package", "severity", "date"):
        if cle not in rapport:
            raise ValueError("Cle manquante : " + cle)

    severity = str(rapport["severity"]).upper()

    if severity not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        severity = "LOW"

    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=rapport["date"],
        source="TRIVY",
        component=rapport["package"],
        environment=environment,
        event_type="VULNERABILITY",
        severity=severity,
        message=f"Vulnerabilite {rapport['cve']} dans {rapport['package']}"
    )


def normaliser_pipeline(rapport: dict, numero: int,
                        environment: str = "production") -> Evenement:
    for cle in ("job", "status", "date"):
        if cle not in rapport:
            raise ValueError("Cle manquante : " + cle)

    status = str(rapport["status"])

    if status.lower() == "failed":
        event_type = "PIPELINE_FAILURE"
        severity = "HIGH"
    else:
        event_type = "PIPELINE_OK"
        severity = "LOW"

    return Evenement(
        id=f"EVT-{numero:05d}",
        timestamp=rapport["date"],
        source="CI",
        component=rapport["job"],
        environment=environment,
        event_type=event_type,
        severity=severity,
        message=f"Pipeline {rapport['job']} : {status}"
    )
