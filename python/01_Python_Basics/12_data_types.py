# Name = "Alice" # String
# Age = 11 # Integer
# Height = 3.4 # Float
# Student = True # Boolean

# print(type(Student))
# print(type(Name))
# print(type(Age))
# print(type(Height))

# print("Name:", Name)
# print("Age:", Age) 
# print("Height:", Height)
# print("Student:", Student)

# # more examples of data types
# list = [1, 2, 3, 4, 5] # List, ordered, mutable, allows duplicate elements
# tuple = (1, 2, 3, 4, 5) # Tuple, ordered, immutable
# dict = {"name": "Alice", "age": 11, "height": 3.4} # Dictionary, unordered, mutable
# set = {1, 2, 3, 4, 5} # Set, unordered, mutable, no duplicate elements

# print(type(list))
# print(type(tuple))
# print(type(dict))
# print(type(set))

# print("List:", list)
# print("Tuple:", tuple)
# print("Dictionary:", dict)
# print("Set:", set)

# # examples of indexing and slicing and changing the value of a list plus being mutable
# print(list)
# list[4] = 10 # changing the value of the 5th element in the list
# print(list) # Output: [1, 2, 3, 4, 10]

# fruitsinbasket = ["apple", "banana", "cherry", "date", "elderberry"]
# print(fruitsinbasket)
# fruitsinbasket.append("fig") # adding a new element to the list
# fruitsinbasket.append("grape")
# fruitsinbasket.append("mango")
# print(fruitsinbasket)

# candies = ["snickers", "twix", "kitkat", "milkyway", "hershey", "mnms", "resses", "skittles"]
# print(candies)
# candies.remove("mnms") # removing an element from the list
# print(candies)
# candies.pop(2) # removing an element from the list by index
# print(candies)
# candies.insert(2, "haribo") # adding an element to the list at a specific index
# print(candies)
# candies[1] = "mars" # changing the value of an element in the list
# print(candies)

# exampels of being immutable and changing the value of a tuple
stringbling = "Hello World"
stringbling = stringbling.replace("World", "Python") # changing the value of a string
print(stringbling) # Output: Hello Python

# scores = (90, 95, 83)
# print(scores)
# scores[2] = 100 # This would cause an error since tuples are immutable
# print(scores) # Output: [90, 95, 100]