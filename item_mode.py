from pico2d import *
import game_framework
import play_mode


def init():
    pass


def finish():
    pass


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
    play_mode.render()
