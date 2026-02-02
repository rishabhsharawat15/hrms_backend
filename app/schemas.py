from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"

# Employee Schemas
class EmployeeBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=50)

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    
    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceBase(BaseModel):
    date: date
    status: AttendanceStatus

class AttendanceCreate(AttendanceBase):
    employee_id: int

class AttendanceResponse(AttendanceBase):
    id: int
    employee_id: int
    
    class Config:
        from_attributes = True

class AttendanceWithEmployee(AttendanceResponse):
    employee: EmployeeResponse
    
    class Config:
        from_attributes = True

# Dashboard Schema
class DashboardStats(BaseModel):
    total_employees: int
    total_attendance_today: int
    present_today: int
    absent_today: int

class EmployeeAttendanceSummary(BaseModel):
    employee: EmployeeResponse
    total_present: int
    total_absent: int