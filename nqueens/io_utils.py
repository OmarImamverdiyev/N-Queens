# io_utils.py

def read_input(filename):
    with open(filename, "r") as f:
        board = [int(line.strip()) for line in f if line.strip()]
    return board
