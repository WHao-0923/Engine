
query = input("Please enter your query: ")

words = query.split()

with open('index.txt', 'r+') as f:
    