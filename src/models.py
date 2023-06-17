from src.database import Base
from sqlalchemy import Integer, String, Boolean, ForeignKey, Column, DateTime, Float
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

    profile = relationship('Profile', back_populates='user')


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String, unique=True)
    name = Column(String)
    surname = Column(String)
    status = Column(String)
    city = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='profile')
    photos = relationship('Photo', back_populates='user')
    posts = relationship('Post', back_populates='profile')
    likes = relationship('Like', back_populates='profile')
    comments = relationship('Comment', back_populates='profile')
    notifications = relationship('Notification', back_populates='profile_to')
    groups = relationship('Group', back_populates='creator')
    subscribers = relationship('Subscriber', back_populates='profile')

    def get_attrs(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'tag_name': self.tag_name,
            'status': self.status,
            'city': self.city
        }

    def update_field(self, key, value):
        if value is not None:
            self.__dict__[key] = value


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey('profiles.id'))

    user = relationship('Profile', back_populates='photos')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    datetime_create  = Column(DateTime)
    profile_id = Column(Integer, ForeignKey('profiles.id'))

    profile = relationship('Profile', back_populates='posts')
    likes = relationship('Like', back_populates='posts', cascade="all, delete")
    images = relationship("ImagePost", back_populates='post', cascade="all, delete")
    comments = relationship('Comment', back_populates='post', cascade="all, delete")
    notifications = relationship('Notification', back_populates='post', cascade="all, delete")


class ImagePost(Base):
    __tablename__ = 'imageposts'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    post_id = Column(Integer, ForeignKey('posts.id'))

    post = relationship('Post', back_populates='images')


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('profiles.id'))

    posts = relationship('Post', back_populates='likes')
    profile = relationship('Profile', back_populates='likes')
    notifications = relationship('Notification', back_populates='like', cascade="all, delete")


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    create_date_time = Column(DateTime)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('profiles.id'))

    post = relationship('Post', back_populates='comments')
    profile = relationship('Profile', back_populates='comments')
    notifications = relationship('Notification', back_populates='comment', cascade="all, delete")


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    type = Column(String, nullable=False)
    viewed = Column(Boolean, default=False)

    comment_id = Column(Integer, ForeignKey('comments.id'))
    like_id = Column(Integer, ForeignKey('likes.id'))
    request_friend_id = Column(Integer, ForeignKey('requestsfriends.id'))
    accept_friend_id = Column(Integer, ForeignKey('acceptsfriends.id'))

    profile_to_id = Column(Integer, ForeignKey('profiles.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    post = relationship('Post', back_populates='notifications')
    comment = relationship('Comment', back_populates='notifications')
    like = relationship('Like', back_populates='notifications')
    request_friend = relationship('RequestFriend', back_populates='notifications')
    accept_friend = relationship('AcceptFriend', back_populates='notifications')
    profile_to = relationship('Profile', back_populates='notifications')


class RequestFriend(Base):
    __tablename__ = 'requestsfriends'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    accept = Column(Boolean, default=False)
    profile_from_id = Column(Integer, ForeignKey('profiles.id'))
    profile_to_id = Column(Integer, ForeignKey('profiles.id'))

    profile_from = relationship('Profile', foreign_keys=[profile_from_id])
    profile_to = relationship('Profile', foreign_keys=[profile_to_id])
    accept_friend = relationship('AcceptFriend', back_populates='request_friend', cascade="all, delete")
    notifications = relationship('Notification', back_populates='request_friend', cascade="all, delete")


class AcceptFriend(Base):
    __tablename__ = 'acceptsfriends'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    who_accept_id = Column(Integer, ForeignKey('profiles.id'))
    who_send_id = Column(Integer, ForeignKey('profiles.id'))
    request_friend_id = Column(Integer, ForeignKey('requestsfriends.id'))

    who_accept = relationship('Profile', foreign_keys=[who_accept_id])
    who_send = relationship('Profile', foreign_keys=[who_send_id])
    request_friend = relationship('RequestFriend', back_populates='accept_friend')
    notifications = relationship('Notification', back_populates='accept_friend', cascade="all, delete")


class Friend(Base):
    __tablename__ = 'friends'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    friend_id = Column(Integer, ForeignKey('profiles.id'))

    profile = relationship('Profile', foreign_keys=[profile_id])
    friend = relationship('Profile', foreign_keys=[friend_id])


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, index=True)
    datetime_create = Column(DateTime)
    check = Column(Boolean, default=True)
    profile_first_id = Column(Integer, ForeignKey('profiles.id'))
    profile_second_id = Column(Integer, ForeignKey('profiles.id'))

    profile_first = relationship('Profile', foreign_keys=[profile_first_id])
    profile_second = relationship('Profile', foreign_keys=[profile_second_id])
    messages = relationship('Message', back_populates='chat')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    viewed = Column(Boolean, default=False)
    datetime_create = Column(DateTime)
    datetime_update = Column(DateTime)
    datetime_create_float = Column(Float)
    datetime_update_float = Column(Float)
    profile_from_id = Column(Integer, ForeignKey('profiles.id'))
    profile_to_id = Column(Integer, ForeignKey('profiles.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))

    profile_from = relationship('Profile', foreign_keys=[profile_from_id])
    profile_to = relationship('Profile', foreign_keys=[profile_to_id])
    chat = relationship('Chat', back_populates='messages')


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String, unique=True)
    title = Column(String(length=48))
    genre = Column(String)
    count_subscribers = Column(Integer)
    creator_id = Column(Integer, ForeignKey('profiles.id'))

    creator = relationship('Profile', back_populates='groups')
    subscribers = relationship('Subscriber', back_populates='group')
    avatar = relationship('GroupAvatar', back_populates='group')


class GroupAvatar(Base):
    __tablename__ = 'avatar_group'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))

    group = relationship('Group', back_populates='avatar')


class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    profile = relationship('Profile', back_populates='subscribers')
    group = relationship('Group', back_populates='subscribers')






