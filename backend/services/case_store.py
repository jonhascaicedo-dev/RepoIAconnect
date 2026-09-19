from threading import Lock
from backend.domain.clinical_case import ClinicalCase

class ClinicalCaseStore:
    def __init__(self):
        self._cases = {}
        self._lock = Lock()

    def save(self, case: ClinicalCase):
        with self._lock:
            self._cases[case.id] = case
        return case

    def get(self, case_id: str):
        with self._lock:
            return self._cases.get(case_id)

STORE = ClinicalCaseStore()
