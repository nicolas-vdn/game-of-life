import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
from matplotlib.widgets import Slider
from matplotlib.colors import ListedColormap
from matplotlib.backend_bases import MouseButton

# Variables du tableau
N = 250
p = 0.3
vals = [0, 1, 2]

grid = np.random.choice(vals, N*N, p=[p-0.1, 1-p, 0.1]).reshape(N, N)

cmap = ListedColormap(["w", "k", "b"])

fig, ax = plt.subplots()

mat = ax.matshow(grid, cmap=cmap)

grid[np.where(grid == 2)] = 0

mat.set_data(grid)

# Variable d'actions

draw = False

pause = False

stable = False

last_key_pressed = None

# Variables paramètres

interval = 1
count_interval = 0

image_save = "None"

min_birth_time = 0

image_displayed = 1

# Variables de stockage des informations

total_alive = len(grid[np.where(grid == 0)])

total_dead = len(grid[np.where(grid == 1)])

last_deaths = len(grid[np.where(grid == 1)])

last_births = len(grid[np.where(grid == 0)])

# Variables d'affichage des informations

figtext = plt.figtext(0.5, 0.01, "", wrap=True,
                      horizontalalignment='center', fontsize=12)

datatext = plt.figtext(0.88, 0.75, "", wrap=True,
                       horizontalalignment='center', fontsize=12)

infostext = plt.figtext(0.88, 0.25, "", wrap=True,
                        horizontalalignment='center', fontsize=12)

axamp = fig.add_axes([0.1, 0.25, 0.0225, 0.63])

birth_slider = Slider(
    ax=axamp,
    label="Itérations avant naissance",
    valmin=0,
    valmax=20,
    valinit=0,
    orientation="vertical"
)


def change_slider_val(val):   # Utilisation du slider, changement du nombre d'itérations
    global min_birth_time
    if (val == round(birth_slider.val)):
        return
    rounded_val = round(val)
    min_birth_time = rounded_val
    birth_slider.set_val(rounded_val)


birth_slider.on_changed(change_slider_val)


def update(frame):  # Actualisation de l'image
    global interval
    global count_interval
    global image_displayed
    global grid
    global mat
    global draw
    global last_key_pressed

    if (draw):
        mat.set_data(grid)
        ani.pause()
        print("pause")
        return

    if (last_key_pressed == None):
        last_key_pressed = "None"

    datatext.set_text(
        f"Alive cells : {total_alive}\nDead cells : {total_dead}\n\nBirths on last iteration : {last_births}\nDeaths on last iteration : {last_deaths}")
    figtext.set_text(
        f"Image n°{image_displayed}. Last key pressed : {last_key_pressed}. Last saved frame : {image_save}.")

    infostext.set_text(
        f"Interval : {interval*100} ms.\nStability reached ? : {stable}")

    if (count_interval < interval):
        count_interval += 1
        return

    image_displayed += 1
    count_interval = 0

    grid = np.array(check_dead_and_birth(grid))

    ax.set_prop_cycle(color=['red', 'green', 'blue'])

    mat.set_data(grid)

    return [mat]


ani = animation.FuncAnimation(fig, update, interval=10, save_count=1)

