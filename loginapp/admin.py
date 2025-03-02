from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from loginapp import app, db, flask_bcrypt
import re

# Create a blueprint for admin-related routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard page."""
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get statistics for the dashboard
    with db.get_cursor() as cursor:
        # Count users by role
        cursor.execute('''
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        ''')
        user_stats = cursor.fetchall()
        
        # Count issues by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM issues
            GROUP BY status
        ''')
        issue_stats = cursor.fetchall()
        
        # Get recent issues
        cursor.execute('''
            SELECT i.*, u.username
            FROM issues i
            JOIN users u ON i.user_id = u.user_id
            ORDER BY i.created_at DESC
            LIMIT 5
        ''')
        recent_issues = cursor.fetchall()
    
    return render_template('admin/dashboard.html', 
                          user_stats=user_stats, 
                          issue_stats=issue_stats, 
                          recent_issues=recent_issues)

@admin_bp.route('/admin/users')
def manage_users():
    """Manage users page."""
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get all users from the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT user_id, username, email, first_name, last_name, location, role, status
            FROM users
            ORDER BY username
        ''')
        users = cursor.fetchall()
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit a user's details."""
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get the user from the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT user_id, username, email, first_name, last_name, location, role, status
            FROM users
            WHERE user_id = %s
        ''', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        location = request.form.get('location', '').strip()
        role = request.form.get('role', '').strip()
        status = request.form.get('status', '').strip()
        
        # Validate form data
        errors = {}
        if not email:
            errors['email'] = 'Email is required'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please enter a valid email address'
        
        if not first_name:
            errors['first_name'] = 'First name is required'
        elif len(first_name) > 50:
            errors['first_name'] = 'First name must be 50 characters or less'
        
        if not last_name:
            errors['last_name'] = 'Last name is required'
        elif len(last_name) > 50:
            errors['last_name'] = 'Last name must be 50 characters or less'
        
        if not location:
            errors['location'] = 'Location is required'
        elif len(location) > 50:
            errors['location'] = 'Location must be 50 characters or less'
        
        if role not in ['visitor', 'helper', 'admin']:
            errors['role'] = 'Invalid role'
        
        if status not in ['active', 'inactive']:
            errors['status'] = 'Invalid status'
        
        if errors:
            return render_template('admin/edit_user.html', user=user, errors=errors)
        
        # Update the user in the database
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET email = %s, first_name = %s, last_name = %s, location = %s, role = %s, status = %s
                WHERE user_id = %s
            ''', (email, first_name, last_name, location, role, status, user_id))
        
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
def reset_user_password(user_id):
    """Reset a user's password."""
    if 'loggedin' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Get the user from the database
    with db.get_cursor() as cursor:
        cursor.execute('SELECT username FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate form data
        errors = {}
        if len(new_password) < 8:
            errors['new_password'] = 'Password must be at least 8 characters long'
        
        if new_password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        if errors:
            return render_template('admin/reset_password.html', user=user, errors=errors)
        
        # Update the password
        password_hash = flask_bcrypt.generate_password_hash(new_password)
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
            ''', (password_hash, user_id))
        
        flash('Password reset successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/reset_password.html', user=user)

# Register the blueprint with the app
app.register_blueprint(admin_bp)