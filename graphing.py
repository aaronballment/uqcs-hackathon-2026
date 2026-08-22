import numpy as np
import sympy as sp
import os
from sympy.parsing.latex import parse_latex
import matplotlib.pyplot as plt
#from main import extract_math


def latex_conversion(latex: str, filename: str, ) -> bool:
    expression = parse_latex(latex)
    x = sp.Symbol("x")
    
    func = sp.lambdify(x, expression, 'numpy')
    
    x_values = np.linspace(x_min, x_max, 400)
    y_values = func(x_values)

    fig, ax = plt.subplots(figsize=(6, 6))

    '''
    Attempting to implement style changes to make the graph more readable
        set_title()
        <xlabel, ylabel>

        plot(..., color=#1A365D, linewidth=, linestyle=)
    '''

    ax.plot(x_values, y_values, color="#1051AB", linewidth=4)

    for spine in ['top', 'right' ]:
        ax.spines[spine].set_visible(False)

    ax.spines['bottom'].set_linewidth(4.5)
    ax.spines['bottom'].set_color("#D51E1E")
    ax.spines['left'].set_linewidth(4.5)
    ax.spines['left'].set_color("#D51E1E")

    ax.grid(axis='y', linestyle = '-', linewidth = 1.5, color = '#E2E8F0', zorder = 0)
    ax.grid(axis = 'x', linestyle = '-', linewidth = 1.5, color = '#E2E8F0', zorder = 0)
    ax.set_axisbelow(True)

    plt.tick_params('both', labelcolor = "#D51E1E", labelsize = 14)

    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    plt.savefig(filepath, transparent=True)
    plt.close()

    return True


if __name__ == "__main__":
    latex_conversion(r"x^2 - 4", "test_plot2.png")
    print("SUCCESS")
    