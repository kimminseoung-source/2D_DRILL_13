import runpy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pico2d as p
import logo_mode
import title_mode
import play_mode
import item_mode
import item_state
import game_framework
import game_world


class StartupFlowTests(unittest.TestCase):
    def test_main_logo_title_play_item_pause_and_exit(self):
        counts = {'logo': 0, 'title': 0, 'play': 0, 'item': 0}
        def counted(name, render):
            def wrapped():
                render()
                counts[name] += 1
            return wrapped
        actions = iter([p.SDLK_i, p.SDLK_SPACE, p.SDLK_p, p.SDLK_p, p.SDLK_ESCAPE])
        def key(value):
            return [SimpleNamespace(type=p.SDL_KEYDOWN, key=value, repeat=False)]
        with patch.object(logo_mode, 'get_time', side_effect=[0.0, 0.0, 2.1, 2.1]), \
             patch.object(logo_mode, 'get_events', return_value=[]), \
             patch.object(title_mode, 'get_events', side_effect=lambda: key(p.SDLK_RETURN)), \
             patch.object(play_mode, 'get_events', side_effect=lambda: key(next(actions))), \
             patch.object(item_mode, 'get_events', side_effect=lambda: key(p.SDLK_2)), \
             patch.object(logo_mode, 'render', counted('logo', logo_mode.render)), \
             patch.object(title_mode, 'render', counted('title', title_mode.render)), \
             patch.object(play_mode, 'render', counted('play', play_mode.render)), \
             patch.object(item_mode, 'render', counted('item', item_mode.render)):
            runpy.run_path(str(ROOT / 'main.py'), run_name='__main__')
        self.assertTrue(all(counts.values()), counts)
        self.assertEqual(item_state.selected.value, 2)
        self.assertFalse(game_framework.running)
        self.assertEqual(game_framework.stack, [])
        self.assertTrue(all(not layer for layer in game_world.world))


if __name__ == '__main__':
    unittest.main()
