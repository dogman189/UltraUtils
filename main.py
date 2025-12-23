import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
import random
import string
import base64
import sys

# --- Optional Imports ---
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark")

# --- Helper Function for Clipboard ---
def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # Keeps clipboard content after window closes

# --- Utility Windows ---

class StickyNotes(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Sticky Notes")
        self.geometry("300x320")
        
        # Toolbar
        self.toolbar = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=5, pady=2)
        
        self.lbl = ctk.CTkLabel(self.toolbar, text="📝 Auto-saves on close", font=("Arial", 10))
        self.lbl.pack(side="left", padx=5)

        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 14), wrap="word")
        self.textbox.pack(pady=5, padx=10, fill="both", expand=True)
        
        try:
            with open("sticky_notes.txt", "r") as f:
                self.textbox.insert("0.0", f.read())
        except FileNotFoundError:
            pass

        self.protocol("WM_DELETE_WINDOW", self.save_and_close)

    def save_and_close(self):
        try:
            with open("sticky_notes.txt", "w") as f:
                f.write(self.textbox.get("0.0", "end-1c"))
        except Exception as e:
            print(f"Save error: {e}")
        self.destroy()

class PomodoroTimer(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Focus Timer")
        self.geometry("300x220")
        
        self.time_left = 25 * 60
        self.running = False
        
        self.timer_lbl = ctk.CTkLabel(self, text="25:00", font=("Impact", 60))
        self.timer_lbl.pack(pady=(30, 20))
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack()
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start", command=self.start_timer, width=80)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        self.reset_btn = ctk.CTkButton(self.btn_frame, text="Reset", command=self.reset_timer, width=80, fg_color="#C0392B", hover_color="#A93226")
        self.reset_btn.grid(row=0, column=1, padx=10)

    def update_clock(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.timer_lbl.configure(text=f"{mins:02}:{secs:02}")
            self.after(1000, self.update_clock)
        elif self.time_left == 0:
            self.running = False
            self.timer_lbl.configure(text="DONE!", text_color="#2ECC71")

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_clock()

    def reset_timer(self):
        self.running = False
        self.time_left = 25 * 60
        self.timer_lbl.configure(text="25:00", text_color=("black", "white"))

class SystemMonitor(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Stats")
        self.geometry("280x180")
        
        if not PSUTIL_AVAILABLE:
            ctk.CTkLabel(self, text="⚠ Install 'psutil' library").pack(pady=50)
            return

        self.cpu_prog = ctk.CTkProgressBar(self, width=200)
        self.cpu_prog.pack(pady=(20, 5))
        self.cpu_lbl = ctk.CTkLabel(self, text="CPU: 0%")
        self.cpu_lbl.pack(pady=(0, 15))
        
        self.ram_prog = ctk.CTkProgressBar(self, width=200, progress_color="#E67E22")
        self.ram_prog.pack(pady=(10, 5))
        self.ram_lbl = ctk.CTkLabel(self, text="RAM: 0%")
        self.ram_lbl.pack()
        
        self.update_stats()

    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self.cpu_prog.set(cpu / 100)
            self.cpu_lbl.configure(text=f"CPU: {cpu}%")
            
            self.ram_prog.set(ram / 100)
            self.ram_lbl.configure(text=f"RAM: {ram}%")
            
            self.after(1500, self.update_stats)
        except Exception:
            pass

class PasswordGenerator(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Pass Gen")
        self.geometry("350x250")
        
        self.grid_columnconfigure(0, weight=1)
        
        self.slider_val = ctk.IntVar(value=12)
        
        self.lbl = ctk.CTkLabel(self, text="Length: 12", font=("Arial", 14))
        self.lbl.pack(pady=(20, 5))
        
        self.slider = ctk.CTkSlider(self, from_=6, to=30, number_of_steps=24, variable=self.slider_val, command=self.update_label)
        self.slider.pack(pady=5)
        
        # Result area with copy button
        self.res_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.res_frame.pack(pady=20)
        
        self.result_entry = ctk.CTkEntry(self.res_frame, width=200, font=("Consolas", 14))
        self.result_entry.grid(row=0, column=0, padx=5)
        
        self.copy_btn = ctk.CTkButton(self.res_frame, text="📋", width=40, command=self.copy_pass)
        self.copy_btn.grid(row=0, column=1, padx=5)
        
        self.gen_btn = ctk.CTkButton(self, text="Generate Password", command=self.generate)
        self.gen_btn.pack(pady=10)

    def update_label(self, value):
        self.lbl.configure(text=f"Length: {int(value)}")

    def generate(self):
        length = int(self.slider.get())
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = ''.join(random.choice(chars) for _ in range(length))
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, pwd)

    def copy_pass(self):
        pwd = self.result_entry.get()
        if pwd:
            copy_to_clipboard(self, pwd)
            self.gen_btn.configure(text="Copied!", fg_color="#27AE60")
            self.after(1500, lambda: self.gen_btn.configure(text="Generate Password", fg_color=["#3B8ED0", "#1F6AA5"]))

class Base64Converter(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Base64 Tool")
        self.geometry("400x350")
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_enc = self.tabview.add("Encode")
        self.tab_dec = self.tabview.add("Decode")
        
        self.setup_tab(self.tab_enc, "encode")
        self.setup_tab(self.tab_dec, "decode")

    def setup_tab(self, tab, mode):
        txt_in = ctk.CTkTextbox(tab, height=80)
        txt_in.pack(fill="x", pady=5)
        txt_in.insert("0.0", "Input text here...")
        
        btn = ctk.CTkButton(tab, text=f"{mode.title()}", 
                            command=lambda: self.process(mode, txt_in, txt_out))
        btn.pack(pady=5)
        
        txt_out = ctk.CTkTextbox(tab, height=80)
        txt_out.pack(fill="x", pady=5)
        
        # Copy Button
        copy_btn = ctk.CTkButton(tab, text="Copy Output", 
                                 command=lambda: copy_to_clipboard(self, txt_out.get("0.0", "end-1c")))
        copy_btn.pack(pady=5)

    def process(self, mode, t_in, t_out):
        data = t_in.get("0.0", "end-1c")
        try:
            if mode == "encode":
                res = base64.b64encode(data.encode()).decode()
            else:
                res = base64.b64decode(data).decode()
        except Exception:
            res = "Error: Invalid Input"
            
        t_out.delete("0.0", "end")
        t_out.insert("0.0", res)

class UnitConverter(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self.geometry("300x200")
        self.val = ctk.StringVar()
        
        ctk.CTkLabel(self, text="Kilometers to Miles").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.val).pack(pady=10)
        ctk.CTkButton(self, text="Convert", command=self.calc).pack(pady=10)
        self.res = ctk.CTkLabel(self, text="-- Miles", font=("Arial", 16, "bold"))
        self.res.pack(pady=10)

    def calc(self):
        try:
            v = float(self.val.get())
            self.res.configure(text=f"{v * 0.621371:.2f} Miles")
        except ValueError:
            self.res.configure(text="Invalid")

# --- Color Picker Logic (No Class needed) ---
def launch_color_picker(parent_app):
    color = colorchooser.askcolor(title="Pick a Color")
    if color[1]:
        copy_to_clipboard(parent_app, color[1])
        # Show a small toast notification on the main app
        original_title = parent_app.title()
        parent_app.title(f"Copied {color[1]} to Clipboard!")
        parent_app.after(3000, lambda: parent_app.title(original_title))

# --- Main Dashboard ---

class ToolCard(ctk.CTkFrame):
    """ Custom widget that looks like a card """
    def __init__(self, parent, title, icon, command, color=None):
        super().__init__(parent, corner_radius=15, fg_color=color)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Icon
        self.icon_lbl = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 40))
        self.icon_lbl.grid(row=0, column=0, pady=(15, 0))
        
        # Title
        self.title_lbl = ctk.CTkLabel(self, text=title, font=("Arial", 14, "bold"))
        self.title_lbl.grid(row=1, column=0, pady=(5, 15))
        
        # Button (stretched to fill bottom)
        self.btn = ctk.CTkButton(self, text="Open", command=command, height=35, corner_radius=10)
        self.btn.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")

class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("UltraUtils")
        self.geometry("700x670")
        self.resizable(False, False)
        
        # Header
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=10)
        
        self.title_lbl = ctk.CTkLabel(self.header, text="🛠️UltraUtils", font=("Roboto", 26, "bold"))
        self.title_lbl.pack(side="left")

        # Grid Container
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configure Grid Layout (3 columns)
        self.grid_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Tool Definitions
        tools = [
            ("Sticky Notes", "📝", StickyNotes),
            ("Pomodoro", "⏱️", PomodoroTimer),
            ("Monitor", "📊", SystemMonitor),
            ("Converter", "⚖️", UnitConverter),
            ("Passwords", "🔑", PasswordGenerator),
            ("Base64", "🔌", Base64Converter),
        ]

        # Generate Cards
        for i, (name, icon, cls) in enumerate(tools):
            row = i // 3
            col = i % 3
            card = ToolCard(self.grid_frame, name, icon, lambda c=cls: self.open_tool(c))
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Color Picker is special (System Dialog)
        # We put it in a prominent row or appended
        picker_card = ToolCard(self.grid_frame, "Color Picker", "🎨", lambda: launch_color_picker(self), color="#4A235A")
        picker_card.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        picker_card.btn.configure(fg_color="#8E44AD", hover_color="#9B59B6")

    def open_tool(self, tool_class):
        # Open the window
        tool_class()

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()