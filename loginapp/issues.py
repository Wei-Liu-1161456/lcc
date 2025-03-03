from loginapp import app
from loginapp import db
from flask import redirect, render_template, request, session, url_for, flash
import MySQLdb.cursors
from datetime import datetime

@app.route('/issues/report', methods=['GET', 'POST'])
def report_issue():
    """Report new issue endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get form data
        form_data = {
            'summary': request.form.get('summary', '').strip(),
            'description': request.form.get('description', '').strip()
        }
        
        # Validate input
        errors = {}
        if not form_data['summary']:
            errors['summary'] = 'Summary is required'
        if not form_data['description']:
            errors['description'] = 'Description is required'

        if not errors:
            with db.get_cursor() as cursor:
                # Create new issue
                cursor.execute('''
                    INSERT INTO issues (user_id, summary, description, status)
                    VALUES (%s, %s, %s, %s)
                ''', (session['user_id'], form_data['summary'], 
                      form_data['description'], 'new'))
                db.get_db().commit()
                
                flash('Issue reported successfully!', 'success')
                return redirect(url_for('list_issues'))
        
        return render_template('issues/report.html', errors=errors, form_data=form_data)

    # GET request - show empty form
    return render_template('issues/report.html', 
                         errors={}, 
                         form_data={})

@app.route('/issues/list')
def list_issues():
    """View issues list endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # Get filter parameter
    filter_type = request.args.get('filter')

    with db.get_cursor() as cursor:
        base_query = '''
            SELECT i.*, u.username, u.first_name, u.last_name, u.profile_image,
                   COUNT(c.comment_id) as comment_count 
            FROM issues i 
            JOIN users u ON i.user_id = u.user_id 
            LEFT JOIN comments c ON i.issue_id = c.issue_id 
        '''

        if session['role'] in ['helper', 'admin']:
            if filter_type == 'resolved':
                # Show only resolved issues
                cursor.execute(base_query + '''
                    WHERE i.status = 'resolved'
                    GROUP BY i.issue_id 
                    ORDER BY i.created_at DESC
                ''')
                issues = cursor.fetchall()
                return render_template('issues/list.html',
                                    issues=issues,
                                    filter_type=filter_type)
            else:
                # Show active issues
                cursor.execute(base_query + '''
                    WHERE i.status != 'resolved'
                    GROUP BY i.issue_id 
                    ORDER BY 
                        CASE i.status
                            WHEN 'new' THEN 1
                            WHEN 'open' THEN 2
                            WHEN 'stalled' THEN 3
                        END,
                        i.created_at DESC
                ''')
                issues = cursor.fetchall()
                return render_template('issues/list.html',
                                    issues=issues,
                                    filter_type=filter_type)
        else:
            # For visitors: show ALL their own issues
            cursor.execute(base_query + '''
                WHERE i.user_id = %s
                GROUP BY i.issue_id 
                ORDER BY 
                    CASE 
                        WHEN i.status = 'resolved' THEN 2  -- Show resolved issues after active ones
                        ELSE 1
                    END,
                    CASE i.status  -- Sort active issues by priority
                        WHEN 'new' THEN 1
                        WHEN 'open' THEN 2
                        WHEN 'stalled' THEN 3
                    END,
                    i.created_at DESC
            ''', (session['user_id'],))
            issues = cursor.fetchall()
            return render_template('issues/list.html',
                                issues=issues,
                                filter_type=filter_type)

@app.route('/issues/<int:issue_id>')
def view_issue(issue_id):
    """View issue details endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    with db.get_cursor() as cursor:
        # Get issue details with reporter info
        cursor.execute('''
            SELECT i.*, u.username, u.first_name, u.last_name, u.profile_image
            FROM issues i 
            JOIN users u ON i.user_id = u.user_id 
            WHERE i.issue_id = %s
        ''', (issue_id,))
        issue = cursor.fetchone()

        if not issue:
            flash('Issue not found', 'error')
            return redirect(url_for('list_issues'))

        # Check if user has permission to view this issue
        if session['role'] not in ['helper', 'admin'] and issue['user_id'] != session['user_id']:
            return render_template('access_denied.html'), 403

        # Get comments with user info
        cursor.execute('''
            SELECT c.*, u.username, u.first_name, u.last_name, u.profile_image, u.role
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.issue_id = %s
            ORDER BY c.created_at ASC
        ''', (issue_id,))
        comments = cursor.fetchall()

    return render_template('issues/detail.html', issue=issue, comments=comments)

@app.route('/issues/<int:issue_id>/comment', methods=['POST'])
def add_comment(issue_id):
    """Add comment to issue endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('view_issue', issue_id=issue_id))

    with db.get_cursor() as cursor:
        # Get issue details to check permissions
        cursor.execute('SELECT * FROM issues WHERE issue_id = %s', (issue_id,))
        issue = cursor.fetchone()

        if not issue:
            flash('Issue not found', 'error')
            return redirect(url_for('list_issues'))

        # Check if user has permission to comment
        if session['role'] not in ['helper', 'admin'] and issue['user_id'] != session['user_id']:
            return render_template('access_denied.html'), 403

        # Add comment
        cursor.execute('''
            INSERT INTO comments (issue_id, user_id, content)
            VALUES (%s, %s, %s)
        ''', (issue_id, session['user_id'], content))

        # Update issue status if helper/admin comments on new/stalled/resolved issue
        if session['role'] in ['helper', 'admin'] and issue['status'] != 'open':
            cursor.execute('''
                UPDATE issues 
                SET status = 'open'
                WHERE issue_id = %s
            ''', (issue_id,))

        db.get_db().commit()
        flash('Comment added successfully', 'success')

    return redirect(url_for('view_issue', issue_id=issue_id))

@app.route('/issues/<int:issue_id>/status', methods=['POST'])
def update_issue_status(issue_id):
    """Update issue status endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    if session['role'] not in ['helper', 'admin']:
        return render_template('access_denied.html'), 403
        
    new_status = request.form.get('status')
    if new_status not in ['new', 'open', 'stalled', 'resolved']:
        flash('Invalid status', 'error')
        return redirect(url_for('list_issues'))
        
    with db.get_cursor() as cursor:
        cursor.execute('''
            UPDATE issues 
            SET status = %s
            WHERE issue_id = %s
        ''', (new_status, issue_id))
        db.get_db().commit()
        
    flash('Issue status updated successfully', 'success')
    return redirect(url_for('list_issues')) 