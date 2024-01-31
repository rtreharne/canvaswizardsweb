import numpy as np

def read_file(fname):
    with open(fname, 'r') as f:
        lines = [list(x.replace("\n", "")) for x in f.readlines()]
        # convert list of lists to matrix
        matrix = np.array(lines)
        return matrix

def get_coords(matrix):
    # find coords of elements in matrix that are not "."
    coords = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] != ".":
                coords.append((i, j))
    return coords

def galactic_centre(coords):
    # calculate average x and average y from coords
    x = [x[0] for x in coords]
    y = [x[1] for x in coords]
    avg_x = sum(x) / len(x)
    avg_y = sum(y) / len(y)
    return (avg_x, avg_y)
    

if __name__ == "__main__":
    matrix = read_file("test_input.txt")
    coords = get_coords(matrix)

    gc = galactic_centre(coords)


    x = round(gc[0]*100)
    y = round(gc[1]*100)
    print(int(str(x)+str(y)))

