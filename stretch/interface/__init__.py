import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from importlib import resources
from .. import interface
runtime = resources.files(interface) / "runtime"

def clear():
    with runtime.open('w') as run_file:
        pass


def read_output():
    with runtime.open('r') as run_file:
        return run_file.read()

def output(*args, end="\n", join=", "):
    with runtime.open('r') as run_file:
        prev = run_file.read()
    
    with runtime.open('w') as run_file:
        run_file.write(prev + join.join(args) + end)
    
output("hello")
    


from itertools import chain
def get_events(widget):
    return set(chain.from_iterable(widget.bind_class(cls) for cls in widget.bindtags()))

class StatusBar(tk.Frame):
    def __init__(self, master, title="Status:", defaultText="", backgroundColor="#F4F4F4", borderColor=None):
        tk.Frame.__init__(self, master, background=backgroundColor, highlightbackground=(borderColor or backgroundColor), highlightthickness=1)
        
        
        # title label
        self.title = tk.Label(self, fg="black")
        self.title.pack(side=tk.LEFT)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.set_title(title)
        
        # label
        self.label = tk.Label(self, fg="black")
        self.label.pack(side=tk.LEFT)
        self.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.default = defaultText
        self.set_text(self.default)
    
    def set_title(self, newText):
        self.title.config(text=newText)
    
    def set_text(self, newText):
        self.label.config(text=newText)
 
    def clear_text(self):
        self.label.config(text=self.default)

class InputDialogue(tk.Toplevel):
    def __init__(self, master, interface):
        tk.Toplevel.__init__(self, master)
        self.window = master
        self.interface = interface
        self.title("Input")
        self.geometry("300x55")
        
        self.prompt = tk.Label(self)
        self.prompt.pack(pady=2)
        self.input = ttk.Entry(self)
        self.input.pack(side="bottom", fill="x", padx=5, pady=2.5)

        self.bind("<Key>", self.handle)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.withdraw()
        
    def handle(self, event):
        # 13
        if event.keycode == 13:
            self.close()
            
    
    def close(self):
        if self in self.interface.modal_windows:
            self.interface.modal_windows.remove(self)

        self.withdraw()
        self.grab_release()
        self.window.focus_force()
        
        
    def __call__(self, prompt=""):
        self.input.delete(-1, tk.END)
        self.prompt.config(text=prompt)
        self.interface.modal_windows.add(self)
        self.deiconify()
        self.grab_set()
        return self
    def __promise__(self):
        return self.input.get()


class Interface:
    def __init__(self, driver):
        self.driver = driver
        self.modal_windows = set()
        
        # setup window
        self.window = tk.Tk()
        self.window.title("Stretch Interpreter v0.0.1")
        self.window.protocol("WM_DELETE_WINDOW", lambda : self.driver.terminate())
        self.resize(400, 500)
        
        self.get_input = InputDialogue(self.window, self)
        
        
                
        # status bar
        self.status_bar = StatusBar(self.window, defaultText="running", borderColor="#292929")
        self.status_bar.set_text("starting")
        
        self.output = scrolledtext.ScrolledText(self.window)
        self.output.pack(padx=20, pady=20, fill=tk.Y)
        self.output.configure(state="disabled")
        
        self.hide()
        
    def resize(self, width=None, height=None):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = width or screen_width
        height = height or screen_height
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self):
        self.window.deiconify()
    def hide(self):
        self.window.withdraw()
        
    def update(self):
        self.window.update_idletasks()
        self.window.update()
        if len(self.modal_windows) > 0:
            return False
        return True






