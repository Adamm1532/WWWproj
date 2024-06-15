import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, relationship
import datetime
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = mapped_column(sa.Integer(), primary_key=True)
    user_id = mapped_column(sa.Integer(), sa.ForeignKey('user.id'))
    role_id = mapped_column(sa.Integer(), sa.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = mapped_column(sa.Integer(), primary_key=True)
    name = mapped_column(sa.String(80), unique=True)
    description = mapped_column(sa.String(255))
    users = relationship('User', secondary='roles_users', back_populates="roles", lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = mapped_column(sa.Integer(), primary_key=True)
    email = mapped_column(sa.String(255), unique=True)
    username = mapped_column(sa.String(255), unique=True, nullable=True)
    password = mapped_column(sa.String(255), nullable=False)
    last_login_at = mapped_column(sa.DateTime())
    current_login_at = mapped_column(sa.DateTime())
    last_login_ip = mapped_column(sa.String(100))
    current_login_ip = mapped_column(sa.String(100))
    login_count = mapped_column(sa.Integer())
    active = mapped_column(sa.Boolean())
    fs_uniquifier = mapped_column(sa.String(255), unique=True, nullable=False)
    confirmed_at = mapped_column(sa.DateTime())
    roles = relationship('Role', secondary='roles_users', back_populates="users", lazy=True)
    moderator_request = mapped_column(sa.Boolean(), nullable=False, default=False)
    speedruns = relationship('Speedruns', back_populates='user', lazy=True)
    def has_role(self, role):
        return role in self.roles

class Speedruns(db.Model):
    __tablename__ = 'speedruns'
    id = mapped_column(sa.Integer, primary_key=True)
    user_id = mapped_column(sa.Integer(), sa.ForeignKey('user.id'), nullable=False)
    time = mapped_column(sa.Interval(), nullable=False)
    date = mapped_column(sa.DateTime(), nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    link_id = mapped_column(sa.String(255), nullable=False)
    verified = mapped_column(sa.Boolean(), nullable=False, default=False)
    category = mapped_column(sa.String(255), nullable=False)
    user = relationship("User", back_populates='speedruns', lazy=False)

