import numpy as np
import sympy as sp
from sympy.parsing.latex import parse_latex
import matplotlib.pyplot as plt


def latex_conversion(latex: str, filename: str, ) -> bool:
    expression = parse_latex(latex)
    x = sp.Symbol("x")
    
    func = sp.lambdify(x, expression, 'numpy')
    
    x_values = np.linspace(-10, 10, 400)
    y_values = func(x_values)


    fig, ax = plt.subplots(figsize=(6, 6))

    ax.plot(x_values, y_values, color='#00ffcc')


    plt.savefig(filename, transparent = True)
    plt.close()

    return True


if __name__ == "__main__":
    latex_conversion(r"x^2 - 4", "test_plot.png")
    print("SUCCESS")