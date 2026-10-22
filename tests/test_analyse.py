import unittest

from src.analyse import (analyser, chercher_procedures, classifier,
                         compter_erreurs, est_doublon)
from src.contrat import PROCEDURES, Evenement


def evt(type_="LOG", severity="HIGH", message="OOMKilled restarts=14",
        composant="backend"):
    return Evenement("EVT-00001", "2026-10-05T10:00:00Z", "DOCKER", composant,
                     "production", type_, severity, message)


class TestAnalyse(unittest.TestCase):
    def test_doublon(self):
        vus = set()
        self.assertFalse(est_doublon(evt(), vus))
        self.assertTrue(est_doublon(evt(), vus))

    def test_pas_doublon_si_seconde_differente(self):
        vus = set()
        e2 = evt()
        e2.timestamp = "2026-10-05T10:00:01Z"
        self.assertFalse(est_doublon(evt(), vus))
        self.assertFalse(est_doublon(e2, vus))

    def test_compter_erreurs_log_grave(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(), compteur), 1)
        self.assertEqual(compter_erreurs(evt(), compteur), 2)
        self.assertEqual(compteur["backend"], 2)

    def test_compter_erreurs_ignore(self):
        compteur = {}
        self.assertEqual(compter_erreurs(evt(severity="LOW"), compteur), 0)
        self.assertEqual(compter_erreurs(evt(type_="VULNERABILITY"), compteur), 0)
        self.assertEqual(compteur, {})

    def test_chercher_procedures(self):
        self.assertEqual(chercher_procedures(evt(), PROCEDURES),
                         [PROCEDURES["oomkilled"]])

    def test_chercher_procedures_vide(self):
        self.assertEqual(chercher_procedures(evt(message="Service demarre"),
                                             PROCEDURES), [])

    def test_classifier_boucle(self):
        e = evt()
        self.assertEqual(classifier(e, 3), "CRITICAL")
        self.assertEqual(classifier(e, 2), "HIGH")

    def test_analyser_vulnerabilite(self):
        e = evt("VULNERABILITY", "CRITICAL",
                "Vulnerabilite CVE-2026-1234 dans lib-xyz", "lib-xyz")
        a = analyser(e, PROCEDURES)
        self.assertEqual(a.action, "Mettre a jour la dependance lib-xyz")
        self.assertFalse(a.sensitive)

    def test_analyser_pipeline(self):
        e = evt("PIPELINE_FAILURE", "HIGH", "Pipeline build : failed", "build")
        a = analyser(e, PROCEDURES)
        self.assertEqual(a.action, "Relancer le pipeline build")
        self.assertFalse(a.sensitive)

    def test_analyser_critique_sensible(self):
        a = analyser(evt(), PROCEDURES, 3)
        self.assertEqual(a.level, "CRITICAL")
        self.assertEqual(a.action, "Redemarrer le service backend")
        self.assertTrue(a.sensitive)
        self.assertEqual(a.explanation, PROCEDURES["oomkilled"])

    def test_analyser_cause_inconnue(self):
        e = evt(severity="LOW", message="Service demarre")
        a = analyser(e, PROCEDURES)
        self.assertEqual(a.action, "Surveiller")
        self.assertEqual(a.explanation, "Cause inconnue : analyse manuelle requise")
        self.assertEqual(a.sources, ["DOCKER"])
        self.assertEqual(e.status, "ANALYZED")


if __name__ == "__main__":
    unittest.main()