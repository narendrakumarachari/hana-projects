from books import books
print("Welcome to Rose Library")
def checkout():
    while True:
        book=input("what would you like to check out today (or type 'done' to finish): ")
        if book.lower() == "done":
            break

        elif book in books.values():
            found_key = next(key for key, title in books.items() if title == book)
            print("Thank you for visiting! You have taken",books[found_key])
            del books[found_key]

        else:
            print("this book is on an other account come back later")
try:
    attempts = 0

    while attempts < 5:
        residentid = int(input("Enter your ID number: "))

        if residentid == 123:
            print("Welcome Alice")
            print (books.values())
            checkout()
            break

        elif residentid == 456:
            print("Welcome Tom")
            print (books.values())
            checkout()
            break

        else:
            attempts += 1
            print("Wrong ID try again")

    if attempts == 5:
        print("Access DENIED")

except:
    print("Something went wrong")