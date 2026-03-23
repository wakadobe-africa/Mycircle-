# MyCIRCLE Project Documentation

## 1. Project Overview

MyCIRCLE is a Flask-based web platform for community engagement. Users can create accounts, build communities, request membership in communities, post content, and comment on posts. Community creators moderate join requests. A separate admin area supports high-level monitoring and management tasks such as category creation and user/community status toggling.

Primary goals of the application:
- Create focused communities by category.
- Enable controlled membership through approval workflows.
- Provide simple, community-scoped discussions via posts and comments.
- Provide an admin dashboard for platform operations.

---

## 2. Technology Stack

Backend:
- Flask 3.1.3
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.47
- Flask-Migrate 4.1.0 + Alembic 1.18.4
- Flask-WTF 1.2.2
- WTForms 3.2.1
- mysql-connector 2.2.9
- Werkzeug 3.1.5

Database:
- MySQL (configured through SQLAlchemy URI)

Frontend:
- Jinja2 templates
- Bootstrap
- jQuery
- Font Awesome
- Custom CSS

Security and validation:
- Password hashing with Werkzeug (generate_password_hash/check_password_hash)
- CSRF protection through Flask-WTF
- Form-level validation with WTForms validators

---

## 3. Application Architecture

### 3.1 Entrypoint and App Factory
- run.py starts the Flask app on port 5000 with debug enabled.
- mycirclepkg/__init__.py defines create_app(), loads configuration, initializes:
  - SQLAlchemy database instance
  - Flask-Migrate
  - CSRFProtect
- Route and form modules are imported after app initialization.

### 3.2 Core Modules
- mycirclepkg/model.py: all ORM entities and key model methods.
- mycirclepkg/user_form.py: all WTForms classes.
- mycirclepkg/user_routes.py: user-facing routes and community workflows.
- mycirclepkg/devadmin_routes.py: admin-facing routes.

### 3.3 Template Organization
- mycirclepkg/templates/users/: user pages and partials.
- mycirclepkg/templates/admin/: admin dashboard and management pages.

### 3.4 Static Assets
- mycirclepkg/static/: CSS, JS, icons, images, and uploads.
- Uploaded profile images are saved to mycirclepkg/static/uploads/.

---

## 4. Data Model

The project defines these main entities in mycirclepkg/model.py:

### 4.1 Admin
- Purpose: admin authentication and profile metadata.
- Key fields:
  - id_admin
  - adm_email (unique)
  - userName
  - password (hashed)
  - approval_status
  - role
  - auth_level

### 4.2 User
- Purpose: end-user account and profile.
- Key fields:
  - userId
  - user_username
  - user_fname, user_lname
  - user_email
  - user_password (hashed)
  - user_profilePic
  - date_joined
- Relationships:
  - posts (one-to-many)
  - comments (one-to-many)
  - memberships via CommunityMember

### 4.3 Category
- Purpose: classify communities.
- Key fields:
  - category_id
  - category_name (unique)

### 4.4 Community
- Purpose: central collaboration space.
- Key fields:
  - idcommunity
  - communityname
  - community_desc
  - category_id
  - createdByUserId
  - admin_userId
  - date_created
- Relationships:
  - category
  - posts
  - members through CommunityMember
- Domain methods:
  - send_join_request(user_id)
  - handle_join_request(member_id, action)

### 4.5 CommunityMember
- Purpose: join table for community membership with status workflow.
- Composite key:
  - community_id + member_id
- Key fields:
  - status: pending, approved, rejected
  - date_joined

### 4.6 Post
- Purpose: message/content unit inside a community.
- Key fields:
  - postId
  - community_id
  - user_id
  - post_content
  - post_created
  - contribution_Count
- Relationships:
  - author (User)
  - community (Community)
  - comments (Comment)
  - images (PostImage)

### 4.7 Comment
- Purpose: contribution/comment on a post.
- Key fields:
  - contribution_id
  - contribution_Content
  - user_id
  - post_id
  - comment_Date

### 4.8 PostImage
- Purpose: image references linked to posts.
- Key fields:
  - id_image
  - image_URL
  - post_id

### 4.9 Relationship
- Purpose: additional mapping table between community, post, member, and contribution.
- Composite key:
  - community_id + post_id + member_id

---

## 5. Features Implemented and Functional Behavior

## 5.1 User Account Features
- User registration with validation:
  - unique email check
  - required terms/privacy checkbox
  - password hashing
