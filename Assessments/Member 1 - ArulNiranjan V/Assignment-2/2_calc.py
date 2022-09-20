def add(a,b):
        return a+b
def sub(a,b):
        return a-b
def mul(a,b):
        return a * b
def div(a,b):
        return a / b
def mod(a,b):
        return a % b
        
a = int(input("Enter the first number: "))
b = int(input("Enter the second number: "))

choice = int(input("select the operation to be performed:\n 1.add\t 2.sub\t 3.mul\t 4.div\t 5.mod\t\nEnter Your Choice\t:"))

if choice == 1:
    print(add(a,b))
elif choice == 2:
    print(sub(a,b))
elif choice == 3:
    print(mul(a,b))
elif choice == 4:
    print(div(a,b))
else:
    print(mod(a,b))