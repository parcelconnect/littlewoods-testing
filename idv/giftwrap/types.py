from enum import Enum, unique


@unique
class GiftWrapRequestStatus(Enum):
    New = 'new'
    Success = 'success'
    Failed = 'failed'
    Error = 'error'
    Rejected = 'rejected'


@unique
class DeliverBySpecialDate(Enum):
    Before = "Before"
    On = "On"
