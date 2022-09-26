

def fun(variable):
    userGroups = ['bug_report', 'academic']
    if (variable in userGroups):
        return True
    else:
        return False

subjects = ['bug_report', 'false_positive', 'suggestions', 'academic', 'other']

filtered = filter(fun, subjects)
myList = []

print('The filtered letters are:')
for s in filtered:
    myList.append(s)
    print(s)

print("my list down there")
for i in myList:
    print(i)

print(len(myList))