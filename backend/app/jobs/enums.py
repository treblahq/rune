from enum import StrEnum


class SourceType(StrEnum):
    Upload = "upload"
    Link = "link"


class JobStatus(StrEnum):
    Queued = "queued"
    Downloading = "downloading"
    Preparing = "preparing"
    Transcribing = "transcribing"
    Diarizing = "diarizing"
    Finalizing = "finalizing"
    Completed = "completed"
    Failed = "failed"
    Cancelled = "cancelled"


ACTIVE_JOB_STATUSES = frozenset(
    {
        JobStatus.Downloading,
        JobStatus.Preparing,
        JobStatus.Transcribing,
        JobStatus.Diarizing,
        JobStatus.Finalizing,
    }
)


TERMINAL_JOB_STATUSES = frozenset(
    {
        JobStatus.Completed,
        JobStatus.Failed,
        JobStatus.Cancelled,
    }
)


ALLOWED_JOB_TRANSITIONS: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.Queued: frozenset(
        {JobStatus.Downloading, JobStatus.Preparing, JobStatus.Cancelled, JobStatus.Failed}
    ),
    JobStatus.Downloading: frozenset({JobStatus.Preparing, JobStatus.Failed, JobStatus.Cancelled}),
    JobStatus.Preparing: frozenset({JobStatus.Transcribing, JobStatus.Failed, JobStatus.Cancelled}),
    JobStatus.Transcribing: frozenset(
        {
            JobStatus.Diarizing,
            JobStatus.Finalizing,
            JobStatus.Failed,
            JobStatus.Cancelled,
        }
    ),
    JobStatus.Diarizing: frozenset({JobStatus.Finalizing, JobStatus.Failed, JobStatus.Cancelled}),
    JobStatus.Finalizing: frozenset({JobStatus.Completed, JobStatus.Failed, JobStatus.Cancelled}),
    JobStatus.Completed: frozenset(),
    JobStatus.Failed: frozenset({JobStatus.Queued}),
    JobStatus.Cancelled: frozenset({JobStatus.Queued}),
}
