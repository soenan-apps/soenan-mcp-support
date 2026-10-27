from enum import Enum


class AccountPermission(str, Enum):
    BILLINGMANAGE = "billing:manage"
    BILLINGREAD = "billing:read"
    MEMBERSHIPINVITE = "membership:invite"
    MEMBERSHIPMANAGE = "membership:manage"
    MEMBERSHIPREAD = "membership:read"
    ORGANIZATIONCLOSE = "organization:close"
    ORGANIZATIONREAD = "organization:read"
    ORGANIZATIONUPDATE = "organization:update"
    PRODUCTACCESS = "product:access"
    ROLEMANAGE = "role:manage"
    ROLEREAD = "role:read"
    SEATMANAGE = "seat:manage"
    SEATREAD = "seat:read"

    def __str__(self) -> str:
        return str(self.value)
