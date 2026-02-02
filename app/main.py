from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app import models, schemas, crud
from app.database import engine, get_db, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HRMS Lite API",
    description="Lightweight Human Resource Management System",
    version="1.0.0"
)

# CORS Configuration - Update with your frontend URL in production
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "https://your-frontend-url.vercel.app",  # Update after deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def read_root():
    return {"message": "HRMS Lite API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Employee Endpoints
@app.post("/api/employees", response_model=schemas.EmployeeResponse, status_code=201)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db=db, employee=employee)

@app.get("/api/employees", response_model=List[schemas.EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud.get_all_employees(db, skip=skip, limit=limit)
    return employees

@app.get("/api/employees/{employee_id}", response_model=schemas.EmployeeResponse)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee_by_db_id(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.delete("/api/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    crud.delete_employee(db, db_id=employee_id)
    return None

# Attendance Endpoints
@app.post("/api/attendance", response_model=schemas.AttendanceResponse, status_code=201)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    return crud.create_attendance(db=db, attendance=attendance)

@app.get("/api/attendance", response_model=List[schemas.AttendanceWithEmployee])
def read_attendance(
    date: Optional[date] = None,
    employee_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    if employee_id:
        attendances = db.query(models.Attendance).filter(
            models.Attendance.employee_id == employee_id
        ).offset(skip).limit(limit).all()
    else:
        attendances = crud.get_all_attendance(db, skip=skip, limit=limit, date_filter=date)
    return attendances

@app.get("/api/employees/{employee_id}/attendance", response_model=List[schemas.AttendanceResponse])
def read_employee_attendance(employee_id: int, db: Session = Depends(get_db)):
    return crud.get_attendance_by_employee(db, employee_id=employee_id)

@app.get("/api/employees/{employee_id}/attendance/summary")
def get_attendance_summary(employee_id: int, db: Session = Depends(get_db)):
    # Verify employee exists
    employee = crud.get_employee_by_db_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud.get_employee_attendance_summary(db, employee_id)

# Dashboard Endpoints
@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@app.get("/api/dashboard/attendance-summary", response_model=List[schemas.EmployeeAttendanceSummary])
def get_all_attendance_summaries(db: Session = Depends(get_db)):
    employees = crud.get_all_employees(db)
    result = []
    for emp in employees:
        summary = crud.get_employee_attendance_summary(db, emp.id)
        result.append({
            "employee": emp,
            "total_present": summary["present"],
            "total_absent": summary["absent"]
        })
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)