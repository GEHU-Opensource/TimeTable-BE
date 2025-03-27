# Timetable Scheduling Backend

## 📚 Overview
Welcome to the **Timetable Scheduling Backend** repository! This project serves as the backend system for managing and automating the timetable scheduling process. Built with Django, it provides APIs, database management, and support for integrating with the Genetic Algorithm logic to create optimized timetables.


## 🔍 Key Features
- **Database Management**: Handles storage for teachers, rooms, courses, and scheduling data.
- **API Endpoints**: Provides RESTful APIs for interacting with the timetable data.
- **Admin Interface**: A built-in admin panel to manage data easily.
- **Integration Ready**: Designed to integrate seamlessly with the Genetic Algorithm logic for timetable generation.


## 🛠️ Installation
To run this backend project, follow these steps:

### Prerequisites
Ensure you have the following installed:
- Python 3.8+  
- pip  
- A virtual environment tool (e.g., `venv`)  
- Database system (MongoDB and PostgreSQL)  

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/GEHU-TimeTable-BE.git
   cd GEHU-TimeTable-BE
   ```

2. **Set Up the Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**:
   - Update the `DATABASES` setting in `timetable/settings.py` with your database credentials.

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser** (for the admin panel):
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```


## Access the app at `http://127.0.0.1:8000`
## Access the API Documentation at `https://documenter.getpostman.com/view/32556794/2sAYQggTLS`


## 🛠️ Features in Progress
- **Timetable Integration**: Integrate with the Genetic Algorithm logic to dynamically generate timetables based on constraints.
- **Authentication**: Add user roles (Admin, Faculty) for managing timetable access.
- **Enhanced Scheduling Options**: Support for recurring events, holidays, and priority-based scheduling.


## Star Developers:
- Special thanks to @vibha-chandola, for the endless efforts to make this happen.