from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Optional, Type
from uuid import UUID

import pytest
from pydantic import (
    UUID3,
    UUID4,
    BaseModel,
    EmailStr,
    HttpUrl,
    IPvAnyAddress,
    ValidationError,
)
from pydantic.types import NegativeInt

from dydantic import create_model_from_schema


class StatusEnum(str, Enum):
    planning = "planning"
    active = "active"
    completed = "completed"
    archived = "archived"


class RoleEnum(str, Enum):
    owner = "owner"
    admin = "admin"
    contributor = "contributor"
    viewer = "viewer"


class TaskStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Member(BaseModel):
    user_id: UUID4
    role: RoleEnum
    joined_date: datetime


class SubTask(BaseModel):
    sub_task_id: UUID3
    name: str
    status: TaskStatusEnum


class Task(BaseModel):
    task_id: UUID
    name: str
    task_description: Optional[str] = None
    status: TaskStatusEnum
    priority: PriorityEnum
    assigned_to: List[UUID4] = []
    due_date: datetime
    sub_tasks: List[SubTask]


class Project(BaseModel):
    project_id: UUID4
    project_name: str
    start_date: datetime
    end_date: datetime
    status: StatusEnum
    budget: Optional[float] = None
    days_left: Optional[NegativeInt] = None
    members: List[Member] = []
    tasks: List[Task] = []


@pytest.mark.parametrize(
    "x, error_message",
    [
        # Test case 1: Valid input
        (
            {
                "project_id": "3dd68ce0-91af-4782-8fe0-3e5fd4ff9a57",
                "project_name": "Test Project",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2022-01-31T23:59:59Z",
                "status": "active",
                "budget": 1000.0,
                "members": [
                    {
                        "user_id": "ac77f482-0033-41d0-9f50-4730c6799661",
                        "role": "owner",
                        "joined_date": "2022-01-01T00:00:00Z",
                    },
                    {
                        "user_id": "ac77f482-0033-41d0-9f50-4730c6799661",
                        "role": "contributor",
                        "joined_date": "2022-01-02T00:00:00Z",
                    },
                ],
                "tasks": [
                    {
                        "task_id": "ac77f482-0033-41d0-9f50-4730c6799661",
                        "name": "Task 1",
                        "status": "not_started",
                        "priority": "medium",
                        "assigned_to": [
                            "ac77f482-0033-41d0-9f50-4730c6799661",
                            "ac77f482-0033-41d0-9f50-4730c6799661",
                        ],
                        "due_date": "2022-01-10T23:59:59Z",
                        "sub_tasks": [
                            {
                                "sub_task_id": "9073926b-929f-31c2-abc9-fad77ae3e8eb",
                                "name": "Subtask 1",
                                "status": "not_started",
                            },
                            {
                                "sub_task_id": "9073926b-929f-31c2-abc9-fad77ae3e8eb",
                                "name": "Subtask 2",
                                "status": "not_started",
                            },
                        ],
                    }
                ],
            },
            None,
        ),
        (
            {
                "project_id": "3dd68ce0-91af-4782-8fe0-3e5fd4ff9a57",
                "project_name": "Test Project",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "My favorite day",
                "status": "active",
                "budget": 1000.0,
                "members": [],
                "tasks": [],
            },
            "1 validation error for Project\nend_date\n",
        ),
        # Test task ID is not a valid UUID
        (
            {
                "project_id": "3dd68ce0-91af-4782-8fe0-3e5fd4ff9a57",
                "project_name": "Test Project",
                "start_date": "2022-01-01T00:00:00Z",
                "end_date": "2022-01-31T23:59:59Z",
                "status": "active",
                "budget": 1000.0,
                "members": [],
                "tasks": [
                    {
                        # Bad UUID
                        "task_id": "Z23e4567-e89b-12d3-a456-426614174003",
                        "name": "Task 1",
                        "task_description": "Description 1",
                        "status": "not_started",
                        "priority": "medium",
                        "assigned_to": [],
                        "due_date": "2022-01-10T23:59:59Z",
                        "sub_tasks": [],
                    }
                ],
            },
            "1 validation error for Project\ntasks",
        ),
    ],
)
def test_nested_create_model_from_schema(x: dict, error_message: Optional[str]):
    model = create_model_from_schema(Project.model_json_schema())
    if not error_message:
        model.model_validate(x)
    else:
        with pytest.raises(ValidationError, match=error_message):
            model.model_validate(x)


class DateModel(BaseModel):
    date_field: date


class TimeModel(BaseModel):
    time_field: time


