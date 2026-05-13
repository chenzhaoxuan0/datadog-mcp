from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MonitorSummary:
    id: int
    name: str = ""
    type: str = ""
    status: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict) -> MonitorSummary:
        return cls(
            id=d.get("id", 0),
            name=d.get("name", ""),
            type=d.get("type", ""),
            status=d.get("overall_state", ""),
            data=d,
        )


@dataclass(frozen=True)
class DashboardSummary:
    id: str
    title: str = ""
    author: str = ""
    modified: str = ""
    url: str = ""

    @classmethod
    def from_api(cls, d: dict) -> DashboardSummary:
        return cls(
            id=d.get("id", ""),
            title=d.get("title", ""),
            author=d.get("author", {}).get("handle", "") if isinstance(d.get("author"), dict) else "",
            modified=d.get("modified", ""),
            url=d.get("url", ""),
        )


@dataclass(frozen=True)
class MetricQueryResult:
    success: bool
    series: list[dict] = field(default_factory=list)
    from_ts: int = 0
    to_ts: int = 0
    error: str = ""


@dataclass(frozen=True)
class LogEntry:
    timestamp: str = ""
    message: str = ""
    service: str = ""
    status: str = ""
    attributes: dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict) -> LogEntry:
        attrs = d.get("attributes", {})
        return cls(
            timestamp=attrs.get("timestamp", ""),
            message=attrs.get("message", d.get("message", ""))[:500],
            service=attrs.get("service", ""),
            status=attrs.get("status", ""),
            attributes=attrs,
        )


@dataclass(frozen=True)
class IncidentSummary:
    id: str
    title: str = ""
    state: str = ""
    severity: str = ""
    created: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict) -> IncidentSummary:
        attrs = d.get("attributes", {})
        return cls(
            id=d.get("id", ""),
            title=attrs.get("title", ""),
            state=attrs.get("state", ""),
            severity=attrs.get("severity", ""),
            created=attrs.get("creation_time", ""),
            data=d,
        )


@dataclass(frozen=True)
class SLOSummary:
    id: str
    name: str = ""
    type: str = ""
    target: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict) -> SLOSummary:
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            type=d.get("type", {}).get("name", "") if isinstance(d.get("type"), dict) else "",
            target=d.get("target", 0.0),
            data=d,
        )


# --- Result types ---


@dataclass(frozen=True)
class ListMonitorsResult:
    success: bool
    monitors: list[MonitorSummary] = field(default_factory=list)
    error: str = ""


@dataclass(frozen=True)
class GetMonitorResult:
    success: bool
    monitor: MonitorSummary | None = None
    error: str = ""


@dataclass(frozen=True)
class ListDashboardsResult:
    success: bool
    dashboards: list[DashboardSummary] = field(default_factory=list)
    error: str = ""


@dataclass(frozen=True)
class GetDashboardResult:
    success: bool
    dashboard: dict[str, Any] = field(default_factory=dict)
    error: str = ""


@dataclass(frozen=True)
class SearchLogsResult:
    success: bool
    logs: list[LogEntry] = field(default_factory=list)
    error: str = ""


@dataclass(frozen=True)
class ListIncidentsResult:
    success: bool
    incidents: list[IncidentSummary] = field(default_factory=list)
    error: str = ""


@dataclass(frozen=True)
class ListSLOsResult:
    success: bool
    slos: list[SLOSummary] = field(default_factory=list)
    error: str = ""