- User login with credential validation.
- Session-based authentication using session keys:
  - useronline
  - userid
- Logout by clearing session.
- Password reset endpoint using validated reset form and hashed storage.

Functional behavior:
- Registration prevents duplicate emails.
- Login redirects authenticated users to dashboard.
- Invalid credentials trigger flash messages.
- Password reset returns JSON responses for frontend handling.

### 5.2 User Profile Features
- Profile view page.
- Profile update with:
  - username, first name, last name, email
  - optional password change flow
  - optional image upload (jpg, jpeg, png, gif)

Functional behavior:
- Email uniqueness is enforced against other users.
- Password update requires all password fields and current password verification.
- Uploaded image name is tokenized before saving.

### 5.3 Community Discovery and Management
- Create community form with category selection from DB.
- Browse communities page for communities user has not created and not yet approved in.
- My communities page separating:
  - created communities
  - approved member communities
- Edit community available to creator only.

Functional behavior:
- Community creation persists name, description, category, creator.
- Edit action updates selected fields and redirects to chat view.
- Community browsing excludes already-connected communities.

### 5.4 Join Request and Moderation Workflow
- Send join request endpoint.
- Notification page for creators showing pending requests.
- Manage request endpoint allowing approve/reject.

Functional behavior:
- New request creates pending membership.
- If already pending, request remains pending.
- If rejected, request can be resent and becomes pending.
- If approved, user is treated as a member for access checks.

### 5.5 Community Chat, Posts, and Comments
- Load community chat endpoint with access control.
- Create post endpoint.
- Add comment endpoint.
- Load comments endpoint.

Functional behavior:
- Only creator or approved member can view community chat.
- Posts are shown in ascending creation order.
- Comment creation persists user and post linkage.
- Member count is calculated for chat header context.

### 5.6 Search Feature
- Search communities endpoint using query parameter q.
- Returns up to 4 matches by community name (case-insensitive with ilike).

Functional behavior:
- Empty query returns first 4 communities.
- JSON payload includes name, description, and category label.

### 5.7 Admin Features
- Admin login/logout flow with separate session keys:
  - adminonline
  - adminid
- Admin dashboard with summary counts and recent records.
- Admin users page and communities page.
- Admin categories page with category creation and duplicate prevention.
- Admin profile update including role, auth_level, email, username, optional password update.
- Admin account creation route.

Functional behavior:
- Category creation prevents case-insensitive duplicates.
- Admin dashboard surfaces key recent activity snapshots.

---

## 6. Event and Process Flows

This section highlights the key event-driven flows implemented in the application.

### 6.1 Event Flow: User Registration
1. User opens registration page.
2. Form submit triggers validation.
3. System checks if email exists.
4. System verifies terms checkbox.
5. Password is hashed.
6. New user record is inserted.
7. User is redirected to login.

### 6.2 Event Flow: User Login
1. User submits email/password.
2. System fetches user by email.
3. Password hash is verified.
4. Session keys are set.
5. User is redirected to dashboard.

### 6.3 Event Flow: Create Community
1. Authenticated user opens create community form.
2. Categories are loaded from database.
3. User submits name, description, category.
4. Community is inserted with creator user ID.
5. User is redirected to dashboard.

### 6.4 Event Flow: Join Request Lifecycle
1. User clicks join on community card.
2. Backend checks existing membership state.
3. One of four outcomes occurs:
   - sent (new pending)
   - pending (already pending)
   - already_member (already approved)
   - resent (was rejected, now pending)
4. Community creator sees pending request in notifications page.
5. Creator approves or rejects via request management endpoint.
6. Membership state changes accordingly.

### 6.5 Event Flow: Community Access Control
1. User requests community chat page.
2. Backend verifies user is creator or approved member.
3. If authorized, posts and member count are loaded.
4. If unauthorized, access is rejected with 403.

### 6.6 Event Flow: Post Creation
1. Authorized member/creator submits message and community ID.
2. Backend creates post linked to user and community.
3. Database commit completes.
4. JSON success response is returned for UI update.

### 6.7 Event Flow: Comment Creation
1. Authorized user submits comment text and post ID.
2. Backend creates comment linked to user and post.
3. Database commit completes.
4. JSON success response is returned.

