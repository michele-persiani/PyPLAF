# PyPLAF
Python library for Probabilistic Logical Argumentation Frameworks




Example utilization:
```
# Definition of arguments
arguments = [
    make_simple_logic_argument({"A": True}, {"C": False}),
    make_simple_logic_argument({"B": True}, {"C": True}),
    make_simple_logic_argument({"D": True}, {"C": False})
]

# Creation of argumentation framework
af = make_argumentation_framework(arguments)

# Probabilistic wrapper
paf = ProbabilisiticWrapper(af)


# Graphical User Interface to modify and visualize the argumentation graph
root = tk.Tk()

args_module = ArgumentListModule(root, 1, 1, arguments)
prob_module = FrameworkProbabilitiesModule(root, 1, 2, paf)

plt_module = ArgumentationFrameworkGraph(root, 1, 3, paf)

ext_module = ExtensionsGraph(root, 2, 3, paf)

tk.mainloop()
```
