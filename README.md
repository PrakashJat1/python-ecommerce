Django E-commerce Web Application

A complete e-commerce web application built with Django and PostgreSQL.
The project supports multiple roles (User, Seller, Delivery Team) and covers the core functionality of a modern online store – from product listings to secure checkout.

  Features

Authentication & Roles

User registration and login with OTP verification

Role-based access for Users, Sellers, and Delivery Team

Product Management

Add, edit, and manage products (Seller dashboard)

Product listing with search, category filter, and pagination

Product detail pages with dynamic slug URLs

Shopping Experience

Add to Cart and Wishlist functionality

Manage saved addresses (Add, Update, Delete)

Checkout flow with COD and Online Payment options

Order & Payment

Place orders and track them from the profile

Integrated payment gateway for online payments

Order confirmation email on successful purchase

Profile Management

Upload profile picture

Update personal details

Change password

View past orders

Performance Optimization

Emails (OTP, order confirmation) handled via Celery + Redis for async background tasks

  Tech Stack

Backend: Django, Django REST Framework

Database: PostgreSQL

Async Tasks: Celery, Redis

Frontend: HTML, Bootstrap

Other: SMTP (for emails), Payment Gateway Integration

  Project Setup

Clone the repository:

git clone git@github.com:PrakashJat1/python-ecommerce.git
cd django-ecommerce


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Setup database (PostgreSQL):

Create a new database

Update settings.py with your DB credentials

Run migrations:

python manage.py migrate


Start the development server:

python manage.py runserver
