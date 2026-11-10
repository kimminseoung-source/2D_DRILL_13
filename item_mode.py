from pico2d import *
import game_framework
import play_mode
import item_state
import game_world
from ball import Ball
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
        elif event.type == SDL_KEYDOWN:
            if getattr(event, 'repeat', False):
                continue
            choices_by_key = {
                SDLK_0: 0, SDLK_1: 1, SDLK_2: 2,
                SDLK_KP_0: 0, SDLK_KP_1: 1, SDLK_KP_2: 2,
            }
            if event.key in choices_by_key:
                item_state.select(choices_by_key[event.key])
                game_framework.pop_mode()
                return
            if event.key in (SDLK_ESCAPE, SDLK_i):
                game_framework.pop_mode()
                return


def update():
    # 이동 입력은 막고 대기·수면 상태와 기존 공의 이동은 계속 갱신한다.
    play_mode.boy.update()
    for layer in game_world.world:
        for obj in layer[:]:
            if isinstance(obj, Ball):
                obj.update()


def render():
    clear_canvas()
    play_mode.draw_scene()
    cx, cy = get_canvas_width() // 2, get_canvas_height() // 2
    panel.draw(cx, cy)
    choices.draw(cx, cy + 10)
    status.draw(cx, cy - 125)
    update_canvas()
