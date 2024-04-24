from PIL import Image, ImageOps, ImageTk
import re
import ssh_getter
import sympy as sp
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk


class SSHGui:
    hostname = "jigwe.kzoo.edu"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jigwe Transition Getter")
        self.root.geometry('1920x1080')

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
                                            state='readonly',
                                            width=3)
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

        transition_matrix_display.grid(row=1, column=1, columnspan=1, padx=3, pady=3)
        b0_matrix_display.grid(row=2, column=1, columnspan=1, padx=3, pady=3)
        b1_matrix_display.grid(row=3, column=1, columnspan=1, padx=3, pady=3)

        transition_clipboard_button = ttk.Button(transition_frame, text="Copy T to Clipboard",
                                                 command=lambda: self.copy_into_clipboard(self.transition_matrix_string.get()))
        b0_clipboard_button = ttk.Button(transition_frame, text="Copy B0 to Clipboard",
                                         command=lambda: self.copy_into_clipboard(self.b0_matrix_string.get()))
        b1_clipboard_button = ttk.Button(transition_frame, text="Copy B1 to Clipboard",
                                         command=lambda: self.copy_into_clipboard(self.b1_matrix_string.get()))

        transition_clipboard_button.grid(row=1, column=10, columnspan=10)
        b0_clipboard_button.grid(row=2, column=10, columnspan=10)
        b1_clipboard_button.grid(row=3, column=10, columnspan=10)

        # transition navigation
        self.remote_results = []  # will store the transitions retrieved from remote
        self.result_index = tk.IntVar(value=0)
        self.result_index.trace_add('write', self.update_transition_display)

        self.index_changer = ttk.Spinbox(transition_frame, from_=0, to=0, textvariable=self.result_index, width=3)
        self.index_changer.grid(row=5, column=10)

        self.num_results = tk.IntVar(value=0)
        tk.Label(transition_frame, text="out of").grid(row=5, column=11)
        tk.Label(transition_frame, textvariable=self.num_results).grid(row=5, column=12)

        # image
        self.equation_image = tk.Label(transition_frame)
        self.equation_image.grid(row=10, column=0, columnspan=20)
        self.update_equation_image(r'Equation will be here.')

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

        # try to get the results from remote
        try:
            self.remote_results = ssh_getter.get_transitions_from_remote(starting_pt_array, ending_pt_array, self.centralizer_string.get(), hostname=self.hostname)
            self.num_results.set(len(self.remote_results))

            if len(self.remote_results) == 0:
                self.result_index.set(0)
                self.index_changer['from'] = 0
                self.index_changer['to'] = 0
            else:
                self.result_index.set(1)
                self.index_changer['from'] = 1
                self.index_changer['to'] = self.num_results.get()

            self.transition_status.set(f"{starting_pt_array} --> {ending_pt_array} under {self.centralizer_string.get()} symmetry.")
            self.update_transition_display()

            self.display_label.configure(foreground='green')
            self.display_text.set("Successfully retrieved from Jigwe!")
        except FileNotFoundError:
            self.display_label.configure(foreground='red')
            self.display_text.set(f"Transition file for {starting_pt_array} --> {ending_pt_array} under {self.centralizer_string.get()} symmetry does not exist on {self.hostname}.")

    def update_ssh_info_display(self):
        try:
            self.ssh_config_is_setup = ssh_getter.verify_ssh_config_is_setup(self.hostname)
            if self.ssh_config_is_setup:
                self.ssh_info_label.configure(foreground="green", text=f"Your SSH configuration is setup for {self.hostname}!")
            else:
                self.ssh_info_label.configure(foreground="red", text=f"Your SSH configuration is NOT setup for {self.hostname}!\nSee the README!")
        except FileNotFoundError:
            self.ssh_info_label.configure(foreground="red", text="SSH configuration file does not exist!\nSee the README!")

    def update_transition_display(self, *args):
        """
        Updates the displayed T, B0, B1 with what is specified by remote results and index.
        To be run whenever result_index changes.
        :return:
        """
        # add *args because trace_add adds unneeded arguments
        if self.num_results.get() == 0:
            self.transition_matrix_string.set("None")
            self.b0_matrix_string.set("None")
            self.b1_matrix_string.set("None")
            self.update_equation_image("None")
            return

        # we want the display to be 1 indexed so we subtract 1 here
        result_index = self.result_index.get() - 1
        curr_result = self.remote_results[result_index]
        self.transition_matrix_string.set(self.create_formatted_sympy_matrix_string(curr_result[2]))
        self.b0_matrix_string.set(self.create_formatted_sympy_matrix_string(curr_result[3]))
        self.b1_matrix_string.set(self.create_formatted_sympy_matrix_string(curr_result[4]))

        equation = (f"$${sp.latex(curr_result[2], fold_short_frac=True)}\cdot"
                    f"{sp.latex(curr_result[3], fold_short_frac=True)} = "
                    f"{sp.latex(curr_result[4], fold_short_frac=True)}$$")
        self.update_equation_image(equation)

    def update_equation_image(self, equation):
        """
        Creates image from a LaTeX equation, resizes it, pads it, then updates the label.
        :param equation: String representing a LaTeX equation
        :return:
        """
        sp.preview(equation, viewer="file", filename="latex.png", dvioptions=['-D', '1200', "-M", "100"], euler=False)
        image = Image.open("latex.png")
        image = ImageOps.contain(image, (1000, 500))

        # specify padding
        padx = 10
        pady = 10

        # create padding
        width, height = image.size
        new_width = width + padx*2
        new_height = height + pady*2
        result = Image.new(image.mode, (new_width, new_height), color='white')
        result.paste(image, (padx, pady))

        # put image into Tk image
        image = ImageTk.PhotoImage(result)

        # configure label
        self.equation_image.configure(image=image)
        self.equation_image.image = image

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

    def create_formatted_sympy_matrix_string(self, matrix):
        """
        Takes a sympy matrix and returns its nested list form (without the 'Matrix(...)' business)
        :param matrix:
        :return:
        """
        matrix_regex = "Matrix\((.*)\)"
        return re.fullmatch(matrix_regex, str(matrix)).group(1)

    def copy_into_clipboard(self, string):
        self.root.clipboard_clear()
        self.root.clipboard_append(string)


if __name__ == "__main__":
    SSHGui()
