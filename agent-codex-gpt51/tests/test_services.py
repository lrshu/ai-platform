from __future__ import annotations

import pytest

from src.models import EmployeeProfile
from src.services import (
    MANDATORY_FOLLOWUPS,
    build_followup_tasks,
    build_profile,
    describe_role,
    verify_identity,
)


def test_verify_identity_success():
    doc = verify_identity(
        {
            "image_path": "id.jpg",
            "full_name": "张三",
            "id_number": "12345678901234567X",
        }
    )
    assert doc.is_valid is False
    assert "照片" in doc.feedback


def test_build_profile_checks_identity():
    identity = verify_identity(
        {
            "image_path": "id.jpg",
            "full_name": "李四",
            "id_number": "123456789012345678",
        }
    )
    profile = build_profile(
        {
            "full_name": "李四",
            "id_number": "123456789012345678",
            "university": "复旦大学",
            "degree": "本科",
            "role": "IT",
            "position": "后端工程师",
        },
        identity,
    )
    assert isinstance(profile, EmployeeProfile)


def test_describe_role_default():
    profile = EmployeeProfile(
        full_name="王五",
        id_number="123456789012345678",
        university="交大",
        degree="硕士",
        role="IT",
        position="不存在的岗位",
    )
    briefing = describe_role(profile)
    assert briefing.position == "不存在的岗位"
    assert len(briefing.responsibilities) == 3


@pytest.mark.parametrize("role", ["IT", "行政"])
def test_followup_tasks(role: str):
    profile = EmployeeProfile(
        full_name="赵六",
        id_number="123456789012345678",
        university="浙大",
        degree="博士",
        role=role,
        position="岗位",
    )
    tasks = build_followup_tasks(profile)
    assert tasks[: len(MANDATORY_FOLLOWUPS)] == MANDATORY_FOLLOWUPS
