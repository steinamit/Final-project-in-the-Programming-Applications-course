import tkinter as tk
import os
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Class 1 - Manages directory analysis and file-size data collection
class DirectoryScanner:
    """
    This class is responsible for analyzing a given directory, extracting file sizes,
    and constructing a hierarchical structure of files and subdirectories.
    """
    def __init__(self, user_path):
        """
        Initializes the DirectoryScanner instance by scanning the directory and
        computing its structure and total size.

        user_path: The path to the directory that will be analyzed.
        """
        self.path = user_path
        self.file_sizes = [] 
        self.structure, self.total_size = self.scan_file(user_path) 

    def convert_size(self, size, decimal_places=4):
        """
        Converts a file size from bytes to megabytes (MB).
        """
        return round(size / (2 ** 20), decimal_places)
    
    def scan_file(self, directory_path):
        """
        Recursively scans the given directory path to construct a tree structure
        of files and subdirectories. 
        It calculates the total file size in bytes and organizes the data in a dictionary.
    
        directory_path: Path of the directory to scan.
        return: A tuple (directory_structure, total_size) 
        where directory_structure is a nested dictionary of (name, MB_size)->sub_structure
        and total_size is the cumulative size in bytes.
        """
        directory_structure = {}
        total_size = 0
    
        with os.scandir(directory_path) as entries:
            entries_list = list(entries)
    
        # First process directories recursively
        dir_entries = [entry for entry in entries_list if entry.is_dir()]
        for dir_entry in dir_entries:
            sub_structure, sub_size = self.scan_file(dir_entry.path)
            total_size += sub_size
            directory_structure[(dir_entry.name, self.convert_size(sub_size))] = sub_structure
    
        # Then process files first
        file_entries = [entry for entry in entries_list if entry.is_file()]
        for file_entry in file_entries:
            file_size = file_entry.stat().st_size
            self.file_sizes.append(file_size)
            total_size += file_size
            directory_structure[(file_entry.name, self.convert_size(file_size))] = None
        
        return directory_structure, total_size


# Class 2 - GUI and user interactions
class TreeApp:
    """
    This class is responsible for managing the graphical user interface (GUI)
    for the directory analysis application.
    """
    def __init__(self, root):
        """
        Initializes the main Tkinter window and creates the UI components for user interaction.
        """
        self.window = root
        self.window.geometry("800x600")
        self.window.title("Folder Analysis Tool")

        self.path_var = tk.StringVar()
        tk.Label(self.window, text='Enter directory path:', font=('Arial', 14)).grid(row=1, column=1)
        tk.Entry(self.window, width=60, textvariable=self.path_var).grid(row=1, column=2)

        self.exe_button = tk.Button(self.window, text='EXE', font=('Arial', 14, 'bold'), command=self.win_buttons)
        self.exe_button.grid(row=2, column=4)
        tk.Button(self.window, text='EXIT', font=('Arial', 14, 'bold'), command=self.window.destroy).grid(row=2, column=5)

    def win_buttons(self):
        """
        Retrieves the directory path entered by the user and initiates the analysis.
        Displays an error message if the path is invalid, otherwise creates a DirectoryScanner instance.
        """
        user_path = self.path_var.get().strip()
        if not os.path.isdir(user_path): #Error in a case of wrong path
            tk.messagebox.showerror('Directory not found.') 
            return

        self.analysis = DirectoryScanner(user_path)
        self.exe_button.grid_forget()
        tk.Button(self.window, text='TREE', font=('Arial', 14, 'bold'), command=self.display_tree).grid(row=3, column=4)
        tk.Button(self.window, text='STAT', font=('Arial', 14, 'bold'), command=self.display_statistics).grid(row=3, column=5)

    def display_tree(self):
        """
        Displays the hierarchical directory structure in a new Tkinter window,
        using a Listbox to show folder/file data with indentation and a scrollbar.
        """
        tree_window = tk.Toplevel(self.window)
        tree_window.title("Directory Tree - " + self.analysis.path.split('\\')[-1])
        tree_window.geometry("800x600")

        frame = tk.Frame(tree_window)
        frame.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree_listbox = tk.Listbox(frame, width=100, yscrollcommand=scrollbar.set)
        tree_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.build_tree(tree_listbox, self.analysis.structure, self.analysis.total_size / (2 ** 20))
        
        scrollbar.config(command=tree_listbox.yview)

    def build_tree(self, tree_listbox, structure, level_size, indent=0):
        """
        Recursively populates the Listbox with folders and files from 'structure'.
        'level_size' is the size of the parent folder in MB, used to calculate
        the percentage that each item occupies.
        'indent' controls how many branch symbols are used for indentation.
        """
        branch_symbol = "│   "  # Symbol for tree branches
        last_branch = "└── "  # Symbol for last branch in a folder
        middle_branch = "├── "  # Symbol for middle branches

        items = list(structure.keys()) 
        for index, key in enumerate(items):
            percent = round(key[1] / level_size * 100, 2) if level_size else 0
            is_last = index == len(items) - 1  # Check if the item is the last one in the directory
            prefix = (branch_symbol * indent) + (last_branch if is_last else middle_branch)

            if structure[key] is None:  
                tree_listbox.insert(tk.END, f"{prefix}📄 {key[0]} - ({key[1]}MB || {percent}%)")
            else: 
                tree_listbox.insert(tk.END, f"{prefix}📁 {key[0]} - ({key[1]}MB || {percent}%)")
                self.build_tree(tree_listbox, structure[key], key[1], indent + 1)
                
    def display_statistics(self):
        """
        Displays a statistical analysis of file sizes in the analyzed directory,
        using seaborn and matplotlib for visualization.
        """
        stat_window = tk.Toplevel(self.window)
        stat_window.title("Statistical Review - " + self.analysis.path.split("\\")[-1])

        bins = [0, 10**3, 10**4, 10**5, 10**6, 10**7, 10**8]
        labels = ['1KB', '10KB', '100KB', '1MB', '10MB', '100MB+']
        file_size_categories = pd.cut(self.analysis.file_sizes, bins=bins, labels=labels)
        size_counts = file_size_categories.value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
        sns.barplot(x=size_counts.index, y=size_counts.values, color="purple", ax=ax)
        sns.lineplot(x=size_counts.index, y=size_counts.values, marker="o", color="pink", ax=ax)

        ax.set_title("Distribution of File Sizes")
        ax.set_xlabel("File Size Category")
        ax.set_ylabel("Count")

        total_size_label = tk.Label(stat_window, text=f'Total Size: {round(self.analysis.total_size / (2 ** 20), 2)} MB', font=('Arial', 18, 'bold'))
        total_size_label.pack()
            
        canvas = FigureCanvasTkAgg(fig, stat_window)
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)

"""
Create the main window and run the app
"""
if __name__ == "__main__":
    root = tk.Tk()
    app = TreeApp(root)
    root.mainloop()

