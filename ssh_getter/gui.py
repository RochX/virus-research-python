import re
import ssh_getter
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk


class SSHGui:
    hostname = "jigwe.kzoo.edu"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jigwe Transition Getter")
        self.root.geometry('1500x500')

        # mainframe
        mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, columnspan=2)

        # ssh config message
        ssh_info_frame = ttk.LabelFrame(mainframe, text="SSH Info")
        self.ssh_config_is_setup = False
        self.ssh_info_label = ttk.Label(ssh_info_frame, text="RUN UPDATE SSH LABEL")
        self.ssh_info_label.grid(row=0, column=0)
        self.update_ssh_info_display()
        ttk.Button(ssh_info_frame, text="Refresh Status", command=self.update_ssh_info_display).grid(row=0, column=1)

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

        self.centralizer_string = tk.StringVar()
        centralizer_selector = ttk.Combobox(data_input_frame,
                                            textvariable=self.centralizer_string,
                                            values=['A4', 'D10', 'D6'],
                                            state='readonly')
        centralizer_selector.grid(row=25, column=0)
        centralizer_selector.bind('<<ComboboxSelected>>', lambda event: centralizer_selector.selection_clear())
        ttk.Label(data_input_frame, text="Select Symmetry").grid(row=25, column=1)

        # getting transitions!
        ttk.Button(data_input_frame, text="Get Transitions!", command=self.get_transitions_on_click).grid(row=30, column=0, columnspan=2)

        self.display_text = tk.StringVar(value="Not printed")
        self.display_label = tk.Label(data_input_frame, textvariable=self.display_text)
        self.display_label.grid(row=40, column=0, columnspan=2)

        data_input_frame.grid(row=20, column=0, columnspan=10)

        # transition frame
        transition_frame = ttk.LabelFrame(mainframe, text="Transitions:", borderwidth="20", relief="sunken", padding="5")
        transition_frame.grid(row=60, column=0)

        self.transition_status = tk.StringVar(value="No data yet.")
        transition_status_label = ttk.Label(transition_frame, textvariable=self.transition_status)
        transition_status_label.grid(row=0, column=0, columnspan=10)

        # labels for transition frame
        ttk.Label(transition_frame, text="T: ").grid(row=1, column=0)
        ttk.Label(transition_frame, text="B0:").grid(row=2, column=0)
        ttk.Label(transition_frame, text="B1:").grid(row=3, column=0)

        self.transition_matrix_string = tk.StringVar(value="T will be here")
        self.b0_matrix_string = tk.StringVar(value="B0 will be here")
        self.b1_matrix_string = tk.StringVar(value="B1 will be here")

        transition_matrix_display = ttk.Label(transition_frame, textvariable=self.transition_matrix_string, borderwidth=2, relief='sunken', padding=1)
        b0_matrix_display = ttk.Label(transition_frame, textvariable=self.b0_matrix_string, borderwidth=2, relief='sunken', padding=1)
        b1_matrix_display = ttk.Label(transition_frame, textvariable=self.b1_matrix_string, borderwidth=2, relief='sunken', padding=1)

        transition_matrix_display.grid(row=1, column=1, padx=3, pady=3)
        b0_matrix_display.grid(row=2, column=1, padx=3, pady=3)
        b1_matrix_display.grid(row=3, column=1, padx=3, pady=3)

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

        if self.centralizer_string.get() == "":
            self.display_label.configure(foreground='red')
            self.display_text.set("Please set value for symmetry.")
            return

        starting_pt_array = self.pt_array_str_to_tuple(self.starting_pt_array.get())
        ending_pt_array = self.pt_array_str_to_tuple(self.ending_pt_array.get())

        if len(starting_pt_array) != len(ending_pt_array):
            self.display_label.configure(foreground='red')
            self.display_text.set("Point array lengths do not match.")
            return

        if len(starting_pt_array) == 1:
            starting_pt_array = starting_pt_array[0]
        if len(ending_pt_array) == 1:
            ending_pt_array = ending_pt_array[0]

        self.display_label.configure(foreground='green')
        self.display_text.set(f"{starting_pt_array} --> {ending_pt_array} under {self.centralizer_string.get()} symmetry.\nTODO GET TRANSITIONS")

        # try to get the results from remote
        try:
            remote_results = ssh_getter.get_transitions_from_remote(starting_pt_array, ending_pt_array, self.centralizer_string.get(), hostname=self.hostname)

            if len(remote_results) == 0:
                first_result = ["None"]*5
            else:
                first_result = remote_results[0]

            self.transition_status.set(f"{starting_pt_array} --> {ending_pt_array} under {self.centralizer_string.get()} symmetry.\nCURRENTLY ONLY GETS FIRST TRANSITION FOUND.")
            self.transition_matrix_string.set(first_result[2])
            self.b0_matrix_string.set(first_result[3])
            self.b1_matrix_string.set(first_result[4])
        except FileNotFoundError:
            self.display_label.configure(foreground='red')
            self.display_text.set(f"Transition file for {starting_pt_array} --> {ending_pt_array} under {self.centralizer_string.get()} symmetry does not exist on {self.hostname}.")

    def update_ssh_info_display(self):
        try:
            self.ssh_config_is_setup = ssh_getter.verify_ssh_config_is_setup(self.hostname)
            if self.ssh_config_is_setup:
                self.ssh_info_label.configure(foreground="green", text=f"Your SSH configuration is setup for {self.hostname}!")
            else:
                self.ssh_info_label.configure(foreground="red", text=f"Your SSH configuration is NOT setup for {self.hostname}!")
        except FileNotFoundError:
            self.ssh_info_label.configure(foreground="red", text="SSH configuration file does not exist!")


    def validate_pt_array_string(self, pt_array_string):
        """
        Validates whether the param is a point array string.
        :param pt_array_string:
        :return:
        """
        pt_array_regex = "[0-9]+(?:,[0-9]+)*,?"

        return re.fullmatch(pt_array_regex, pt_array_string) is not None or pt_array_string == ""

    def pt_array_str_to_tuple(self, string):
        if string[-1] == ',':
            string = string[:-1]

        return tuple(map(int, string.split(",")))


if __name__ == "__main__":
    SSHGui()
