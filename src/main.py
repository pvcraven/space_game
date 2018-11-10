import arcade
import os
import math
import random
import pymunk
from pymunk import Vec2d

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

MOVEMENT_SPEED = 5
ANGLE_SPEED = 15

PLAYER_MOVE_FORCE = 1500

class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 2
        self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, filename, width, height, x, y, mass, space):

        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = pymunk.Vec2d(x, y)
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = 0.3
        self.body = body
        space.add(body, shape)
        super().__init__(shape, filename)

        self.width = width
        self.height = height

class PlayerSprite(arcade.Sprite):
    def __init__(self, filename, width, height, x, y, mass, space):

        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = pymunk.Vec2d(x, y)
        shape = [pymunk.Segment(body, (-14, 14), (-14, -14), 2),
                 pymunk.Segment(body, (-14, -14), (14, -14), 2),
                 pymunk.Segment(body, (14, -14), (14, 14), 2)
                 ]
        # print("Player:", shape.get_vertices())
        # shape.friction = 0.3
        space.add(shape)
        space.add(body)
        self.body = body
        super().__init__(filename)

        self.width = width
        self.height = height


class MothershipSprite(arcade.Sprite):
    def __init__(self, filename, width, height, x, y, mass, space):

        moment = pymunk.moment_for_box(mass, (width, height))
        body = space.static_body
        body.position = pymunk.Vec2d(x, y)
        shape = [pymunk.Segment(body, (-128, -32), (-128, 32), 1),
                 pymunk.Segment(body, (-128, 32), (-98, 32), 1),
                 pymunk.Segment(body, (-98, 32), (-98, 0), 1),
                 pymunk.Segment(body, (-98, 0), (-58, 0), 1),
                 pymunk.Segment(body, (-58, 0), (-58, 32), 1),
                 pymunk.Segment(body, (-58, 32), (128, 32), 1),
                 pymunk.Segment(body, (128, 32), (128, -32), 1),
                 pymunk.Segment(body, (128, -32), (-128, -32), 1),
                 ]
        # print("Player:", shape.get_vertices())
        # shape.friction = 0.3
        space.add(shape)
        # space.add(body)
        self.body = body
        super().__init__(filename)

        self.width = width
        self.height = height

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)

        self.forward_engines = False
        self.reverse_engines = False
        self.rotate_left = False
        self.rotate_right = False
        self.slide_left = False
        self.slide_right = False
        self.stabilize = False

        # Variables that will hold sprite lists
        self.player_list = None
        self.asteroid_list = None
        self.physics_sprite_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.physics_sprite_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        # self.player_sprite = Player("images/ship_01.png", SPRITE_SCALING)
        # self.player_sprite.center_x = SCREEN_WIDTH / 2
        # self.player_sprite.center_y = SCREEN_HEIGHT / 2
        # self.player_list.append(self.player_sprite)


        size = 32
        cx = SCREEN_WIDTH / 2
        cy = SCREEN_HEIGHT / 2
        mass = 12
        self.player_sprite = PlayerSprite("images/ship_02.png",
                                       x=cx, y=cy,
                                       mass=mass,
                                       space=self.space,
                                       width=size, height=size)
        self.player_sprite.turn_rate = 1
        self.player_list.append(self.player_sprite)
        self.physics_sprite_list.append(self.player_sprite)


        cx = SCREEN_WIDTH / 2
        cy = 32
        mass = 12
        sprite = MothershipSprite("images/mothership.png",
                                       x=cx, y=cy,
                                       mass=mass,
                                       space=self.space,
                                       width=256, height=64)
        self.player_list.append(sprite)
        self.physics_sprite_list.append(sprite)



        for asteroid_index in range(30):
            rock_type = random.randrange(2)
            cx = random.randrange(SCREEN_WIDTH)
            cy = random.randrange(SCREEN_HEIGHT)

            if rock_type == 0:
                # asteroid = arcade.Sprite("images/rock_01.png", SPRITE_SCALING)
                size = 32
                mass = 24
                asteroid = BoxSprite("images/rock_01.png",
                                     x=cx, y=cy,
                                     mass=mass,
                                     space=self.space,
                                     width=size, height=size)
                self.physics_sprite_list.append(asteroid)
            else:
                size = 16
                mass = 6
                asteroid = BoxSprite("images/rock_small_01.png",
                                     x=cx, y=cy,
                                     mass=mass,
                                     space=self.space,
                                     width=size, height=size)
                self.physics_sprite_list.append(asteroid)

            self.asteroid_list.append(asteroid)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.player_list.draw()
        self.asteroid_list.draw()

    def update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        force = [0, 0]

        if self.forward_engines and not self.reverse_engines:
            force[1] = PLAYER_MOVE_FORCE
        if self.reverse_engines and not self.forward_engines:
            force[1] = -PLAYER_MOVE_FORCE
        if self.slide_left and not self.slide_right:
            force[0] = -PLAYER_MOVE_FORCE
        if self.slide_right and not self.slide_left:
            force[0] = PLAYER_MOVE_FORCE
        if self.stabilize:
            vx = self.player_sprite.body.velocity[0]
            vy = self.player_sprite.body.velocity[1]
            a = self.player_sprite.body.angle
            sx = math.sin(a) * vy + math.cos(a) * vx
            sy = math.sin(a) * -vx + math.cos(a) * vy

            print(f"1 {vx:5.2f} {vy:5.2f} {a:5.2f}")
            print(f"2 {sx:5.2f} {sy:5.2f} {a:5.2f}")
            force = [0, 0]
            if sy > 0:
                force[1] = -PLAYER_MOVE_FORCE
            elif sy < 0:
                force[1] = PLAYER_MOVE_FORCE
            if sx > 0:
                force[0] = -PLAYER_MOVE_FORCE
            elif sx < 0:
                force[0] = PLAYER_MOVE_FORCE

        self.player_sprite.body.apply_force_at_local_point(force, (0, 0))
        self.space.step(1 / 60.0)

        # Move sprites to where physics objects are
        for sprite in self.physics_sprite_list:
            sprite.center_x = sprite.body.position.x
            sprite.center_y = sprite.body.position.y
            sprite.angle = math.degrees(sprite.body.angle)

        # rocks_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_list)
        #
        # for rock in rocks_hit_list:
        #     rock.remove_from_sprite_lists()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.forward_engines = True
        elif key == arcade.key.DOWN:
            self.reverse_engines = True
        elif key == arcade.key.S:
            self.stabilize = True
        elif key == arcade.key.A:
            self.slide_left = True
        elif key == arcade.key.D:
            self.slide_right = True

        elif key == arcade.key.LEFT:
            self.player_sprite.body.angular_velocity = self.player_sprite.turn_rate
        elif key == arcade.key.RIGHT:
            self.player_sprite.body.angular_velocity = -self.player_sprite.turn_rate

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.forward_engines = False
        elif key == arcade.key.DOWN:
            self.reverse_engines = False
        elif key == arcade.key.A:
            self.slide_left = False
        elif key == arcade.key.S:
            self.stabilize = False
        elif key == arcade.key.D:
            self.slide_right = False

        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.body.angular_velocity = 0.0


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()