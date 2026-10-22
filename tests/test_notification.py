
import unittest

from src.contrat import Analyse, Evenement
from src.notification import (
    choisir_canal,
    rediger,
    notifier,
    valider_action,
    tracer_decision,
)


def exemple(sensible=True, niveau="CRITICAL"):
    e = Evenement(
        "EVT-00125", "2026-10-05T10:02:11Z",
        "DOCKER", "backend", "production",
        "LOG", "HIGH", "OOMKilled restarts=14"
    )
    a = Analyse(
        "EVT-00125", niveau, "Manque de memoire",
        "Redemarrer le service backend",
        sensible, ["DOCKER"]
    )
    return e, a


class TestNotification(unittest.TestCase):

    def test_canaux(self):
        self.assertEqual(choisir_canal("CRITICAL"), "TEAMS")
        self.assertEqual(choisir_canal("HIGH"), "SLACK")
        self.assertEqual(choisir_canal("MEDIUM"), "EMAIL")
        self.assertEqual(choisir_canal("LOW"), "DASHBOARD")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_rediger(self):
        e, a = exemple()
        texte = rediger(e, a)
        self.assertEqual(len(texte.split("\n")), 5)
        self.assertIn("[CRITICAL] Composant : backend", texte)
        self.assertIn("Sources : DOCKER", texte)

    def test_notifier(self):
        e, a = exemple()
        historique = []
        notification = notifier(e, a, historique)

        self.assertEqual(notification.channel, "TEAMS")
        self.assertEqual(notification.recipient, "equipe-ops")
        self.assertEqual(len(historique), 1)
        self.assertEqual(e.status, "NOTIFIED")

    def test_validation(self):
        _, a = exemple()
        self.assertTrue(valider_action(a, " OUI "))
        self.assertFalse(valider_action(a, "n"))

    def test_action_non_sensible(self):
        _, a = exemple(sensible=False)
        self.assertTrue(valider_action(a, "n"))

    def test_tracer_decision(self):
        _, a = exemple()
        journal = []
        decision = tracer_decision(
            a, True, "ops-oncall",
            journal, "2026-10-05T10:10:00Z"
        )

        self.assertEqual(decision["event_id"], "EVT-00125")
        self.assertTrue(decision["approved"])
        self.assertEqual(decision["actor"], "ops-oncall")
        self.assertEqual(len(journal), 1)


if __name__ == "__main__":
    unittest.main()
