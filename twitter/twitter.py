from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:

    # The user who is logged in is stored as an instance variable
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
        first_tweet = True
        for tweet in tweets:
            # Put a line before each tweet except the first one
            if first_tweet:
                first_tweet = False
                print("") # put a new line before the first tweet
            else:
                print("==============================")
            print(tweet)

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
        # We could query for User.username but it would return a list of tuples,
        # so we would have to run an extra line like [x[0] for x in current_users]
        # which is equally annoying
        current_users = db_session.query(User)
        usernames = [u.username for u in current_users]

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
                self.current_user = new_user # "logs in" the user
                print("You have been logged in as well!")
                return


    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        while True:
            username = input("Username: ")
            password = input("Password: ")
            user = db_session.query(User).where((User.username==username) & (User.password==password)).first()
            if user is None:
                print("Invalid username or password")
            else:
                print("You're logged in!")
                self.current_user = user
                return

        
    """
    Logs out the user.
    """
    def logout(self):
        self.current_user = None
        print("You have been logged out!")

    """
    Allows the user to login,  
    register, or exit.

    The boolean returned indicates whether the user wants to exit.
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
            return False

    """
    Allows the user to follow another user.
    Prevents them from following themselves or a user that does not exist.
    """
    def follow(self):
        while True:
            follow = input("Who would you like to follow?")
            user = db_session.query(User).where(User.username == follow).first() # user to be followed
            currently_following = [u.username for u in self.current_user.following]
            if user is None:
                print("That user does not exist")
            elif user is self.current_user:
                print("You can't follow yourself lmao")
            elif follow in currently_following:
                print("You already follow " + follow)
            else:
                self.current_user.following.append(user)
                db_session.commit()
                print("Success! YOU NOW FOLLOW " + follow)
                return # break out of the loop since we have succeeded

    """
    Allows the current user to unfollow another user.
    Prevents them from unfollowing a user which does not exist
    or a user which they don't already follow.
    """
    def unfollow(self):
        while True:
            follow = input("Who would you like to unfollow?")
            user = db_session.query(User).where(User.username == follow).first()
            currently_following = [u.username for u in self.current_user.following]
            if user is None:
                print("That user does not exist") 
            elif follow not in currently_following:
                print("You don't follow " + follow)
            else:
                self.current_user.following.remove(user)
                db_session.commit()
                print("Success! You no longer " + follow)
                return

    def tweet(self):
        content = input("Create Tweet: ")
        tag_names = input("Enter your tags separated by spaces (don't use hashtags): ").split(" ")
        new_tweet = Tweet(content, datetime.now(), self.current_user.username)
        db_session.add(new_tweet)

        tags = [] # Stores the Tag variables associated with the new tweet
        for tag_name in tag_names:
            tag_in_database = db_session.query(Tag).where(Tag.content==tag_name).first()
            
            # If this is a new tag, create it
            if tag_in_database is None:
                new_tag = Tag(tag_name)
                db_session.add(new_tag)
                tags.append(new_tag)
            else:
                tags.append(tag_in_database)
        for tag in tags:
            new_tweet.tags.append(tag) # add all the necessary tags to the new tweet
        
        db_session.commit()
        print("Success!")
    
    """
    Allows the user to view their tweets.
    """
    def view_my_tweets(self):
        tweets = db_session.query(Tweet).where(Tweet.username==self.current_user.username)
        self.print_tweets(tweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        tweets = db_session.query(Tweet).order_by(Tweet.timestamp.desc()) # all the tweets, ordered by date

        # Gets only the tweets that are tweeted by a user the current user follows
        tweets = list(filter(lambda t: t.username in [u.username for u in self.current_user.following], tweets))
        
        # Takes the most recent 5 tweets
        self.print_tweets(tweets[:5])

    """
    Shows the tweets by a given user.
    """
    def search_by_user(self):
        username = input("What username do you want to search for?")
        users = db_session.query(User)
        usernames = [u.username for u in users]
        if username not in usernames:
            print("There is no user with that username")
        else:
            # Gets the User object corresponding to the desired username 
            # then creates a new Twitter class with that user logged in and calls view_my_tweets()
            Twitter(list(filter(lambda x: x.username==username, users))[0]).view_my_tweets()

    """
    Shows the tweets with a given tag.
    """
    def search_by_tag(self):
        tag_name = input("What tag do you want to search for?")
        tag = db_session.query(Tag).where(Tag.content == tag_name).first()
        if tag is None:
            print("That tag does not exist")
        else:
            self.print_tweets(tag.tweets)

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        while True:
            print("Welcome to ATCS Twitter!")
            if not self.startup():
                break

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
