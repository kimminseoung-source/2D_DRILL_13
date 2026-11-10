from pico2d import get_canvas_width, load_image
from resources import asset
from item_state import Item
import game_world


class Ball:
    images = {}

    def __init__(self, x, y, velocity, item=Item.SMALL):
        self.item = Item(item)
        if self.item == Item.NONE:
            raise ValueError('NONE does not create a ball')
        self.size = 21 if self.item == Item.SMALL else 41
        if self.item not in Ball.images:
            Ball.images[self.item] = load_image(asset(f'ball{self.size}x{self.size}.png'))
        self.image = Ball.images[self.item]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y, self.size, self.size)
