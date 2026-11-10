import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pico2d as p
import game_framework as framework
import game_world
import item_state
import item_mode
import play_mode


def send(mode, key, event_type=p.SDL_KEYDOWN, repeat=False):
    event = SimpleNamespace(type=event_type, key=key, repeat=repeat)
    with patch.object(mode, 'get_events', return_value=[event]):
        mode.handle_events()


class ModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p.open_canvas()

    @classmethod
    def tearDownClass(cls):
        p.close_canvas()

    def setUp(self):
        play_mode.init()
        framework.stack = [play_mode]
        framework.running = True

    def tearDown(self):
        while framework.stack:
            framework.stack.pop().finish()
        framework.running = False

    def test_selection_freezes_existing_boy_and_ball(self):
        send(play_mode, p.SDLK_RIGHT)
        send(play_mode, p.SDLK_SPACE)
        boy = play_mode.boy
        ball = game_world.world[1][-1]
        before = (boy.x, boy.frame, ball.x)
        send(play_mode, p.SDLK_i)
        for _ in range(10):
            framework.stack[-1].update()
        self.assertEqual(before, (boy.x, boy.frame, ball.x))
        item_mode.render()
        send(item_mode, p.SDLK_2)
        self.assertIs(play_mode.boy, boy)
        self.assertIn(ball, game_world.world[1])
        self.assertEqual(item_state.selected, item_state.Item.LARGE)

    def test_item_time_does_not_advance_sleep_timer(self):
        play_mode.boy.idle_started_at = 5.0
        with patch.object(play_mode, 'get_time', return_value=10.0):
            send(play_mode, p.SDLK_i)
        with patch.object(play_mode, 'get_time', return_value=30.0):
            send(item_mode, p.SDLK_ESCAPE)
        self.assertEqual(play_mode.boy.idle_started_at, 25.0)

    def test_resume_does_not_keep_moving_from_old_key(self):
        send(play_mode, p.SDLK_RIGHT)
        send(play_mode, p.SDLK_i)
        send(item_mode, p.SDLK_RIGHT, p.SDL_KEYUP)
        send(item_mode, p.SDLK_1)
        before = play_mode.boy.x
        play_mode.update()
        self.assertEqual(play_mode.boy.x, before)
        self.assertEqual(play_mode.boy.state, 'IDLE')
        send(play_mode, p.SDLK_LEFT)
        play_mode.update()
        self.assertLess(play_mode.boy.x, before)


if __name__ == '__main__':
    unittest.main()
