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

def rocket(human, check=None):
    # seed random using human slug
    random.seed(str(human.slug))

    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(100000, 999999))

    if check:
        # Add all numbers in random_numbers
        total = 0
        for number in random_numbers:
            if fizzbuzzcheck(number):
                total += number
     
        if check == total:
            return True

    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string

def fibonacci(n):
    """Return a list of the first n Fibonacci numbers."""
    fib = []
    a, b = 0, 1
    while len(fib) < n:
        fib.append(b)
        a, b = b, a + b
    return fib


def fuel(human, check=False):
    # seed random using human slug
    random.seed(str(human.slug))

    fibonacci_list = fibonacci(20)
    fibonacci_list = random.sample(fibonacci_list, 5)

    random_list = random.sample(range(max(fibonacci_list)), 9995)

    new_list = random_list + fibonacci_list

    # shuffle new list
    random.shuffle(new_list)

    if check:
        # find all fibonacci numbers in new_list and sum them
        total = 0
        for number in new_list:
            if number in fibonacci_list:
                total += number

                return True

    return ",".join(str(x) for x in new_list)

# Write a "FizzBuzz" checker. Return True if number is divisible by 3, 5, or both.
def fizzbuzzcheck(value):
    if value % 3 == 0 and value % 5 == 0:
        return True
    elif value % 3 == 0:
        return True
    elif value % 5 == 0:
        return True
    else:
        return False
    

def visualize():
    pass



if __name__ == "__main__":
    visualize()

    

    