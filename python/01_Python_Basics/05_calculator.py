a=int(input("Enter number"))
b=int(input("Enter another number"))
question=input("Enter the operation you want to perform: ")
if question=="+":
    print(a+b)
elif question=="-":
    print(a-b)
elif question=="*":
    print(a*b)
elif question=="/":
    print(a/b)
else:
    print("Invalid operation")