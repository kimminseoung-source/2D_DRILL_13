from resources import asset
from pathlib import Path
from pico2d import *
import game_framework
import game_world
import item_state
from boy import Boy
from grass import Grass

boy = None
paused = False
pause_started_at = 0.0
pause_image = None
hud_images = []


def init():
    global boy, paused, pause_started_at, pause_image, hud_images

    paused = False
    pause_started_at = 0.0
    pause_image = load_image(str(Path(__file__).parent / 'pause_message.png'))
    hud_images = [load_image(asset(f'play_hud_{i}.png')) for i in range(3)]
    game_world.clear()
    item_state.reset()
    boy = Boy()
    game_world.add_oject(boy)
    grass = Grass()
    game_world.add_oject(grass, 0)


def toggle_pause():
    global paused, pause_started_at

    if not paused:
        pause_started_at = get_time()
        paused = True
    else:
        # Do not count paused time toward the boy's sleep timer.
        boy.idle_started_at += get_time() - pause_started_at
        paused = False


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            if not getattr(event, 'repeat', False):
                import item_mode
                game_framework.push_mode(item_mode)
                return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', False):
                toggle_pause()
        elif not paused:
            boy.handle_event(event)
        elif event.type == SDL_KEYUP:
            # Clear released keys without changing the frozen pose.
            boy.pressed_keys.discard(event.key)


def update():
    if not paused:
        # Reconcile direction keys released while paused.
        if boy.state == 'RUN' and not boy.pressed_keys:
            boy.dir = 0
            boy.stop_run()
        elif boy.state == 'RUN':
            boy.dir = (int(SDLK_RIGHT in boy.pressed_keys) -
                       int(SDLK_LEFT in boy.pressed_keys))
        game_world.update()


def draw_scene():
    game_world.render()
    hud_images[item_state.selected.value].draw(get_canvas_width() // 2, get_canvas_height() - 28)


def render():
    clear_canvas()
    draw_scene()
    if paused:
        pause_image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    update_canvas()


def finish():
    global boy, paused, pause_image, hud_images

    game_world.clear()
    boy = None
    paused = False
    pause_image = None
    hud_images = []


item_opened_at = 0.0


def pause():
    global item_opened_at
    item_opened_at = get_time()
    boy.pressed_keys.clear()


def resume():
    boy.idle_started_at += get_time() - item_opened_at
    boy.pressed_keys.clear()
    boy.dir = 0
    if boy.state == 'RUN':
        boy.stop_run()
