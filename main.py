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

# --- Visual Constants (The "Wireframe" Look) ---
COLOR_BG = "#000000"        # True Black
COLOR_TEXT = "#FFFFFF"      # Stark White
COLOR_BORDER = "#FFFFFF"    # White Borders (High Contrast)
COLOR_DIM = "#333333"       # Dim Grey for empty bars/borders
FONT_HEADER = ("Helvetica", 24, "bold")
FONT_BODY = ("Consolas", 12) # Monospaced for a technical look

ctk.set_appearance_mode("Dark")

# --- Custom UI Elements for the Aesthetic ---

class WireframeButton(ctk.CTkButton):
    """ A custom button that inverts colors on hover """
    def __init__(self, master, **kwargs):
        super().__init__(master, 
                         fg_color="transparent", 
                         border_color=COLOR_TEXT, 
                         border_width=1, 
                         text_color=COLOR_TEXT, 
                         corner_radius=0, 
                         hover_color=COLOR_TEXT, # Background becomes white on hover
                         **kwargs)
        
        # Bind events to invert text color on hover
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(text_color=COLOR_BG) # Text becomes black

    def on_leave(self, event):
        self.configure(text_color=COLOR_TEXT) # Text becomes white

class BaseWindow(ctk.CTkToplevel):
    """ Parent window to enforce the Black Theme on all tools """
    def __init__(self, title, width=400, height=300):
        super().__init__()
        self.title(title.upper())
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=COLOR_BG)
        self.after(10, self.lift) # Bring to front

# --- Helper Logic ---
def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

# --- The Utilities (Original Logic Restored) ---

class StickyNotes(BaseWindow):
    def __init__(self):
        super().__init__("Sticky Notes", 350, 350)
        
        # Toolbar (Styled Black)
        self.toolbar = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=10, pady=5)
        
        self.lbl = ctk.CTkLabel(self.toolbar, text="[ AUTO-SAVE ENABLED ]", font=("Arial", 10, "bold"), text_color=COLOR_TEXT)
        self.lbl.pack(side="left")

        # Text Area (Sharp corners, dark grey bg)
        self.textbox = ctk.CTkTextbox(self, font=FONT_BODY, wrap="word",
                                      fg_color="#111111", text_color=COLOR_TEXT,
                                      border_color=COLOR_DIM, border_width=1, corner_radius=0)
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
        except: pass
        self.destroy()

