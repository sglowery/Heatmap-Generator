# heatmap_interface written by Stephen Lowery
# Github: sglowery
# Email: stephen.g.lowery@gmail.com


from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from os import path
import heatmap


class IncompleteEntryException(Exception):
    pass


class HeatmapGenerator:

    def __init__(self, master):

        self.columns = 3
        self.padding = 5
        self.sigma = 1.2
        self.max_score = 30
        self.picked_file = ""

        # http://matplotlib.org/examples/color/colormaps_reference.html
        self.colormap_options = [
            'viridis', 'plasma', 'inferno', 'magma',
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c',
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']
        self.cmaps_image = ImageTk.PhotoImage(Image.open("colormaps.png"))

        master.title("Heatmap Generator")

        ## File picker
        self.file_picker_label = Label(master, text="Pick a file",
                                       padx=self.padding, pady=self.padding)
        self.file_picker_button = Button(master, text="Browse", command=self.pick_file,
                                         padx=self.padding, pady=self.padding)
        self.picked_file_var = StringVar()
        self.picked_file_var.set("No file picked yet!")
        self.file_picker_display = Label(master, textvariable=self.picked_file_var,
                                         padx=self.padding, pady=self.padding)
        ## Max score
        self.max_score_label = Label(master, text="Max score",
                                     padx=self.padding, pady=self.padding)
        validate_max_score_reg = master.register(self.validate_float)
        self.max_score_entry = Entry(master, validate="key", validatecommand=(validate_max_score_reg, '%P', 'i'))
        self.max_score_entry.insert(END, str(self.max_score))

        ## Blur amount
        self.sigma_label = Label(master, text="Blur amount",
                                 padx=self.padding, pady=self.padding)
        validate_sigma_reg = master.register(self.validate_float)
        self.sigma_entry = Entry(master, text="2", validate="key", validatecommand=(validate_sigma_reg, '%P', 'f'))
        self.sigma_entry.insert(END, str(self.sigma))

        ## Colormap
        # instead of finangling with grid and column width, i make a separate Frame instance and add the listbox and
        # scrollbar to it. the Frame can then be put as a whole into the root Tk() instance the same as any other
        # element
        self.colormap_frame = Frame(master)
        self.colormap_label = Label(master, text="Choose a set of colors\n for the heatmap",
                                    padx=self.padding, pady=self.padding)
        self.colormap_scrollbar = Scrollbar(self.colormap_frame)
        self.colormap_listbox = Listbox(self.colormap_frame,
                                        yscrollcommand=self.colormap_scrollbar.set, exportselection=False)
        # exportselection=False preserves the selected value of the listbox if it loses focus (e.g. clicking anywhere
        # on the interface or interacting with another element like a button)

        self.colormap_listbox.grid(row=0, column=0, sticky=W+E)
        self.colormap_scrollbar.grid(row=0, column=1, sticky=N+S)
        self.colormap_scrollbar.config(command=self.colormap_listbox.yview)
        self.colormap_button = Button(master, text="?", command=self.show_colormaps,
                                      padx=self.padding, pady=self.padding)

        for i, option in enumerate(self.colormap_options):
            self.colormap_listbox.insert(i, option)

        # these commands set the default selection value of the listbox and scroll it to ensure that value is seen,
        # respectively
        self.colormap_listbox.selection_set(self.colormap_options.index("jet"))
        self.colormap_listbox.see(self.colormap_options.index("jet"))

        self.generate_button = Button(master, text="Generate data heatmap", command=self.generate_heatmap, bg="#BBBBBB",
                                      padx=self.padding, pady=self.padding)

        ## Layout

        # this tuple of lists represents the order of the elements to populate the GUI with; each list represents a row,
        # and each item in a list represents a new column containing that item
        self.layout = (
            [self.file_picker_label, self.file_picker_button],
            [self.file_picker_display],
            [self.max_score_label, self.max_score_entry],
            [self.sigma_label, self.sigma_entry],
            [self.colormap_label, self.colormap_frame, self.colormap_button],
            [self.generate_button]

        )

        # this iterates through the layout list and adds them to the master instance with the grid() method.
        # if a row only contains one item, allow its cell to span extra columns
        for row, items in enumerate(self.layout):
            for column, item in enumerate(items):
                item.grid(row=row, column=column, columnspan=1+(2 if len(items) < 2 else 0))

    def pick_file(self):
        self.picked_file = askopenfilename(initialdir=path.dirname(__file__),
                                           filetypes=(("CSV Files", "*.csv"), ("Text files", "*.txt")))
        if len(self.picked_file) == 0:
            self.picked_file_var.set("No file picked yet!")
        else:
            self.picked_file_var.set(self.picked_file)

    # validate_float() is called when the user presses a key to type in an entry field. returning True allows the
    # pressed button's value to be entered; returning False will prevent the value from showing up entirely.
    # i only want numbers in the entry fields, but the entry fields will either require an integer or a floating-point
    # number, so both of those cases are taken care of here
    def validate_float(self, new_text, num_type):
        if not new_text:
            if num_type == 'f':
                self.sigma = -1
            elif num_type == 'i':
                self.max_score = -1
            return True
        try:
            if num_type == 'f':
                self.sigma = float(new_text)
            elif num_type == 'i':
                self.max_score = int(new_text)
            return True
        except ValueError:
            return False

    # creating a new instance of Toplevel() is how to create a new child window of the main window
    def show_colormaps(self):
        cmap_window = Toplevel()
        cmap_window.wm_title("Available colormaps")
        cmaps_label = Label(cmap_window, image=self.cmaps_image)
        cmaps_label.pack(fill="both", expand=True)

    # most of this code ensures there are no PEBCAK errors before finally calling the heatmap generation code
    def generate_heatmap(self):
        try:
            colormap = plt.get_cmap(self.colormap_options[self.colormap_listbox.curselection()[0]])
            with open(self.picked_file) as file:
                if self.max_score < 0 or self.sigma < 0:
                    raise IncompleteEntryException
        except FileNotFoundError:
            if len(self.picked_file) == 0:
                messagebox.showerror("Error", "No file picked!")
            else:
                messagebox.showerror("Error", "Error: {} not found".format(file))
        except TypeError:
            messagebox.showerror("Error", "Error: No file picked")
        except IncompleteEntryException:
            messagebox.showerror("Error", "Max score and sigma can't be blank")
        else:
            heatmap.gen_heatmap(self.picked_file, max_score=self.max_score, sigma=self.sigma, colormap=colormap)


root = Tk()
root.resizable(width=False, height=False)
my_gui = HeatmapGenerator(root)
root.mainloop()