### 6.8 Event Flow: Profile Update
1. User opens profile edit form prefilled from DB.
2. User updates identity fields and optional media/password.
3. Backend validates email uniqueness and password logic.
4. Optional photo is saved to uploads and filename persisted.
5. User record is committed and success message shown.

### 6.9 Event Flow: Admin Category Creation
1. Admin opens categories page.
2. Admin submits category name.
3. Backend trims input and checks emptiness.
4. Backend checks case-insensitive duplicate.
5. On success, category is inserted and flash message shown.

---

## 7. Route Inventory

## 7.1 User Routes
- GET / : landing page
- GET, POST /create/account/mycircle/ : register user
- GET, POST /login/mycircle/account/ : login user
- POST /password-reset/ : reset password
- GET /dashboard/mycircle/ : user dashboard
- GET /logout/mycircle/ : logout user
- GET /profile/mycircle/ : view profile
- GET, POST /profile/update/mycircle/ : update profile
- GET, POST /create/community/mycircle/ : create community
- GET /communities/ : browse communities
- GET /my-communities/ : list created/member communities
- GET, POST /edit-community/<community_id>/ : edit community
- POST /send-join-request/<community_id>/ : submit join request
- GET /notifications : creator notifications
- POST /community/request/<community_id>/<user_id>/<action> : approve/reject request
- GET, POST /load-community-chat/<community_id> : community chat view
- POST /create-post : create post
- GET /load-comments/<post_id> : load comments
- POST /new/comment/ : create comment
- GET /community/detail/<community_id>/ : community detail view
- GET /search_communities : community search

## 7.2 Admin Routes
- GET /admin/users.html : admin users listing
- GET /admin/communities.html : admin communities listing
- GET /admin/categories.html : admin categories listing
- GET, POST /admin/dashboard/ : dashboard metrics page
- GET, POST /admin/login/ : admin login
- GET /admin/logout/ : admin logout
- POST /admin/users/disable/<user_id> : disable user
- POST /admin/users/enable/<user_id> : enable user
- POST /admin/communities/disable/<community_id> : disable community
- POST /admin/communities/enable/<community_id> : enable community
- POST /admin/categories/create : create category
- GET, POST /admin/profile/ : admin profile update
- GET, POST /admin/create/ : admin account creation

---

## 8. Operational Setup

### 8.1 Local Setup
1. Create or activate virtual environment.
2. Install dependencies from requirements.txt.
3. Configure instance/config.py with required environment values.
4. Ensure MySQL database exists and connection URI is valid.
5. Apply migrations.
6. Start app with run.py.

### 8.2 Expected Runtime
- Flask app runs on port 5000.
- Static files and uploads are served through Flask static path in development.
- Session and flash messaging are used heavily in both user and admin experiences.

---

## 9. Known Constraints and Gaps

Important known issues inferred from current implementation:
- User and Community models do not define is_active fields, but admin enable/disable routes attempt to write them.
- Community.handle_join_request updates status but does not commit internally; commit is currently done in route.
- load_comments renders a template named comments.html, but this template is not present in the current workspace template folders.
- load_comments membership check does not enforce approved status (it checks membership existence).
- Some endpoints rely on session values without role-based abstraction layers.
- Global no-cache header in after_request may affect client-side caching behavior across all responses.
- PostImage and Relationship models are defined but not actively used by routes.

---

## 10. Suggested Enhancements

High-value improvements:
- Add explicit is_active columns and corresponding migrations for User and Community.
- Add missing comments.html template or update route to use an existing partial template.
- Add edit/delete for posts and comments.
- Add pagination for large lists (communities, posts, comments).
- Add stronger authorization decorators for user/admin route groups.
- Add automated tests for auth, membership workflows, and admin operations.
- Add API-level error schema consistency for JSON endpoints.

---

## 11. Quick Feature Matrix

Implemented:
- User registration and login
- Password reset endpoint
- Profile updates with image upload
- Community creation and editing
- Join request workflow with creator moderation
- Community chat with posting and commenting
- Search communities
- Admin dashboard and category management

Partially implemented or pending hardening:
- Admin disable/enable for users and communities (depends on missing model fields)
- Comment loading template path consistency
- Extended moderation and activity controls

---

## 12. Conclusion

The current MyCIRCLE codebase provides a solid baseline for a moderated community platform. The strongest implemented flows are account lifecycle, community lifecycle, and creator-controlled membership approvals. The next engineering focus should be model-route consistency fixes, missing template completion, and test coverage to harden production readiness.
