import tkinter as tk
from tkinter import ttk


class StatistikTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, padding=(5, 5, 12, 0), *args, **kwargs)

        table_frame = ttk.Frame(self)
        labels = ["Vagthavende", "Dagsvagt", "Nattevagt", "Kabys"]
        for row in range(63):
            for col in range(4):
                if row == 0:
                    self.make_box(
                        table_frame,
                        row + 1,
                        col + 1,
                        labels[col],
                        14,
                        False,
                        #self.selected_vagtliste_var[(time, opgave)],
                    )
                else:
                    if col == 0:
                        self.make_box(
                            table_frame,
                            row + 1,
                            col + 1,
                            str(row),
                            14,
                            False,
                            #self.selected_vagtliste_var[(time, opgave)],
                        )
                    else:
                        self.make_box(
                            table_frame,
                            row + 1,
                            col + 1,
                            "",
                            14,
                            False,
                            #self.selected_vagtliste_var[(time, opgave)],
                        )
        table_frame.pack()

    def make_box(self, parent, row, col, text, width, readonly, sv=None):
        entry1 = tk.Entry(
            parent,
            textvariable=sv if sv is not None else tk.StringVar(self, value=text),
            width=width,
            **{"validatecommand": self.vcmd} if readonly else {},
        )
        entry1.update()
        entry1.configure(validate="key")
        entry1.grid(row=row, column=col + 2)
                
#   | Vagthavende | Fysisk Dagsvagt | Fysisk Nattevagt | Dækselev i Kabys
# 1:    2 timer         7 timer                        
# 2:
# 3:
# 4:
# 5:
# 6:
# 7:
#  
