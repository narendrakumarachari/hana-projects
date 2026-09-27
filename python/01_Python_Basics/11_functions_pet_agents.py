# def greet():
#     print("Hello!")
# # while i <= 5:
# #  print(i)
# #  i = i + 1
# greet()



# call=input('Type "vet" to see what a vet can do for you: ')
# def vet():
#     print("Hello I am a vet,so how can I help you?")
#     print("pls tell my your name, location, and pet type:")
#     print("I will provide with a basic treatmet plan groom your pet and give you a list of things to do to keep your pet healthy")

# this is an argument function, it takes an argument and prints it
# def greet(name):
#     print("Hello", name)

# greet(input("Enter your name: "))


def catcare():
    print("Hi, I am a Cat Care Agent.")
    print("How can I assist you?")

def fishcare():
    print("Hi, I am a Fish Care Agent.")
    print("How can I assist you?")

def dogcare():
    print("Hi, I am a Dog Care Agent.")
    print("How can I assist you?")

def birdcare():
    print("Hi, I am a Bird Care Agent.")
    print("How can I assist you?")


choice = int(input("Enter 1, 2, 3 or 4: "))

if choice == 1:
    catcare()
elif choice == 2:
    fishcare()
elif choice == 3:
    dogcare()
elif choice == 4:
    birdcare()
else:
    print("Invalid choice")