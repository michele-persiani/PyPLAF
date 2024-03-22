from argumentation_framework.util import draw_extensions, draw_networkx_figure
from gui.modules import ListModule, PltFigureModule, GUIModule
from argumentation_framework.logical_arguments import Argument
from argumentation_framework.solved_af import *
import tkinter as tk
from argumentation_framework.frameworks import ArgumentationFramework, ProbabilisiticWrapper
import matplotlib.pyplot as plt
import numpy as np


REFRESH_EVENT = '<<ArgFrameworkChanged>>'


class ArgumentListModule(ListModule):


    def __init__(self, master, row_num, column_num, items, **kwargs):
        super().__init__(master, row_num, column_num, items, **kwargs)


    def build_list_element(self, master, i, item: Argument):
        w = tk.Frame(master)
        lbl = tk.Label(w,
                       text=f'{i})  {str(item)}',
                       height=self.get_kwarg('height_elem', 2),
                       font=self.get_kwarg('font', ("Arial", 15))
                       )
        lbl.pack(side=tk.LEFT)
        return w



class FrameworkProbabilitiesModule(GUIModule):


    def __init__(self, master, row_num, column_num, paf: ProbabilisiticWrapper, **kwargs):
        super().__init__(master, row_num, column_num, **kwargs)
        self.paf = paf

        fcn0 = self.build_p_arg_widget()
        fcn1 = self.build_p_attacks_widget()

        def __f():
            fcn0()
            fcn1()
            self.notify(REFRESH_EVENT)

        self.add_button_option("Apply", __f)

    def get_set_p_a_fcn(self, txt, argn):
        return lambda: self.paf.set_p_arg(argn, float(txt.get("1.0", tk.END)))

    def get_set_fcn(self, txt, frm, to):
        return lambda: self.paf.set_p_attacks(frm, to, float(txt.get("1.0", tk.END)))


    def build_p_attacks_widget(self):
        updates = []

        w = tk.Frame(self.main_frame)
        for i in range(self.paf.wrapped_framework.num_max_arguments):
            tk.Label(w, text=f'{i}').grid(row=1, column=i+2)
        for i in range(self.paf.wrapped_framework.num_max_arguments):
            tk.Label(w, text=f'{i}').grid(row=i+2, column=1)
            for j in range(self.paf.wrapped_framework.num_max_arguments):
                txt = tk.Text(w, width=5, height=1)
                txt.insert('1.0', str(self.paf.get_p_attacks()[i, j]))
                txt.grid(row=i+2, column=j + 2)
                updates += self.get_set_fcn(txt, i, j),
        w.pack()

        def __update():
            for fcn in updates:
                fcn()

        return __update


    def build_p_arg_widget(self):
        w = tk.Frame(self.main_frame)
        tk.Label(w, text='a').grid(row=1, column=1)
        tk.Label(w, text='P(a)').grid(row=2, column=1)

        updates = []

        for i in range(self.paf.wrapped_framework.num_max_arguments):
            tk.Label(w, text=f'{i}').grid(row=1, column=i + 1)
            txt = tk.Text(w, width=5, height=1)
            txt.insert('1.0', str(self.paf.get_p_arg(i)))
            txt.grid(row=2, column=i + 1)
            updates += self.get_set_p_a_fcn(txt, i),
        w.pack()

        def __update():
            for fcn in updates:
                fcn()

        return __update







class ArgumentationFrameworkGraph(PltFigureModule):

    def __init__(self, master, row_num, column_num, paf: ProbabilisiticWrapper, **kwargs):
        super().__init__(master, row_num, column_num, **kwargs)
        self.paf = paf
        self.refresh()

        self.add_button_option("Refresh", self.refresh)

        self.add_observer(self.refresh, lambda x: x == REFRESH_EVENT)


    def get_figure(self):
        fig = plt.figure()
        af = self.paf.wrapped_framework
        draw_networkx_figure(
            af.attacks_matrix,
            af.argument_mask,
            node_labels=None,
            node_colors={a: 'red' if np.any(af.attacks_matrix[:, a]) else 'white' for a in af.arguments}
        )

        return fig


class FrameworksEquivalenceModule(GUIModule):

    def __init__(self, master, row_num, column_num, paf1:ProbabilisiticWrapper, paf2: ProbabilisiticWrapper):
        super().__init__(master, row_num, column_num)
        self.paf1 = paf1
        self.paf2 = paf2

        self.lbl = tk.Label(self, text='None')
        self.lbl.pack()

        self.add_radio_button_option({
            'Preferred': EE_PR,
            'Stable': EE_ST,
            'Complete': EE_CO,
        },
            self.compute_equivalence,
            'Preferred'
        )
        self.refresh()

    def compute_equivalence(self, value):
        equivalence = self.paf1.get_p_equivalent_to(self.paf2, value)
        self.lbl.config(text=f'{equivalence}')


class ExtensionsGraph(PltFigureModule):

    def __init__(self, master, row_num, column_num, paf: ProbabilisiticWrapper, **kwargs):
        super().__init__(master, row_num, column_num, **kwargs)
        self.paf = paf

        self.add_radio_button_option({
            'Preferred': EE_PR,
            'Stable': EE_ST,
            'Complete': EE_CO,
        },
            self.set_extension_type,
            'Preferred'
        )
        self.ext_type = EE_PR

        self.refresh()
        self.add_observer(self.refresh, lambda x: x == REFRESH_EVENT)


    def set_extension_type(self, typ: str):
        self.ext_type = typ.strip()
        self.refresh()


    def get_figure(self):
        fig = plt.figure()
        draw_extensions(
            self.paf.get_p_extension(self.ext_type),
            self.paf.wrapped_framework.attacks_matrix,
            self.paf.wrapped_framework.argument_mask
        )

        return fig

