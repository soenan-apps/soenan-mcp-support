import datetime

from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from soenan.arteligo.crypto.v1 import crypto_pb2 as _crypto_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectPhase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROJECT_PHASE_DRAFT: _ClassVar[ProjectPhase]
    PROJECT_PHASE_ACTIVE: _ClassVar[ProjectPhase]

class ProjectStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROJECT_STATUS_DRAFT: _ClassVar[ProjectStatus]
    PROJECT_STATUS_ACTIVE: _ClassVar[ProjectStatus]
    PROJECT_STATUS_ARCHIVED: _ClassVar[ProjectStatus]

class StageContentPurpose(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_CONTENT_PURPOSE_MIX: _ClassVar[StageContentPurpose]
    STAGE_CONTENT_PURPOSE_VOCAL: _ClassVar[StageContentPurpose]
    STAGE_CONTENT_PURPOSE_VIDEO: _ClassVar[StageContentPurpose]
    STAGE_CONTENT_PURPOSE_SCRIPT: _ClassVar[StageContentPurpose]
    STAGE_CONTENT_PURPOSE_PRODUCTION_PLAN: _ClassVar[StageContentPurpose]
    STAGE_CONTENT_PURPOSE_MODEL_3D: _ClassVar[StageContentPurpose]

class TextTargetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEXT_TARGET_TYPE_COMMENT: _ClassVar[TextTargetType]
    TEXT_TARGET_TYPE_REPLY: _ClassVar[TextTargetType]

class ChatEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHAT_EVENT_TYPE_SENT: _ClassVar[ChatEventType]
    CHAT_EVENT_TYPE_EDITED: _ClassVar[ChatEventType]
    CHAT_EVENT_TYPE_DELETED: _ClassVar[ChatEventType]

class ProjectTaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROJECT_TASK_STATUS_NOT_STARTED: _ClassVar[ProjectTaskStatus]
    PROJECT_TASK_STATUS_IN_PROGRESS: _ClassVar[ProjectTaskStatus]
    PROJECT_TASK_STATUS_DONE: _ClassVar[ProjectTaskStatus]

class PreviewState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PREVIEW_STATE_WAITING: _ClassVar[PreviewState]
    PREVIEW_STATE_QUEUED: _ClassVar[PreviewState]
    PREVIEW_STATE_PROCESSING: _ClassVar[PreviewState]
    PREVIEW_STATE_READY: _ClassVar[PreviewState]
    PREVIEW_STATE_FAILED: _ClassVar[PreviewState]

class LoudnessState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOUDNESS_STATE_MEASURED: _ClassVar[LoudnessState]
    LOUDNESS_STATE_UNMEASURABLE: _ClassVar[LoudnessState]

class FileUploadState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILE_UPLOAD_STATE_UPLOADING: _ClassVar[FileUploadState]
PROJECT_PHASE_DRAFT: ProjectPhase
PROJECT_PHASE_ACTIVE: ProjectPhase
PROJECT_STATUS_DRAFT: ProjectStatus
PROJECT_STATUS_ACTIVE: ProjectStatus
PROJECT_STATUS_ARCHIVED: ProjectStatus
STAGE_CONTENT_PURPOSE_MIX: StageContentPurpose
STAGE_CONTENT_PURPOSE_VOCAL: StageContentPurpose
STAGE_CONTENT_PURPOSE_VIDEO: StageContentPurpose
STAGE_CONTENT_PURPOSE_SCRIPT: StageContentPurpose
STAGE_CONTENT_PURPOSE_PRODUCTION_PLAN: StageContentPurpose
STAGE_CONTENT_PURPOSE_MODEL_3D: StageContentPurpose
TEXT_TARGET_TYPE_COMMENT: TextTargetType
TEXT_TARGET_TYPE_REPLY: TextTargetType
CHAT_EVENT_TYPE_SENT: ChatEventType
CHAT_EVENT_TYPE_EDITED: ChatEventType
CHAT_EVENT_TYPE_DELETED: ChatEventType
PROJECT_TASK_STATUS_NOT_STARTED: ProjectTaskStatus
PROJECT_TASK_STATUS_IN_PROGRESS: ProjectTaskStatus
PROJECT_TASK_STATUS_DONE: ProjectTaskStatus
PREVIEW_STATE_WAITING: PreviewState
PREVIEW_STATE_QUEUED: PreviewState
PREVIEW_STATE_PROCESSING: PreviewState
PREVIEW_STATE_READY: PreviewState
PREVIEW_STATE_FAILED: PreviewState
LOUDNESS_STATE_MEASURED: LoudnessState
LOUDNESS_STATE_UNMEASURABLE: LoudnessState
FILE_UPLOAD_STATE_UPLOADING: FileUploadState
RECORD_KIND_FIELD_NUMBER: _ClassVar[int]
record_kind: _descriptor.FieldDescriptor

class RecordReference(_message.Message):
    __slots__ = ("id", "revision")
    ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    id: str
    revision: int
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ...) -> None: ...

class MemberActor(_message.Message):
    __slots__ = ("membership_id", "user_id", "display_name")
    MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    membership_id: str
    user_id: str
    display_name: str
    def __init__(self, membership_id: _Optional[str] = ..., user_id: _Optional[str] = ..., display_name: _Optional[str] = ...) -> None: ...

class ProjectBrief(_message.Message):
    __slots__ = ("request_song", "reference_track", "mix_direction", "keep_nuance")
    REQUEST_SONG_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_TRACK_FIELD_NUMBER: _ClassVar[int]
    MIX_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    KEEP_NUANCE_FIELD_NUMBER: _ClassVar[int]
    request_song: str
    reference_track: str
    mix_direction: str
    keep_nuance: str
    def __init__(self, request_song: _Optional[str] = ..., reference_track: _Optional[str] = ..., mix_direction: _Optional[str] = ..., keep_nuance: _Optional[str] = ...) -> None: ...

class Responsibility(_message.Message):
    __slots__ = ("revision", "waiting_on")
    REVISION_FIELD_NUMBER: _ClassVar[int]
    WAITING_ON_FIELD_NUMBER: _ClassVar[int]
    revision: int
    waiting_on: MemberActor
    def __init__(self, revision: _Optional[int] = ..., waiting_on: _Optional[_Union[MemberActor, _Mapping]] = ...) -> None: ...

