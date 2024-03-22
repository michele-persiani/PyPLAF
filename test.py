from gui.impl import *
import tkinter as tk






if __name__ == '__main__':
    af = ArgumentationFramework(10)
    paf = ProbabilisiticWrapper(af)


    # Graphical User Interface
    root = tk.Tk()

    prob_module = FrameworkProbabilitiesModule(root, 1, 2, paf)

    plt_module = ArgumentationFrameworkGraph(root, 1, 3, paf)

    ext_module = ExtensionsGraph(root, 2, 3, paf)

    tk.mainloop()
