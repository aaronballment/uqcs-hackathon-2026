import os
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib as mpl
from sympy.parsing.latex import parse_latex
import trimesh

def process_latex_input(latex: str, base_filename: str, x_min=-10.0, x_max=10.0, y_min=-10.0, y_max=10.0):
    x_min, x_max = float(x_min), float(x_max)
    y_min, y_max = float(y_min), float(y_max)

    expr = parse_latex(latex)
    x, y = sp.symbols('x y')
    has_y = expr.has(y)

    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)

    if has_y:
        # 3D Mesh Output (.glb)
        out_filename = f"{base_filename}.glb"
        filepath = os.path.join(output_dir, out_filename)

        grid_res = 60
        x_vals = np.linspace(x_min, x_max, grid_res)
        y_vals = np.linspace(y_min, y_max, grid_res)
        X, Y = np.meshgrid(x_vals, y_vals)

        func = sp.lambdify((x, y), expr, modules=['numpy', 'math'])
        
        try:
            Z = func(X, Y)
            if not isinstance(Z, np.ndarray):
                Z = np.full_like(X, float(Z))
        except Exception:
            Z = np.zeros_like(X)
            for i in range(grid_res):
                for j in range(grid_res):
                    try:
                        res = expr.subs({x: X[i, j], y: Y[i, j]}).evalf()
                        Z[i, j] = float(res) if res.is_real else 0.0
                    except Exception:
                        Z[i, j] = 0.0

        Z = np.nan_to_num(Z, nan=0.0, posinf=10.0, neginf=-10.0)

        # Normalize bounding box
        X_norm = (X - x_min) / (x_max - x_min) - 0.5
        Y_norm = (Y - y_min) / (y_max - y_min) - 0.5

        z_min, z_max = np.min(Z), np.max(Z)
        z_range = z_max - z_min
        
        if z_range > 1e-5:
            Z_norm = ((Z - z_min) / z_range - 0.5) * 0.5
        else:
            Z_norm = np.zeros_like(Z)

        vertices = np.column_stack((X_norm.ravel(), Z_norm.ravel(), Y_norm.ravel()))

        faces = []
        for i in range(grid_res - 1):
            for j in range(grid_res - 1):
                idx = i * grid_res + j
                faces.append([idx, idx + 1, idx + grid_res])
                faces.append([idx + 1, idx + grid_res + 1, idx + grid_res])

        # Height-mapped vertex color gradient
        norm_heights = (Z.ravel() - z_min) / (z_range if z_range > 1e-5 else 1.0)
        cmap = mpl.colormaps['plasma']
        vertex_colors = (cmap(norm_heights) * 255).astype(np.uint8)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=vertex_colors, process=True)
        mesh.fix_normals()
        mesh.export(filepath, file_type='glb')

        return out_filename, True

    else:
        out_filename = f"{base_filename}.png"
    filepath = os.path.join(output_dir, out_filename)

    func = sp.lambdify(x, expr, modules=['numpy', 'math'])
    x_values = np.linspace(x_min, x_max, 400)
    
    try:
        y_values = func(x_values)
        if not isinstance(y_values, np.ndarray):
            y_values = np.full_like(x_values, float(y_values))
    except Exception:
        y_list = []
        for val in x_values:
            try:
                res = expr.subs(x, val).evalf()
                y_list.append(float(res) if res.is_real else np.nan)
            except Exception:
                y_list.append(np.nan)
        y_values = np.array(y_list, dtype=float)

    fig, ax = plt.subplots(figsize=(10, 10))
    if max(y_values) >= 20:
        ax.set_ylim(-20, 20)
    ax.plot(x_values, y_values, color="#1051AB", linewidth=4)

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    ax.spines['bottom'].set_linewidth(4.5)
    ax.spines['bottom'].set_color("#D51E1E")
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_linewidth(4.5)
    ax.spines['left'].set_color("#D51E1E")
    ax.spines['left'].set_position('zero')


    ax.grid(axis='y', linestyle='-', linewidth=1.5, color='#E2E8F0', zorder=0)
    ax.grid(axis='x', linestyle='-', linewidth=1.5, color='#E2E8F0', zorder=0)
    ax.set_axisbelow(True)

    plt.tick_params('both', labelcolor="#D51E1E", labelsize=24)

    plt.savefig(filepath, transparent=True)
    plt.close(fig)

    return out_filename, False