class PomodoroTimer(BaseWindow):
    def __init__(self):
        super().__init__("Focus Timer", 350, 250)
        self.time_left = 25 * 60
        self.running = False
        
        self.timer_lbl = ctk.CTkLabel(self, text="25:00", font=("Helvetica", 60, "bold"), text_color=COLOR_TEXT)
        self.timer_lbl.pack(pady=(40, 30))
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack()
        
        self.start_btn = WireframeButton(self.btn_frame, text="START", command=self.start_timer, width=100)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        self.reset_btn = WireframeButton(self.btn_frame, text="RESET", command=self.reset_timer, width=100)
        self.reset_btn.grid(row=0, column=1, padx=10)

    def update_clock(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.timer_lbl.configure(text=f"{mins:02}:{secs:02}")
            self.after(1000, self.update_clock)
        elif self.time_left == 0:
            self.running = False
            self.timer_lbl.configure(text="DONE")

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_clock()

    def reset_timer(self):
        self.running = False
        self.time_left = 25 * 60
        self.timer_lbl.configure(text="25:00")

class SystemMonitor(BaseWindow):
    def __init__(self):
        super().__init__("System Monitor", 300, 200)
        
        if not PSUTIL_AVAILABLE:
            ctk.CTkLabel(self, text="ERROR: psutil not installed").pack(pady=50)
            return

        # CPU Section
        self.cpu_lbl = ctk.CTkLabel(self, text="CPU LOAD", font=("Arial", 10, "bold"))
        self.cpu_lbl.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.cpu_prog = ctk.CTkProgressBar(self, width=260, height=10, corner_radius=0, 
                                           progress_color=COLOR_TEXT, fg_color=COLOR_DIM)
        self.cpu_prog.pack(pady=0)
        
        # RAM Section
        self.ram_lbl = ctk.CTkLabel(self, text="RAM USAGE", font=("Arial", 10, "bold"))
        self.ram_lbl.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.ram_prog = ctk.CTkProgressBar(self, width=260, height=10, corner_radius=0, 
                                           progress_color=COLOR_TEXT, fg_color=COLOR_DIM)
        self.ram_prog.pack(pady=0)
        
        self.val_lbl = ctk.CTkLabel(self, text="Initializing...", font=FONT_BODY)
        self.val_lbl.pack(pady=20)

        self.update_stats()

    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self.cpu_prog.set(cpu / 100)
            self.ram_prog.set(ram / 100)
            self.val_lbl.configure(text=f"CPU: {cpu}%  |  RAM: {ram}%")
            
            self.after(1500, self.update_stats)
        except: pass

class PasswordGenerator(BaseWindow):
    def __init__(self):
        super().__init__("Password Gen", 400, 300)
        
        self.slider_val = ctk.IntVar(value=12)
        
        self.lbl = ctk.CTkLabel(self, text="LENGTH: 12", font=("Helvetica", 14, "bold"))
        self.lbl.pack(pady=(30, 10))
        
        # White slider with sharp edges
        self.slider = ctk.CTkSlider(self, from_=6, to=30, number_of_steps=24, 
                                    variable=self.slider_val, command=self.update_label,
                                    button_color=COLOR_TEXT, progress_color=COLOR_TEXT, fg_color=COLOR_DIM,
                                    button_corner_radius=0, corner_radius=0)
        self.slider.pack(pady=10, fill="x", padx=40)
        
        # Result Area
        self.res_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.res_frame.pack(pady=20)
        
        self.result_entry = ctk.CTkEntry(self.res_frame, width=200, font=FONT_BODY, 
                                         fg_color=COLOR_BG, border_color=COLOR_BORDER, corner_radius=0)
        self.result_entry.grid(row=0, column=0, padx=5)
        
        self.copy_btn = WireframeButton(self.res_frame, text="COPY", width=60, command=self.copy_pass)
        self.copy_btn.grid(row=0, column=1, padx=5)
        
        self.gen_btn = WireframeButton(self, text="GENERATE NEW", command=self.generate, width=200)
        self.gen_btn.pack(pady=10)

    def update_label(self, value):
        self.lbl.configure(text=f"LENGTH: {int(value)}")

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
            self.copy_btn.configure(text="OK")
            self.after(1500, lambda: self.copy_btn.configure(text="COPY"))

class Base64Converter(BaseWindow):
    def __init__(self):
        super().__init__("Base64 Tool", 450, 400)
        
        # Custom Tabview Styling for Monochrome
        self.tabview = ctk.CTkTabview(self, fg_color=COLOR_BG, 
                                      segmented_button_fg_color=COLOR_BG,
                                      segmented_button_selected_color=COLOR_TEXT,
                                      segmented_button_selected_hover_color=COLOR_TEXT,
                                      segmented_button_unselected_color=COLOR_BG,
                                      segmented_button_unselected_hover_color=COLOR_DIM,
                                      text_color=COLOR_TEXT) 
        
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_enc = self.tabview.add("ENCODE")
        self.tab_dec = self.tabview.add("DECODE")
        
        self.setup_tab(self.tab_enc, "encode")
        self.setup_tab(self.tab_dec, "decode")

    def setup_tab(self, tab, mode):
        # Input
        ctk.CTkLabel(tab, text="INPUT", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        txt_in = ctk.CTkTextbox(tab, height=80, fg_color="#111111", text_color=COLOR_TEXT, border_color=COLOR_DIM, border_width=1, corner_radius=0)
        txt_in.pack(fill="x", pady=(0, 10))
        
        # Action
        btn = WireframeButton(tab, text=f"EXECUTE {mode.upper()}", 
                            command=lambda: self.process(mode, txt_in, txt_out))
        btn.pack(pady=5)
        
        # Output
        ctk.CTkLabel(tab, text="OUTPUT", font=("Arial", 10, "bold"), anchor="w").pack(fill="x", pady=(10,0))
        txt_out = ctk.CTkTextbox(tab, height=80, fg_color="#111111", text_color=COLOR_TEXT, border_color=COLOR_DIM, border_width=1, corner_radius=0)
        txt_out.pack(fill="x")
        
        # Copy
        copy_btn = WireframeButton(tab, text="COPY OUTPUT", 
                                 command=lambda: copy_to_clipboard(self, txt_out.get("0.0", "end-1c")))
        copy_btn.pack(pady=10)

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

class UnitConverter(BaseWindow):
    def __init__(self):
        super().__init__("Unit Converter", 300, 250)
        self.val = ctk.StringVar()
        
        ctk.CTkLabel(self, text="KILOMETERS ➔ MILES", font=("Helvetica", 12, "bold")).pack(pady=30)
        
        entry = ctk.CTkEntry(self, textvariable=self.val, font=FONT_BODY, justify="center",
                             fg_color=COLOR_BG, border_color=COLOR_BORDER, corner_radius=0)
        entry.pack(pady=10)
        
        WireframeButton(self, text="CONVERT", command=self.calc).pack(pady=10)
        
        self.res = ctk.CTkLabel(self, text="-- MILES", font=("Helvetica", 16, "bold"))
        self.res.pack(pady=20)

    def calc(self):
        try:
            v = float(self.val.get())
            self.res.configure(text=f"{v * 0.621371:.2f} MILES")
        except ValueError:
            self.res.configure(text="INVALID INPUT")

# --- Launcher Dashboard ---

class Card(ctk.CTkFrame):
    def __init__(self, parent, title, subtitle, icon, command):
        super().__init__(parent, fg_color="transparent", border_color=COLOR_DIM, border_width=1, corner_radius=0)
        
        self.command = command
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 
        
        # Header
        self.lbl_title = ctk.CTkLabel(self, text=title.upper(), font=("Helvetica", 14, "bold"), text_color=COLOR_TEXT, anchor="w")
        self.lbl_title.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,0))
        
        self.lbl_sub = ctk.CTkLabel(self, text=subtitle, font=("Arial", 9), text_color="grey", anchor="w")
        self.lbl_sub.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 5))

        # Icon (Using Emoji for simplicity, but large)
        self.icon = ctk.CTkLabel(self, text=icon, font=("Arial", 30))
        self.icon.grid(row=2, column=0, pady=10)
        
        # Button
        self.btn = ctk.CTkButton(self, text="OPEN ↗", command=command, width=0, height=30,
                                 fg_color="transparent", text_color=COLOR_TEXT, hover_color="#222222",
                                 font=("Arial", 11), corner_radius=0, border_width=0, anchor="e")
        self.btn.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        # Interaction (Hovering the card creates a 'focus' effect)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.icon.bind("<Enter>", self.on_hover) # Bind children too
        self.lbl_title.bind("<Enter>", self.on_hover)

    def on_hover(self, e):
        self.configure(border_color=COLOR_TEXT) 
        
    def on_leave(self, e):
        self.configure(border_color=COLOR_DIM)

