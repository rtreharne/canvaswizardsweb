import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def normal(human, check=None, example=False):

    if example:
        random.seed(str("example"))
    else:
        random.seed(str(human.slug))

    # Choose a random number between 1000 and 9999
    mean = random.randint(1000, 9999)
    std_dev = random.randint(100, 999)
    samples = [int(random.normalvariate(mean, std_dev)) for _ in range(1000)]

    mean = np.mean(samples)
    std_dev = np.std(samples, ddof=1)

    if check:
        print("checking")
        print(check, int(mean * std_dev), mean, std_dev)
        # multiply mean my std_dev and round to nearest integer
        if check == int(mean * std_dev):
            return True

    random_numbers_string = ""
    for number in samples:
        random_numbers_string += f"{number}\n"

    return random_numbers_string

def name_seed(human, check=None):
    random.seed(str(human.slug))

    random_number = random.randint(100000,999999)

    if check:
        if check == random_number:
            return True
        
    return random_number

def trantor(human, check=None):
    # Quesiton 1

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
    # Question 2

    # ADD EVEN NUMBERS ONLY

    # seed random using human slug
    random.seed(str(human.slug)+str(human.first_name)+str(human.last_name))

    # Create a list of 10000 random numbers between 1000000 and 9999999
    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(1000000, 9999999))

    if check:
        # Add all numbers in random_numbers
        total = 0
        for number in random_numbers:
            if number % 2 == 0:
                total += number
     
        if check == total:
            return True
    
    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string

def rocket(human, check=None):
    # Question 3

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
        random_numbers_string += f"{number},"

    # remove final comma
    random_numbers_string = random_numbers_string[:-1]
    
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
    # Question 4

    # seed random using human slug
    random.seed(str(human.slug))

    fibonacci_list = fibonacci(20)
    fibonacci_list = random.sample(fibonacci_list, 5)

    random_list = [random.randint(1, max(fibonacci_list)) for x in range(1, 1000)]

    new_list = random_list + fibonacci_list

    random.shuffle(new_list)

    if check:
        # find all fibonacci numbers in new_list and sum them
        fibonacci_list = fibonacci(20)
        total = 0
        for number in new_list:
            if number in fibonacci_list:
                print(number)
                total += number

        print("TOTAL", total)

        if check == total:
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
    

def starmap(human, check=False):
    # Question 5

    random.seed(str(human.slug))

    map = ""
    
    for i in range(100):
        for j in range(100):
            if random.random() < 0.1:
                map += "*"
            else:
                map += "."
        map += "\n"

    if check:
        lines = list(map.split("\n"))
        coords = []
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                if lines[i][j] != ".":
                    coords.append((j, i))
        
        x_sum = 0
        y_sum = 0
        for coord in coords:
            x_sum += coord[0]
            y_sum += coord[1]
        
        avg_x = x_sum / len(coords)
        avg_y = y_sum / len(coords)

        x = round(avg_x * 100)
        y = round(avg_y * 100)
        if check == int(str(x) + str(y)):
            return True

    return map

def enlightenment(human, check=False):
    # Question 6

    random.seed(str(human.first_name)+str(human.last_name))


    if check:
        if check == random.randint(100000, 999999):
            return True
    
    
    # Create a blank image with a white background
    image_width = 500
    image_height = 200
    background_color = (255, 255, 255)
    image = Image.new("RGB", (image_width, image_height), background_color)

    # Specify the font and size
    font_size = 18
    font = ImageFont.load_default(font_size)

    # Specify the text and its position
    text = str(random.randint(100000, 999999))
    text_color = (0, 0, 0)
    text_position = (50, 30)

    # Draw the text on the image
    draw = ImageDraw.Draw(image)
    draw.text(text_position, text, font=font, fill=text_color)


    # Reverse engineer the draw object to extract coordinates of black pixels that can be plotted on a scatterplot
    black_pixels = []

    for x in range(image_width):
        for y in range(image_height):
            if draw._image.getpixel((x,y)) != (255,255,255):
                black_pixels.append((x,y))
  

    x = [x[0] for x in black_pixels]
    y = [x[1] for x in black_pixels]

    # reverse y-axes
    y = [image_height - y for y in y]

    # format x and y into a text file
    text_file = ""
    for i in range(len(x)):
        text_file += f"{x[i]},{y[i]}\n"

    return text_file
  
        
    