class DateTimeModel(BaseModel):
    datetime_field: datetime


class DurationModel(BaseModel):
    duration_field: timedelta


class EmailModel(BaseModel):
    email_field: EmailStr


class IPv4Model(BaseModel):
    ipv4_field: IPvAnyAddress


class IPv6Model(BaseModel):
    ipv6_field: IPvAnyAddress


class UriModel(BaseModel):
    uri_field: HttpUrl


class UuidModel(BaseModel):
    uuid_field: UUID


@pytest.mark.parametrize(
    "model, inputs",
    [
        (DateModel, {"date_field": "2022-01-01"}),
        (DateModel, {"date_field": "invalid-date"}),
        (TimeModel, {"time_field": "12:34:56"}),
        (TimeModel, {"time_field": "invalid-time"}),
        (DateTimeModel, {"datetime_field": "2022-01-01T12:34:56Z"}),
        (DateTimeModel, {"datetime_field": "invalid-datetime"}),
        (DurationModel, {"duration_field": "P3DT12H30M5S"}),
        (DurationModel, {"duration_field": "invalid-duration"}),
        (EmailModel, {"email_field": "user@example.com"}),
        (EmailModel, {"email_field": "invalid-email"}),
        (IPv4Model, {"ipv4_field": "192.168.0.1"}),
        (IPv4Model, {"ipv4_field": "invalid-ipv4"}),
        (IPv6Model, {"ipv6_field": "2001:db8::8a2e:370:7334"}),
        (IPv6Model, {"ipv6_field": "invalid-ipv6"}),
        (UriModel, {"uri_field": "https://example.com"}),
        (UriModel, {"uri_field": "invalid-uri"}),
        (UuidModel, {"uuid_field": "123e4567-e89b-12d3-a456-426614174000"}),
        (UuidModel, {"uuid_field": "invalid-uuid"}),
    ],
)
def test_create_model_from_schema_formats(model: Type[BaseModel], inputs: dict):
    dynamic_model = create_model_from_schema(model.model_json_schema())
    dynamic_model.schema_json()  # test it is serializable
    dynamic_model.model_json_schema()  # test it is serializable using the v2 schema
    error = None
    try:
        model.model_validate(inputs)
    except Exception as e:
        error = str(e)
    if not error:
        result = dynamic_model.model_validate(inputs)
        dynamic_model.model_validate(result.model_dump())
    else:
        with pytest.raises(Exception):
            dynamic_model.model_validate(inputs)


# Enum tests
class ColorEnum(str, Enum):
    red = "red"
    green = "green"
    blue = "blue"


class SizeEnum(int, Enum):
    small = 1
    medium = 2
    large = 3


class InlineEnumModel(BaseModel):
    color: ColorEnum
    size: SizeEnum


def test_enum_string_validation():
    """Test that string enum values are properly validated."""
    schema = InlineEnumModel.model_json_schema()
    DynamicModel = create_model_from_schema(schema)
    
    # Valid enum values should work
    valid_data = {"color": "red", "size": 2}
    result = DynamicModel.model_validate(valid_data)
    assert result.color.value == "red"
    assert result.size.value == 2
    
    # Invalid enum values should be rejected
    invalid_data = {"color": "yellow", "size": 2}
    with pytest.raises(ValidationError) as exc_info:
        DynamicModel.model_validate(invalid_data)
    assert "color" in str(exc_info.value)


def test_enum_integer_validation():
    """Test that integer enum values are properly validated."""
    schema = InlineEnumModel.model_json_schema()
    DynamicModel = create_model_from_schema(schema)
    
    # Valid enum values should work
    valid_data = {"color": "blue", "size": 3}
    result = DynamicModel.model_validate(valid_data)
    assert result.size.value == 3
    
    # Invalid enum values should be rejected
    invalid_data = {"color": "red", "size": 99}
    with pytest.raises(ValidationError) as exc_info:
        DynamicModel.model_validate(invalid_data)
    assert "size" in str(exc_info.value)


def test_enum_ref_resolution():
    """Test that enums referenced via $ref in $defs are properly handled."""
    # Use the existing Project model which has enums in $defs
    schema = Project.model_json_schema()
    DynamicProject = create_model_from_schema(schema)
    
    # Valid data with proper enum values
    valid_data = {
        "project_id": "3dd68ce0-91af-4782-8fe0-3e5fd4ff9a57",
        "project_name": "Test Project",
        "start_date": "2022-01-01T00:00:00Z",
        "end_date": "2022-01-31T23:59:59Z",
        "status": "active",
    }
    result = DynamicProject.model_validate(valid_data)
    assert result.status.value == "active"
    
    # Invalid enum value should be rejected
    invalid_data = valid_data.copy()
    invalid_data["status"] = "invalid_status"
    with pytest.raises(ValidationError) as exc_info:
        DynamicProject.model_validate(invalid_data)
    assert "status" in str(exc_info.value)


