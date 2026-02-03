Published services URL : https://hrms-backend-prod.onrender.com

# HRMS Lite

A lightweight Human Resource Management System built with FastAPI and React.

## Live Demo

- **Frontend**: https://hrmanagemntsyslite.netlify.app
- **Backend API**: https://hrms-backend-prod.onrender.com

## Features

- ✅ Employee Management (Add, View, Delete)
- ✅ Attendance Tracking (Mark Present/Absent)
- ✅ Date-based Attendance Filtering
- ✅ Dashboard with Statistics
- ✅ Responsive Design
- ✅ Form Validations
- ✅ Error Handling

## Tech Stack

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL (Production) / SQLite (Development)
- Uvicorn

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

**Deployment:**
- Backend: Render
- Frontend: Vercel

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
