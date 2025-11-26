from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime

from server.models import AccountType, AuditOutcome, AuditRecord

LOGGER = logging.getLogger("mcp.audit")


class AuditLogger:
    def __init__(self) -> None:
        self.logger = LOGGER

    def _mask_id(self, national_id: str) -> str:
        return f"{national_id[:3]}****{national_id[-4:]}"

    def log_event(
        self,
        *,
        national_id: str,
        request_type: AccountType,
        outcome: AuditOutcome,
        detail: str | None = None,
        start_time: float | None = None,
    ) -> AuditRecord:
        audit_id = uuid.uuid4().hex
        created_at = datetime.utcnow()
        masked_id = self._mask_id(national_id)
        latency_ms = None
        if start_time is not None:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        record = AuditRecord(
            audit_id=audit_id,
            masked_id=masked_id,
            request_type=request_type,
            outcome=outcome,
            created_at=created_at,
            detail=detail,
        )
        extra = {"audit_id": audit_id, "masked_id": masked_id, "latency_ms": latency_ms}
        self.logger.info(
            "Audit event", extra={k: v for k, v in extra.items() if v is not None}
        )
        return record


def create_audit_logger() -> AuditLogger:
    return AuditLogger()