def check_dead_and_birth(grid):   # Actualisation de l'état 
    global image_displayed
    global min_birth_time
    global total_alive
    global total_dead
    global last_deaths
    global last_births
    global stable

    new_grid = []

    last_deaths = 0

    last_births = 0

    for i in range(len(grid)):
        temp_array = []

        if (i != 0):
            i_not_0 = True
        else:
            i_not_0 = False
        if (i != len(grid)-1):
            i_not_end = True
        else:
            i_not_end = False

        for j in range(len(grid)):
            if (j != 0):
                j_not_0 = True
            else:
                j_not_0 = False
            if (j != len(grid)-1):
                j_not_end = True
            else:
                j_not_end = False
            dead_count = 0

            if (i_not_0 and
                (grid[i-1][j] == 0) or
                (j_not_0 and grid[i-1][j-1] == 0) or
                (j_not_end and grid[i-1][j+1] == 0)):
                        dead_count += 1

            if (i_not_end and
                ((grid[i+1][j] == 0) or
                (j_not_0 and grid[i+1][j-1] == 0) or
                (j_not_end and (grid[i+1][j+1] == 0 or grid[i][j-1] == 0)))):
                    dead_count += 1

            if (j_not_end and grid[i][j+1] == 0):
                    dead_count += 1

            cell_value = grid[i][j]

            if (cell_value >= 2):
                cell_value += 1
            else:
                if (dead_count < 2 or dead_count > 3) and cell_value < 2:
                    #print("cellvalue 1")
                    if (cell_value == 0):
                        last_deaths += 1
                    cell_value = 1
                elif (dead_count == 3):
                    #print("cellvalue 2")
                    if (cell_value == 1):
                        cell_value = 2
            if (cell_value >= 2+min_birth_time):
                cell_value = 0
                last_births += 1
            temp_array.append(cell_value)

        total_dead += last_deaths

        total_alive += last_births

        if (last_births == last_deaths == 0):
            stable = True
        else:
            stable = False

        new_grid.append(temp_array)

    return new_grid

def on_press(event):
    global last_key_pressed
    global ani
    global pause
    global draw
    global image_save
    global interval

    last_key_pressed = event.key
    match last_key_pressed:
        case "+":
            add_interval()
        case "-":
            remove_interval()
        case "z":
            if (pause):
                pause = False
                if (draw == False):
                    ani.resume()
            else:
                ani.pause()
                pause = True
        case "r":
            interval = 5
        case "b":
            if (birth_slider.val != 20):
                change_slider_val(birth_slider.val+1)
        case "n":
            if (birth_slider.val != 0):
                change_slider_val(birth_slider.val-1)
        case "v":
            save_json()
        case "j":
            load_json()
    return event


def add_interval():
    global interval
    interval += 1


def remove_interval():
    global interval
    interval -= 1
    if (interval < 1):
        interval = 1
    else:
        return interval-1


def save_json():
    global image_save
    image_save = image_displayed
    dictionnary = {
        'grid': grid.tolist(),
        'images_affichee': image_displayed,
        'last_births': last_births,
        'last_deaths': last_deaths,
        'interval': interval,
        'total_alive': total_alive,
        'total_dead': total_dead,
        "tours_naissances": birth_slider.val
    }
    json_data = json.dumps(dictionnary)

    with open("grid.json", "w") as json_file:
        json_file.write(json_data)


def load_json():
    global grid
    global image_displayed
    global last_births
    global last_deaths
    global interval
    global total_alive
    global total_dead

    with open('grid.json') as json_file:
        game_data = json.load(json_file)
    grid = np.array(game_data["grid"])
    image_displayed = game_data["images_affichee"]
    last_births = game_data["last_births"]
    last_deaths = game_data["last_deaths"]
    interval = game_data["interval"]
    total_alive = game_data["total_alive"]
    total_dead = game_data["total_dead"]
    birth_slider.val = game_data["tours_naissances"]

    mat.set_data(grid)


def on_move(event):
    global grid
    global total_alive

    if event.inaxes:
        grid[round(event.ydata)][round(event.xdata)] = 0
        total_alive += 1
        if (draw):
            print("play")
            ani.resume()

def on_click(event):
    global id_deplacement
    global draw

    if event.button is MouseButton.LEFT:
        ani.pause()
        draw = True
        id_deplacement = fig.canvas.mpl_connect('motion_notify_event', on_move)


def on_release(event):
    global id_deplacement
    global draw
    global pause

    if event.button is MouseButton.LEFT:
        fig.canvas.mpl_disconnect(id_deplacement)
        draw = False
        print(draw, pause)
        if pause == False:
            ani.resume()
        else:
            ani.pause()


fig.canvas.mpl_connect('key_press_event', on_press)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_release_event', on_release)

plt.show()