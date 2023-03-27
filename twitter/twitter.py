from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:

    def __init__(self, current_user=None):
        self.current_user = current_user

    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        current_users = db_session.query(User)
        usernames = {u.username for u in current_users}
        while True:
            username = input("What will your twitter handle be?")
            pass1 = input("Enter a password:")
            pass2 = input("Re-enter your password:")
            if pass1 != pass2:
                print("That passwords don't math. Try again.")
            elif username in usernames:
                print("That username is already taken. Try again.")
            else:
                new_user = User(username, pass1)
                db_session.add(new_user)
                db_session.commit()
                print("Welcome " + username + "!")
                self.current_user = new_user
                print("You have been logged in as well!")
                break


    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        while True:
            username = input("Username: ")
            password = input("Password: ")
            result = db_session.query(User).where((User.username==username) & (User.password==password)).first()
            if result == None:
                print("Invalid username or password")
            else:
                print("You're logged in!")
                self.current_user = result
                break

        
    
    def logout(self):
        self.current_user = None

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        i = input("Please select a menu option \n1. Login \n2. Register User \n0. Exit\n")
        if i=="1":
            self.login()
            return True
        elif i=="2":
            self.register_user()
            return True
        else:
            self.end()
            return False

    def follow(self):
        while True:
            follow = input("Who would you like to follow?")
            currently_following = {u.username for u in self.current_user.following} 
            if follow in currently_following:
                print("You already follow " + follow)
            else:
                db_session.add(Follower(self.current_user.username, follow))
                db_session.commit()
                print("Success! YOU NOW FOLLOW " + follow)
                return

    def unfollow(self):
        while True:
            follow = input("Who would you like to unfollow?")
            currently_following = {u.username for u in self.current_user.following} 
            if follow not in currently_following:
                print("You don't follow " + follow)
            else:
                db_session.delete(db_session.query(Follower).where((Follower.follower_id == self.current_user.username) & (Follower.following_id == follow)).first())
                db_session.commit()
                print("Success! You no longer " + follow)
                return

    def tweet(self):
        content = input("Create Tweet: ")
        tags = input("Enter your tags separated by spaces (don't use hashtags): ").split(" ")
        db_session.add(Tweet(content, datetime.now(), self.current_user.username))
        db_session.commit()

        tweet_id = db_session.query(Tweet).order_by(Tweet.id.desc()).first().id

        tag_ids = []
        for tag in tags:
            tag_in_database = db_session.query(Tag).where(Tag.content==tag).first()
            if tag_in_database is None:
                db_session.add(Tag(tag))
                db_session.commit()
                tag_ids.append(db_session.query(Tag).order_by(Tag.id.desc()).first().id)
            else:
                tag_ids.append(tag_in_database.id)
        for id in tag_ids:
            db_session.add(TweetTag(tweet_id, id))
        db_session.commit()

        print("Success!")
    
    def view_my_tweets(self):
        tweets = db_session.query(Tweet).where(Tweet.username ==self.current_user.username)
        for tweet in tweets:
            print(str(tweet) + "\n====================")
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        tweets = db_session.query(Tweet).order_by(Tweet.timestamp.desc()).limit(5)
        for t in tweets:
            if t.username in {u.username for u in self.current_user.following}:
                print(str(t) + "\n====================")

    def search_by_user(self):
        username = input("What username do you want to search for?")
        users = db_session.query(User)
        usernames = list(map(lambda x: x.username, users))
        if username not in usernames:
            print("There is no user with that username")
        else:
            Twitter(db_session.query(User).where(User.username==username).first()).view_my_tweets()

    def search_by_tag(self):
        tag = input("What tag do you want to search for?")
        tags = list(map(lambda x: x.content, db_session.query(Tag)))
        if tag not in tags:
            print("That tag does not exist")
        else:
            tweets = db_session.query(Tweet).join(TweetTag, TweetTag.tweet_id==Tweet.id).join(Tag, Tag.id==TweetTag.tag_id).where(Tag.content==tag)
            for tweet in tweets:
                print(str(tweet) + "\n====================")

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        while True:
            print("Welcome to ATCS Twitter!")
            if not self.startup():
                return

            while True:
                self.print_menu()
                option = int(input(""))

                if option == 1:
                    self.view_feed()
                elif option == 2:
                    self.view_my_tweets()
                elif option == 3:
                    self.search_by_tag()
                elif option == 4:
                    self.search_by_user()
                elif option == 5:
                    self.tweet()
                elif option == 6:
                    self.follow()
                elif option == 7:
                    self.unfollow()
                else:
                    self.logout()
                    break
        
        self.end()
