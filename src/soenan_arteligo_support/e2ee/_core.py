from __future__ import annotations

from google.protobuf.message import DecodeError
from soenan.arteligo.crypto.v1 import crypto_pb2 as crypto

from ._crypto import E2eeError


class CryptoCore:
    def execute(self, request: crypto.CoreRequest) -> crypto.CoreResponse:
        try:
            from arteligo_e2ee_native import execute_core
            response = crypto.CoreResponse.FromString(execute_core(request.SerializeToString()))
        except (ImportError, OSError, DecodeError, ValueError, RuntimeError):
            raise E2eeError("crypto_unavailable") from None
        result = response.WhichOneof("result")
        if result == "error":
            raise E2eeError(response.error)
        expected = {"open": "opened", "prepare": "prepared", "enroll": "identity_change", "rotate": "identity_change"}
        if result != expected.get(request.WhichOneof("operation")):
            raise E2eeError("invalid_crypto_response")
        return response

    def execute_utility(self, request: crypto.CoreUtilityRequest) -> crypto.CoreUtilityResponse:
        try:
            from arteligo_e2ee_native import execute_utility
            response = crypto.CoreUtilityResponse.FromString(execute_utility(request.SerializeToString()))
        except (ImportError, OSError, DecodeError, ValueError, RuntimeError):
            raise E2eeError("crypto_unavailable") from None
        result = response.WhichOneof("result")
        if result == "error":
            raise E2eeError(response.error)
        expected = {"seal_stream": "stream_sealed", "open_stream": "stream_opened",
            "seal_local": "local_sealed", "open_local": "local_plaintext",
            "prove": "proof", "random": "random_bytes"}
        if result != expected.get(request.WhichOneof("operation")):
            raise E2eeError("invalid_crypto_response")
        return response
