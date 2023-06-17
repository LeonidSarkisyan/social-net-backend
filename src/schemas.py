import datetime
from pydantic import BaseModel, conlist
from typing import List
from src.database import get_db


class Login(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserAfterCreate(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Image(BaseModel):
    url: str


class Like(BaseModel):
    user_id: int
    post_id: int

    class Config:
        orm_mode = True


class ProfileComment(BaseModel):
    id: int
    name: str
    surname: str
    tag_name: str

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    text: str
    user_id: int
    post_id: int

    class Config:
        orm_mode = True


class Comment(BaseModel):
    id: int
    text: str
    user_id: int
    post_id: int
    create_date_time: datetime.datetime
    profile: ProfileComment

    class Config:
        orm_mode = True


class PostNotification(BaseModel):
    id: int
    text: str
    profile: ProfileComment

    class Config:
        orm_mode = True


class CommentNoti(BaseModel):
    id: int
    text: str
    # create_date_time: datetime.datetime
    profile: ProfileComment
    post: PostNotification

    class Config:
        orm_mode = True


class LikeNoti(BaseModel):
    id: int
    user_id: int
    post_id: int
    profile: ProfileComment
    posts: PostNotification

    class Config:
        orm_mode = True


class RequestFriendNoti(BaseModel):
    id: int
    accept: bool
    profile_from_id: int
    profile_to_id: int
    profile_from: ProfileComment

    class Config:
        orm_mode = True


class AcceptFriend(BaseModel):
    id: int
    who_accept_id: int
    who_send_id: int
    who_accept: ProfileComment

    class Config:
        orm_mode = True


class Post(BaseModel):
    profile_id: int
    id: int
    text: str | None = None
    datetime_create: datetime.datetime
    likes: list[Like] = []
    comments: list[CommentCreate] = []

    class Config:
        orm_mode = True


class PostCreate(BaseModel):
    text: str | None = None
    profile_id: int

    likes: list[Like] = []
    comments: list[Comment] = []

    class Config:
        orm_mode = True


class Friend(BaseModel):
    id: int
    name: str
    surname: str
    avatar: Image | None = None


class ProfileCreate(BaseModel):
    tag_name: str
    name: str
    surname: str
    status: str | None = None
    city: str | None = None
    user_id: int

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    username: str
    password: str
    profile: ProfileCreate


class Profile(BaseModel):
    id: int
    tag_name: str
    name: str
    surname: str
    status: str | None = None
    city: str | None = None
    avatar: Image | None = None
    posts: List[Post]
    friends: List[Friend]


class UpdateProfile(BaseModel):
    name: str | None = None
    surname: str | None = None
    tag_name: str | None = None
    status: str | None = None
    city: str | None = None


class Notification(BaseModel):
    id: int
    type: str
    date: datetime.datetime
    viewed: bool
    comment: CommentNoti | None = None
    like: LikeNoti | None = None
    request_friend: RequestFriendNoti | None = None
    accept_friend: AcceptFriend | None = None

    class Config:
        orm_mode = True


class RequestFriendCreate(BaseModel):
    profile_from_id: int
    profile_to_id: int

    class Config:
        orm_mode = True

class RequestFriend(BaseModel):
    id: int
    profile_from_id: int
    profile_to_id: int
    date: datetime.datetime

    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    text: str
    profile_from_id: int
    profile_to_id: int
    chat_id: int


class Message(MessageCreate):
    id: int
    viewed: bool = False
    datetime_create_float: float
    datetime_update_float: float

    class Config:
        orm_mode = True


class ChatCreate(BaseModel):
    profile_first_id: int
    profile_second_id: int

    class Config:
        orm_mode = True


class Chat(BaseModel):
    id: int
    profile_first_id: int
    profile_second_id: int
    check: bool
    messages: list[Message]

    class Config:
        orm_mode = True


class ChatSimple(BaseModel):
    id: int
    profile_first_id: int
    profile_second_id: int
    check: bool

    class Config:
        orm_mode = True


class FriendOut(BaseModel):
    id: int
    profile_id: int
    friend_id: int
    friend: ProfileComment

    class Config:
        orm_mode = True


class GroupCreate(BaseModel):
    tag_name: str
    title: str
    genre: str

    class Config:
        orm_mode = True


class Group(GroupCreate):
    id: int
    creator_id: int

    class Config:
        orm_mode = True


class SubGroup(BaseModel):
    id: int
    group: Group

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
