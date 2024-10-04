'''
This script is a simple UI for converting G-code files to Spider G-code files. 
and it is intended to use with only SPIDER V2.0
fire310w 11/6/2024
'''
import tkinter as tk
from tkinter import filedialog
import os
import re

def process_gcode():

    input_file = input_entry.get()
    if not input_file:
        result_label.config(text="Please select a file")
        return

    # If file is .nc, convert extension to .gcode
    if input_file.lower().endswith('.nc'):
        gcode_file_name, _ = os.path.splitext(input_file)
        input_file = f'{gcode_file_name}.gcode'

    gcode_file_name, gcode_file_extention = os.path.splitext(input_file)
    new_file_name = f'{gcode_file_name}_Spider{gcode_file_extention}'

    try:
        with open(input_file, 'r') as gcode_file, open(new_file_name, 'w') as gcode_file_new:
            last_command = ''
            last_G_command = ''

            for line in gcode_file:
                gcode = line.strip()
                # for F, S, M5, M05 add with last G command (Feedrate, Spindle Speed, Spindle Stop, Spindle Start)
                if gcode.startswith(('F', 'S', 'M5', 'M05')):
                    if gcode.startswith('M'):
                        gcode = 'S0'
                    last_command += ' ' + gcode
                    continue
                # for Empty X,Y,Z add with last G command
                elif gcode.startswith(('X', 'Y', 'Z')):
                    if last_G_command:
                        gcode = f'{last_G_command.strip()} {gcode}'
                # use Inline Mode
                elif gcode.startswith(('M3', 'M4', 'M5')) and 'I' not in gcode:
                    gcode += ' I'
                # for G0, G1, G2, G3 add with last command for only first one
                elif gcode.startswith(('G0', 'G1', 'G2', 'G3', 'G01', 'G02', 'G03')):
                    if last_command:
                        gcode = f'{gcode} {last_command.strip()}'
                        last_command = ''
                    # Parse G command
                    matchG1 = re.match(r"(G\d+)", gcode)
                    if matchG1:
                        last_G_command = matchG1.group(1)
                # Write the line to the new file
                gcode_file_new.write(gcode + '\n')
            # Add a final move to the origin and turn off the spindle
            gcode_file_new.write('G1 X0 Y0 F800 S0\nM5 I\n')

        result_label.config(text=f'New file created: {new_file_name}')
    except Exception as e:
        result_label.config(text=f'Error: {e}')


def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("G-code files", "*.gcode"), ("LaserGRBL files", "*.nc")])
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)


# Create the main window
root = tk.Tk()
root.title("G-code Processor for Spider V2.0")
root.geometry("500x100")
root.resizable(False, False)

# Create the file selection UI elements
input_label = tk.Label(root, text="Select G-code file:")
input_label.grid(row=0, column=0, padx=5, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Create the process button
process_button = tk.Button(root, text="Process G-code", command=process_gcode)
process_button.grid(row=1, column=1, padx=5, pady=5)

# Create a label for displaying the result
result_label = tk.Label(root, text="")
result_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

# Run the main event loop
root.mainloop()
