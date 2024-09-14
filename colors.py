import tkinter as tk
import itertools

# Initialize the main window
root = tk.Tk()

# Generate all RGB combinations with pwm bits = 2 (values 0 to 3)
colors = list(itertools.product(range(4), repeat=3))  # Generate all RGB combinations

columns = 8  # Number of columns to fit better on screen

for i, color in enumerate(colors):
    # Convert the RGB values (0-3) to 0-255 scale
    r, g, b = [int(255 * (value / 3)) for value in color]
    hex_color = f'#{r:02x}{g:02x}{b:02x}'

    # Create a frame for each color
    frame = tk.Frame(root, width=50, height=50, bg=hex_color)
    frame.grid(row=i // columns, column=(i % columns) * 2)  # Color square in column 0

    # Create a label for the RGB values (0-255 scale)
    label_text = f"R: {r}, G: {g}, B: {b}"
    label = tk.Label(root, text=label_text)
    label.grid(row=i // columns, column=(i % columns) * 2 + 1, padx=10)  # RGB values in column 1

# Run the GUI application
root.mainloop()
