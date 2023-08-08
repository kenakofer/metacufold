# This file has classes for presenting a tkinter GUI, with a grid of arbs, and each arb having a table of markets.

# Imports
import tkinter as tk
from tkinter import ttk

class TkinterGUI:
    def __init__(self, arbs, platforms):
        self.arbs = arbs
        self.platforms = platforms
        self.root = tk.Tk()
        self.root.title("Arb Finder")
        self.root.geometry("1000x800")
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

        arb_tables = [self.create_arb_table(arb, arb_grid_canvas_frame) for arb in arbs]
        for arb_table in arb_tables:
            arb_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Update scroll region now that the widgets are packed
        arb_grid_canvas.configure(scrollregion=arb_grid_canvas.bbox("all"))

    def create_arb_table(self, arb, arb_grid_canvas_frame):
        columns = ('platform', 'title', 'odds', 'stake', 'url')

        # Create the table with the specified columns
        arb_table = ttk.Treeview(
            arb_grid_canvas_frame,
            columns = columns,
            show = 'headings' # Hides a weird empty column

        )

        for column in columns:
            arb_table.heading(column, text=column)

        # Populate the table with the data in the arb markets
        for market in arb.markets():
            # Insert the market into the table
            arb_table.insert(
                parent='',
                index='end',
                iid=market.market_id,
                values=(
                    market.PLATFORM_NAME,
                    market.title(),
                    market.probability(),
                    market.user_position_shares(),
                    market.url()
                )
            )

        # Remove extra vertical space under the entries
        arb_table.configure(height=len(arb.markets())+1)


        return arb_table


if __name__ == '__main__':
    from main import get_arbs_sorted_by_score

    platforms = ['metaculus', 'manifold']
    arbs = get_arbs_sorted_by_score(platforms)

    gui = TkinterGUI(arbs, platforms)
