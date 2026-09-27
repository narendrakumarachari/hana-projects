print("Welcome to Hello.py!")
print("I'm Python")
name = input("What is your name? ")
print(f"Hello, {name}!")
ans = input("are you friendly? (yes/no) ")
if ans == "yes":
    print("That's great to hear!")
    print(f"Nice to meet you, {name}!")
elif ans == "no":
    print("A snake can bite,Grrrrrr!")
    print(f"you are not friendly, {name}!")
else:
    print("I didn't understand your answer.")