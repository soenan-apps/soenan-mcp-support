from .types import File
from .api.account import begin_account_email_change as _endpoint_1

def _call_1(client, body=None, **parameters):
    parameters['body'] = _endpoint_1.BeginAccountEmailChangeRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_1.BeginAccountEmailChangeSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_1.sync_detailed(client=client, **parameters)
from .api.account import begin_passkey_registration as _endpoint_2

def _call_2(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_2.BeginPasskeyRegistrationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_2.sync_detailed(client=client, **parameters)
from .api.account import change_account_password as _endpoint_3

def _call_3(client, body=None, **parameters):
    parameters['body'] = _endpoint_3.ChangePasswordRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_3.ChangeAccountPasswordSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_3.sync_detailed(client=client, **parameters)
from .api.account import close_account as _endpoint_4

def _call_4(client, body=None, **parameters):
    parameters['body'] = _endpoint_4.CloseAccountRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_4.CloseAccountSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_4.sync_detailed(client=client, **parameters)
from .api.account import complete_account_email_change as _endpoint_5

def _call_5(client, body=None, **parameters):
    parameters['body'] = _endpoint_5.EmailLinkRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_5.CompleteAccountEmailChangeSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_5.sync_detailed(client=client, **parameters)
from .api.account import complete_account_totp as _endpoint_6

def _call_6(client, body=None, **parameters):
    parameters['body'] = _endpoint_6.AccountTOTPCompletionRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_6.CompleteAccountTOTPSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_6.sync_detailed(client=client, **parameters)
from .api.account import complete_passkey_registration as _endpoint_7

def _call_7(client, body=None, **parameters):
    parameters['body'] = _endpoint_7.PasskeyRegistrationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_7.CompletePasskeyRegistrationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_7.sync_detailed(client=client, **parameters)
from .api.account import delete_account_passkey as _endpoint_8

def _call_8(client, body=None, **parameters):
    if 'passkey_id' in parameters:
        parameters['passkey_id'] = _endpoint_8.UUID(parameters['passkey_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_8.DeleteAccountPasskeySecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_8.sync_detailed(client=client, **parameters)
from .api.account import get_account_dashboard as _endpoint_9

def _call_9(client, body=None, **parameters):
    return _endpoint_9.sync_detailed(client=client, **parameters)
from .api.account import get_account_profile as _endpoint_10

def _call_10(client, body=None, **parameters):
    return _endpoint_10.sync_detailed(client=client, **parameters)
from .api.account import get_account_totp as _endpoint_11

def _call_11(client, body=None, **parameters):
    return _endpoint_11.sync_detailed(client=client, **parameters)
from .api.account import list_account_passkeys as _endpoint_12

def _call_12(client, body=None, **parameters):
    return _endpoint_12.sync_detailed(client=client, **parameters)
from .api.account import prepare_account_totp as _endpoint_13

def _call_13(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_13.PrepareAccountTOTPSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_13.sync_detailed(client=client, **parameters)
from .api.account import update_account_profile as _endpoint_14

def _call_14(client, body=None, **parameters):
    parameters['body'] = _endpoint_14.UpdateAccountProfileRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_14.UpdateAccountProfileSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_14.sync_detailed(client=client, **parameters)
from .api.authentication import begin_passkey_authentication as _endpoint_16

def _call_16(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_16.BeginPasskeyAuthenticationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_16.sync_detailed(client=client, **parameters)
from .api.authentication import complete_account_recovery as _endpoint_17

def _call_17(client, body=None, **parameters):
    parameters['body'] = _endpoint_17.AccountRecoveryCompletionRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_17.CompleteAccountRecoverySecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_17.sync_detailed(client=client, **parameters)
from .api.authentication import complete_passkey_authentication as _endpoint_18

def _call_18(client, body=None, **parameters):
    parameters['body'] = _endpoint_18.PasskeyAuthenticationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_18.CompletePasskeyAuthenticationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_18.sync_detailed(client=client, **parameters)
from .api.authentication import complete_sign_in_totp as _endpoint_19

def _call_19(client, body=None, **parameters):
    parameters['body'] = _endpoint_19.TOTPCompletionRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_19.CompleteSignInTOTPSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_19.sync_detailed(client=client, **parameters)
from .api.authentication import complete_sign_up as _endpoint_20

def _call_20(client, body=None, **parameters):
    parameters['body'] = _endpoint_20.EmailTOTPCompletionRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_20.CompleteSignUpSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_20.sync_detailed(client=client, **parameters)
from .api.authentication import get_session as _endpoint_21

def _call_21(client, body=None, **parameters):
    return _endpoint_21.sync_detailed(client=client, **parameters)
from .api.authentication import get_sign_up_configuration as _endpoint_22

def _call_22(client, body=None, **parameters):
    return _endpoint_22.sync_detailed(client=client, **parameters)
from .api.authentication import initiate_account_recovery as _endpoint_23

def _call_23(client, body=None, **parameters):
    parameters['body'] = _endpoint_23.AccountRecoveryRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_23.InitiateAccountRecoverySecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_23.sync_detailed(client=client, **parameters)
from .api.authentication import initiate_sign_in as _endpoint_24

def _call_24(client, body=None, **parameters):
    parameters['body'] = _endpoint_24.SignInRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_24.InitiateSignInSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_24.sync_detailed(client=client, **parameters)
from .api.authentication import initiate_sign_up as _endpoint_25

def _call_25(client, body=None, **parameters):
    parameters['body'] = _endpoint_25.SignUpRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_25.InitiateSignUpSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_25.sync_detailed(client=client, **parameters)
from .api.authentication import prepare_account_recovery as _endpoint_26

def _call_26(client, body=None, **parameters):
    parameters['body'] = _endpoint_26.EmailLinkRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_26.PrepareAccountRecoverySecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_26.sync_detailed(client=client, **parameters)
from .api.authentication import prepare_sign_up as _endpoint_27

def _call_27(client, body=None, **parameters):
    parameters['body'] = _endpoint_27.EmailLinkRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_27.PrepareSignUpSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_27.sync_detailed(client=client, **parameters)
from .api.authentication import refresh_session as _endpoint_28

def _call_28(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_28.RefreshSessionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_28.sync_detailed(client=client, **parameters)
from .api.authentication import sign_out as _endpoint_29

def _call_29(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_29.SignOutSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_29.sync_detailed(client=client, **parameters)
from .api.commerce import begin_group_purchase as _endpoint_31

def _call_31(client, body=None, **parameters):
    parameters['body'] = _endpoint_31.CommerceBeginRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_31.BeginGroupPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_31.sync_detailed(client=client, **parameters)
from .api.commerce import begin_personal_purchase as _endpoint_32

def _call_32(client, body=None, **parameters):
    parameters['body'] = _endpoint_32.CommerceBeginRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_32.BeginPersonalPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_32.sync_detailed(client=client, **parameters)
from .api.commerce import create_group_management_session as _endpoint_33

def _call_33(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_33.UUID(parameters['purchase_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_33.CreateGroupManagementSessionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_33.sync_detailed(client=client, **parameters)
from .api.commerce import create_group_plan_change_session as _endpoint_34

def _call_34(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_34.UUID(parameters['purchase_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_34.CreateGroupPlanChangeSessionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_34.sync_detailed(client=client, **parameters)
from .api.commerce import create_personal_management_session as _endpoint_35

def _call_35(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_35.UUID(parameters['purchase_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_35.CreatePersonalManagementSessionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_35.sync_detailed(client=client, **parameters)
from .api.commerce import create_personal_plan_change_session as _endpoint_36

def _call_36(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_36.UUID(parameters['purchase_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_36.CreatePersonalPlanChangeSessionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_36.sync_detailed(client=client, **parameters)
from .api.commerce import download_personal_product as _endpoint_37

def _call_37(client, body=None, **parameters):
    return _endpoint_37.sync_detailed(client=client, **parameters)
from .api.commerce import get_group_commerce as _endpoint_38

def _call_38(client, body=None, **parameters):
    return _endpoint_38.sync_detailed(client=client, **parameters)
from .api.commerce import get_group_manual_invoice as _endpoint_39

def _call_39(client, body=None, **parameters):
    if 'invoice_id' in parameters:
        parameters['invoice_id'] = _endpoint_39.UUID(parameters['invoice_id'])
    return _endpoint_39.sync_detailed(client=client, **parameters)
from .api.commerce import get_group_purchase_attempt as _endpoint_40

def _call_40(client, body=None, **parameters):
    if 'attempt_id' in parameters:
        parameters['attempt_id'] = _endpoint_40.UUID(parameters['attempt_id'])
    return _endpoint_40.sync_detailed(client=client, **parameters)
from .api.commerce import get_personal_commerce as _endpoint_41

def _call_41(client, body=None, **parameters):
    return _endpoint_41.sync_detailed(client=client, **parameters)
from .api.commerce import get_personal_manual_invoice as _endpoint_42

def _call_42(client, body=None, **parameters):
    if 'invoice_id' in parameters:
        parameters['invoice_id'] = _endpoint_42.UUID(parameters['invoice_id'])
    return _endpoint_42.sync_detailed(client=client, **parameters)
from .api.commerce import get_personal_purchase_attempt as _endpoint_43

def _call_43(client, body=None, **parameters):
    if 'attempt_id' in parameters:
        parameters['attempt_id'] = _endpoint_43.UUID(parameters['attempt_id'])
    return _endpoint_43.sync_detailed(client=client, **parameters)
from .api.commerce import list_group_manual_invoices as _endpoint_44

def _call_44(client, body=None, **parameters):
    return _endpoint_44.sync_detailed(client=client, **parameters)
from .api.commerce import list_personal_downloads as _endpoint_45

def _call_45(client, body=None, **parameters):
    return _endpoint_45.sync_detailed(client=client, **parameters)
from .api.commerce import list_personal_manual_invoices as _endpoint_46

def _call_46(client, body=None, **parameters):
    return _endpoint_46.sync_detailed(client=client, **parameters)
from .api.commerce import observe_group_purchase_completion as _endpoint_47

def _call_47(client, body=None, **parameters):
    parameters['body'] = _endpoint_47.CommerceAttemptCompletionReference.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_47.ObserveGroupPurchaseCompletionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_47.sync_detailed(client=client, **parameters)
from .api.commerce import observe_personal_purchase_completion as _endpoint_48

def _call_48(client, body=None, **parameters):
    parameters['body'] = _endpoint_48.CommerceAttemptCompletionReference.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_48.ObservePersonalPurchaseCompletionSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_48.sync_detailed(client=client, **parameters)
from .api.commerce import reconcile_group_purchase as _endpoint_49

def _call_49(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_49.UUID(parameters['purchase_id'])
    parameters['body'] = _endpoint_49.CommerceReconcilePurchaseRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_49.ReconcileGroupPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_49.sync_detailed(client=client, **parameters)
from .api.commerce import reconcile_personal_purchase as _endpoint_50

def _call_50(client, body=None, **parameters):
    if 'purchase_id' in parameters:
        parameters['purchase_id'] = _endpoint_50.UUID(parameters['purchase_id'])
    parameters['body'] = _endpoint_50.CommerceReconcilePurchaseRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_50.ReconcilePersonalPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_50.sync_detailed(client=client, **parameters)
from .api.commerce import verify_group_purchase as _endpoint_51

def _call_51(client, body=None, **parameters):
    parameters['body'] = _endpoint_51.CommerceVerifyRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_51.VerifyGroupPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_51.sync_detailed(client=client, **parameters)
from .api.commerce import verify_personal_purchase as _endpoint_52

def _call_52(client, body=None, **parameters):
    parameters['body'] = _endpoint_52.CommerceVerifyRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_52.VerifyPersonalPurchaseSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_52.sync_detailed(client=client, **parameters)
from .api.legal_terms import get_current_account_legal_terms as _endpoint_54

def _call_54(client, body=None, **parameters):
    return _endpoint_54.sync_detailed(client=client, **parameters)
from .api.legal_terms import get_legal_terms_version as _endpoint_55

def _call_55(client, body=None, **parameters):
    if 'version_id' in parameters:
        parameters['version_id'] = _endpoint_55.UUID(parameters['version_id'])
    return _endpoint_55.sync_detailed(client=client, **parameters)
from .api.o_auth import approve_o_auth_authorization_request as _endpoint_57

def _call_57(client, body=None, **parameters):
    parameters['body'] = _endpoint_57.OAuthAuthorizationApproval.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_57.ApproveOAuthAuthorizationRequestSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_57.sync_detailed(client=client, **parameters)
from .api.o_auth import authorize_o_auth_client as _endpoint_58

def _call_58(client, body=None, **parameters):
    if 'response_type' in parameters:
        parameters['response_type'] = _endpoint_58.AuthorizeOAuthClientResponseType(parameters['response_type'])
    if 'code_challenge_method' in parameters:
        parameters['code_challenge_method'] = _endpoint_58.AuthorizeOAuthClientCodeChallengeMethod(parameters['code_challenge_method'])
    if 'prompt' in parameters:
        parameters['prompt'] = _endpoint_58.AuthorizeOAuthClientPrompt(parameters['prompt'])
    return _endpoint_58.sync_detailed(client=client, **parameters)
from .api.o_auth import deny_o_auth_authorization_request as _endpoint_59

def _call_59(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_59.DenyOAuthAuthorizationRequestSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_59.sync_detailed(client=client, **parameters)
from .api.o_auth import exchange_o_auth_token as _endpoint_60

def _call_60(client, body=None, **parameters):
    parameters['body'] = _endpoint_60.OAuthTokenRequest.from_dict(body)
    return _endpoint_60.sync_detailed(client=client, **parameters)
from .api.o_auth import get_o_auth_authorization_request as _endpoint_61

def _call_61(client, body=None, **parameters):
    return _endpoint_61.sync_detailed(client=client, **parameters)
from .api.o_auth import get_o_auth_authorization_server_metadata as _endpoint_62

def _call_62(client, body=None, **parameters):
    return _endpoint_62.sync_detailed(client=client, **parameters)
from .api.o_auth import get_public_jwks as _endpoint_63

def _call_63(client, body=None, **parameters):
    return _endpoint_63.sync_detailed(client=client, **parameters)
from .api.o_auth import list_mcp_authorizations as _endpoint_64

def _call_64(client, body=None, **parameters):
    return _endpoint_64.sync_detailed(client=client, **parameters)
from .api.o_auth import register_o_auth_client as _endpoint_65

def _call_65(client, body=None, **parameters):
    parameters['body'] = _endpoint_65.OAuthClientRegistrationRequest.from_dict(body)
    return _endpoint_65.sync_detailed(client=client, **parameters)
from .api.o_auth import revoke_mcp_authorization as _endpoint_66

def _call_66(client, body=None, **parameters):
    if 'authorization_id' in parameters:
        parameters['authorization_id'] = _endpoint_66.UUID(parameters['authorization_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_66.RevokeMCPAuthorizationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_66.sync_detailed(client=client, **parameters)
from .api.o_auth import revoke_o_auth_token as _endpoint_67

def _call_67(client, body=None, **parameters):
    parameters['body'] = _endpoint_67.OAuthTokenRevocationRequest.from_dict(body)
    return _endpoint_67.sync_detailed(client=client, **parameters)
from .api.organizations import accept_organization_invitation as _endpoint_69

def _call_69(client, body=None, **parameters):
    parameters['body'] = _endpoint_69.AcceptOrganizationInvitationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_69.AcceptOrganizationInvitationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_69.sync_detailed(client=client, **parameters)
from .api.organizations import archive_organization_role as _endpoint_70

def _call_70(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_70.ArchiveOrganizationRoleSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_70.sync_detailed(client=client, **parameters)
from .api.organizations import assign_arteligo_seat as _endpoint_71

def _call_71(client, body=None, **parameters):
    parameters['body'] = _endpoint_71.OrganizationSeatRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_71.AssignArteligoSeatSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_71.sync_detailed(client=client, **parameters)
from .api.organizations import assign_organization_member_role as _endpoint_72

def _call_72(client, body=None, **parameters):
    parameters['body'] = _endpoint_72.OrganizationMemberRoleRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_72.AssignOrganizationMemberRoleSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_72.sync_detailed(client=client, **parameters)
from .api.organizations import close_organization as _endpoint_73

def _call_73(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_73.CloseOrganizationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_73.sync_detailed(client=client, **parameters)
from .api.organizations import create_organization as _endpoint_74

def _call_74(client, body=None, **parameters):
    parameters['body'] = _endpoint_74.CreateOrganizationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_74.CreateOrganizationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_74.sync_detailed(client=client, **parameters)
from .api.organizations import create_organization_role as _endpoint_75

def _call_75(client, body=None, **parameters):
    parameters['body'] = _endpoint_75.OrganizationRoleRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_75.CreateOrganizationRoleSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_75.sync_detailed(client=client, **parameters)
from .api.organizations import get_organization_detail as _endpoint_76

def _call_76(client, body=None, **parameters):
    return _endpoint_76.sync_detailed(client=client, **parameters)
from .api.organizations import issue_organization_invitation as _endpoint_77

def _call_77(client, body=None, **parameters):
    parameters['body'] = _endpoint_77.OrganizationInvitationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_77.IssueOrganizationInvitationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_77.sync_detailed(client=client, **parameters)
from .api.organizations import leave_organization as _endpoint_78

def _call_78(client, body=None, **parameters):
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_78.LeaveOrganizationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_78.sync_detailed(client=client, **parameters)
from .api.organizations import list_organizations as _endpoint_79

def _call_79(client, body=None, **parameters):
    return _endpoint_79.sync_detailed(client=client, **parameters)
from .api.organizations import reactivate_organization_member as _endpoint_80

def _call_80(client, body=None, **parameters):
    parameters['body'] = _endpoint_80.OrganizationMemberRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_80.ReactivateOrganizationMemberSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_80.sync_detailed(client=client, **parameters)
from .api.organizations import release_arteligo_seat as _endpoint_81

def _call_81(client, body=None, **parameters):
    parameters['body'] = _endpoint_81.OrganizationSeatRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_81.ReleaseArteligoSeatSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_81.sync_detailed(client=client, **parameters)
from .api.organizations import remove_organization_member as _endpoint_82

def _call_82(client, body=None, **parameters):
    parameters['body'] = _endpoint_82.OrganizationMemberRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_82.RemoveOrganizationMemberSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_82.sync_detailed(client=client, **parameters)
from .api.organizations import revoke_organization_invitation as _endpoint_83

def _call_83(client, body=None, **parameters):
    if 'invitation_id' in parameters:
        parameters['invitation_id'] = _endpoint_83.UUID(parameters['invitation_id'])
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_83.RevokeOrganizationInvitationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_83.sync_detailed(client=client, **parameters)
from .api.organizations import revoke_organization_member_role as _endpoint_84

def _call_84(client, body=None, **parameters):
    parameters['body'] = _endpoint_84.OrganizationMemberRoleRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_84.RevokeOrganizationMemberRoleSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_84.sync_detailed(client=client, **parameters)
from .api.organizations import suspend_organization_member as _endpoint_85

def _call_85(client, body=None, **parameters):
    parameters['body'] = _endpoint_85.OrganizationMemberRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_85.SuspendOrganizationMemberSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_85.sync_detailed(client=client, **parameters)
from .api.organizations import transfer_organization_ownership as _endpoint_86

def _call_86(client, body=None, **parameters):
    parameters['body'] = _endpoint_86.TransferOrganizationOwnershipRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_86.TransferOrganizationOwnershipSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_86.sync_detailed(client=client, **parameters)
from .api.organizations import update_organization as _endpoint_87

def _call_87(client, body=None, **parameters):
    parameters['body'] = _endpoint_87.UpdateOrganizationRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_87.UpdateOrganizationSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_87.sync_detailed(client=client, **parameters)
from .api.organizations import update_organization_role as _endpoint_88

def _call_88(client, body=None, **parameters):
    parameters['body'] = _endpoint_88.UpdateOrganizationRoleRequest.from_dict(body)
    if 'sec_fetch_site' in parameters:
        parameters['sec_fetch_site'] = _endpoint_88.UpdateOrganizationRoleSecFetchSite(parameters['sec_fetch_site'])
    return _endpoint_88.sync_detailed(client=client, **parameters)

OPERATIONS = {
    "beginAccountEmailChange": _call_1,
    "beginPasskeyRegistration": _call_2,
    "changeAccountPassword": _call_3,
    "closeAccount": _call_4,
    "completeAccountEmailChange": _call_5,
    "completeAccountTOTP": _call_6,
    "completePasskeyRegistration": _call_7,
    "deleteAccountPasskey": _call_8,
    "getAccountDashboard": _call_9,
    "getAccountProfile": _call_10,
    "getAccountTOTP": _call_11,
    "listAccountPasskeys": _call_12,
    "prepareAccountTOTP": _call_13,
    "updateAccountProfile": _call_14,
    "beginPasskeyAuthentication": _call_16,
    "completeAccountRecovery": _call_17,
    "completePasskeyAuthentication": _call_18,
    "completeSignInTOTP": _call_19,
    "completeSignUp": _call_20,
    "getSession": _call_21,
    "getSignUpConfiguration": _call_22,
    "initiateAccountRecovery": _call_23,
    "initiateSignIn": _call_24,
    "initiateSignUp": _call_25,
    "prepareAccountRecovery": _call_26,
    "prepareSignUp": _call_27,
    "refreshSession": _call_28,
    "signOut": _call_29,
    "beginGroupPurchase": _call_31,
    "beginPersonalPurchase": _call_32,
    "createGroupManagementSession": _call_33,
    "createGroupPlanChangeSession": _call_34,
    "createPersonalManagementSession": _call_35,
    "createPersonalPlanChangeSession": _call_36,
    "downloadPersonalProduct": _call_37,
    "getGroupCommerce": _call_38,
    "getGroupManualInvoice": _call_39,
    "getGroupPurchaseAttempt": _call_40,
    "getPersonalCommerce": _call_41,
    "getPersonalManualInvoice": _call_42,
    "getPersonalPurchaseAttempt": _call_43,
    "listGroupManualInvoices": _call_44,
    "listPersonalDownloads": _call_45,
    "listPersonalManualInvoices": _call_46,
    "observeGroupPurchaseCompletion": _call_47,
    "observePersonalPurchaseCompletion": _call_48,
    "reconcileGroupPurchase": _call_49,
    "reconcilePersonalPurchase": _call_50,
    "verifyGroupPurchase": _call_51,
    "verifyPersonalPurchase": _call_52,
    "getCurrentAccountLegalTerms": _call_54,
    "getLegalTermsVersion": _call_55,
    "approveOAuthAuthorizationRequest": _call_57,
    "authorizeOAuthClient": _call_58,
    "denyOAuthAuthorizationRequest": _call_59,
    "exchangeOAuthToken": _call_60,
    "getOAuthAuthorizationRequest": _call_61,
    "getOAuthAuthorizationServerMetadata": _call_62,
    "getPublicJWKS": _call_63,
    "listMCPAuthorizations": _call_64,
    "registerOAuthClient": _call_65,
    "revokeMCPAuthorization": _call_66,
    "revokeOAuthToken": _call_67,
    "acceptOrganizationInvitation": _call_69,
    "archiveOrganizationRole": _call_70,
    "assignArteligoSeat": _call_71,
    "assignOrganizationMemberRole": _call_72,
    "closeOrganization": _call_73,
    "createOrganization": _call_74,
    "createOrganizationRole": _call_75,
    "getOrganizationDetail": _call_76,
    "issueOrganizationInvitation": _call_77,
    "leaveOrganization": _call_78,
    "listOrganizations": _call_79,
    "reactivateOrganizationMember": _call_80,
    "releaseArteligoSeat": _call_81,
    "removeOrganizationMember": _call_82,
    "revokeOrganizationInvitation": _call_83,
    "revokeOrganizationMemberRole": _call_84,
    "suspendOrganizationMember": _call_85,
    "transferOrganizationOwnership": _call_86,
    "updateOrganization": _call_87,
    "updateOrganizationRole": _call_88,
}

STREAM_OPERATIONS = {
}
