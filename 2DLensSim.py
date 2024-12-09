import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.animation import FuncAnimation
from shapely.geometry import Polygon, MultiPolygon
import matplotlib
matplotlib.use('TkAgg')

# Global variables for simulation parameters
lens_width = 100  # Width of the lens (horizontal rectangle area)
lens_height = 50  # Height of the lens
wheel_size = 20   # Size of the diamond wheel (customizable octagon)
cutting_phases = []  # Cutting phases configuration

# Define the lens (as a Shapely polygon)
def create_lens():
    return Polygon([
        [-lens_width / 2, lens_height / 2],
        [lens_width / 2, lens_height / 2],
        [lens_width / 2, -lens_height / 2],
        [-lens_width / 2, -lens_height / 2]
    ])

lens = create_lens()

# Diamond wheel as an octagon
def create_wheel(center_x, center_y):
    vertices = np.array([
        [-wheel_size / 2, wheel_size / 2],
        [0, wheel_size],
        [wheel_size / 2, wheel_size / 2],
        [wheel_size, 0],
        [wheel_size / 2, -wheel_size / 2],
        [0, -wheel_size],
        [-wheel_size / 2, -wheel_size / 2],
        [-wheel_size, 0]
    ])
    return Polygon(vertices + [center_x, center_y])

# Initialize figure and axis
fig, ax = plt.subplots()
ax.set_aspect('equal', adjustable='box')
ax.set_xlim(-200, 200)
ax.set_ylim(-200, 200)

# Plot lens
lens_patch = MplPolygon(np.array(lens.exterior.coords), closed=True, color='blue', alpha=0.5, label='Lens')
ax.add_patch(lens_patch)

# Initialize wheel
wheel_x = 0
wheel_y = lens_height / 2
wheel = create_wheel(wheel_x, wheel_y)

wheel_patch = MplPolygon(np.array(wheel.exterior.coords), closed=True, color='darkgrey', alpha=0.9, label='Diamond Wheel')
ax.add_patch(wheel_patch)

def update_wheel_patch():
    global wheel_patch
    wheel_patch.set_xy(np.array(wheel.exterior.coords))

# Cutting logic
def cut_lens():
    global lens, wheel
    if lens.intersects(wheel):
        result = lens.difference(wheel)
        if isinstance(result, Polygon):
            lens = result
            lens_patch.set_xy(np.array(lens.exterior.coords))
        elif isinstance(result, MultiPolygon):
            lens = result
            combined_coords = []
            for polygon in lens.geoms:
                combined_coords.extend(polygon.exterior.coords)
            lens_patch.set_xy(np.array(combined_coords))
        elif result.is_empty:
            lens_patch.set_xy([])

def update(frame):
    global wheel_x, wheel_y, cutting_phases, wheel
    if not cutting_phases:
        return

    if frame < len(cutting_phases):
        phase = cutting_phases[frame]

        if phase['movement'] == 'down':
            wheel_y -= phase['step']
        elif phase['movement'] == 'left':
            wheel_x -= phase['step']
        elif phase['movement'] == 'up':
            wheel_y += phase['step']
        elif phase['movement'] == 'right':
            wheel_x += phase['step']

        # Update wheel position
        wheel = create_wheel(wheel_x, wheel_y)
        update_wheel_patch()

        # Perform cutting
        cut_lens()

# Desktop Application
class LensCuttingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lens Cutting Simulation")

        # Main Frames
        self.simulation_frame = tk.Frame(root)
        self.simulation_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Embed Matplotlib Plot
        self.canvas = FigureCanvasTkAgg(fig, master=self.simulation_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Controls
        self.create_controls()

    def create_controls(self):
        # Lens Dimensions
        lens_label = tk.Label(self.controls_frame, text="Lens Dimensions (mm)")
        lens_label.pack()

        self.lens_width_entry = tk.Entry(self.controls_frame)
        self.lens_width_entry.insert(0, str(lens_width))
        self.lens_width_entry.pack()

        self.lens_height_entry = tk.Entry(self.controls_frame)
        self.lens_height_entry.insert(0, str(lens_height))
        self.lens_height_entry.pack()

        # Wheel Dimensions
        wheel_label = tk.Label(self.controls_frame, text="Wheel Size (mm)")
        wheel_label.pack()

        self.wheel_size_entry = tk.Entry(self.controls_frame)
        self.wheel_size_entry.insert(0, str(wheel_size))
        self.wheel_size_entry.pack()

        # Cutting Steps
        steps_label = tk.Label(self.controls_frame, text="Cutting Steps")
        steps_label.pack()

        self.steps_text = tk.Text(self.controls_frame, height=10)
        self.steps_text.insert(tk.END, "down,10\nleft,5\nup,10")
        self.steps_text.pack()

        # Buttons
        apply_button = tk.Button(self.controls_frame, text="Apply Settings", command=self.apply_settings)
        apply_button.pack()

        start_button = tk.Button(self.controls_frame, text="Start Simulation", command=self.start_simulation)
        start_button.pack()

    def apply_settings(self):
        global lens_width, lens_height, wheel_size, cutting_phases, lens

        # Update dimensions
        lens_width = float(self.lens_width_entry.get())
        lens_height = float(self.lens_height_entry.get())
        wheel_size = float(self.wheel_size_entry.get())

        # Update cutting phases
        cutting_phases = []
        for line in self.steps_text.get("1.0", tk.END).strip().split("\n"):
            direction, distance = line.split(",")
            cutting_phases.append({"movement": direction, "step": float(distance)})

        # Recreate lens and wheel
        lens = create_lens()
        lens_patch.set_xy(np.array(lens.exterior.coords))
        update_wheel_patch()

        self.canvas.draw()

    def start_simulation(self):
        # Start the simulation for one full sequence of steps
        ani = FuncAnimation(fig, update, frames=len(cutting_phases), interval=100, repeat=False)
        self.canvas.draw()

# Run the app
root = tk.Tk()
app = LensCuttingApp(root)
root.mainloop()
