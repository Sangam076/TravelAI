<<<<<<< HEAD
# AI-Powered-Travel-Planner
All-in-One Travel App
=======
# Blog-Everyday

## Overview

Blog-Everyday is a feature-rich blogging platform built using the Django framework for the backend and Tailwind CSS for the frontend. The platform enables users to perform CRUD operations on blog posts, create and manage profiles, and interact with other users through comments and blog posts. It also integrates TinyMCE, a rich text editor, for enhanced blog post customization. The website features an authentication system with user registration and login, and the admin section is protected and accessible only by superusers.

## Features

- **User Authentication**: 
  - Users can register, log in, and manage their sessions.
  - Authentication system is built with Django's built-in user model and session management.
  
- **Profile Management**: 
  - Users can view and edit their own profiles.
  - Users can view other profiles and explore their blog posts.

- **CRUD Operations for Blog Posts**: 
  - Users can create, read, update, and delete their own blog posts.
  - Rich text editing is enabled for blog posts using **TinyMCE** for better customization.

- **Tailwind CSS Integration**: 
  - The frontend is styled using **Tailwind CSS** to create a modern, responsive, and customizable interface.

- **Admin Section**: 
  - The admin section is secured and can only be accessed by superusers.

## Technologies Used

- **Backend**: Django (Python Web Framework)
- **Frontend**: Tailwind CSS, Html, Javascript
- **Rich Text Editor**: TinyMCE (for blog post creation and customization)
- **Database**: SQLite 
- **Authentication**: Django’s built-in authentication system
- **Admin Panel**: Django's Admin, restricted to superusers only

## Installation

To set up this project locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sangam076/Blog-Everyday.git

2. **Navigate to the project directory**:
   ```bash
   cd Blog-Everyday

3. **Apply database migrations: Set up the database by running the migrations**:
   ```bash
   python manage.py migrate
   
4.  **Create a superuser (optional, for accessing the admin panel)**:
    ```bash
    python manage.py createsuperuser


6. **Run the development server: Start the Django development server to view the application**:
   ```bash
   python manage.py runserver

7. **The website will be available at http://127.0.0.1:8000/.**

Usage
User Authentication:
Register and log in to start creating, editing, and managing blog posts.

Profile:
View your own profile and the profiles of other users. You can edit your own profile details.

Blog Management:
Use the TinyMCE editor to write and customize your blog posts with rich text formatting.
Admin Access:
The admin section is available to superusers for managing blog posts, users, and other data.

Contributing
Contributions are welcome! To contribute to the project:
Fork the repository.
Create a new branch (git checkout -b feature-name).
Make your changes and commit them (git commit -am 'Add new feature').
Push your changes to your fork (git push origin feature-name).
Submit a pull request for review.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
Django: The framework powering the backend and API.
Tailwind CSS: For building the responsive and modern user interface.
TinyMCE: For the rich text editor functionality.
Django Admin: For managing and administrating the application content.
markdown


### Key sections:

- **Overview**: A clear description of the project, its features, and its purpose.
- **Features**: A detailed list of functionalities, highlighting CRUD operations, profile management, and TinyMCE integration.
- **Technologies Used**: A summary of the tech stack.
- **Installation**: A step-by-step guide for setting up the project locally.
- **Usage**: Instructions on how users can interact with the platform after installation.
- **Contributing**: How others can contribute to the project.
- **License**: MIT license.
- **Acknowledgements**: Credit to the key technologies and frameworks used.


>>>>>>> e97332c (Initial commit - Travel Planner App)
