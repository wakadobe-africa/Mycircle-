import secrets,os
from flask import abort, jsonify, render_template,request,redirect,url_for,flash,session
from werkzeug.security import generate_password_hash,check_password_hash
from mycirclepkg.model import Comment, db,User,Community,Category,Post,CommunityMember
from mycirclepkg import app,user_form

# Helper function to check if user is logged in
def is_user_logged_in():
    return session.get('useronline') and session.get('userid')

def get_user_id():
    return session.get('userid')

@app.errorhandler(404)
def errorNotfound(error):
    return render_template('user/404.html', error=error),404

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response


@app.get('/')
def index():
    return render_template('users/index.html')
    
@app.route('/create/account/mycircle/',methods=['GET','POST'])
def user_register():
    createform = user_form.CreateAccount()
    if createform.validate_on_submit():
        email = createform.email.data
        if User.is_email_used(email):
            flash('You have registered before', 'danger')
            return render_template('users/signUp.html', createform=createform)
        user = User(
            user_email=email,
            user_username=createform.username.data,
            user_password=generate_password_hash(createform.password.data)
        )
        chk = request.form.get('checked')
        if not chk:
            flash('You must agree to the terms and privacy policy',category='danger')
            return render_template('users/signUp.html', createform=createform)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful',category='success')
        return redirect(url_for('user_login'))

    return render_template('users/signUp.html', createform=createform)

@app.route('/login/mycircle/account/',methods=['GET','POST'])
def user_login():
    loginform=user_form.LoginForm()
    resetform=user_form.PasswordResetForm()
    if loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data
        userdeets = User.query.filter(User.user_email==email).first()
        if userdeets:#the email exists, then check if email is correct 
            check = check_password_hash(userdeets.user_password, password)
            if check:
                session['useronline']= userdeets.user_username
                session['userid'] = userdeets.userId        
                return redirect(url_for('dashboard'))
            else:
                flash('invalid password', category='user') 
                return redirect(url_for('user_login'))
        else:#email does not exists 
            flash('invalid credentials', category='user')
            return redirect(url_for('user_login'))
    else:    
        return render_template('users/login.html', loginform=loginform, resetform=resetform)


@app.route('/password-reset/', methods=['POST'])
def password_reset_request():
    resetform = user_form.PasswordResetForm()
    if resetform.validate_on_submit():
        email = resetform.email.data
        user = User.query.filter_by(user_email=email).first()
        if not user:
            return jsonify({'success': False, 'message': 'No account found with that email address.'})
        user.user_password = generate_password_hash(resetform.new_password.data)
        db.session.commit()
        return jsonify({'success': True, 'redirect': url_for('user_login')})
    
    return jsonify({'success': False, 'message': 'Please check your email and password fields.'})
    
@app.route('/dashboard/mycircle/')
def dashboard():
    if get_user_id():
        # to load all communities, relationship will let us access category.name
        communities = Community.query.join(Category).limit(4).all()
        return render_template('users/home.html', communities=communities)
    else:
        flash('Please login here to continue', category='user')
        return redirect(url_for('user_login'))


@app.route('/logout/mycircle/')
def user_logout():
    if is_user_logged_in(): 
        session.clear()
        flash('You are now logged out', category='user')  
        return redirect(url_for('user_login'))

@app.route('/profile/mycircle/')
def user_profile():
    if not get_user_id():
        flash('Please log in to view your profile',category='user')
        return redirect(url_for('user_login'))
    
    userdeets = User.query.get(get_user_id())
    if not userdeets:
        session.clear()
        flash('User not found', category='user')
        return redirect(url_for('user_login'))
    return render_template('users/profile_view.html', userdeets=userdeets)

@app.route('/profile/update/mycircle/', methods=['GET', 'POST'])
def profile_update():
    if not get_user_id():
        flash('Please log in to update your profile',category='user')
        return redirect(url_for('user_login'))
    updateform = user_form.ProfileUpdate()
    online_user = User.query.get(get_user_id())
    
    if request.method == 'GET' and online_user:
        updateform.username.data = online_user.user_username
        updateform.firstname.data = online_user.user_fname
        updateform.lastname.data = online_user.user_lname
        updateform.email.data = online_user.user_email
        
    if updateform.validate_on_submit():
        email = updateform.email.data
        if User.is_email_used(email) and email != online_user.user_email:
            flash('Email is already in use', category='user')
            return render_template('users/profile.html', updateform=updateform, userdeets=online_user)

        current_password = (updateform.current_password.data or '').strip()
        new_password = (updateform.new_password.data or '').strip()
        confirm_new_password = (updateform.confirm_new_password.data or '').strip()

        password_fields_provided = any([current_password, new_password, confirm_new_password])
        if password_fields_provided:
            if not all([current_password, new_password, confirm_new_password]):
                flash('To change password, fill current password, new password, and confirm new password.', category='user')
                return render_template('users/profile.html', updateform=updateform, userdeets=online_user)

            if not check_password_hash(online_user.user_password, current_password):
                flash('Current password is incorrect.', category='user')
                return render_template('users/profile.html', updateform=updateform, userdeets=online_user)

            online_user.user_password = generate_password_hash(new_password)

        online_user.user_username = updateform.username.data
        online_user.user_fname = updateform.firstname.data
        online_user.user_lname = updateform.lastname.data
        online_user.user_email = email
        
        if updateform.photo.data and updateform.photo.data.filename != '':
            photo_obj = updateform.photo.data
            photo_filename = photo_obj.filename
            name,extension = os.path.splitext(photo_filename)
            newname = secrets.token_hex(10)+extension
            photo_obj.save("mycirclepkg/static/uploads/"+ newname)
            online_user.user_profilePic = newname

        db.session.add(online_user)
        db.session.commit()
        flash('Profile updated successfully', category='user')
        return redirect(url_for('user_profile'))
    return render_template('users/profile.html', updateform=updateform,userdeets=online_user)

