'''
    Author: Sean Cavalieri
    Manage the Database
'''
import sqlalchemy as db
import pandas as pd
from datetime import datetime

# Creating SQLite3 engine automatically creates datafile if it does not exist
engine = db.create_engine('sqlite:///SSdatabase.sqlite')
connection = engine.connect()
metadata = db.MetaData()

# Create accounts Table
accounts = db.Table('accounts', metadata,
              db.Column('id', db.Integer(), primary_key=True, autoincrement=True),
              db.Column('username', db.String(255), nullable=False),
              db.Column('password', db.String(255), nullable=False),
              )
# Create profiles Table
profiles = db.Table('profiles', metadata,
              db.Column('id', db.Integer(), primary_key=True, autoincrement=True),
              db.Column('firstName', db.String(255), nullable=False),
              db.Column('lastName', db.String(255), nullable=False),
              db.Column('userID', db.Integer()),
              db.Column('dateAdded', db.DateTime()),
              )
metadata.create_all(engine) #Creates both tables

# Create whole new user
def createUser(username, password):
    connection = engine.connect()
    query = db.insert(accounts).values(username=username, password=password)
    connection.execute(query)
    # get the id of above row to insert in profiles row
    query2 = db.select([accounts]).where(accounts.columns.username == username)
    ResultProxy = connection.execute(query2)
    resultRows = ResultProxy.fetchone()
    # Make profiles row using id from previous query
    if resultRows:
        query3 = db.insert(profiles).values(firstName="-", lastName="-", userID=resultRows[0], dateAdded=datetime.now())
        connection.execute(query3)
        return True
    return False

# Delete a whole user
#  Usage --> database.deleteUser(sessionTokens[sessionID])
def deleteUser(username):
    connection = engine.connect()
    # First get id from accounts with username to identify accounts/profiles rows
    query = db.select([accounts]).where(accounts.columns.username == username)
    ResultProxy = connection.execute(query)
    resultRow = ResultProxy.fetchone()
    if resultRow:
        # account found
        id = resultRow[0]
        # actually delete
        query2 = db.delete(accounts)
        query2 = query2.where(accounts.columns.id == id)
        connection.execute(query2)
        query3 = db.delete(profiles)
        query3 = query3.where(profiles.columns.userID == id)
        connection.execute(query3)
        return True
    else:
        return False

# Check if username is in use
def isUsernameTaken(username):
    connection = engine.connect()
    query = db.select([accounts]).where(accounts.columns.username == username)
    ResultProxy = connection.execute(query)
    resultRow = ResultProxy.fetchone()
    if resultRow:
        return True
    else:
        return False

# Check if valid username password pair
def authenticate(username, password):
    connection = engine.connect()
    query = db.select([accounts]).where(accounts.columns.username == username)
    ResultProxy = connection.execute(query)
    resultRow = ResultProxy.fetchone()
    if resultRow:
        # username exists
        if resultRow[2] == password:
            # password is correct
            return True
    return False

# Change password to newPassword for user with username
def changePassword(username, newPassword):
    connection = engine.connect()
    query = db.update(accounts).values(password = newPassword).where(accounts.columns.username == username)
    connection.execute(query)
    return True

def changeFirstLast(id, newFirstName, newLastName):
    connection = engine.connect()
    query = db.update(profiles).values(firstName = newFirstName, lastName = newLastName).where(profiles.columns.userID == id)
    connection.execute(query)

# Get information of another user
def viewProfileOf(username):
    connection = engine.connect()
    query = db.select([accounts]).where(accounts.columns.username == username)
    ResultProxy = connection.execute(query)
    resultRow = ResultProxy.fetchone()
    if(resultRow):
        id = resultRow[0]
        query2 = db.select([profiles]).where(profiles.columns.userID == id)
        ResultProxy2 = connection.execute(query2)
        resultRow2 = ResultProxy2.fetchone()
        if resultRow2:
            arr = [username]
            arr.append(resultRow2[1])
            arr.append(resultRow2[2])
            arr.append(resultRow2[3])
            arr.append(resultRow2[4])
            return arr
    return []

    # Get information of another user by userID
def viewProfileByID(userID):
    connection = engine.connect()
    query = db.select([accounts]).where(accounts.columns.id == userID)
    ResultProxy = connection.execute(query)
    resultRow = ResultProxy.fetchone()
    if(resultRow):
        username = resultRow[1]
        query2 = db.select([profiles]).where(profiles.columns.userID == userID)
        ResultProxy2 = connection.execute(query2)
        resultRow2 = ResultProxy2.fetchone()
        if resultRow2:
            arr = [username]
            arr.append(resultRow2[1])
            arr.append(resultRow2[2])
            arr.append(resultRow2[3])
            arr.append(resultRow2[4])
            return arr
    return []

# Get information of all users
def viewAllAccounts():
    connection = engine.connect()
    query = db.select([profiles])
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    query2 = db.select([accounts])
    ResultProxy2 = connection.execute(query2)
    ResultSet2 = ResultProxy2.fetchall()
    members = []
    for member in ResultSet2:
        members.append([member[0], member[1]])
    for member in members:
        for check in ResultSet:
            if member[0] == check[3]:
                member.append(check[1])
                member.append(check[2])
                member.append(check[4])
                break
    return members
