from enum import Enum


class E2EeOwnerBindingProofOperation(str, Enum):
    OWNER_CANDIDATE_OFFER = "owner_candidate_offer"
    OWNER_KEY_REGISTER = "owner_key_register"

    def __str__(self) -> str:
        return str(self.value)
