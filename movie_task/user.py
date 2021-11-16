from . import schema

allUsers = []

def createUser(user):
    allUsers.append(user.dict())
    return allUsers[-1]

def authentication(user):
    import pdb; pdb.set_trace()
    for i in allUsers:
        if i['username'] == user["username"] and i['password'] == user["password"]:
            return i
    else:
        return None  
    