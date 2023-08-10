# This file has classes for presenting a tkinter GUI, with a grid of arbs, and each arb having a table of markets.

# Imports
import tkinter as tk
from tkinter import ttk
from printing import pretty_percent, pretty_days
import webbrowser

REFRESH_SYMBOL="↻ "

class TkinterGUI:
    def __init__(self, arbs, platforms):
        self.arbs = arbs
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

        self.create_arb_grid(arbs)
        self.root.mainloop()

    def create_arb_grid(self, arbs):
        # Create a canvas for the arb grid
        arb_grid_canvas = tk.Canvas(self.root)
        arb_grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Create a scrollbar for the arb grid
        arb_grid_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=arb_grid_canvas.yview)
        arb_grid_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Configure the arb grid canvas
        arb_grid_canvas.configure(yscrollcommand=arb_grid_scrollbar.set)
        arb_grid_canvas.bind('<Configure>', lambda e: arb_grid_canvas.configure(scrollregion=arb_grid_canvas.bbox("all")))
        # Create a frame for the arb grid canvas
        arb_grid_canvas_frame = tk.Frame(arb_grid_canvas)
        arb_grid_canvas.create_window((0, 0), window=arb_grid_canvas_frame, anchor="nw")

        self.root.bind('<MouseWheel>', lambda e: arb_grid_canvas.yview_scroll(int(-1*e.delta/120), "units"))
        self.root.bind('<Button-4>', lambda e: arb_grid_canvas.yview_scroll(-1, "units"))  # Linux and Windows
        self.root.bind('<Button-5>', lambda e: arb_grid_canvas.yview_scroll(1, "units"))  # Linux and Windows

        scroll_function = lambda e: print(e)

        arb_tables = []
        for arb in arbs:
            arb_table = self.create_arb_table(arb.title(), arb_grid_canvas_frame)
            TkinterGUI.repopulate_arb_table(arb_table, arb)
            arb_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Update scroll region now that the widgets are packed
        arb_grid_canvas.configure(scrollregion=arb_grid_canvas.bbox("all"))

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



    def create_arb_table(self, title, arb_grid_canvas_frame):
        columns = ('refresh', 'days', 'title', 'size', 'odds', 'stake', 'url')
        headers = (REFRESH_SYMBOL, 'Days', title, 'Size', 'Odds', 'Stake', 'URL')
        column_widths = (30, 40, 300, 60, 60, 70, 70)

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
                    am.market.url()
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
    from main import get_arbs_sorted_by_score

    platforms = ['metaculus', 'manifold']
    arbs = get_arbs_sorted_by_score(platforms)

    gui = TkinterGUI(arbs, platforms)
