import tkinter as tk
from ui.truss_app import TrussApp

if __name__ == "__main__":
    root = tk.Tk()
    app = TrussApp(root)
    root.mainloop()