def test_enum_roundtrip():
    """Test roundtrip: Pydantic model -> JSON schema -> dynamic model."""
    # Original model with enum
    original_data = {"color": "green", "size": 2}
    original_instance = InlineEnumModel.model_validate(original_data)
    
    # Generate schema and create dynamic model
    schema = InlineEnumModel.model_json_schema()
    DynamicModel = create_model_from_schema(schema)
    
    # Validate same data with dynamic model
    dynamic_instance = DynamicModel.model_validate(original_data)
    
    # Values should match
    assert dynamic_instance.color.value == original_instance.color.value
    assert dynamic_instance.size.value == original_instance.size.value
    
    # Serialized forms should be compatible
    assert dynamic_instance.model_dump() == original_instance.model_dump()


def test_enum_in_nested_model():
    """Test that enums work in nested models."""
    # Project model has nested Member with RoleEnum
    schema = Project.model_json_schema()
    DynamicProject = create_model_from_schema(schema)
    
    data = {
        "project_id": "3dd68ce0-91af-4782-8fe0-3e5fd4ff9a57",
        "project_name": "Test Project",
        "start_date": "2022-01-01T00:00:00Z",
        "end_date": "2022-01-31T23:59:59Z",
        "status": "planning",
        "members": [
            {
                "user_id": "ac77f482-0033-41d0-9f50-4730c6799661",
                "role": "admin",
                "joined_date": "2022-01-01T00:00:00Z",
            }
        ],
    }
    
    result = DynamicProject.model_validate(data)
    assert result.members[0].role.value == "admin"
    
    # Invalid role should be rejected
    data["members"][0]["role"] = "invalid_role"
    with pytest.raises(ValidationError) as exc_info:
        DynamicProject.model_validate(data)
    assert "role" in str(exc_info.value).lower()


def test_const_keyword():
    """Test that const keyword is handled as Literal type."""
    schema = {
        "title": "ConstModel",
        "type": "object",
        "properties": {
            "constant_value": {"const": "fixed"},
            "number_const": {"const": 42},
        },
        "required": ["constant_value", "number_const"],
    }
    
    DynamicModel = create_model_from_schema(schema)
    
    # Valid data with correct const values
    valid_data = {"constant_value": "fixed", "number_const": 42}
    result = DynamicModel.model_validate(valid_data)
    assert result.constant_value == "fixed"
    assert result.number_const == 42
    
    # Invalid const value should be rejected
    invalid_data = {"constant_value": "different", "number_const": 42}
    with pytest.raises(ValidationError) as exc_info:
        DynamicModel.model_validate(invalid_data)
    assert "constant_value" in str(exc_info.value)


def test_inline_enum_in_schema():
    """Test enum defined inline in a schema property (not in $defs)."""
    schema = {
        "title": "InlineEnumSchema",
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["pending", "approved", "rejected"],
                "title": "Status",
            },
            "priority": {
                "type": "integer",
                "enum": [1, 2, 3],
                "title": "Priority",
            },
        },
        "required": ["status", "priority"],
    }
    
    DynamicModel = create_model_from_schema(schema)
    
    # Valid data
    valid_data = {"status": "approved", "priority": 2}
    result = DynamicModel.model_validate(valid_data)
    assert result.status.value == "approved"
    assert result.priority.value == 2
    
    # Invalid status
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"status": "unknown", "priority": 2})
    
    # Invalid priority
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"status": "pending", "priority": 99})


def test_mixed_type_enum():
    """Test enum with mixed types (no type specified in schema)."""
    schema = {
        "title": "MixedTypeEnumModel",
        "type": "object",
        "properties": {
            "mixed_field": {
                "enum": ["option_a", 1, "option_b", 2],
                "title": "MixedField",
            }
        },
        "required": ["mixed_field"],
    }
    
    DynamicModel = create_model_from_schema(schema)
    
    # Valid string value
    result1 = DynamicModel.model_validate({"mixed_field": "option_a"})
    assert result1.mixed_field.value == "option_a"
    
    # Valid integer value
    result2 = DynamicModel.model_validate({"mixed_field": 1})
    assert result2.mixed_field.value == 1
    
    # Invalid value should be rejected
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"mixed_field": "invalid"})
