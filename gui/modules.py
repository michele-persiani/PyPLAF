import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # , NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
from inspect import signature


class Observable:


    def __init__(self):
        self.observers = list()

    def add_observer(self, callable, evt_filter=None):
        self.observers += (callable, evt_filter,),


    def remove_observer(self, callable):
        for i, callable_filter in enumerate(list(self.observers)):
            cbk, filter = callable_filter
            if cbk == callable:
                self.observers.remove(i)

    def notify(self, event):
        for cbk, filter in self.observers:
            if filter is None or not filter(event):
                continue
            num_params = len(signature(cbk).parameters)
            cbk() if num_params == 0 else cbk(event)


class GUIModule(tk.Frame):
    """
    Each module has two parts. The first shows the module's contents, while the second is for the module's options.
    Widgets can be added to the main part by using self.main_frame as master.
    Options should be added using the factory methods
    """

    observable = Observable()

    def __init__(self, master, row_num, column_num, **kwargs):
        super().__init__(master, **kwargs)
        self._kwargs = kwargs
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side=tk.TOP)
        self._options_frame = tk.Frame(self)
        self._options_frame.pack(side=tk.BOTTOM)
        self.options = []
        self.grid(column=column_num, row=row_num)


    def add_observer(self, callable, evt_filter=None):
        self.observable.add_observer(callable, evt_filter)


    def remove_observer(self, callable):
        self.observable.remove_observer(callable)

    def notify(self, event):
        self.observable.notify(event)


    def refresh(self):
        pass


    def get_kwarg(self, name, default_value):
        return self._kwargs[name] if name in self._kwargs else default_value


    def show_alert(self, title, message):
        messagebox.showerror(title, message)


    def add_button_option(self, text, on_click):
        w = tk.Frame(self._options_frame)

        def __fcn():
            on_click()
            self.refresh()

        btn = tk.Button(w, text=text, command=__fcn)
        btn.pack()
        self.options += w,
        w.grid(row=len(self.options), column=1)


    def add_string_option(self, name, text_width, on_click, initial_value=None):

        w = tk.Frame(self._options_frame)
        lbl = tk.Label(w, text=name)
        lbl.grid(row=1, column=1)
        txt = tk.Text(w, width=text_width, height=1)
        if initial_value is not None:
            txt.insert("1.0", initial_value)
        txt.grid(row=1, column=2)

        def __fcn():
            on_click(txt.get("1.0", tk.END))
            self.refresh()

        btn = tk.Button(w, text='Ok', command=__fcn)
        btn.grid(row=1, column=3)

        self.options += w,

        w.grid(row=len(self.options), column=1)


    def add_radio_button_option(self, values: dict, on_click, initial_value):

        v = tk.StringVar()
        v.set(values[initial_value])

        j = 0
        for k, value in values.items():
            btn = tk.Radiobutton(self._options_frame,
                                 text=str(k),
                                 padx=20,
                                 variable=v,
                                 command=lambda: on_click(v.get()),
                                 value=value)
            btn.grid(column=j, row=1)
            j += 1


class PltFigureModule(GUIModule):

    def __init__(self, master, row_num, column_num, **kwargs):
        super().__init__(master, row_num, column_num, **kwargs)
        self.canvas = None


    def get_figure(self):
        raise NotImplementedError

    def refresh(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        fig = self.get_figure()
        self.canvas = FigureCanvasTkAgg(fig, self.main_frame)
        self.canvas.get_tk_widget().pack()



class ListModule(GUIModule):

    def __init__(self, master, row_num, column_num, items: list, **kwargs):
        super().__init__(master, row_num, column_num, **kwargs)
        self.items = items
        self._previous_elements = []
        self.refresh()

    def refresh(self):
        for e in self._previous_elements:
            e.destroy()

        for i in range(self.count_list_items):
            e = self.build_list_element(self.main_frame, i, self.items[i])
            e.grid(row=i)
            self._previous_elements += e,

    @property
    def count_list_items(self):
        return len(self.items)

    def build_list_element(self, master, i, item):
        raise NotImplementedError
