from flask import session

from datetime import datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, UniqueConstraint

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = "admin"
    id_admin = db.Column(db.Integer, primary_key=True)
    adm_email = db.Column(db.String(100), nullable=False, unique=True)
    userName = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    lastLogged_in = db.Column(db.TIMESTAMP)
    approval_status = db.Column(db.Enum("approved", "rejected", "pending"), default="pending")
    

class User(db.Model):
    __tablename__ = "user"
    userId = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(45))
    user_fname = db.Column(db.String(45))
    user_lname = db.Column(db.String(45))
    user_email = db.Column(db.String(100))
    user_password = db.Column(db.String(255))
    user_Phone = db.Column(db.String(45))
    user_profilePic = db.Column(db.String(45))
    date_joined = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    posts = db.relationship(
        "Post",
        back_populates="author",
        cascade="all, delete"
    )

    comments = db.relationship(
        "Comment",
        back_populates="user"
    )

    memberships = db.relationship(
        "CommunityMember",
        back_populates="member"
    )
    @classmethod
    def is_email_used(cls,email):
        email_used = cls.query.filter(cls.user_email==email).first()
        return email_used
    
    @staticmethod
    def get_active_user_id():
        """Fetch the userId of the active user from session."""
        return session.get('useronline')

    @classmethod
    def is_active(cls):
        """Return True if the user in session is active, else False."""
        user_id = session.get('useronline')
        if not user_id:
            return False
        user = cls.query.get(user_id)
        return user.is_active 
    

class CommunityMember(db.Model):
    __tablename__ = "community_members"

    community_id = db.Column(
        db.Integer,
        db.ForeignKey("community.idcommunity"),
        primary_key=True
    )

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )

    date_joined = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow
    )

    community = db.relationship(
        "Community",
        back_populates="members"
    )

    member = db.relationship(
        "User",
        back_populates="memberships"
    )
    status = db.Column(Enum("pending", "approved", "rejected"), default="pending")
    
class Category(db.Model):
    __tablename__ = "category"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    communities = db.relationship(
        "Community",
        back_populates="category"
    )


class Community(db.Model):
    __tablename__ = "community"

    idcommunity = db.Column(db.Integer, primary_key=True)
    community_desc = db.Column(db.Text)
    communityname = db.Column(db.String(45))
    
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.category_id")
    )

    createdByUserId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId")
    )

    admin_userId = db.Column(
        db.Integer,
        db.ForeignKey("admin.id_admin")
    )
    date_created = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    category = db.relationship(
        "Category",
        back_populates="communities"
    )

    last_read = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow
    )

    posts = db.relationship(
        "Post",
        back_populates="community",
        cascade="all, delete"
    )

    members = db.relationship(
        "CommunityMember",
        back_populates="community"
    )

    def send_join_request(self, user_id):

        existing = CommunityMember.query.filter_by(
            community_id=self.idcommunity,
            member_id=user_id
        ).first()

        if not existing:
            join_request = CommunityMember(
                community_id=self.idcommunity,
                member_id=user_id,
                status="pending"
            )

            db.session.add(join_request)
            db.session.commit()

            return "sent"

        if existing.status == "approved":
            return "already_member"

        if existing.status == "pending":
            return "pending"

        if existing.status == "rejected":
            existing.status = "pending"
            db.session.commit()
            return "resent"

    def handle_join_request(self, member_id, action):

        membership = CommunityMember.query.filter_by(
            community_id=self.idcommunity,
            member_id=member_id
        ).first()

        if not membership:
            return "not_found"

        if action == "approve":
            membership.status = "approved"

        elif action == "reject":
            membership.status = "rejected"

        else:
            return "invalid_action"

        return "updated"

    @classmethod
    def is_community_active(cls, community_id):
        community = cls.query.get(community_id)
        if not community:
            return False
        return bool(community.is_active)



class Post(db.Model):
    __tablename__ = "posts"

    postId = db.Column(db.Integer, primary_key=True)

    community_id = db.Column(
        db.Integer,
        db.ForeignKey("community.idcommunity")
    )

    post_content = db.Column(db.String(6200))


    contribution_Count = db.Column(db.Integer)

    post_created = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.userId")
    )

    community = db.relationship(
        "Community",
        back_populates="posts"
    )

    author = db.relationship(
        "User",
        back_populates="posts"
    )

    images = db.relationship(
        "PostImage",
        back_populates="post"
    )

    comments = db.relationship(
        "Comment",
        back_populates="post"
    )



class PostImage(db.Model):
    __tablename__ = "post_image"

    id_image = db.Column(db.Integer, primary_key=True)

    image_URL = db.Column(db.String(45))

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.postId")
    )

    post = db.relationship(
        "Post",
        back_populates="images"
    )


class Comment(db.Model):
    __tablename__ = "comments"

    contribution_id = db.Column(db.Integer, primary_key=True)

    contribution_Content = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.userId")
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.postId")
    )

    comment_Date = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="comments"
    )

    post = db.relationship(
        "Post",
        back_populates="comments"
    )


class Relationship(db.Model):
    __tablename__ = "relationship"

    community_id = db.Column(
        db.Integer,
        db.ForeignKey("community.idcommunity"),
        primary_key=True
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("posts.postId"),
        primary_key=True
    )

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )

    contribution_id = db.Column(
        db.Integer,
        db.ForeignKey("comments.contribution_id")
    )

    joined_at = db.Column(
        db.TIMESTAMP,
        default=datetime.utcnow
    )