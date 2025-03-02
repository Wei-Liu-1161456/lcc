"""Script to generate password hashes for one or more user accounts.

This script generates bcrypt password hashes for all the initial user accounts
required for the LCC Issue Tracker application. It creates hashes for:
- 20 visitors
- 5 helpers
- 2 administrators

The generated hashes will be used in the populate_database.sql script.
"""
from collections import namedtuple
from flask import Flask
from flask_bcrypt import Bcrypt

# Define a UserAccount named tuple to store username, password, and role
UserAccount = namedtuple('UserAccount', ['username', 'password', 'role'])

app = Flask(__name__)
flask_bcrypt = Bcrypt(app)

# List of users for the LCC Issue Tracker
# Format: UserAccount(username, password, role)
users = [
    # Visitors (20)
    UserAccount('visitor1', 'Visitor1Pass!', 'visitor'),
    UserAccount('visitor2', 'Visitor2Pass!', 'visitor'),
    UserAccount('visitor3', 'Visitor3Pass!', 'visitor'),
    UserAccount('visitor4', 'Visitor4Pass!', 'visitor'),
    UserAccount('visitor5', 'Visitor5Pass!', 'visitor'),
    UserAccount('visitor6', 'Visitor6Pass!', 'visitor'),
    UserAccount('visitor7', 'Visitor7Pass!', 'visitor'),
    UserAccount('visitor8', 'Visitor8Pass!', 'visitor'),
    UserAccount('visitor9', 'Visitor9Pass!', 'visitor'),
    UserAccount('visitor10', 'Visitor10Pass!', 'visitor'),
    UserAccount('visitor11', 'Visitor11Pass!', 'visitor'),
    UserAccount('visitor12', 'Visitor12Pass!', 'visitor'),
    UserAccount('visitor13', 'Visitor13Pass!', 'visitor'),
    UserAccount('visitor14', 'Visitor14Pass!', 'visitor'),
    UserAccount('visitor15', 'Visitor15Pass!', 'visitor'),
    UserAccount('visitor16', 'Visitor16Pass!', 'visitor'),
    UserAccount('visitor17', 'Visitor17Pass!', 'visitor'),
    UserAccount('visitor18', 'Visitor18Pass!', 'visitor'),
    UserAccount('visitor19', 'Visitor19Pass!', 'visitor'),
    UserAccount('visitor20', 'Visitor20Pass!', 'visitor'),
    
    # Helpers (5)
    UserAccount('helper1', 'Helper1Pass!', 'helper'),
    UserAccount('helper2', 'Helper2Pass!', 'helper'),
    UserAccount('helper3', 'Helper3Pass!', 'helper'),
    UserAccount('helper4', 'Helper4Pass!', 'helper'),
    UserAccount('helper5', 'Helper5Pass!', 'helper'),
    
    # Administrators (2)
    UserAccount('admin1', 'Admin1Pass!', 'admin'),
    UserAccount('admin2', 'Admin2Pass!', 'admin')
]

print('Username | Password | Role | Hash | Password Matches Hash')
print('-' * 100)

# Generate SQL INSERT statements for the populate_database.sql file
print('\nSQL INSERT statements for populate_database.sql:')
print('\n-- Users table data')
print('INSERT INTO `users` (`username`, `password_hash`, `email`, `first_name`, `last_name`, `location`, `role`, `status`) VALUES')

sql_values = []

for i, user in enumerate(users):
    # Generate a bcrypt hash
    password_hash = flask_bcrypt.generate_password_hash(user.password)
    
    # Check if the hash matches the original password
    password_matches_hash = flask_bcrypt.check_password_hash(password_hash, user.password)

    # Output for verification
    print(f'{user.username} | {user.password} | {user.role} | {password_hash.decode()} | {password_matches_hash}')
    
    # Generate SQL statement
    first_name = user.role.capitalize() + str(i % 20 + 1)
    last_name = "User"
    location = "Lincoln" if i % 3 == 0 else "Christchurch" if i % 3 == 1 else "Canterbury"
    
    # Format the SQL value string
    sql_value = f"('{user.username}', '{password_hash.decode()}', '{user.username}@example.com', '{first_name}', '{last_name}', '{location}', '{user.role}', 'active')"
    
    # Add comma if not the last item
    if i < len(users) - 1:
        sql_value += ','
    
    sql_values.append(sql_value)

# Print SQL values with proper formatting
for value in sql_values:
    print(value)

print(';\n')