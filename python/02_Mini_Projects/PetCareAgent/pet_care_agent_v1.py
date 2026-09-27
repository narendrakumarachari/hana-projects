


def catcare():
    print("Hi, I am a Cat Care Agent.")
    whatcat=input ("How can I assist you?")
    if whatcat=="treatment":
        print("I can provide you with a basic treatment plan for your cat.")
    elif whatcat=="grooming":
        print("I can provide you with grooming tips for your cat.")
    elif whatcat=="health":
        print("I can provide you with a list of things to do to keep your cat healthy.")
    else:
        print("I do not understand your request. Please choose from treatment, grooming, or health.")

def fishcare():
    print("Hi, I am a Fish Care Agent.")
    whatfish=input ("How can I assist you?")
    if whatfish=="treatment":
        print("I can provide you with a basic treatment plan for your fish.")
    elif whatfish=="supplements":
        print("I can provide you with information about extra supplements for your fish.")
    elif whatfish=="health":
        print("I can provide you with a list of things to do to keep your fish healthy.")
    else:
        print("I do not understand your request. Please choose from treatment, supplements, or health.")

def birdcare():
    print("Hi, I am a Bird Care Agent.")
    whatbird = input("How can I assist you?")
    if whatbird == "treatment":
        print("I can provide you with a basic treatment plan for your bird.")
    elif whatbird == "toys":
        print("I can provide you with information about toys for your bird.")
    elif whatbird == "health":
        print("I can provide you with a list of things to do to keep your bird healthy.")
    else:
        print("I do not understand your request. Please choose from treatment, toys, or health.")


def dogcare():
    print("Hi, I am a Dog Care Agent.")
    whatdog = input("How can I assist you?")
    if whatdog == "treatment":
        print("I can provide you with a basic treatment plan for your dog.")
    elif whatdog == "grooming":
        print("I can provide you with grooming tips for your dog.")
    elif whatdog == "health":
        print("I can provide you with a list of things to do to keep your dog healthy.")
    else:
        print("I do not understand your request. Please choose from treatment, grooming, or health.")


phone = input("Please enter who you want to call: ")
if phone == "123 4567":
    print("Welcome to the Pet Care!")
    summonag = input('If you need an agent to help you with your pet, please select "agent" or type "exit" to exit the program: ')
    if summonag == "agent":
        choice = int(input("Enter 1 for Cat Care, 2 for Fish Care, 3 for Dog Care, or 4 for Bird Care: "))

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
    elif summonag == "exit":
        print("Thank you for using the Pet Care program. Goodbye!")
    else:
        print("Invalid selection. Please type 'agent' or 'exit'.")
else:
    print("The person you are trying to reach is currently unavailable.")