from pico2d import *
import game_framework
import play_mode
import item_state
from resources import asset

panel = None
choices = None
status = None


def init():
    global panel, choices, status
    panel = load_image(asset('item_panel.png'))
    choices = load_image(asset('item_select.png'))
    status = load_image(asset(f'item_status_{item_state.selected.value}.png'))


def finish():
    global panel, choices, status
    panel = choices = status = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key in (SDLK_ESCAPE, SDLK_i):
            game_framework.pop_mode()
            return


def update():
    pass


def render():
    clear_canvas()
    play_mode.draw_scene()
    cx, cy = get_canvas_width() // 2, get_canvas_height() // 2
    panel.draw(cx, cy)
    choices.draw(cx, cy + 10)
    status.draw(cx, cy - 125)
    update_canvas()
