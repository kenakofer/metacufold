# This file has classes for presenting a tkinter GUI, with a grid of arbs, and each arb having a table of markets.

# Imports
import tkinter as tk
from tkinter import ttk
from printing import pretty_percent, pretty_days
import webbrowser
import threading

REFRESH_SYMBOL="↻ "
PLATFORMS = ['metaculus', 'manifold']
# PLATFORMS = []

class TkinterGUI:
    def __init__(self, platforms = None):
        if platforms is None:
            platforms = PLATFORMS
        self.platforms = platforms

        self.root = tk.Tk()
        self.root.title("Arb Finder")
        self.root.geometry("1000x800")

        # Configure dark theme
        s = ttk.Style()
        s.configure("Treeview",
            background="black",
            foreground="white",
            fieldbackground="black"
        )

        s.configure("Treeview.Heading",
            background="#555555",
            foreground="white"
        )

        # Fix headings on Windows
        s.theme_use("clam")

        # Add a top row with a text box for filtering
        top_row = tk.Frame(self.root)
        top_row.pack(side=tk.TOP, fill=tk.X)
        self.filter_text = tk.StringVar()
        # self.filter_text.trace("w", lambda name, index, mode, sv=self.filter_text: self.filter_changed())
        self.filter_entry = tk.Entry(top_row, textvariable=self.filter_text)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entry.focus_set()
        self.filter_entry.bind('<Return>', lambda e: self.filter_changed())
        self.filter_entry.bind('<Escape>', lambda e: self.filter_entry.delete(0, tk.END))

        # Add a status bar label at the bottom
        self.status_bar_label = tk.StringVar()
        self.status_bar_label.set("Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status_bar_label, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        arbs = get_arbs_generator(self.platforms, status_callback=self.status_bar_label.set)
        self.arb_list = []

        canvas, frame = TkinterGUI.setup_arb_list(arbs, self.root)
        # Threading for populate_arb_list
        threading.Thread(target=TkinterGUI.populate_arb_list, args=(self.arb_list, arbs, canvas, frame, self.root)).start()

        self.root.mainloop()

    def filter_changed(self):
        # For each word in the filter text, check if it is in the arb title. If any word is missing, hide the arb.table
        filter_words = self.filter_text.get().lower().split()
        for arb_table in self.arb_list:
            if not filter_words or all(word in arb_table.arb.title().lower() for word in filter_words):
                arb_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            else:
                arb_table.pack_forget()

    def setup_arb_list(arbs, root):
        # Create a canvas for the arb grid
        arb_list_canvas = tk.Canvas(root)
        arb_list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Create a scrollbar for the arb grid
        arb_list_scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=arb_list_canvas.yview)
        arb_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Configure the arb grid canvas
        arb_list_canvas.configure(yscrollcommand=arb_list_scrollbar.set)
        arb_list_canvas.bind('<Configure>', lambda e: arb_list_canvas.configure(scrollregion=arb_list_canvas.bbox("all")))
        # Create a frame for the arb grid canvas
        arb_list_canvas_frame = tk.Frame(arb_list_canvas)
        arb_list_canvas.create_window((0, 0), window=arb_list_canvas_frame, anchor="nw")

        root.bind('<MouseWheel>', lambda e: arb_list_canvas.yview_scroll(int(-1*e.delta/120), "units"))
        root.bind('<Button-4>', lambda e: arb_list_canvas.yview_scroll(-1, "units"))
        root.bind('<Button-5>', lambda e: arb_list_canvas.yview_scroll(1, "units"))

        return arb_list_canvas, arb_list_canvas_frame

    def populate_arb_list(arb_list, arbs, canvas, canvas_frame, root):
        # Running the arbs generator is long running
        for arb in arbs:
            TkinterGUI.add_arb_table(arb, arb_list, canvas_frame)
            # Update scroll region now that the widgets are packed
            canvas.configure(scrollregion=canvas.bbox("all"))

    def activate_row(tree, event):
        row = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        print(event, column, row)
        if column == '#7':
            if row != '':
                url = tree.item(row)['values'][6]
                webbrowser.open(url)
            else:
                # Open every row's url
                for row in tree.get_children():
                    url = tree.item(row)['values'][6]
                    webbrowser.open(url)
        elif column == '#1':
            if row != '':
                print("Refreshing " + str(row))
                tree.arb.refresh(int(row))
            else:
                # Refresh every row
                for row in tree.get_children():
                    print("Refreshing " + str(row))
                    tree.arb.refresh(int(row))
            TkinterGUI.repopulate_arb_table(tree, tree.arb)


    def add_arb_table(arb, arb_list, arb_grid_canvas_frame):
        arb_table = TkinterGUI.setup_table(arb.title(), arb_grid_canvas_frame)
        arb_table.arb = arb
        TkinterGUI.repopulate_arb_table(arb_table, arb)
        # Insert the arb table such that the arb list stays sorted by arb_table.arb.score()
        for i, arb_table2 in enumerate(arb_list):
            if arb.score() > arb_table2.arb.score():
                arb_list.insert(i, arb_table)
                arb_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, before=arb_table2)
                break
        else:
            arb_list.append(arb_table)
            arb_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        return arb_table

    def setup_table(title, arb_grid_canvas_frame):
        columns = ('refresh', 'days', 'title', 'size', 'odds', 'stake', 'url')
        headers = (REFRESH_SYMBOL, 'Days', title, 'Size', 'Odds', 'Stake', 'URL')
        column_widths = (30, 40, 300, 60, 60, 70, 140)

        # Create the table with the specified columns
        arb_table = ttk.Treeview(
            arb_grid_canvas_frame,
            columns = columns,
            show = 'headings' # Hides a weird empty column
        )

        # Use a dark background color and white text
        # arb_table.tag_configure('oddrow', background='#222222')
        # arb_table.tag_configure('evenrow', background='#333333')
        # arb_table.tag_configure('oddrow', foreground='#eeeeee')
        # arb_table.tag_configure('evenrow', foreground='#eeeeee')

        for column, width, header in zip(columns, column_widths, headers):
            arb_table.heading(column, text=header)
            arb_table.column(column, width=width)

        return arb_table

    def repopulate_arb_table(arb_table, arb):

        # Delete any rows that are already in the table
        arb_table.delete(*arb_table.get_children())

        # Store the arb on the table object
        arb_table.arb = arb

        # Populate the table with the data in the arb markets
        for i, am in enumerate(arb.arb_markets()):
            # Insert the market into the table
            arb_table.insert(
                parent='',
                index=0,
                iid=i,
                tag=[i, am.market.PLATFORM_NAME, 'oddrow' if i%2 else 'evenrow'],
                values=(
                    REFRESH_SYMBOL,
                    pretty_days(am.market),
                    am.market.title(),
                    am.market.size_string(),
                    pretty_percent(am, color=False),
                    am.pretty_pos(),
                    am.market.url().replace('https://', '').replace('www.', '')
                )
            )

        # Double clicking the row opens the market in a browser
        arb_table.bind('<Double-1>', lambda e: TkinterGUI.activate_row(arb_table, e))
        arb_table.bind('<Button-1>', lambda e: TkinterGUI.activate_row(arb_table, e))
        arb_table.bind('<Return>', lambda e: TkinterGUI.activate_row(arb_table, e))

        # Remove extra vertical space under the entries
        arb_table.configure(height=len(arb.markets())+1)

        # Use a dark background color and white text
        arb_table.tag_configure('oddrow', background='#222222')
        arb_table.tag_configure('evenrow', background='#333333')
        arb_table.tag_configure('oddrow', foreground='#ffffff')
        arb_table.tag_configure('evenrow', foreground='#ffffff')


if __name__ == '__main__':
    from main import get_arbs_generator


    TkinterGUI()
