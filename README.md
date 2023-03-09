This project was to create a CRUD backend server application using the Python programming language (Python 3)
and the server framework Django. It was suggest additionally the "Django REST Framework" to be used.

Requirements it had to fulfill:
- Use a version control system (suggestion: git) while developing your app (and use meaningful commit messages).
- Write tests covering your codebase to > 80%
- Create a test-coverage report (e.g. with pip package 'coverage')
- Write readable and consistently formatted/presented code (see: PEP8)
- Create some objects in your database to show how they relate to each other, so you can present your results.
- Please document and comment your code as seen fit.

Optional Requirements:
- Document and validate the API using OpenAPI / Swagger / other similar tool.
- Document your result with some UML diagrams
- Allow an Employee to have multiple work arrangements (e.g. Two 50% jobs) (1:n relationships)

App Description:
The assignment is to write a fictional company's employee management system. This company is organized in separate teams of
employees with one team leader per team. Every employee has an hourly rate they get paid for their work. Not everybody in the
company is a full time employee. Team leaders are paid an additional 10% for their work.
Create an API which lets the company's accountant retrieve the list of employees with their respective pay for the month.

Details:
- Create Objects:
- Employee - Name
- Employee ID
- Which team they are a part of - Hourly Rate
- Team
- Team Leader
- Team Employee
- Work Arrangement (worktime)
- Full-time (40h/week)
- Part-time
- Percentage (e.g. 75% of 40h => 30h)

Hints:
- You will need 5 routes per object
- Get all objects
- Get single specific object
- Create new object
- Change an object's values - Delete an object
- You can test your routes using using "curl" - Use foreign keys for some of the relations