@app.route('/create/community/mycircle/', methods=['GET', 'POST'])
def create_community():
    if not get_user_id():
        flash('Please log in to create a community', category='user')
        return redirect(url_for('user_login'))
        
    communityform = user_form.CreateCommunity()
    # To load category choices from database so select dropdown is populated
    categories = db.session.query(Category).all()
    # Set choices for the SelectField
    communityform.category_id.choices = [(c.category_id, c.category_name) for c in categories]
    if communityform.validate_on_submit():
        community = Community(
                communityname=communityform.name_com.data,
                community_desc=communityform.desc_com.data,
                createdByUserId=get_user_id(),
                category_id=communityform.category_id.data
            )
        db.session.add(community)
        db.session.commit()
        flash('Community created successfully',category='user')
        return redirect(url_for('dashboard'))
        
    return render_template('users/createForm_community.html', communityform=communityform, categories=categories)

@app.route('/communities/')
def communities():

    if not session.get('userid'):
        flash('Please log in to view communities', category='user')
        return redirect(url_for('user_login'))
    
    user_id = session.get('userid')

    # Get IDs of communities user already joined (approved only)
    joined_ids = db.session.query(CommunityMember.community_id).filter(
        CommunityMember.member_id == user_id,
        CommunityMember.status == 'approved'
    )

    # Get IDs of communities user created
    created_ids = db.session.query(Community.idcommunity).filter(
        Community.createdByUserId == user_id    
    )

    # Fetch ONLY communities user has no connection to or are pending
    all_communities = Community.query.join(Category).filter(
        Community.idcommunity.not_in(joined_ids),
        Community.idcommunity.not_in(created_ids)
    ).all()
    return render_template('users/communities.html',
        all_communities=all_communities
        
    )                      

# community dashboard route to show all communities user is part of (both created and member) with links to chat details, and option to edit if creator. This will replace the previous /community/chat/ route which only showed member communities.
@app.route('/my-communities/')
def my_communities():
    if not get_user_id():
        flash('Please log in to view your communities',category='user')
        return redirect(url_for('user_login'))
    else:
        user_id = get_user_id()
        # Only show approved member communities
        member_communities = Community.query.join(CommunityMember).\
            filter(CommunityMember.member_id == user_id, CommunityMember.status == 'approved').all()
        # Created communities (always show)
        created_communities = Community.query.filter(Community.createdByUserId == user_id).all()
        comm_id = request.args.get('community_id')
        comm= Community.query.get(comm_id)

        return render_template('users/my_communities.html',
                            member_communities=member_communities,
                            created_communities=created_communities,
                            comm = comm
                           )

@app.route('/edit-community/<int:community_id>/', methods=['GET', 'POST'])
def edit_community(community_id):
    if not get_user_id():
        flash('Please log in to edit communities', category='user')
        return redirect(url_for('user_login'))
    
    user_id = get_user_id()
    community = Community.query.get_or_404(community_id)
    
    # Check if user is the creator of the community
    if community.createdByUserId != user_id:
        flash('You can only edit communities you created', category='user')
        return redirect(url_for('my_communities'))
    
    editform = user_form.EditCommunity()
    categories = db.session.query(Category).all()
    # Set choices for the SelectField
    editform.category_id.choices = [(c.category_id, c.category_name) for c in categories]
    
    if request.method == 'GET':
        # Pre-populate form with current community data
        editform.name_com.data = community.communityname
        editform.desc_com.data = community.community_desc
        editform.category_id.data = community.category_id
    
    if editform.validate_on_submit():
        community.communityname = editform.name_com.data
        community.community_desc = editform.desc_com.data
        community.category_id = editform.category_id.data
        
        db.session.commit()
        flash('Community updated successfully', category='user')
        return redirect(url_for('load_community_chat', community_id=community.idcommunity))
    
    return render_template('users/edit_community.html', editform=editform, community=community, categories=categories)

@app.route('/send-join-request/<int:community_id>/', methods=['POST'])
def send_join_request(community_id):

    if not get_user_id():
        return {"status": "login_required"}, 401

    user_id = get_user_id()

    community = db.session.get(Community, community_id)

    result = community.send_join_request(user_id)

    if result == "sent":
        return {"status": "success", "message": "Pending"}, 200

    elif result == "already_member":
        return {"status": "error", "message": "Member"}, 200

    elif result == "pending":
        return {"status": "error", "message": "Pending"}, 200

    elif result == "resent":
        return {"status": "success", "message": "Pending"}, 200

    return {"status": "error", "message": "Error"}, 400

