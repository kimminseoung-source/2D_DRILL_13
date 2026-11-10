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

    def test_selection_stops_walking_but_updates_idle_and_balls(self):
        send(play_mode, p.SDLK_RIGHT)
        send(play_mode, p.SDLK_SPACE)
        boy = play_mode.boy
        ball = game_world.world[1][-1]
        before = (boy.x, boy.frame, ball.x)
        send(play_mode, p.SDLK_i)
        for _ in range(10):
            framework.stack[-1].update()
        self.assertEqual(before[0], boy.x)
        self.assertEqual(boy.state, 'IDLE')
        self.assertEqual(boy.frame, 10 % 8)
        self.assertEqual(ball.x, before[2] + 10 * ball.velocity)
        item_mode.render()
        send(item_mode, p.SDLK_2)
        self.assertIs(play_mode.boy, boy)
        self.assertIn(ball, game_world.world[1])
        self.assertEqual(item_state.selected, item_state.Item.LARGE)

    def test_item_time_advances_sleep_timer_as_reference_video(self):
        play_mode.boy.idle_started_at = 5.0
        send(play_mode, p.SDLK_i)
        with patch('boy.get_time', return_value=10.1):
            item_mode.update()
        self.assertEqual(play_mode.boy.state, 'SLEEP')
        send(item_mode, p.SDLK_ESCAPE)
        self.assertEqual(play_mode.boy.idle_started_at, 5.0)
        self.assertEqual(play_mode.boy.state, 'SLEEP')

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


    def test_pause_blocks_item_mode_and_freezes_world(self):
        send(play_mode, p.SDLK_RIGHT)
        send(play_mode, p.SDLK_p)
        before = (play_mode.boy.x, play_mode.boy.frame)
        send(play_mode, p.SDLK_i)
        self.assertEqual(framework.stack, [play_mode])
        play_mode.update()
        self.assertEqual(before, (play_mode.boy.x, play_mode.boy.frame))
        send(play_mode, p.SDLK_p, repeat=True)
        self.assertTrue(play_mode.paused)
        send(play_mode, p.SDLK_RIGHT, p.SDL_KEYUP)
        send(play_mode, p.SDLK_p)
        self.assertFalse(play_mode.paused)
        x = play_mode.boy.x
        play_mode.update()
        self.assertEqual(play_mode.boy.x, x)

    def test_item_mode_ignores_pause_and_held_i(self):
        send(play_mode, p.SDLK_i)
        send(item_mode, p.SDLK_p)
        send(item_mode, p.SDLK_i, repeat=True)
        self.assertEqual(framework.stack, [play_mode, item_mode])
        self.assertFalse(play_mode.paused)
        send(item_mode, p.SDLK_i)
        self.assertEqual(framework.stack, [play_mode])

    def test_escape_exits_while_paused(self):
        send(play_mode, p.SDLK_p)
        send(play_mode, p.SDLK_ESCAPE)
        self.assertFalse(framework.running)



    def test_all_choices_control_firing_and_keep_existing_balls(self):
        for key, value in ((p.SDLK_1, 1), (p.SDLK_2, 2), (p.SDLK_0, 0)):
            send(play_mode, p.SDLK_i)
            send(item_mode, key)
            before = list(game_world.world[1])
            send(play_mode, p.SDLK_SPACE)
            if value == 0:
                self.assertEqual(before, game_world.world[1])
            else:
                ball = game_world.world[1][-1]
                self.assertEqual(ball.size, 21 if value == 1 else 41)
                self.assertEqual(game_world.world[1][:-1], before)
        self.assertEqual(len(game_world.world[1]), 3)

    def test_keypad_and_cancel_preserve_selection(self):
        for key, value in ((p.SDLK_KP_0, 0), (p.SDLK_KP_1, 1), (p.SDLK_KP_2, 2)):
            send(play_mode, p.SDLK_i)
            send(item_mode, key)
            self.assertEqual(item_state.selected.value, value)
        send(play_mode, p.SDLK_i)
        send(item_mode, p.SDLK_ESCAPE)
        self.assertEqual(item_state.selected.value, 2)

    def test_facing_and_offscreen_cleanup(self):
        from ball import Ball
        item_state.select(2)
        play_mode.boy.face_dir = -1
        play_mode.boy.fire_ball()
        ball = game_world.world[1][-1]
        self.assertLess(ball.velocity, 0)
        ball.x = 0
        ball.update()
        self.assertNotIn(ball, game_world.world[1])

    def test_window_close_from_item_mode(self):
        send(play_mode, p.SDLK_i)
        send(item_mode, 0, p.SDL_QUIT)
        self.assertFalse(framework.running)

    def test_window_close_from_play_mode(self):
        send(play_mode, 0, p.SDL_QUIT)
        self.assertFalse(framework.running)



    def test_item_mode_moves_both_ball_sizes_in_their_directions(self):
        from ball import Ball
        small = Ball(300, 100, 10, item_state.Item.SMALL)
        large = Ball(500, 100, -10, item_state.Item.LARGE)
        game_world.add_oject(small)
        game_world.add_oject(large)
        send(play_mode, p.SDLK_i)
        for _ in range(5):
            item_mode.update()
        self.assertEqual((small.x, large.x), (350, 450))
        send(item_mode, p.SDLK_0)
        play_mode.update()
        self.assertEqual((small.x, large.x), (360, 440))

    def test_item_mode_removes_balls_crossing_either_edge(self):
        from ball import Ball
        left = Ball(0, 100, -10)
        right = Ball(p.get_canvas_width(), 100, 10, item_state.Item.LARGE)
        survivor = Ball(400, 100, 10)
        for ball in (left, right, survivor):
            game_world.add_oject(ball)
        send(play_mode, p.SDLK_i)
        item_mode.update()
        self.assertNotIn(left, game_world.world[1])
        self.assertNotIn(right, game_world.world[1])
        self.assertIn(survivor, game_world.world[1])
        self.assertEqual(survivor.x, 410)



    def test_selecting_item_does_not_wake_sleeping_boy(self):
        play_mode.boy.fall_asleep()
        send(play_mode, p.SDLK_i)
        item_mode.update()
        send(item_mode, p.SDLK_2)
        self.assertEqual(play_mode.boy.state, 'SLEEP')
        before = len(game_world.world[1])
        send(play_mode, p.SDLK_SPACE)
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertEqual(len(game_world.world[1]), before)


if __name__ == '__main__':
    unittest.main()
