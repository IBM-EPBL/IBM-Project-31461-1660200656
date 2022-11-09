def add(a,b):
        return a+b
def sub(a,b):
        return a-b
def mul(a,b):
        return a * b
def div(a,b):
        return a / b
a = int(input("Enter the first number: "))
b = int(input("Enter the second number: "))

option = int(input("select the operation to be performed:\n 1.add\t 2.sub\t 3.mul\t 4.div\t \nEnter Your Choice\t:"))

if option == 1:
    print(add(a,b))
elif option == 2:
    print(sub(a,b))
elif option == 3:
    print(mul(a,b))
else:
    print(div(a,b))
