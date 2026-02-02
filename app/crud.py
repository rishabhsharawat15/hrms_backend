from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import date
from typing import List, Optional
from fastapi import HTTPException

from app import models, schemas

# Employee CRUD
def get_employee_by_id(db: Session, employee_id: str):
    return db.query(models.Employee).filter(models.Employee.employee_id == employee_id).first()

def get_employee_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_employee_by_db_id(db: Session, db_id: int):
    return db.query(models.Employee).filter(models.Employee.id == db_id).first()

def get_all_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    # Check for duplicate employee_id
    if get_employee_by_id(db, employee.employee_id):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Check for duplicate email
    if get_employee_by_email(db, employee.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    try:
        db.commit()
        db.refresh(db_employee)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Employee already exists")
    return db_employee

def delete_employee(db: Session, db_id: int):
    db_employee = get_employee_by_db_id(db, db_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return db_employee

# Attendance CRUD
def get_attendance_by_employee_and_date(db: Session, employee_id: int, date: date):
    return db.query(models.Attendance).filter(
        and_(
            models.Attendance.employee_id == employee_id,
            models.Attendance.date == date
        )
    ).first()

def get_attendance_by_employee(db: Session, employee_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id
    ).offset(skip).limit(limit).all()

def get_all_attendance(db: Session, skip: int = 0, limit: int = 100, date_filter: Optional[date] = None):
    query = db.query(models.Attendance)
    if date_filter:
        query = query.filter(models.Attendance.date == date_filter)
    return query.offset(skip).limit(limit).all()

def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    # Verify employee exists
    employee = get_employee_by_db_id(db, attendance.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if attendance already exists for this date
    existing = get_attendance_by_employee_and_date(db, attendance.employee_id, attendance.date)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Attendance already marked for this date. Please update instead."
        )
    
    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_employee_attendance_summary(db: Session, employee_id: int):
    present_count = db.query(models.Attendance).filter(
        and_(
            models.Attendance.employee_id == employee_id,
            models.Attendance.status == models.AttendanceStatus.PRESENT
        )
    ).count()
    
    absent_count = db.query(models.Attendance).filter(
        and_(
            models.Attendance.employee_id == employee_id,
            models.Attendance.status == models.AttendanceStatus.ABSENT
        )
    ).count()
    
    return {"present": present_count, "absent": absent_count}

def get_dashboard_stats(db: Session):
    today = date.today()
    
    total_employees = db.query(models.Employee).count()
    
    today_attendance = db.query(models.Attendance).filter(
        models.Attendance.date == today
    )
    
    present_today = today_attendance.filter(
        models.Attendance.status == models.AttendanceStatus.PRESENT
    ).count()
    
    absent_today = today_attendance.filter(
        models.Attendance.status == models.AttendanceStatus.ABSENT
    ).count()
    
    return {
        "total_employees": total_employees,
        "total_attendance_today": present_today + absent_today,
        "present_today": present_today,
        "absent_today": absent_today
    }
