from flask import render_template,abort,session,request,redirect,flash,url_for
from werkzeug.security import check_password_hash, generate_password_hash
from mycirclepkg import app
from mycirclepkg.model import db,Admin
from mycirclepkg.user_form import CreateAccount, ProfileUpdate, LoginForm, AdminProfileUpdate


@app.errorhandler(404)
def errorNotfound(error):
    return render_template('404.html', error=error),404
    
@app.route('/admin/users.html')
def admin_users_template():
    from mycirclepkg.model import User
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# Admin route to view communities template
@app.route('/admin/communities.html')
def admin_communities_template():
    from mycirclepkg.model import Community
    communities = Community.query.all()
    return render_template('admin/communities.html', communities=communities)


@app.route('/admin/categories.html')
def admin_categories_template():
    if not session.get('adminonline'):
        abort(403)
    from mycirclepkg.model import Category
    categories = Category.query.order_by(Category.category_name.asc()).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/dashboard/', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('adminonline') and session.get('adminid'):
        from mycirclepkg.model import User, Community, Post, Category
        total_users_count = User.query.count()
        total_communities_count = Community.query.count()
        
        # Fetch recent signups (last 5)
        recent_signups = User.query.order_by(User.userId.desc()).limit(5).all()
        

        # Fetch recent communities (last 9)
        recent_communities = Community.query.order_by(Community.idcommunity.desc()).limit(9).all()
        
        return render_template(
            'admin/dashboard.html',
            total_users_count=total_users_count,
            total_communities_count=total_communities_count,
            recent_signups=recent_signups,
            recent_communities=recent_communities
        )
    else:
        flash("you must be logged in as an admin",category='admin')
        return redirect(url_for('admin_login'))
        



@app.route('/admin/login/',methods=['POST','GET'])
def admin_login():
    from mycirclepkg.user_form import LoginForm
    form = LoginForm()
    if request.method == 'GET':
        return render_template('admin/login.html', form=form)
    else:
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            admin = Admin.query.filter(Admin.adm_email==email).first()
            if admin:
                stored_pass = admin.password
                chk = check_password_hash(stored_pass, password)
                if chk:
                    session['adminonline'] = admin.userName 
                    session['adminid'] = admin.id_admin
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid password", category='admin')
            else:
                flash("Invalid email", category='admin')
        return render_template('admin/login.html',  form=form)
        


@app.route('/admin/logout/')
def admin_logout():
    if session.get('adminonline') and session.get('adminid'):
        session.pop('adminonline',None)
        session.pop('adminid',None)
        session.clear()
    return redirect(url_for('admin_login'))


# Admin route to disable a user
@app.route('/admin/users/disable/<int:user_id>', methods=['POST'])
def disable_user(user_id):
    if not session.get('adminonline'):
        abort(403)
    from mycirclepkg.model import User, db
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        db.session.commit()
        flash(f"User {user.user_username} disabled.", category='admin')
    else:
        flash("User not found.", category='admin')
    return redirect(url_for('admin_users_template'))


# Admin route to enable a user
@app.route('/admin/users/enable/<int:user_id>', methods=['POST'])
def enable_user(user_id):
    if not session.get('adminonline'):
        abort(403)
    from mycirclepkg.model import User, db
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash(f"User {user.user_username} enabled.", category='admin')
    else:
        flash("User not found.", category='admin')
    return redirect(url_for('admin_users_template'))

# Admin route to disable a community
@app.route('/admin/communities/disable/<int:community_id>', methods=['POST'])
def disable_community(community_id):
    if not session.get('adminonline'):
        abort(403)
    from mycirclepkg.model import Community, db
    community = Community.query.get(community_id)
    if community:
        community.is_active = False
        db.session.commit()
        flash(f"Community {community.communityname} disabled.", category='admin')
    else:
        flash("Community not found.", category='admin')
    return redirect(url_for('admin_communities_template'))

# Admin route to enable a community
@app.route('/admin/communities/enable/<int:community_id>', methods=['POST'])
def enable_community(community_id):
    if not session.get('adminonline'):
        abort(403)
    from mycirclepkg.model import Community
    community = Community.query.get(community_id)
    if community:
        community.is_active = True
        db.session.commit()
        flash(f"Community {community.communityname} enabled.", category='admin')
    else:
        flash("Community not found.", category='admin')
    return redirect(url_for('admin_communities_template'))

# Admin route to create a new category
@app.route('/admin/categories/create', methods=['POST'])
def create_category():
    if not session.get('adminonline'):
        abort(403)
    name = (request.form.get('name') or '').strip()
    if not name:
        flash("Category name required.", category='admin')
        return redirect(url_for('admin_categories_template'))
    from mycirclepkg.model import Category, db
    existing_category = Category.query.filter(Category.category_name.ilike(name)).first()
    if existing_category:
        flash(f"Category '{name}' already exists.", category='admin')
        return redirect(url_for('admin_categories_template'))

    new_category = Category(category_name=name)
    db.session.add(new_category)
    db.session.commit()
    flash(f"Category '{name}' created.", category='admin')
    return redirect(url_for('admin_categories_template'))


# Admin route to create a new admin account
@app.route('/admin/create/', methods=['GET', 'POST'])
def admin_create():
    form = CreateAccount()
    if request.method == 'GET':
        return render_template('admin/signup.html', form=form)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        adm_email= form.email.data
        hashed_password = generate_password_hash(password)
        new_admin = Admin(userName=username, password=hashed_password, adm_email=adm_email)
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin account created successfully.', 'admin')
        return redirect(url_for('admin_login'))
    else:
        flash('Please correct the errors in the form.', 'admin')
        return render_template('admin/signup.html', form=form)