class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ultrautils v0.5")
        self.geometry("850x600")
        self.configure(fg_color=COLOR_BG)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color="transparent", width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        
        ctk.CTkLabel(self.sidebar, text="ULTRAUTILS", 
                     font=("Helvetica", 32, "bold"), text_color=COLOR_TEXT, justify="left", anchor="w").pack(anchor="w")
                     
        ctk.CTkLabel(self.sidebar, text="PYTHON UTILITY HUB", 
                     font=("Arial", 10), text_color="grey", anchor="w").pack(anchor="w", pady=(10, 0))

        # Color Picker Button (Bottom of Sidebar)
        btn_color = WireframeButton(self.sidebar, text="COLOR PICKER", command=self.open_color)
        btn_color.pack(side="bottom", fill="x")

        # Grid Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=30)
        self.content.grid_columnconfigure((0,1,2), weight=1)

        # Tools Config
        tools = [
            ("Sticky Notes", "AUTO-SAVING", "📝", StickyNotes),
            ("Pomodoro", "FOCUS TIMER", "⏱️", PomodoroTimer),
            ("System", "CPU & RAM", "📊", SystemMonitor),
            ("Converter", "KM TO MILES", "⚖️", UnitConverter),
            ("Passwords", "GENERATOR", "🔑", PasswordGenerator),
            ("Base64", "ENC/DEC TOOLS", "🔌", Base64Converter),
        ]

        for i, (name, sub, icon, cls) in enumerate(tools):
            r = i // 3
            c = i % 3
            card = Card(self.content, name, sub, icon, lambda c=cls: self.open_tool(c))
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)

    def open_tool(self, tool_cls):
        tool_cls()

    def open_color(self):
        c = colorchooser.askcolor(title="COLOR")
        if c[1]: copy_to_clipboard(self, c[1])

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()