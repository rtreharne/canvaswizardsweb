from PIL import Image, ImageDraw, ImageFont
import random

random.seed("robert-treharne")

# Create a blank image with a white background
image_width = 2000
image_height = 100
background_color = (255, 255, 255)
image = Image.new("RGB", (image_width, image_height), background_color)

# Specify the font and size
font_size = 40
font = ImageFont.truetype("arial.ttf", font_size)

# Specify the text and its position
text = "robertwozere"+str(random.randint(1000000, 9999999))
text_color = (0, 0, 0)
text_position = (50, 30)

# Draw the text on the image
draw = ImageDraw.Draw(image)
draw.text(text_position, text, font=font, fill=text_color)

# Reverse engineer the draw object to extract coordinates of black pixels that can be plotted on a scatterplot
black_pixels = []
for x in range(image_width):
    for y in range(image_height):
        if draw._image.getpixel((x,y)) == (0,0,0):
            black_pixels.append((x,y))

# Plot the black pixels
import matplotlib.pyplot as plt
x = [x[0] for x in black_pixels]
y = [x[1] for x in black_pixels]

# reverse y-axes
y = [image_height - y for y in y]
plt.scatter(x, y)
plt.show()

