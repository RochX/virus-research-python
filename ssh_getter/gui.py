import tkinter as tk
from tkinter import ttk


class SSHGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jigwe Transition Getter")
        self.root.geometry('350x200')

        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)

        self.username = tk.StringVar()
        name = ttk.Entry(mainframe, textvariable=self.username)
        name.grid(column=0, row=0)

        button = ttk.Button(mainframe, text="Print Username", command=self.update_display)
        button.grid(column=1, row=0)

        self.display = tk.StringVar(value="Not printed")
        label = tk.Label(mainframe, textvariable=self.display)
        label.grid(column=0, row=1, columnspan=2)

        self.root.mainloop()

    def update_display(self):
        self.display.set(self.username.get())


if __name__ == "__main__":
    SSHGui()
