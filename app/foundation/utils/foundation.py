import random

def trantor(human, check=None):
    # seed random using human slug
    random.seed(str(human.slug))

    # Create a list of 10000 random numbers between 1000000 and 9999999
    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(1000000, 9999999))

    if check:
        # Add all numbers in random_numbers
        total = 0
        for number in random_numbers:
            total += number
     
        if check == total:
            return True
    
    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string

def portal(human, check=None):
    # seed random using human slug
    random.seed(str(human.slug))

    # Create a random string of 10000 integers
    random_integer_string = ""
    for i in range(10000):
        random_integer_string += str(random.randint(0, 9))
    
    if check:
        reverse = random_integer_string[::-1]
        prod = 1
        for item in reverse[::3]:
            if item != "0":
                prod *= int(item)
        if check == len(str(prod)):
            return True
        
    return random_integer_string

    