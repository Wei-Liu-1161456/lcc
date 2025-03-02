from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from loginapp import app, db
import datetime

# Create a blueprint for issue-related routes
issues_bp = Blueprint('issues', __name__)

@issues_bp.route('/issues')
def list_issues():
    """Display a list of all issues."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Get all issues from the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT i.*, u.username, u.first_name, u.last_name 
            FROM issues i
            JOIN users u ON i.user_id = u.user_id
            ORDER BY i.created_at DESC
        ''')
        issues = cursor.fetchall()
    
    return render_template('issues/list.html', issues=issues)

@issues_bp.route('/issues/new', methods=['GET', 'POST'])
def new_issue():
    """Create a new issue."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        summary = request.form.get('summary', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate form data
        errors = {}
        if not summary:
            errors['summary'] = 'Summary is required'
        elif len(summary) > 255:
            errors['summary'] = 'Summary must be 255 characters or less'
        
        if not description:
            errors['description'] = 'Description is required'
        
        if errors:
            return render_template('issues/new.html', errors=errors, summary=summary, description=description)
        
        # Insert the new issue into the database
        with db.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO issues (user_id, summary, description, status)
                VALUES (%s, %s, %s, %s)
            ''', (session['id'], summary, description, 'new'))
        
        flash('Issue created successfully', 'success')
        return redirect(url_for('issues.list_issues'))
    
    return render_template('issues/new.html')

@issues_bp.route('/issues/<int:issue_id>')
def view_issue(issue_id):
    """View a single issue and its comments."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Get the issue from the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT i.*, u.username, u.first_name, u.last_name 
            FROM issues i
            JOIN users u ON i.user_id = u.user_id
            WHERE i.issue_id = %s
        ''', (issue_id,))
        issue = cursor.fetchone()
        
        if not issue:
            flash('Issue not found', 'error')
            return redirect(url_for('issues.list_issues'))
        
        # Get comments for this issue
        cursor.execute('''
            SELECT c.*, u.username, u.first_name, u.last_name, u.role
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.issue_id = %s
            ORDER BY c.created_at ASC
        ''', (issue_id,))
        comments = cursor.fetchall()
    
    return render_template('issues/view.html', issue=issue, comments=comments)

@issues_bp.route('/issues/<int:issue_id>/comment', methods=['POST'])
def add_comment(issue_id):
    """Add a comment to an issue."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('issues.view_issue', issue_id=issue_id))
    
    # Insert the comment into the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            INSERT INTO comments (issue_id, user_id, content)
            VALUES (%s, %s, %s)
        ''', (issue_id, session['id'], content))
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('issues.view_issue', issue_id=issue_id))

@issues_bp.route('/issues/<int:issue_id>/status', methods=['POST'])
def update_status(issue_id):
    """Update the status of an issue."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Only helpers and admins can update status
    if session['role'] not in ['helper', 'admin']:
        flash('You do not have permission to update issue status', 'error')
        return redirect(url_for('issues.view_issue', issue_id=issue_id))
    
    new_status = request.form.get('status')
    valid_statuses = ['new', 'open', 'stalled', 'resolved']
    
    if new_status not in valid_statuses:
        flash('Invalid status', 'error')
        return redirect(url_for('issues.view_issue', issue_id=issue_id))
    
    # Update the issue status
    with db.get_cursor() as cursor:
        cursor.execute('''
            UPDATE issues
            SET status = %s
            WHERE issue_id = %s
        ''', (new_status, issue_id))
    
    flash(f'Issue status updated to {new_status}', 'success')
    return redirect(url_for('issues.view_issue', issue_id=issue_id))

# Register the blueprint with the app
app.register_blueprint(issues_bp) 