@app.route("/notifications")
def notifications():
    if not get_user_id():
        flash('Please log in to view notifications', category='user')
        return redirect(url_for('user_login'))
    user_id = get_user_id()

    pending_requests = (
        db.session.query(CommunityMember)
        .join(Community, CommunityMember.community_id == Community.idcommunity)
        .join(User, CommunityMember.member_id == User.userId)
        .filter(
            Community.createdByUserId == user_id,
            CommunityMember.status == "pending"
        )
        .all()
    )

    return render_template(
        "users/notifications.html",
        pending_requests=pending_requests
    )

@app.route("/community/request/<int:community_id>/<int:user_id>/<action>", methods=["POST"])
def manage_request(community_id, user_id, action):

    community = Community.query.get_or_404(community_id)

    if community.createdByUserId != get_user_id():
        abort(403)

    result = community.handle_join_request(user_id, action)

    db.session.commit()

    return jsonify({"status": result})


@app.route('/load-community-chat/<int:community_id>',methods=['GET','POST'])
def load_community_chat(community_id):
    if not get_user_id():
        print("DEBUG: No user in session.")
        return "Unauthorized", 401

    user_id   = get_user_id()
    community = Community.query.get_or_404(community_id)

    # check relationship
    is_creator = community.createdByUserId == user_id
    is_member  = CommunityMember.query.filter_by(
        community_id=community_id,
        member_id=user_id,
        status='approved'
    ).first()

    

    # block outsiders
    if not is_creator and not is_member:
        return "Not authorized", 403

    posts = Post.query.filter_by(
        community_id=community_id
    ).order_by(Post.post_created.asc()).all()

    member_count = CommunityMember.query.filter_by(
        community_id=community_id
    ).count()

    return render_template(
        "users/chat_partial.html", 
        community=community,
        posts=posts,
        member_count=member_count,
        user_id=user_id,
        is_creator=is_creator,
        is_member=bool(is_member)
    )


@app.route('/create-post', methods=['POST'])
def create_post():
    if not get_user_id():
        return "Unauthorized", 401
    user_id = get_user_id()

    content = request.form.get("message")
    community_id = request.form.get("community_id")  # FIXED: match form field

    post = Post(
        user_id=user_id,
        community_id=community_id,
        post_content=content
    )

    db.session.add(post)
    db.session.commit()
    return jsonify({"status":"success"})

@app.route('/load-comments/<int:post_id>')
def load_comments(post_id):
        if not get_user_id():
            return "Unauthorized", 401
    
        user_id = get_user_id()
    
        post = Post.query.get_or_404(post_id)
        community = Community.query.get(post.community_id)
        is_creator = community.createdByUserId == user_id
        is_member  = CommunityMember.query.filter_by(
            community_id=community.idcommunity,
            member_id=user_id
        ).first()
    
        if not is_creator and not is_member:
            return "Not authorized", 403
        comments = Comment.query.filter_by(
        post_id=post.postId
    ).all()

        return render_template(
        "comments.html",
        comments=comments
    )

@app.route('/new/comment/', methods=['POST'])
def addComment():
    if not get_user_id():
        return "Unauthorized", 401
    user_id = get_user_id()

    post_id = request.form.get("post_id")
    text = request.form.get("comment")

    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        contribution_Content=text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({"status":"success"})

@app.route('/community/detail/<int:community_id>/')
def community_detail(community_id):
    user_id = get_user_id()
    community = Community.query.get_or_404(community_id)
    # Get admin user object
    admin_user = User.query.get(community.createdByUserId)
    # Check if user is a member or admin
    is_admin = (community.createdByUserId == user_id)
    is_member = CommunityMember.query.filter_by(community_id=community.idcommunity, member_id=user_id, status='approved').first()
    if not is_admin and not is_member:
        flash('You are not authorized to view this community', category='user')
        return redirect(url_for('my_communities'))
    # Get member count
    member_count = CommunityMember.query.filter_by(community_id=community.idcommunity, status='approved').count()
    # Get pending join requests (only for admin)
    pending_requests = []
    if is_admin:
        pending_requests = CommunityMember.query.filter_by(community_id=community.idcommunity, status='pending').all()
    return render_template(
        'users/community_detail.html',
        community=community,
        admin_user=admin_user,
        is_admin=is_admin,
        member_count=member_count,
        pending_requests=pending_requests
    )
 
@app.route('/search_communities', methods=['GET'])
def search_communities():
    query = request.args.get('q', '').strip()
    if not query:
        communities = Community.query.limit(4).all()
    else:
        communities = Community.query.filter(Community.communityname.ilike(f'%{query}%')).limit(4).all()
    results = []
    for community in communities:
        results.append({
            'communityname': community.communityname,
            'community_desc': community.community_desc,
            'category_name': community.category.category_name if community.category else 'Uncategorized'
        })
    return jsonify({'communities': results})