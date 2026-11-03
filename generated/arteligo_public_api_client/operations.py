from .types import File
from .api.default import approve_crypto_invitation as _endpoint_1

def _call_1(client, body=None, **parameters):
    parameters['body'] = _endpoint_1.CryptoProtoMessage.from_dict(body)
    return _endpoint_1.sync_detailed(client=client, **parameters)
from .api.default import attest_crypto as _endpoint_2

def _call_2(client, body=None, **parameters):
    parameters['body'] = _endpoint_2.CryptoProtoMessage.from_dict(body)
    return _endpoint_2.sync_detailed(client=client, **parameters)
from .api.default import commit_crypto as _endpoint_3

def _call_3(client, body=None, **parameters):
    parameters['body'] = _endpoint_3.CryptoProtoMessage.from_dict(body)
    return _endpoint_3.sync_detailed(client=client, **parameters)
from .api.default import create_crypto_file_upload_capability as _endpoint_4

def _call_4(client, body=None, **parameters):
    parameters['body'] = _endpoint_4.CryptoProtoMessage.from_dict(body)
    return _endpoint_4.sync_detailed(client=client, **parameters)
from .api.default import create_crypto_invitation as _endpoint_5

def _call_5(client, body=None, **parameters):
    parameters['body'] = _endpoint_5.CryptoProtoMessage.from_dict(body)
    return _endpoint_5.sync_detailed(client=client, **parameters)
from .api.default import create_crypto_project as _endpoint_6

def _call_6(client, body=None, **parameters):
    parameters['body'] = _endpoint_6.CryptoProtoMessage.from_dict(body)
    return _endpoint_6.sync_detailed(client=client, **parameters)
from .api.default import enroll_crypto as _endpoint_7

def _call_7(client, body=None, **parameters):
    parameters['body'] = _endpoint_7.CryptoProtoMessage.from_dict(body)
    return _endpoint_7.sync_detailed(client=client, **parameters)
from .api.default import genesis_crypto as _endpoint_8

def _call_8(client, body=None, **parameters):
    parameters['body'] = _endpoint_8.CryptoProtoMessage.from_dict(body)
    return _endpoint_8.sync_detailed(client=client, **parameters)
from .api.default import get_crypto_project_audience as _endpoint_9

def _call_9(client, body=None, **parameters):
    parameters['body'] = _endpoint_9.CryptoProtoMessage.from_dict(body)
    return _endpoint_9.sync_detailed(client=client, **parameters)
from .api.default import get_crypto_settings as _endpoint_10

def _call_10(client, body=None, **parameters):
    parameters['body'] = _endpoint_10.CryptoProtoMessage.from_dict(body)
    return _endpoint_10.sync_detailed(client=client, **parameters)
from .api.default import list_crypto_projects as _endpoint_11

def _call_11(client, body=None, **parameters):
    parameters['body'] = _endpoint_11.CryptoProtoMessage.from_dict(body)
    return _endpoint_11.sync_detailed(client=client, **parameters)
from .api.default import prepare_crypto_group_member as _endpoint_12

def _call_12(client, body=None, **parameters):
    parameters['body'] = _endpoint_12.CryptoProtoMessage.from_dict(body)
    return _endpoint_12.sync_detailed(client=client, **parameters)
from .api.default import prepare_crypto_owner_delivery as _endpoint_13

def _call_13(client, body=None, **parameters):
    parameters['body'] = _endpoint_13.CryptoProtoMessage.from_dict(body)
    return _endpoint_13.sync_detailed(client=client, **parameters)
from .api.default import read_crypto as _endpoint_14

def _call_14(client, body=None, **parameters):
    parameters['body'] = _endpoint_14.CryptoProtoMessage.from_dict(body)
    return _endpoint_14.sync_detailed(client=client, **parameters)
from .api.default import read_crypto_file as _endpoint_15

def _call_15(client, body=None, **parameters):
    parameters['body'] = _endpoint_15.CryptoProtoMessage.from_dict(body)
    return _endpoint_15.sync_detailed(client=client, **parameters)
from .api.default import read_crypto_invitations as _endpoint_16

def _call_16(client, body=None, **parameters):
    parameters['body'] = _endpoint_16.CryptoProtoMessage.from_dict(body)
    return _endpoint_16.sync_detailed(client=client, **parameters)
from .api.default import request_crypto_invitation as _endpoint_17

def _call_17(client, body=None, **parameters):
    parameters['body'] = _endpoint_17.CryptoProtoMessage.from_dict(body)
    return _endpoint_17.sync_detailed(client=client, **parameters)
from .api.default import revoke_crypto_invitation as _endpoint_18

def _call_18(client, body=None, **parameters):
    parameters['body'] = _endpoint_18.CryptoProtoMessage.from_dict(body)
    return _endpoint_18.sync_detailed(client=client, **parameters)
from .api.default import rotate_crypto as _endpoint_19

def _call_19(client, body=None, **parameters):
    parameters['body'] = _endpoint_19.CryptoProtoMessage.from_dict(body)
    return _endpoint_19.sync_detailed(client=client, **parameters)
from .api.session import await_session_authorization as _endpoint_21

def _call_21(client, body=None, **parameters):
    return _endpoint_21.sync_detailed(client=client, **parameters)

OPERATIONS = {
    "approveCryptoInvitation": _call_1,
    "attestCrypto": _call_2,
    "commitCrypto": _call_3,
    "createCryptoFileUploadCapability": _call_4,
    "createCryptoInvitation": _call_5,
    "createCryptoProject": _call_6,
    "enrollCrypto": _call_7,
    "genesisCrypto": _call_8,
    "getCryptoProjectAudience": _call_9,
    "getCryptoSettings": _call_10,
    "listCryptoProjects": _call_11,
    "prepareCryptoGroupMember": _call_12,
    "prepareCryptoOwnerDelivery": _call_13,
    "readCrypto": _call_14,
    "readCryptoFile": _call_15,
    "readCryptoInvitations": _call_16,
    "requestCryptoInvitation": _call_17,
    "revokeCryptoInvitation": _call_18,
    "rotateCrypto": _call_19,
    "awaitSessionAuthorization": _call_21,
}

STREAM_OPERATIONS = {
}
