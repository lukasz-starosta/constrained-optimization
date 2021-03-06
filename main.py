import tkinter as tk
import numpy as np
from matplotlib import cm, pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy.optimize import LinearConstraint

from utils.plot.marker import mark_point
from utils.eval_math_fn import eval_math_fn_at
from hooke_jeeves import hooke_jeeves
from scipy import optimize

max_size = 50


def calculate():
    # get values from input
    fun = fn.get()
    initial_approx = eval(initial_approximation.get())
    init_step = float(initial_step.get())
    eps_step = float(epsilon_step.get())
    eps_abs = float(epsilon_abs.get())
    iter_c = int(iteration_count.get())
    penalty_coeff = float(penalty_coeff_input.get())

    # Clear the figure
    fig.clear()

    # calculate plot points
    x_values = np.arange(-max_size, max_size, 1)
    y_values = np.arange(-max_size, max_size, 1)
    X, Y = np.meshgrid(x_values, y_values)
    Z = eval_math_fn_at(fun, (X, Y))

    # 3d visualization
    # ax = fig.gca(projection='3d')
    # ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.RdBu, antialiased=False)
    # ax.zaxis.set_major_locator(LinearLocator(10))
    # ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    # 2d contour visualization
    ax = fig.gca()
    CS = ax.contour(X, Y, Z)
    ax.clabel(CS, inline=True)

    fun += f' - {penalty_coeff} * log(9 - x**2 - y**2)' if switch_variable.get() == 'circle' else \
        f' - {penalty_coeff} * log(5 - x) - log(5 + x) - log (5 - y) - log (5 + y)'

    f = lambda point: eval_math_fn_at(fun, point)
    point, value = hooke_jeeves(fun=f, u=initial_approx, h=init_step, eps_step=eps_step, eps_abs=eps_abs,
                                max_iterations=iter_c)

    print(f'Wynik: punkt: {point}, wartość: {value}')

    cb = lambda x: print(f'Scipy: punkt: {x}')
    scipy_result = optimize.minimize(f, initial_approx, method='SLSQP', callback=cb,
                                     options={'maxiter': iter_c, 'disp': True})
    if scipy_result.success:
        print(
            f'Wynik scipy.optimize.minimize: punkt: {scipy_result.x}, wartość: {scipy_result.fun}, ilość iteracji: {scipy_result.nit}')
    else:
        print(f'Wynik scipy.optimize.minimize: nie znaleziono minimum')

    fig.canvas.mpl_connect('button_press_event', handle_click)

    mark_point(ax, point)
    canvas.draw()


# GUI SETUP

# the main Tkinter window
master = tk.Tk()

# setting the title
master.title('Hooke-Jeeves Optimization')

# dimensions of the main window
master.geometry('800x800')

# labels
fn_input_label = tk.Label(master, text='f(x,y) = ')
initial_approximation_label = tk.Label(master, text='Początkowe minimum: [x, y]')
initial_step_label = tk.Label(master, text='Początkowa długość kroku')
epsilon_step_label = tk.Label(master, text='Minimalna długość kroku')
epsilon_abs_label = tk.Label(master, text='Dokładność')
iteration_count_label = tk.Label(master, text='Maksymalna ilość iteracji')
penalty_coeff_label = tk.Label(master, text='Współczynnik wielkości kary')

# entry list
fn = tk.Entry(master)
fn.insert(index=tk.END, string='x')

initial_approximation = tk.Entry(master)
initial_approximation.insert(index=tk.END, string='[0, 0]')

initial_step = tk.Entry(master)
initial_step.insert(index=tk.END, string='1')

epsilon_step = tk.Entry(master)
epsilon_step.insert(index=tk.END, string='0.1')

epsilon_abs = tk.Entry(master)
epsilon_abs.insert(index=tk.END, string='0.1')

iteration_count = tk.Entry(master)
iteration_count.insert(index=tk.END, string='10')

penalty_coeff_input = tk.Entry(master)
penalty_coeff_input.insert(index=tk.END, string='0.1')

# place labels and entry in main window
fn_input_label.pack()
fn.pack()

initial_approximation_label.pack()
initial_approximation.pack()

initial_step_label.pack()
initial_step.pack()

epsilon_step_label.pack()
epsilon_step.pack()

epsilon_abs_label.pack()
epsilon_abs.pack()

iteration_count_label.pack()
iteration_count.pack()

penalty_coeff_label.pack()
penalty_coeff_input.pack()

switch_frame = tk.Frame(master)
switch_frame.pack(pady=10)

switch_variable = tk.StringVar(value="square")
square_button = tk.Radiobutton(switch_frame, text="Ograniczenie kwadratowe", variable=switch_variable,
                               indicatoron=False, value="square", width=30)
circle_button = tk.Radiobutton(switch_frame, text="Ograniczenie okrągłe", variable=switch_variable,
                               indicatoron=False, value="circle", width=30)

square_button.pack(side="left")
circle_button.pack(side="left")

# method choice buttons
buttons = tk.Frame(master)
tk.Button(buttons, command=calculate, height=2, width=20, text='Znajdź minimum').pack()
buttons.pack(pady=10)

# PLOT SETUP

# the figure that will contain the plot
fig = Figure(figsize=(5, 4), dpi=100)

# 3d plot
# plot = fig.add_subplot(111, projection='3d')
# 2d contour plot
plot = fig.add_subplot(111)

# creating the Tkinter canvas containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig, master)
canvas.draw()

# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas, master)
fxy = tk.StringVar()


def handle_click(event):
    fxy.set(
        f'f({round(event.xdata, 3)},{round(event.ydata, 3)}) = {round(eval_math_fn_at(fn.get(), [event.xdata, event.ydata]), 3)}')


fxy_label = tk.Label(toolbar, textvariable=fxy)
fxy_label.pack(side="right")
toolbar.update()

# placing the toolbar on the Tkinter window
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# run the gui
master.mainloop()
