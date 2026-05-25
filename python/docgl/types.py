from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Union

# ---------------------------------------------------------------------------
# Primitive types
# ---------------------------------------------------------------------------

# A table row is a flat dict of string → string | int | float
TableRow = dict[str, Union[str, int, float]]

# A variable value is a scalar or a list of table rows
VariableValue = Union[str, int, float, list[TableRow]]

# Key/value map for a single document render
DocumentVariables = dict[str, VariableValue]

# ---------------------------------------------------------------------------
# Request types
# ---------------------------------------------------------------------------


@dataclass
class DocumentInput:
    """A single document to be generated."""

    uuid: str
    """UUID of the template registered in Docgl."""

    filename: str
    """Output filename, e.g. ``"invoice-001.pdf"``."""

    data: list[DocumentVariables]
    """
    List of variable maps. Each entry produces one rendered PDF.
    Provide multiple entries to batch-render the same template with
    different data in a single request.
    """

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "filename": self.filename,
            "data": self.data,
        }


@dataclass
class GenerateRequest:
    """Body sent to ``POST /api/generate``."""

    documents: list[DocumentInput]

    storage_config_uuid: Optional[str] = None
    """
    UUID of a storage configuration registered in Docgl.
    When provided the generated PDF is uploaded to your bucket.
    """

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "documents": [d.to_dict() for d in self.documents],
        }
        if self.storage_config_uuid is not None:
            payload["storageConfigUuid"] = self.storage_config_uuid
        return payload


# ---------------------------------------------------------------------------
# Response types
# ---------------------------------------------------------------------------


@dataclass
class QueuedJob:
    job_id: str
    filename: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueuedJob":
        return cls(job_id=data["jobId"], filename=data["filename"])


@dataclass
class ValidationError:
    filename: str
    errors: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationError":
        return cls(filename=data["filename"], errors=data["errors"])


@dataclass
class GenerateResponse:
    """Response from ``POST /api/generate`` (HTTP 202)."""

    message: str
    queued: list[QueuedJob]
    errors: list[ValidationError] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerateResponse":
        return cls(
            message=data["message"],
            queued=[QueuedJob.from_dict(j) for j in data.get("queued", [])],
            errors=[ValidationError.from_dict(e) for e in data.get("errors", [])],
        )


@dataclass
class JobStatusResponse:
    """Response from ``GET /api/generate/:jobId`` (HTTP 200)."""

    job_id: str
    filename: Optional[str]
    status: str
    """One of: ``waiting``, ``active``, ``completed``, ``failed``, ``delayed``, ``unknown``."""
    result: Any
    failed_reason: Optional[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobStatusResponse":
        return cls(
            job_id=data["jobId"],
            filename=data.get("filename"),
            status=data["status"],
            result=data.get("result"),
            failed_reason=data.get("failedReason"),
        )
