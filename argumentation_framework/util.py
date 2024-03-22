import threading
from concurrent.futures import ThreadPoolExecutor

import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np




def draw_networkx_figure(attack_matrix, arg_mask=None, node_labels=None, node_colors=None, **kwargs):
    G = nx.DiGraph()

    arguments = np.arange(attack_matrix.shape[0])
    if arg_mask is not None:
        arguments = arguments[np.nonzero(arg_mask)]

    colors = defaultdict(lambda: 'white')

    if node_colors is not None:
        colors.update(node_colors)

    labels = {i: i for i in range(len(arguments))}
    if node_labels is not None:
        labels.update(node_labels)

    for i in arguments:
        G.add_node(i)

    for i, j in np.argwhere(attack_matrix > 0):
        G.add_weighted_edges_from([(i, j, 1), ])

    colormap = [colors[arg] for arg in sorted(labels.keys())]
    pos = nx.planar_layout(G, scale=1, dim=2)

    nx.draw(G, labels=labels, node_color=colormap, pos=pos, **kwargs)



def draw_extensions(extensions, attacks_matrix, arg_mask=None, ncols=4):
    extensions = list(extensions)

    if len(extensions) < ncols:
        ncols = max(1, len(extensions))

    nrows = int(np.ceil(len(extensions) / ncols))


    for i, p_ext in enumerate(extensions):
        p, ext = p_ext

        colors = defaultdict(lambda: 'white')
        for e in ext:
            colors[e] = 'yellow'

        ax = plt.subplot(nrows, ncols, i + 1)
        ax.set_title('{:.3f}'.format(p))
        draw_networkx_figure(
            attacks_matrix,
            arg_mask,
            ax=ax,
            node_colors=colors
        )




def execute_with_timeout(timeout_secs, function, *args):
    """
    Executes a function on a separate thread using a timeout.
    execute_with_timeout() ends whenever either the function returns or if the timeout elapses. In the second case
    a TimeoutError is raised.
    :param timeout_secs: timeout in seconds waited for the function to complete
    :param function: function to execute
    :param args: arguments to pass to the function
    :return: the function's returned value, or an error is reaised in timeout elapses
    """
    done = threading.Event()
    done.clear()
    _result = None

    def __fcn(*x):
        nonlocal _result
        _result = function(*x)
        done.set()

    thread = threading.Thread(target=__fcn, args=args)
    thread.start()
    if not done.wait(timeout_secs):
        raise TimeoutError('Timeout elapsed')
    return _result




def parallelize_iterations(generator, function, num_workers=1):
    """
    Parallelize on multiple threads the computations on a collection of elements
    :param generator: generator or iterable yielding the collection of elements
    :param function: function to call on each collection element
    :param num_workers: number of threads to use
    :return: a list with the results
    """
    generator = list(generator)
    #futures = [function(x) for x in generator]
    #return futures
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        generator = list(generator)
        futures = [executor.submit(function, x) for x in generator]
        results = [f.result() for f in futures]

    return results