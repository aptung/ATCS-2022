"""
The file that holds the schema/classes
that will be used to create objects
and connect to data tables.
"""

from sqlalchemy import ForeignKey, Column, INTEGER, TEXT, DATETIME
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    # Columns
    username = Column("username", TEXT, primary_key=True)
    password = Column("password", TEXT, nullable=False)
    tweets = relationship("Tweet", back_populates="user")

    following = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.follower_id",
                             secondaryjoin="User.username==Follower.following_id")
    
    followers = relationship("User", 
                             secondary="followers",
                             primaryjoin="User.username==Follower.following_id",
                             secondaryjoin="User.username==Follower.follower_id",
                             overlaps="following")
    def __init__(self, username, password, tweets=None):
        self.username = username
        self.password = password
        self.tweets = tweets

    def __repr__(self):
        return "@" + self.username


class Follower(Base):
    __tablename__ = "followers"

    # Columns
    id = Column("id", INTEGER, primary_key=True)
    follower_id = Column('follower_id', TEXT, ForeignKey('users.username'))
    following_id = Column('following_id', TEXT, ForeignKey('users.username'))

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column("id", INTEGER, primary_key=True, autoincrement=True)
    content = Column("content", TEXT, nullable=False)
    timestamp = Column("timestamp", TEXT, nullable=False)
    username = Column("username", TEXT, nullable=False)
    user = relationship("User", back_populates="tweets")
    tags = relationship("Tag", back_populates="tweets")

    # Constructor
    def __init__(self, content, timestamp, username):
        # id auto-increments
        self.content=content
        self.timestamp=timestamp
        self.username=username

    def __repr__(self):
        # fix tags?
        return "@" + self.user.username + "\n" + self.content + "\n" + self.tags + "\n" + self.timestamp


class Tag(Base):
    __tablename__ = "tags"

    # Columns
    id = Column("id", INTEGER, primary_key=True, autoincrement=True)
    content = Column("content", TEXT, nullable=False)
    tweets = relationship("Tweet", back_populates="tags")

    # Constructor
    def __init__(self, content):
        # id auto-increments
        self.content=content
    
    def __repr__(self):
        return "#" + self.content


class TweetTag(Base):
    __tablename__ = "tweettags"

    id = Column("id", INTEGER, primary_key=True, autoincrement=True)
    tweet_id = Column("tweet_id", ForeignKey("tweets.id"))
    tag_id = Column("tag_id", ForeignKey("tags.id"))

    # TODO: Complete the class
    pass
