import re
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk


class SSHGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jigwe Transition Getter")
        self.root.geometry('700x500')

        # mainframe
        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, columnspan=2)

        # ssh config message
        ssh_info_frame = ttk.LabelFrame(mainframe, text="SSH Info")
        self.ssh_config_message = tk.StringVar(value="Your SSH config is/is NOT setup!")
        ttk.Label(ssh_info_frame, textvariable=self.ssh_config_message).grid(row=0, column=0, columnspan=10)

        ssh_info_frame.grid(row=0, column=0, columnspan=10)

        # point array entries
        data_input_frame = ttk.LabelFrame(mainframe, text="Point Array Input")
        ttk.Label(data_input_frame, text="Enter point arrays in comma separated format.\n(i.e. \"x,y,z,...\")").grid(row=9,column=0, columnspan=2)

        validate_pt_array_string_wrapper = self.root.register(self.validate_pt_array_string)
        self.starting_pt_array = tk.StringVar()
        ttk.Entry(data_input_frame, textvariable=self.starting_pt_array, validate='key', validatecommand=(validate_pt_array_string_wrapper, '%P')).grid(row=10, column=0)
        ttk.Label(data_input_frame, text="Enter starting point array").grid(row=10, column=1)

        self.ending_pt_array = tk.StringVar()
        ttk.Entry(data_input_frame, textvariable=self.ending_pt_array, validate='key', validatecommand=(validate_pt_array_string_wrapper, '%P')).grid(row=20, column=0)
        ttk.Label(data_input_frame, text="Enter ending point array").grid(row=20, column=1)

        # getting transitions!
        ttk.Button(data_input_frame, text="Get Transitions!", command=self.get_transitions_on_click).grid(row=30, column=0, columnspan=2)

        self.display_text = tk.StringVar(value="Not printed")
        self.display_label = tk.Label(data_input_frame, textvariable=self.display_text)
        self.display_label.grid(row=40, column=0, columnspan=2)

        data_input_frame.grid(row=20, column=0, columnspan=10)

        # transition frame
        transition_frame = ttk.LabelFrame(mainframe, text="Transitions:", borderwidth="20", relief="sunken", padding="5")
        transition_frame.grid(row=60, column=0)

        transition_status = tk.StringVar(value="No data yet.")
        transition_status_label = ttk.Label(transition_frame, textvariable=transition_status)
        transition_status_label.grid(row=1, column=0)

        # place the frames
        mainframe.place(relx=0.5, rely=0.5, anchor="center")

        # run main loop
        self.root.mainloop()

    def get_transitions_on_click(self):
        """
        Update display and process when the "Get Transitions" button is clicked.
        :return:
        """
        if self.starting_pt_array.get() == "" or self.ending_pt_array.get() == "":
            self.display_label.configure(foreground='red')
            self.display_text.set("Please set value for both point arrays.")
            return

        starting_pt_array = self.pt_array_str_to_tuple(self.starting_pt_array.get())
        ending_pt_array = self.pt_array_str_to_tuple(self.ending_pt_array.get())

        self.display_label.configure(foreground='green')
        self.display_text.set(f"{starting_pt_array} --> {ending_pt_array}\nTODO GET TRANSITIONS")

    def validate_pt_array_string(self, pt_array_string):
        """
        Validates whether the param is a point array string.
        :param pt_array_string:
        :return:
        """
        pt_array_regex = "[1-9]+(?:,[1-9]+)*,?"

        return re.fullmatch(pt_array_regex, pt_array_string) is not None or pt_array_string == ""

    def pt_array_str_to_tuple(self, string):
        return tuple(map(int, string.split(",")))


if __name__ == "__main__":
    SSHGui()
