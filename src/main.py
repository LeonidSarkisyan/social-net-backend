from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import profiles, \
    authetication, users, posts, likes, \
    comments, requestsfriends, friends, chats, messages, groups
import src.websocketschats
import src.messagenotifications

import src.notifications
from src.database import engine
from src.models import Base
from fastapi.staticfiles import StaticFiles


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(authetication.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(src.notifications.router)
app.include_router(requestsfriends.router)
app.include_router(friends.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(src.messagenotifications.router)
app.include_router(src.websocketschats.router)
app.include_router(groups.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(engine)

