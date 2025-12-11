# Event Management System

## Overview

The Event Management System is a RESTful API built with Django and Django REST Framework that allows users to create, manage, and interact with events. The system includes user authentication, event management, RSVP functionality, and review capabilities.

## Features

- **User Authentication**: JWT-based authentication with registration, login, and profile management
- **Event Management**: Create, read, update, and delete events with proper permissions
- **RSVP System**: Users can RSVP to events with status options (Going, Maybe, Not Going)
- **Review System**: Rate and comment on attended events
- **Access Control**: Private events accessible only to invited users
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Efficient data retrieval with paginated responses

## Technology Stack

- **Backend**: Django 4.x, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Django REST Framework Browsable API

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/Dhruvisha-Pandya/EventManagerAssignment
cd event-management-system
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure .env file**

```
SECRET_KEY=your-secret-key-here
DB_NAME=event_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
```

5. **run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a superuser**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

**The API will be available at http://localhost:8000/**

## API Endpoints

### 1. Authentication

- POST /api/accounts/register/ - Register new user
- POST /api/accounts/login/ - Login user
- GET /api/accounts/profile/ - Get user profile
- POST /api/token/ - Get JWT token
- POST /api/token/refresh/ - Refresh JWT token

### 2. Events

- GET /api/events/ - List all public events
- POST /api/events/ - Create new event
- GET /api/events/{id}/ - Get event details
- PUT /api/events/{id}/ - Update event
- DELETE /api/events/{id}/ - Delete event

### 3. RSVP

- POST /api/events/{id}/rsvp/ - Create RSVP
- PATCH /api/events/{id}/rsvp/{user_id}/ - Update RSVP status

### 4. Reviews

- POST /api/events/{id}/reviews/ - Create review
- GET /api/events/{id}/reviews/ - List event reviews

## Models

### UserProfile

```
Extends Django User model with:
full_name
bio
location
profile_picture
```

### Event

```
title, description, location
organizer (ForeignKey to User)
start_time, end_time
is_public (Boolean)
invited (ManyToMany to User)
```

### RSVP

```
event (ForeignKey)
user (ForeignKey)
status (Going, Maybe, Not Going)
```

### Review

```
event (ForeignKey)
user (ForeignKey)
rating (1-5)
comment
```

### Permissions

```
Only authenticated users can create events
Only event organizers can update or delete events
Private events are visible only to organizers and invited users
Users can only modify their own RSVPs and reviews
```

## Search, Filtering, and Pagination

```
Default pagination: 10 items per page
Search fields: title, description, location, organizer username
Ordering: start_time, created_at
Filtering: by is_public status
```

## Project Structure

```
event-management-system/
├── event_api/          # Project settings
├── accounts/           # User authentication app
├── events/             # Events, RSVP, Reviews app
├── requirements.txt    # Dependencies
└── README.md           # This file
```
