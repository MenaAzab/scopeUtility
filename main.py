import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

import scope

class OscilloscopeSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scope Screenshoot Tool")

        self.create_ip_address_input()
        self.create_channel_selection()
        self.create_control_buttons()
        self.create_status_label()

        self.ssdir = ""

    def create_ip_address_input(self):
        ip_frame = self.create_section_frame("Oscilloscope IP Address", 0, 0, 2)

        label = tk.Label(ip_frame, text="IP Address")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.ip_entry = tk.Entry(ip_frame)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
    
    def create_channel_selection(self):
        channel_frame = self.create_section_frame("Channel Selection", 1, 0, 2)

        self.channel_labels = {}

        label1 = tk.Label(channel_frame, text="Channel 1")
        label1.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.channel_labels["Channel 1"] = tk.Entry(channel_frame, width=30)
        self.channel_labels["Channel 1"].grid(row=0, column=1, padx=5, pady=5)

        label2 = tk.Label(channel_frame, text="Channel 2")
        label2.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.channel_labels["Channel 2"] = tk.Entry(channel_frame, width=30)
        self.channel_labels["Channel 2"].grid(row=1, column=1, padx=5, pady=5)

        label3 = tk.Label(channel_frame, text="Channel 3")
        label3.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.channel_labels["Channel 3"] = tk.Entry(channel_frame, width=30)
        self.channel_labels["Channel 3"].grid(row=2, column=1, padx=5, pady=5)

        label4 = tk.Label(channel_frame, text="Channel 4")
        label4.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.channel_labels["Channel 4"] = tk.Entry(channel_frame, width=30)
        self.channel_labels["Channel 4"].grid(row=3, column=1, padx=5, pady=5)

    def create_control_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.clear_labels = tk.Button(button_frame, text="Clear Labels", command=self.clear_labels, state='normal')
        self.clear_labels.pack(side=tk.LEFT, padx=5)

        self.screenshot_button = tk.Button(button_frame, text="Get Screenshot", command=self.get_screenshot, state='normal')
        self.screenshot_button.pack(side=tk.LEFT, padx=5)

        self.set_labels = tk.Button(button_frame, text="Set Labels", command=self.set_labels, state='normal')
        self.set_labels.pack(side=tk.LEFT, padx=5)

    def create_status_label(self):
        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=5, column=0, columnspan=2)

    def create_section_frame(self, title, row, col, colspan=1):
        frame = tk.LabelFrame(self.root, text=title, padx=5, pady=5)
        frame.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        return frame

    def connect_and_sync(self):
        ip_address = 'TCPIP::' + self.ip_entry.get() + '::INSTR'
        try:
            self.instr = scope.Oscilloscope(ip_address)  # Create instance based on manufacturer
        except Exception as e:
            self.status_label.config(text=f"Connection error: {e}")
            self.instr = None  
        except ValueError as e:
            self.status_label.config(text=f"Error: {e}")
            self.instr = None

    def set_labels(self):
        self.connect_and_sync()
        if self.instr:  
            try: 
                self.instr.set_labels(self.channel_labels["Channel 1"].get(),self.channel_labels["Channel 2"].get(),
                self.channel_labels["Channel 3"].get(), self.channel_labels["Channel 4"].get())
                self.instr.close()
                self.status_label.config(text="Labels set successfully!")
            except Exception as e:
                self.status_label.config(text=f"Error setting labels: {e}")
        else:
            self.status_label.config(text="Not connected to an oscilloscope!")
    
    def clear_labels(self):
        self.connect_and_sync()
        if self.instr:  
            try: 
                self.instr.set_labels("","","","")
                self.status_label.config(text="Labels cleared successfully!")
                self.instr.close()
            except Exception as e:
                self.status_label.config(text=f"Error clearing labels: {e}")
        else:
            self.status_label.config(text="Not connected to an oscilloscope!")
        
    def get_screenshot(self):
        # Open a file dialog to select the save location and filename

        self.connect_and_sync()

        if self.instr.manufacturer == "KEYSIGHT TECHNOLOGIES":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".bmp",
                filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")],
                title="Save Screenshot"
            )
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Screenshot"
            )

        if self.instr:
            if file_path:
                try:
                    # Call the take_screenshot method
                    self.instr.take_screenshot(file_path)
                    self.status_label.config(text="Screenshot saved!")
                    self.instr.close()
                except Exception as e:
                    self.status_label.config(text=f"Error clearing labels: {e}")
            else:
                self.status_label.config(text="Not connected to an oscilloscope!")
 

if __name__ == "__main__":
    root = tk.Tk()
    app = OscilloscopeSettingsApp(root)
    root.mainloop()