class ProjectInfo(_message.Message):
    __slots__ = ("slug", "title", "brief", "deadline_date", "progress", "responsibility", "phase", "created_at", "updated_at")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    BRIEF_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_DATE_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    RESPONSIBILITY_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    slug: str
    title: str
    brief: ProjectBrief
    deadline_date: str
    progress: float
    responsibility: Responsibility
    phase: ProjectPhase
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, slug: _Optional[str] = ..., title: _Optional[str] = ..., brief: _Optional[_Union[ProjectBrief, _Mapping]] = ..., deadline_date: _Optional[str] = ..., progress: _Optional[float] = ..., responsibility: _Optional[_Union[Responsibility, _Mapping]] = ..., phase: _Optional[_Union[ProjectPhase, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DirectoryRootReference(_message.Message):
    __slots__ = ("root",)
    ROOT_FIELD_NUMBER: _ClassVar[int]
    root: str
    def __init__(self, root: _Optional[str] = ...) -> None: ...

class ProjectRootContent(_message.Message):
    __slots__ = ("project", "last_stage_version", "directory")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    LAST_STAGE_VERSION_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    project: ProjectInfo
    last_stage_version: int
    directory: DirectoryRootReference
    def __init__(self, project: _Optional[_Union[ProjectInfo, _Mapping]] = ..., last_stage_version: _Optional[int] = ..., directory: _Optional[_Union[DirectoryRootReference, _Mapping]] = ...) -> None: ...

class StageFile(_message.Message):
    __slots__ = ("file_id", "relative_path")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_PATH_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    relative_path: str
    def __init__(self, file_id: _Optional[str] = ..., relative_path: _Optional[str] = ...) -> None: ...

class StageContent(_message.Message):
    __slots__ = ("id", "purpose", "title", "files")
    ID_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    id: str
    purpose: StageContentPurpose
    title: str
    files: _containers.RepeatedCompositeFieldContainer[StageFile]
    def __init__(self, id: _Optional[str] = ..., purpose: _Optional[_Union[StageContentPurpose, str]] = ..., title: _Optional[str] = ..., files: _Optional[_Iterable[_Union[StageFile, _Mapping]]] = ...) -> None: ...

class StageDraft(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StagePublication(_message.Message):
    __slots__ = ("version_number", "published_at", "publication_operation", "publication_expected_revision")
    VERSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_AT_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_OPERATION_FIELD_NUMBER: _ClassVar[int]
    PUBLICATION_EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    version_number: int
    published_at: _timestamp_pb2.Timestamp
    publication_operation: str
    publication_expected_revision: int
    def __init__(self, version_number: _Optional[int] = ..., published_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., publication_operation: _Optional[str] = ..., publication_expected_revision: _Optional[int] = ...) -> None: ...

class ProjectStageContent(_message.Message):
    __slots__ = ("contents", "label", "created_at", "updated_at", "draft", "published")
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DRAFT_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    contents: _containers.RepeatedCompositeFieldContainer[StageContent]
    label: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    draft: StageDraft
    published: StagePublication
    def __init__(self, contents: _Optional[_Iterable[_Union[StageContent, _Mapping]]] = ..., label: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., draft: _Optional[_Union[StageDraft, _Mapping]] = ..., published: _Optional[_Union[StagePublication, _Mapping]] = ...) -> None: ...

class PublishStageRequest(_message.Message):
    __slots__ = ("expected_revision", "operation_id")
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    expected_revision: int
    operation_id: str
    def __init__(self, expected_revision: _Optional[int] = ..., operation_id: _Optional[str] = ...) -> None: ...

class ReviewAnchor(_message.Message):
    __slots__ = ("file_id", "stage_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    STAGE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    stage_id: str
    def __init__(self, file_id: _Optional[str] = ..., stage_id: _Optional[str] = ...) -> None: ...

class ReviewTimeSpan(_message.Message):
    __slots__ = ("start_seconds", "end_seconds")
    START_SECONDS_FIELD_NUMBER: _ClassVar[int]
    END_SECONDS_FIELD_NUMBER: _ClassVar[int]
    start_seconds: float
    end_seconds: float
    def __init__(self, start_seconds: _Optional[float] = ..., end_seconds: _Optional[float] = ...) -> None: ...

class ReviewPinRegion(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class ReviewRectangleRegion(_message.Message):
    __slots__ = ("x", "y", "width", "height")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    width: float
    height: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ...) -> None: ...

class ReviewRegion(_message.Message):
    __slots__ = ("pin", "rectangle")
    PIN_FIELD_NUMBER: _ClassVar[int]
    RECTANGLE_FIELD_NUMBER: _ClassVar[int]
    pin: ReviewPinRegion
    rectangle: ReviewRectangleRegion
    def __init__(self, pin: _Optional[_Union[ReviewPinRegion, _Mapping]] = ..., rectangle: _Optional[_Union[ReviewRectangleRegion, _Mapping]] = ...) -> None: ...

class ProjectReference(_message.Message):
    __slots__ = ("file_id", "stage_id", "comment_id", "reply_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    STAGE_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    REPLY_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    stage_id: str
    comment_id: str
    reply_id: str
    def __init__(self, file_id: _Optional[str] = ..., stage_id: _Optional[str] = ..., comment_id: _Optional[str] = ..., reply_id: _Optional[str] = ...) -> None: ...

class CommentOrigin(_message.Message):
    __slots__ = ("anchor", "time_span", "region", "tag", "body", "author", "created_at", "thread_head_id", "body_head_id", "sequence")
    ANCHOR_FIELD_NUMBER: _ClassVar[int]
    TIME_SPAN_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    THREAD_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    anchor: ReviewAnchor
    time_span: ReviewTimeSpan
    region: ReviewRegion
    tag: str
    body: str
    author: MemberActor
    created_at: _timestamp_pb2.Timestamp
    thread_head_id: str
    body_head_id: str
    sequence: int
    def __init__(self, anchor: _Optional[_Union[ReviewAnchor, _Mapping]] = ..., time_span: _Optional[_Union[ReviewTimeSpan, _Mapping]] = ..., region: _Optional[_Union[ReviewRegion, _Mapping]] = ..., tag: _Optional[str] = ..., body: _Optional[str] = ..., author: _Optional[_Union[MemberActor, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., thread_head_id: _Optional[str] = ..., body_head_id: _Optional[str] = ..., sequence: _Optional[int] = ...) -> None: ...

class ReplyOrigin(_message.Message):
    __slots__ = ("parent_comment_id", "body", "references", "author", "created_at", "body_head_id", "sequence")
    PARENT_COMMENT_ID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    BODY_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    parent_comment_id: str
    body: str
    references: _containers.RepeatedCompositeFieldContainer[ProjectReference]
    author: MemberActor
    created_at: _timestamp_pb2.Timestamp
    body_head_id: str
    sequence: int
    def __init__(self, parent_comment_id: _Optional[str] = ..., body: _Optional[str] = ..., references: _Optional[_Iterable[_Union[ProjectReference, _Mapping]]] = ..., author: _Optional[_Union[MemberActor, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., body_head_id: _Optional[str] = ..., sequence: _Optional[int] = ...) -> None: ...

class ThreadHead(_message.Message):
    __slots__ = ("original", "reply_count", "resolution")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    REPLY_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    reply_count: int
    resolution: RecordReference
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., reply_count: _Optional[int] = ..., resolution: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class TextHead(_message.Message):
    __slots__ = ("original", "target_type", "text_revision", "last_edit")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_REVISION_FIELD_NUMBER: _ClassVar[int]
    LAST_EDIT_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    target_type: TextTargetType
    text_revision: int
    last_edit: RecordReference
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., target_type: _Optional[_Union[TextTargetType, str]] = ..., text_revision: _Optional[int] = ..., last_edit: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class TextRevision(_message.Message):
    __slots__ = ("original", "target_type", "body_head_id", "operation_id", "text_revision", "author_account_subject", "body", "committed_at")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    BODY_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_REVISION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_ACCOUNT_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    target_type: TextTargetType
    body_head_id: str
    operation_id: str
    text_revision: int
    author_account_subject: str
    body: str
    committed_at: _timestamp_pb2.Timestamp
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., target_type: _Optional[_Union[TextTargetType, str]] = ..., body_head_id: _Optional[str] = ..., operation_id: _Optional[str] = ..., text_revision: _Optional[int] = ..., author_account_subject: _Optional[str] = ..., body: _Optional[str] = ..., committed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ResolutionEvent(_message.Message):
    __slots__ = ("original", "resolved", "operation_id", "actor")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    resolved: bool
    operation_id: str
    actor: MemberActor
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., resolved: bool = ..., operation_id: _Optional[str] = ..., actor: _Optional[_Union[MemberActor, _Mapping]] = ...) -> None: ...

class ReplyView(_message.Message):
    __slots__ = ("id", "origin", "text_head", "latest_edit")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    TEXT_HEAD_FIELD_NUMBER: _ClassVar[int]
    LATEST_EDIT_FIELD_NUMBER: _ClassVar[int]
    id: str
    origin: ReplyOrigin
    text_head: TextHead
    latest_edit: TextRevision
    def __init__(self, id: _Optional[str] = ..., origin: _Optional[_Union[ReplyOrigin, _Mapping]] = ..., text_head: _Optional[_Union[TextHead, _Mapping]] = ..., latest_edit: _Optional[_Union[TextRevision, _Mapping]] = ...) -> None: ...

class CommentCursor(_message.Message):
    __slots__ = ("sequence", "id")
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    id: str
    def __init__(self, sequence: _Optional[int] = ..., id: _Optional[str] = ...) -> None: ...

class CommentView(_message.Message):
    __slots__ = ("id", "origin", "text_head", "latest_edit", "thread_head", "resolution", "replies", "has_more_replies", "next_reply_cursor")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    TEXT_HEAD_FIELD_NUMBER: _ClassVar[int]
    LATEST_EDIT_FIELD_NUMBER: _ClassVar[int]
    THREAD_HEAD_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    REPLIES_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_REPLIES_FIELD_NUMBER: _ClassVar[int]
    NEXT_REPLY_CURSOR_FIELD_NUMBER: _ClassVar[int]
    id: str
    origin: CommentOrigin
    text_head: TextHead
    latest_edit: TextRevision
    thread_head: ThreadHead
    resolution: ResolutionEvent
    replies: _containers.RepeatedCompositeFieldContainer[ReplyView]
    has_more_replies: bool
    next_reply_cursor: CommentCursor
    def __init__(self, id: _Optional[str] = ..., origin: _Optional[_Union[CommentOrigin, _Mapping]] = ..., text_head: _Optional[_Union[TextHead, _Mapping]] = ..., latest_edit: _Optional[_Union[TextRevision, _Mapping]] = ..., thread_head: _Optional[_Union[ThreadHead, _Mapping]] = ..., resolution: _Optional[_Union[ResolutionEvent, _Mapping]] = ..., replies: _Optional[_Iterable[_Union[ReplyView, _Mapping]]] = ..., has_more_replies: bool = ..., next_reply_cursor: _Optional[_Union[CommentCursor, _Mapping]] = ...) -> None: ...

class ProjectEntryValues(_message.Message):
    __slots__ = ("parent_folder_id", "name", "created_at", "updated_at")
    PARENT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    parent_folder_id: str
    name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, parent_folder_id: _Optional[str] = ..., name: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ProjectFileEntry(_message.Message):
    __slots__ = ("values", "file_id", "description")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    values: ProjectEntryValues
    file_id: str
    description: FileDescription
    def __init__(self, values: _Optional[_Union[ProjectEntryValues, _Mapping]] = ..., file_id: _Optional[str] = ..., description: _Optional[_Union[FileDescription, _Mapping]] = ...) -> None: ...

class ProjectEntry(_message.Message):
    __slots__ = ("id", "revision", "folder", "file")
    ID_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    FOLDER_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    id: str
    revision: int
    folder: ProjectEntryValues
    file: ProjectFileEntry
    def __init__(self, id: _Optional[str] = ..., revision: _Optional[int] = ..., folder: _Optional[_Union[ProjectEntryValues, _Mapping]] = ..., file: _Optional[_Union[ProjectFileEntry, _Mapping]] = ...) -> None: ...

class ProjectEntryIntent(_message.Message):
    __slots__ = ("parent_folder_id", "name")
    PARENT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    parent_folder_id: str
    name: str
    def __init__(self, parent_folder_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class FolderCreation(_message.Message):
    __slots__ = ("request", "response")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    request: ProjectEntryIntent
    response: ProjectEntry
    def __init__(self, request: _Optional[_Union[ProjectEntryIntent, _Mapping]] = ..., response: _Optional[_Union[ProjectEntry, _Mapping]] = ...) -> None: ...

class DirectoryFolder(_message.Message):
    __slots__ = ("entry", "parent", "root", "creation")
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    PARENT_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    CREATION_FIELD_NUMBER: _ClassVar[int]
    entry: ProjectEntry
    parent: str
    root: RecordReference
    creation: FolderCreation
    def __init__(self, entry: _Optional[_Union[ProjectEntry, _Mapping]] = ..., parent: _Optional[str] = ..., root: _Optional[_Union[RecordReference, _Mapping]] = ..., creation: _Optional[_Union[FolderCreation, _Mapping]] = ...) -> None: ...

class DirectoryFileLocator(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: ProjectEntry
    def __init__(self, entry: _Optional[_Union[ProjectEntry, _Mapping]] = ...) -> None: ...

class DirectoryLeaf(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ProjectEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ProjectEntry, _Mapping]]] = ...) -> None: ...

class OrderedEntryKey(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: str
    def __init__(self, name: _Optional[str] = ..., id: _Optional[str] = ...) -> None: ...

class OrderedIndexChild(_message.Message):
    __slots__ = ("first", "node")
    FIRST_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    first: OrderedEntryKey
    node: RecordReference
    def __init__(self, first: _Optional[_Union[OrderedEntryKey, _Mapping]] = ..., node: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class OrderedIndexBranch(_message.Message):
    __slots__ = ("children",)
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    children: _containers.RepeatedCompositeFieldContainer[OrderedIndexChild]
    def __init__(self, children: _Optional[_Iterable[_Union[OrderedIndexChild, _Mapping]]] = ...) -> None: ...

class OrderedIndexEntry(_message.Message):
    __slots__ = ("key", "sequence", "message_revision", "head_id")
    KEY_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_REVISION_FIELD_NUMBER: _ClassVar[int]
    HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    key: OrderedEntryKey
    sequence: int
    message_revision: int
    head_id: str
    def __init__(self, key: _Optional[_Union[OrderedEntryKey, _Mapping]] = ..., sequence: _Optional[int] = ..., message_revision: _Optional[int] = ..., head_id: _Optional[str] = ...) -> None: ...

class OrderedIndexLeaf(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[OrderedIndexEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[OrderedIndexEntry, _Mapping]]] = ...) -> None: ...

class DirectoryOperations(_message.Message):
    __slots__ = ("pending",)
    PENDING_FIELD_NUMBER: _ClassVar[int]
    pending: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, pending: _Optional[_Iterable[str]] = ...) -> None: ...

class DirectoryDeletionWork(_message.Message):
    __slots__ = ("node", "folder_id", "file_id")
    NODE_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    node: RecordReference
    folder_id: str
    file_id: str
    def __init__(self, node: _Optional[_Union[RecordReference, _Mapping]] = ..., folder_id: _Optional[str] = ..., file_id: _Optional[str] = ...) -> None: ...

class DirectoryDeletion(_message.Message):
    __slots__ = ("entry_id", "stack", "overflow", "processed")
    ENTRY_ID_FIELD_NUMBER: _ClassVar[int]
    STACK_FIELD_NUMBER: _ClassVar[int]
    OVERFLOW_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_FIELD_NUMBER: _ClassVar[int]
    entry_id: str
    stack: _containers.RepeatedCompositeFieldContainer[DirectoryDeletionWork]
    overflow: RecordReference
    processed: int
    def __init__(self, entry_id: _Optional[str] = ..., stack: _Optional[_Iterable[_Union[DirectoryDeletionWork, _Mapping]]] = ..., overflow: _Optional[_Union[RecordReference, _Mapping]] = ..., processed: _Optional[int] = ...) -> None: ...

class DirectoryDeletionStack(_message.Message):
    __slots__ = ("items", "next")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    NEXT_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[DirectoryDeletionWork]
    next: RecordReference
    def __init__(self, items: _Optional[_Iterable[_Union[DirectoryDeletionWork, _Mapping]]] = ..., next: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class ChatHeader(_message.Message):
    __slots__ = ("sequence", "events", "messages")
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    events: RecordReference
    messages: RecordReference
    def __init__(self, sequence: _Optional[int] = ..., events: _Optional[_Union[RecordReference, _Mapping]] = ..., messages: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class ChatOrigin(_message.Message):
    __slots__ = ("message_head_id", "terminal_record_id", "author_membership_id", "actor_membership_id", "client_operation_id", "sequence", "references", "body", "committed_at")
    MESSAGE_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTOR_MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    REFERENCES_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    message_head_id: str
    terminal_record_id: str
    author_membership_id: str
    actor_membership_id: str
    client_operation_id: str
    sequence: int
    references: _containers.RepeatedCompositeFieldContainer[ProjectReference]
    body: str
    committed_at: _timestamp_pb2.Timestamp
    def __init__(self, message_head_id: _Optional[str] = ..., terminal_record_id: _Optional[str] = ..., author_membership_id: _Optional[str] = ..., actor_membership_id: _Optional[str] = ..., client_operation_id: _Optional[str] = ..., sequence: _Optional[int] = ..., references: _Optional[_Iterable[_Union[ProjectReference, _Mapping]]] = ..., body: _Optional[str] = ..., committed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChatEdit(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: str
    def __init__(self, body: _Optional[str] = ...) -> None: ...

class ChatDeletion(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ChatEvent(_message.Message):
    __slots__ = ("original", "message_head_id", "author_membership_id", "actor_membership_id", "client_operation_id", "sequence", "message_revision", "committed_at", "edited", "deleted")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTOR_MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_REVISION_FIELD_NUMBER: _ClassVar[int]
    COMMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    EDITED_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    message_head_id: str
    author_membership_id: str
    actor_membership_id: str
    client_operation_id: str
    sequence: int
    message_revision: int
    committed_at: _timestamp_pb2.Timestamp
    edited: ChatEdit
    deleted: ChatDeletion
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., message_head_id: _Optional[str] = ..., author_membership_id: _Optional[str] = ..., actor_membership_id: _Optional[str] = ..., client_operation_id: _Optional[str] = ..., sequence: _Optional[int] = ..., message_revision: _Optional[int] = ..., committed_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., edited: _Optional[_Union[ChatEdit, _Mapping]] = ..., deleted: _Optional[_Union[ChatDeletion, _Mapping]] = ...) -> None: ...

class ChatMessageHead(_message.Message):
    __slots__ = ("original", "message_revision", "last_event", "events")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_REVISION_FIELD_NUMBER: _ClassVar[int]
    LAST_EVENT_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    message_revision: int
    last_event: RecordReference
    events: RecordReference
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., message_revision: _Optional[int] = ..., last_event: _Optional[_Union[RecordReference, _Mapping]] = ..., events: _Optional[_Union[RecordReference, _Mapping]] = ...) -> None: ...

class ChatOperation(_message.Message):
    __slots__ = ("event_id", "message_id", "type")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    message_id: str
    type: ChatEventType
    def __init__(self, event_id: _Optional[str] = ..., message_id: _Optional[str] = ..., type: _Optional[_Union[ChatEventType, str]] = ...) -> None: ...

class ChatTerminal(_message.Message):
    __slots__ = ("original", "message_head_id", "delete_event", "message_revision")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_HEAD_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EVENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_REVISION_FIELD_NUMBER: _ClassVar[int]
    original: RecordReference
    message_head_id: str
    delete_event: RecordReference
    message_revision: int
    def __init__(self, original: _Optional[_Union[RecordReference, _Mapping]] = ..., message_head_id: _Optional[str] = ..., delete_event: _Optional[_Union[RecordReference, _Mapping]] = ..., message_revision: _Optional[int] = ...) -> None: ...

class ChatEventView(_message.Message):
    __slots__ = ("id", "project_id", "message_id", "origin", "event")
    ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    id: str
    project_id: str
    message_id: str
    origin: ChatOrigin
    event: ChatEvent
    def __init__(self, id: _Optional[str] = ..., project_id: _Optional[str] = ..., message_id: _Optional[str] = ..., origin: _Optional[_Union[ChatOrigin, _Mapping]] = ..., event: _Optional[_Union[ChatEvent, _Mapping]] = ...) -> None: ...

class ChatMessageView(_message.Message):
    __slots__ = ("latest", "verified_through_sequence")
    LATEST_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_THROUGH_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    latest: ChatEventView
    verified_through_sequence: int
    def __init__(self, latest: _Optional[_Union[ChatEventView, _Mapping]] = ..., verified_through_sequence: _Optional[int] = ...) -> None: ...

class CalendarDateStart(_message.Message):
    __slots__ = ("date",)
    DATE_FIELD_NUMBER: _ClassVar[int]
    date: str
    def __init__(self, date: _Optional[str] = ...) -> None: ...

class CalendarFloatingStart(_message.Message):
    __slots__ = ("civil_date_time",)
    CIVIL_DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    civil_date_time: str
    def __init__(self, civil_date_time: _Optional[str] = ...) -> None: ...

class CalendarUtcStart(_message.Message):
    __slots__ = ("civil_date_time",)
    CIVIL_DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    civil_date_time: str
    def __init__(self, civil_date_time: _Optional[str] = ...) -> None: ...

class CalendarZonedStart(_message.Message):
    __slots__ = ("civil_date_time", "tzid")
    CIVIL_DATE_TIME_FIELD_NUMBER: _ClassVar[int]
    TZID_FIELD_NUMBER: _ClassVar[int]
    civil_date_time: str
    tzid: str
    def __init__(self, civil_date_time: _Optional[str] = ..., tzid: _Optional[str] = ...) -> None: ...

class CalendarStart(_message.Message):
    __slots__ = ("date", "floating", "utc", "zoned")
    DATE_FIELD_NUMBER: _ClassVar[int]
    FLOATING_FIELD_NUMBER: _ClassVar[int]
    UTC_FIELD_NUMBER: _ClassVar[int]
    ZONED_FIELD_NUMBER: _ClassVar[int]
    date: CalendarDateStart
    floating: CalendarFloatingStart
    utc: CalendarUtcStart
    zoned: CalendarZonedStart
    def __init__(self, date: _Optional[_Union[CalendarDateStart, _Mapping]] = ..., floating: _Optional[_Union[CalendarFloatingStart, _Mapping]] = ..., utc: _Optional[_Union[CalendarUtcStart, _Mapping]] = ..., zoned: _Optional[_Union[CalendarZonedStart, _Mapping]] = ...) -> None: ...

class CalendarDaySpan(_message.Message):
    __slots__ = ("days",)
    DAYS_FIELD_NUMBER: _ClassVar[int]
    days: str
    def __init__(self, days: _Optional[str] = ...) -> None: ...

class CalendarExactSpan(_message.Message):
    __slots__ = ("seconds",)
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    seconds: str
    def __init__(self, seconds: _Optional[str] = ...) -> None: ...

class CalendarNominalSpan(_message.Message):
    __slots__ = ("weeks", "days", "hours", "minutes", "seconds")
    WEEKS_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    HOURS_FIELD_NUMBER: _ClassVar[int]
    MINUTES_FIELD_NUMBER: _ClassVar[int]
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    weeks: str
    days: str
    hours: str
    minutes: str
    seconds: str
    def __init__(self, weeks: _Optional[str] = ..., days: _Optional[str] = ..., hours: _Optional[str] = ..., minutes: _Optional[str] = ..., seconds: _Optional[str] = ...) -> None: ...

class CalendarSpan(_message.Message):
    __slots__ = ("days", "exact", "nominal")
    DAYS_FIELD_NUMBER: _ClassVar[int]
    EXACT_FIELD_NUMBER: _ClassVar[int]
    NOMINAL_FIELD_NUMBER: _ClassVar[int]
    days: CalendarDaySpan
    exact: CalendarExactSpan
    nominal: CalendarNominalSpan
    def __init__(self, days: _Optional[_Union[CalendarDaySpan, _Mapping]] = ..., exact: _Optional[_Union[CalendarExactSpan, _Mapping]] = ..., nominal: _Optional[_Union[CalendarNominalSpan, _Mapping]] = ...) -> None: ...

class CalendarPeriod(_message.Message):
    __slots__ = ("start", "span")
    START_FIELD_NUMBER: _ClassVar[int]
    SPAN_FIELD_NUMBER: _ClassVar[int]
    start: CalendarStart
    span: CalendarSpan
    def __init__(self, start: _Optional[_Union[CalendarStart, _Mapping]] = ..., span: _Optional[_Union[CalendarSpan, _Mapping]] = ...) -> None: ...

class CalendarRDate(_message.Message):
    __slots__ = ("start", "period")
    START_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    start: CalendarStart
    period: CalendarPeriod
    def __init__(self, start: _Optional[_Union[CalendarStart, _Mapping]] = ..., period: _Optional[_Union[CalendarPeriod, _Mapping]] = ...) -> None: ...

class RecurrenceSet(_message.Message):
    __slots__ = ("rule", "rdates")
    RULE_FIELD_NUMBER: _ClassVar[int]
    RDATES_FIELD_NUMBER: _ClassVar[int]
    rule: str
    rdates: _containers.RepeatedCompositeFieldContainer[CalendarRDate]
    def __init__(self, rule: _Optional[str] = ..., rdates: _Optional[_Iterable[_Union[CalendarRDate, _Mapping]]] = ...) -> None: ...

class CalendarExcluded(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CalendarOverride(_message.Message):
    __slots__ = ("title", "period")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    title: str
    period: CalendarPeriod
    def __init__(self, title: _Optional[str] = ..., period: _Optional[_Union[CalendarPeriod, _Mapping]] = ...) -> None: ...

class CalendarException(_message.Message):
    __slots__ = ("id", "excluded", "override")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_FIELD_NUMBER: _ClassVar[int]
    OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    id: CalendarStart
    excluded: CalendarExcluded
    override: CalendarOverride
    def __init__(self, id: _Optional[_Union[CalendarStart, _Mapping]] = ..., excluded: _Optional[_Union[CalendarExcluded, _Mapping]] = ..., override: _Optional[_Union[CalendarOverride, _Mapping]] = ...) -> None: ...

class CalendarSeries(_message.Message):
    __slots__ = ("recurrence", "exceptions")
    RECURRENCE_FIELD_NUMBER: _ClassVar[int]
    EXCEPTIONS_FIELD_NUMBER: _ClassVar[int]
    recurrence: RecurrenceSet
    exceptions: _containers.RepeatedCompositeFieldContainer[CalendarException]
    def __init__(self, recurrence: _Optional[_Union[RecurrenceSet, _Mapping]] = ..., exceptions: _Optional[_Iterable[_Union[CalendarException, _Mapping]]] = ...) -> None: ...

class CalendarStandalone(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CalendarPlan(_message.Message):
    __slots__ = ("period", "standalone", "series")
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    STANDALONE_FIELD_NUMBER: _ClassVar[int]
    SERIES_FIELD_NUMBER: _ClassVar[int]
    period: CalendarPeriod
    standalone: CalendarStandalone
    series: CalendarSeries
    def __init__(self, period: _Optional[_Union[CalendarPeriod, _Mapping]] = ..., standalone: _Optional[_Union[CalendarStandalone, _Mapping]] = ..., series: _Optional[_Union[CalendarSeries, _Mapping]] = ...) -> None: ...

class ProjectTaskValues(_message.Message):
    __slots__ = ("title", "calendar", "assignee_membership_id", "status")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CALENDAR_FIELD_NUMBER: _ClassVar[int]
    ASSIGNEE_MEMBERSHIP_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    title: str
    calendar: CalendarPlan
    assignee_membership_id: str
    status: ProjectTaskStatus
    def __init__(self, title: _Optional[str] = ..., calendar: _Optional[_Union[CalendarPlan, _Mapping]] = ..., assignee_membership_id: _Optional[str] = ..., status: _Optional[_Union[ProjectTaskStatus, str]] = ...) -> None: ...

class ProjectTaskContent(_message.Message):
    __slots__ = ("values", "created_at", "updated_at")
    VALUES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    values: ProjectTaskValues
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, values: _Optional[_Union[ProjectTaskValues, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ProjectTaskSnapshot(_message.Message):
    __slots__ = ("revision", "content")
    REVISION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    revision: int
    content: ProjectTaskContent
    def __init__(self, revision: _Optional[int] = ..., content: _Optional[_Union[ProjectTaskContent, _Mapping]] = ...) -> None: ...

class ProjectTaskCreation(_message.Message):
    __slots__ = ("request", "response")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    request: ProjectTaskValues
    response: ProjectTaskSnapshot
    def __init__(self, request: _Optional[_Union[ProjectTaskValues, _Mapping]] = ..., response: _Optional[_Union[ProjectTaskSnapshot, _Mapping]] = ...) -> None: ...

class ProjectTaskMutation(_message.Message):
    __slots__ = ("identity", "expected_revision", "request", "response")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_REVISION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    identity: str
    expected_revision: int
    request: ProjectTaskValues
    response: ProjectTaskSnapshot
    def __init__(self, identity: _Optional[str] = ..., expected_revision: _Optional[int] = ..., request: _Optional[_Union[ProjectTaskValues, _Mapping]] = ..., response: _Optional[_Union[ProjectTaskSnapshot, _Mapping]] = ...) -> None: ...

class ProjectScheduleContent(_message.Message):
    __slots__ = ("task", "creation", "mutation")
    TASK_FIELD_NUMBER: _ClassVar[int]
    CREATION_FIELD_NUMBER: _ClassVar[int]
    MUTATION_FIELD_NUMBER: _ClassVar[int]
    task: ProjectTaskContent
    creation: ProjectTaskCreation
    mutation: ProjectTaskMutation
    def __init__(self, task: _Optional[_Union[ProjectTaskContent, _Mapping]] = ..., creation: _Optional[_Union[ProjectTaskCreation, _Mapping]] = ..., mutation: _Optional[_Union[ProjectTaskMutation, _Mapping]] = ...) -> None: ...

class FileDescription(_message.Message):
    __slots__ = ("name", "media_type", "plaintext_size", "created_by_user_id", "created_at", "updated_at")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    media_type: str
    plaintext_size: int
    created_by_user_id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., media_type: _Optional[str] = ..., plaintext_size: _Optional[int] = ..., created_by_user_id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FileMetadata(_message.Message):
    __slots__ = ("description", "original", "preview")
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_FIELD_NUMBER: _ClassVar[int]
    description: FileDescription
    original: ObjectLocator
    preview: PreviewMetadata
    def __init__(self, description: _Optional[_Union[FileDescription, _Mapping]] = ..., original: _Optional[_Union[ObjectLocator, _Mapping]] = ..., preview: _Optional[_Union[PreviewMetadata, _Mapping]] = ...) -> None: ...

class ObjectDescriptor(_message.Message):
    __slots__ = ("object_id", "exact_source_binding", "chunks", "ciphertext_size", "chunk_size")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    EXACT_SOURCE_BINDING_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_SIZE_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    exact_source_binding: bytes
    chunks: _containers.RepeatedCompositeFieldContainer[FileChunk]
    ciphertext_size: int
    chunk_size: int
    def __init__(self, object_id: _Optional[str] = ..., exact_source_binding: _Optional[bytes] = ..., chunks: _Optional[_Iterable[_Union[FileChunk, _Mapping]]] = ..., ciphertext_size: _Optional[int] = ..., chunk_size: _Optional[int] = ...) -> None: ...

class ObjectLocator(_message.Message):
    __slots__ = ("descriptor", "stream")
    DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    STREAM_FIELD_NUMBER: _ClassVar[int]
    descriptor: ObjectDescriptor
    stream: _crypto_pb2.StreamState
    def __init__(self, descriptor: _Optional[_Union[ObjectDescriptor, _Mapping]] = ..., stream: _Optional[_Union[_crypto_pb2.StreamState, _Mapping]] = ...) -> None: ...

class FileChunk(_message.Message):
    __slots__ = ("index", "plaintext_offset", "ciphertext_offset", "frame", "ciphertext_size")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    PLAINTEXT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_OFFSET_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_SIZE_FIELD_NUMBER: _ClassVar[int]
    index: int
    plaintext_offset: int
    ciphertext_offset: int
    frame: _crypto_pb2.StreamFrame
    ciphertext_size: int
    def __init__(self, index: _Optional[int] = ..., plaintext_offset: _Optional[int] = ..., ciphertext_offset: _Optional[int] = ..., frame: _Optional[_Union[_crypto_pb2.StreamFrame, _Mapping]] = ..., ciphertext_size: _Optional[int] = ...) -> None: ...

class PreviewMetadata(_message.Message):
    __slots__ = ("preview_id", "source_object_id", "profile", "codec", "filename", "media_type", "duration_seconds", "sample_rate", "channels", "object", "state", "processing_id", "job_id", "failure_code", "loudness")
    PREVIEW_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    CODEC_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MEDIA_TYPE_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PROCESSING_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAILURE_CODE_FIELD_NUMBER: _ClassVar[int]
    LOUDNESS_FIELD_NUMBER: _ClassVar[int]
    preview_id: str
    source_object_id: str
    profile: str
    codec: str
    filename: str
    media_type: str
    duration_seconds: float
    sample_rate: float
    channels: int
    object: ObjectLocator
    state: PreviewState
    processing_id: str
    job_id: str
    failure_code: str
    loudness: LoudnessMetadata
    def __init__(self, preview_id: _Optional[str] = ..., source_object_id: _Optional[str] = ..., profile: _Optional[str] = ..., codec: _Optional[str] = ..., filename: _Optional[str] = ..., media_type: _Optional[str] = ..., duration_seconds: _Optional[float] = ..., sample_rate: _Optional[float] = ..., channels: _Optional[int] = ..., object: _Optional[_Union[ObjectLocator, _Mapping]] = ..., state: _Optional[_Union[PreviewState, str]] = ..., processing_id: _Optional[str] = ..., job_id: _Optional[str] = ..., failure_code: _Optional[str] = ..., loudness: _Optional[_Union[LoudnessMetadata, _Mapping]] = ...) -> None: ...

class LoudnessMetadata(_message.Message):
    __slots__ = ("state", "policy_version", "integrated_loudness_lufs", "true_peak_dbtp", "loudness_range_lu", "target_integrated_loudness_lufs", "maximum_true_peak_dbtp", "maximum_boost_db", "recommended_gain_db")
    STATE_FIELD_NUMBER: _ClassVar[int]
    POLICY_VERSION_FIELD_NUMBER: _ClassVar[int]
    INTEGRATED_LOUDNESS_LUFS_FIELD_NUMBER: _ClassVar[int]
    TRUE_PEAK_DBTP_FIELD_NUMBER: _ClassVar[int]
    LOUDNESS_RANGE_LU_FIELD_NUMBER: _ClassVar[int]
    TARGET_INTEGRATED_LOUDNESS_LUFS_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_TRUE_PEAK_DBTP_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_BOOST_DB_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDED_GAIN_DB_FIELD_NUMBER: _ClassVar[int]
    state: LoudnessState
    policy_version: str
    integrated_loudness_lufs: float
    true_peak_dbtp: float
    loudness_range_lu: float
    target_integrated_loudness_lufs: float
    maximum_true_peak_dbtp: float
    maximum_boost_db: float
    recommended_gain_db: float
    def __init__(self, state: _Optional[_Union[LoudnessState, str]] = ..., policy_version: _Optional[str] = ..., integrated_loudness_lufs: _Optional[float] = ..., true_peak_dbtp: _Optional[float] = ..., loudness_range_lu: _Optional[float] = ..., target_integrated_loudness_lufs: _Optional[float] = ..., maximum_true_peak_dbtp: _Optional[float] = ..., maximum_boost_db: _Optional[float] = ..., recommended_gain_db: _Optional[float] = ...) -> None: ...

class FileUploadDraft(_message.Message):
    __slots__ = ("file_id", "metadata", "entry", "preview_profile", "state")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_PROFILE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    metadata: FileMetadata
    entry: ProjectEntryIntent
    preview_profile: str
    state: FileUploadState
    def __init__(self, file_id: _Optional[str] = ..., metadata: _Optional[_Union[FileMetadata, _Mapping]] = ..., entry: _Optional[_Union[ProjectEntryIntent, _Mapping]] = ..., preview_profile: _Optional[str] = ..., state: _Optional[_Union[FileUploadState, str]] = ...) -> None: ...

class PreviewUploadDraft(_message.Message):
    __slots__ = ("file_id", "metadata", "expected_file_revision", "expected_preview_id", "source_object_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FILE_REVISION_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_PREVIEW_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    metadata: FileMetadata
    expected_file_revision: int
    expected_preview_id: str
    source_object_id: str
    def __init__(self, file_id: _Optional[str] = ..., metadata: _Optional[_Union[FileMetadata, _Mapping]] = ..., expected_file_revision: _Optional[int] = ..., expected_preview_id: _Optional[str] = ..., source_object_id: _Optional[str] = ...) -> None: ...

class RecordContent(_message.Message):
    __slots__ = ("project", "stage", "comment_origin", "reply_origin", "thread_head", "text_head", "text_revision", "resolution", "directory_folder", "directory_file", "directory_leaf", "index_branch", "index_leaf", "directory_operations", "directory_deletion", "directory_deletion_stack", "chat_header", "chat_origin", "chat_event", "chat_message_head", "chat_operation", "chat_terminal", "schedule", "file_metadata", "file_upload", "preview_upload")
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    COMMENT_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    REPLY_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    THREAD_HEAD_FIELD_NUMBER: _ClassVar[int]
    TEXT_HEAD_FIELD_NUMBER: _ClassVar[int]
    TEXT_REVISION_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FOLDER_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_FILE_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_LEAF_FIELD_NUMBER: _ClassVar[int]
    INDEX_BRANCH_FIELD_NUMBER: _ClassVar[int]
    INDEX_LEAF_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_DELETION_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_DELETION_STACK_FIELD_NUMBER: _ClassVar[int]
    CHAT_HEADER_FIELD_NUMBER: _ClassVar[int]
    CHAT_ORIGIN_FIELD_NUMBER: _ClassVar[int]
    CHAT_EVENT_FIELD_NUMBER: _ClassVar[int]
    CHAT_MESSAGE_HEAD_FIELD_NUMBER: _ClassVar[int]
    CHAT_OPERATION_FIELD_NUMBER: _ClassVar[int]
    CHAT_TERMINAL_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    FILE_METADATA_FIELD_NUMBER: _ClassVar[int]
    FILE_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    PREVIEW_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    project: ProjectRootContent
    stage: ProjectStageContent
    comment_origin: CommentOrigin
    reply_origin: ReplyOrigin
    thread_head: ThreadHead
    text_head: TextHead
    text_revision: TextRevision
    resolution: ResolutionEvent
    directory_folder: DirectoryFolder
    directory_file: DirectoryFileLocator
    directory_leaf: DirectoryLeaf
    index_branch: OrderedIndexBranch
    index_leaf: OrderedIndexLeaf
    directory_operations: DirectoryOperations
    directory_deletion: DirectoryDeletion
    directory_deletion_stack: DirectoryDeletionStack
    chat_header: ChatHeader
    chat_origin: ChatOrigin
    chat_event: ChatEvent
    chat_message_head: ChatMessageHead
    chat_operation: ChatOperation
    chat_terminal: ChatTerminal
    schedule: ProjectScheduleContent
    file_metadata: FileMetadata
    file_upload: FileUploadDraft
    preview_upload: PreviewUploadDraft
    def __init__(self, project: _Optional[_Union[ProjectRootContent, _Mapping]] = ..., stage: _Optional[_Union[ProjectStageContent, _Mapping]] = ..., comment_origin: _Optional[_Union[CommentOrigin, _Mapping]] = ..., reply_origin: _Optional[_Union[ReplyOrigin, _Mapping]] = ..., thread_head: _Optional[_Union[ThreadHead, _Mapping]] = ..., text_head: _Optional[_Union[TextHead, _Mapping]] = ..., text_revision: _Optional[_Union[TextRevision, _Mapping]] = ..., resolution: _Optional[_Union[ResolutionEvent, _Mapping]] = ..., directory_folder: _Optional[_Union[DirectoryFolder, _Mapping]] = ..., directory_file: _Optional[_Union[DirectoryFileLocator, _Mapping]] = ..., directory_leaf: _Optional[_Union[DirectoryLeaf, _Mapping]] = ..., index_branch: _Optional[_Union[OrderedIndexBranch, _Mapping]] = ..., index_leaf: _Optional[_Union[OrderedIndexLeaf, _Mapping]] = ..., directory_operations: _Optional[_Union[DirectoryOperations, _Mapping]] = ..., directory_deletion: _Optional[_Union[DirectoryDeletion, _Mapping]] = ..., directory_deletion_stack: _Optional[_Union[DirectoryDeletionStack, _Mapping]] = ..., chat_header: _Optional[_Union[ChatHeader, _Mapping]] = ..., chat_origin: _Optional[_Union[ChatOrigin, _Mapping]] = ..., chat_event: _Optional[_Union[ChatEvent, _Mapping]] = ..., chat_message_head: _Optional[_Union[ChatMessageHead, _Mapping]] = ..., chat_operation: _Optional[_Union[ChatOperation, _Mapping]] = ..., chat_terminal: _Optional[_Union[ChatTerminal, _Mapping]] = ..., schedule: _Optional[_Union[ProjectScheduleContent, _Mapping]] = ..., file_metadata: _Optional[_Union[FileMetadata, _Mapping]] = ..., file_upload: _Optional[_Union[FileUploadDraft, _Mapping]] = ..., preview_upload: _Optional[_Union[PreviewUploadDraft, _Mapping]] = ...) -> None: ...
