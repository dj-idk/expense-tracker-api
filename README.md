# FastAPI Expense Management API

## Overview

This is a FastAPI-based expense management application that allows users to register, authenticate, and manage their expenses. The API provides endpoints for CRUD operations on expenses and expense categories, as well as filtering and searching functionalities.

## Features

- User authentication (registration & login)
- Expense tracking (add, update, delete, search, filter by weeks & category)
- Expense categories management (add, update, delete, list)
- Health check endpoint

### Clone the Repository

```bash
git clone <https://github.com/dj-idk/expense-tracker-api.git>
cd <expense-tracker-api>
```

### Install Dependencies

Create a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Running the Server

To start the FastAPI server, use:

```bash
python manage.py runserver --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### **Default**

| Method | Endpoint   | Description      |
| ------ | ---------- | ---------------- |
| GET    | `/healthy` | Check API health |

### **User Management**

| Method | Endpoint    | Description                                     |
| ------ | ----------- | ----------------------------------------------- |
| POST   | `/register` | Register a new user                             |
| POST   | `/token`    | Authenticate user and get token                 |
| GET    | `/users/me` | Get details of the currently authenticated user |

### **Expense Management**

| Method | Endpoint                        | Description                              |
| ------ | ------------------------------- | ---------------------------------------- |
| POST   | `/expense/`                     | Add an expense                           |
| GET    | `/expense/`                     | Get all expenses                         |
| PUT    | `/expense/{expense_id}`         | Update an expense                        |
| DELETE | `/expense/{expense_id}`         | Delete an expense                        |
| GET    | `/expense/search/{description}` | Search expenses by description           |
| GET    | `/expense/weekly/{weeks}`       | Get expenses from the last `weeks` weeks |

### **Expense Categories**

| Method | Endpoint                          | Description              |
| ------ | --------------------------------- | ------------------------ |
| POST   | `/expense/category`               | Create a new category    |
| GET    | `/expense/category`               | List all categories      |
| PUT    | `/expense/category/{category_id}` | Update a category        |
| DELETE | `/expense/category/{category_id}` | Delete a category        |
| GET    | `/expense/category/{category}`    | Get expenses by category |

## Seeding Fake Expenses

To populate the database with fake expenses, run:

```bash
python manage.py seed --expense 100
```

This will generate 100 fake expense records.
