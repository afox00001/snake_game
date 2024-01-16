from time import sleep
import numpy
import pygame
import json


class KeyEvent:
    def __init__(self, key_event):
        self.key = key_event

    def is_up_key(self):
        return self.key == pygame.K_w or self.key == pygame.K_UP

    def is_down_key(self):
        return self.key == pygame.K_s or self.key == pygame.K_DOWN

    def is_left_key(self):
        return self.key == pygame.K_a or self.key == pygame.K_LEFT

    def is_right_key(self):
        return self.key == pygame.K_d or self.key == pygame.K_RIGHT


class HighScore:
    def __init__(self):
        self.high_score = 0
        self.high_score_file_path = "highscore.json"

    def does_high_score_file_exist(self):
        try:
            open(self.high_score_file_path, "r")
            return True
        except FileNotFoundError:
            with open(self.high_score_file_path, "w") as high_score_file:
                high_score_file.write("")
                high_score_json = {"High Score": 0}
                json.dump(high_score_json, high_score_file)
                return False

    def get_high_score(self):
        if self.does_high_score_file_exist():
            with open(self.high_score_file_path, "r") as high_score_file:
                return json.load(high_score_file)["High Score"]
        return 0

    def set_high_score(self, high_score):
        self.high_score = high_score
        self.does_high_score_file_exist()
        with open(self.high_score_file_path, "w") as high_score_file:
            new_high_score = {"High Score": high_score}
            json.dump(new_high_score, high_score_file)


def number_of_duplicates_in_iterable(list_object: iter) -> int:
    """Returns the number of duplicate elements in an iterable: "list_object" """
    list_object.sort()
    duplicates = 0
    duplicates_high = 0
    previous = None
    for i in list_object:
        if i == previous:
            duplicates += 1
        else:
            if duplicates > duplicates_high:
                duplicates_high = duplicates
            duplicates = 0
        previous = i
    return duplicates_high


def text_objects(text: str, font, text_color) -> (any, any):
    """Generates a text object from Pygame, with the given text, font and text color as specified in the arguments"""
    text_surface = font.render(text, True, text_color)
    return text_surface, text_surface.get_rect()


def display_message_on_screen(text: str, screen, screen_width, screen_height, text_color, display_length=2) -> None:
    """displays text on the screen"""
    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surface, text_rectangle = text_objects(text, large_text, text_color)
    text_rectangle.center = ((screen_width / 2), (screen_height / 2))
    screen.blit(text_surface, text_rectangle)

    pygame.display.update()
    sleep(display_length)


class Game:
    def __init__(self) -> None:
        """NOTE: The text color must be in (R,G,B) (0-255, 0-255, 0-255) format, the player_color, background_color,
        and apple_color can either be a string or in the same (R,G,B) format as the text color is in
        """
        pygame.init()

        self.high_score = HighScore()
        self.player_size = 15
        self.screen = pygame.display.set_mode((1280, 720))
        self.screen_width, self.screen_height = self.screen.get_size()
        self.player = Player(self.screen, self.screen_width, self.screen_height, self.player_size)
        self.clock = pygame.time.Clock()
        self.score = 0
        self.apple_x = 0
        self.apple_y = 0

        self.player_color = "red"
        self.background_color = "black"
        self.apple_color = "green"

        self.text_color = (255, 255, 255)

    def set_player_size(self, player_size: int) -> None:
        """Changes the size of the player, and the size of the grid and apple"""
        self.player_size = player_size
        self.player.player_size = player_size

    def move_apple(self) -> None:
        """Moves the apple to a random position on the screen"""

        number_of_squares_in_grid_height = self.screen_height // self.player_size
        number_of_squares_in_grid_width = self.screen_width // self.player_size

        percentage_of_screen_we_can_spawn_apple = 0.70

        """
        we are subtracting 1 from the percentage_of_screen_we_can_spawn_apple to get a 'border' that the random number
         gen will not be able to generate x or y coordinates for. this is to create a buffer, so the apple will not
          spawn on the edge of the screen.
        """
        self.apple_x = numpy.random.randint(int(
            number_of_squares_in_grid_width * (1 - percentage_of_screen_we_can_spawn_apple)),
            number_of_squares_in_grid_width - int(
                number_of_squares_in_grid_width * (1 - percentage_of_screen_we_can_spawn_apple)))
        self.apple_y = numpy.random.randint(int(
            number_of_squares_in_grid_height * (1 - percentage_of_screen_we_can_spawn_apple)),
            number_of_squares_in_grid_height - int(
                number_of_squares_in_grid_height * (1 - percentage_of_screen_we_can_spawn_apple)))

    def collect_apple(self) -> None:
        """Increases the score, and grows the player"""
        self.score += 1
        self.player.grow_player()
        self.player.grow_player()
        self.move_apple()

    def check_if_player_died(self) -> bool:
        """Checks if the player has died. Returns True if the player has died,
         Returns False if the player has not died"""
        number_of_player_segments_with_same_position_as_players_head = 0
        for body_segment in self.player.player_body_segments:
            if body_segment == self.player.main_player:
                number_of_player_segments_with_same_position_as_players_head += 1
        if number_of_player_segments_with_same_position_as_players_head >= 2:
            return True
        return False

    def reset_game(self) -> None:
        self.score = 0
        self.player.player_body_segments = []
        self.player.main_player = [(self.screen_width // self.player_size) // 2,
                                   (self.screen_height // self.player_size) // 2]

    def is_score_new_high_score(self) -> bool:
        return self.score >= self.high_score.get_high_score()

    def display_new_high_score_message(self) -> None:
        display_message_on_screen(f"NEW HIGHSCORE: {self.high_score.get_high_score()}", self.screen,
                                  self.screen_width, self.screen_height, self.text_color)

    def display_you_died_screen(self) -> None:
        display_message_on_screen("YOU DIED", self.screen, self.screen_width, self.screen_height, self.text_color)

    def game_over(self) -> None:
        if self.is_score_new_high_score():
            self.high_score.set_high_score(self.score)
            self.display_new_high_score_message()
        else:
            self.display_you_died_screen()
        self.reset_game()

    def is_square_in_player_body(self, relative_x: int, relative_y: int):
        return [relative_x, relative_y] in self.player.player_body_segments or [
            relative_x, relative_y] == self.player.main_player

    def draw_square_in_player_body(self, relative_x: int, relative_y: int) -> None:
        pygame.draw.rect(self.screen, self.player_color,
                         pygame.Rect(relative_x, relative_y, self.player_size, self.player_size))

    def is_square_in_apple(self, relative_x: int, relative_y: int) -> bool:
        return relative_x == self.apple_x and relative_y == self.apple_y

    def draw_apple(self, relative_x: int, relative_y: int) -> None:
        pygame.draw.rect(self.screen, self.apple_color,
                         pygame.Rect(relative_x, relative_y, self.player_size, self.player_size))

    def draw_background_square(self, relative_x: int, relative_y: int) -> None:
        pygame.draw.rect(self.screen, self.background_color,
                         pygame.Rect(relative_x, relative_y, self.player_size, self.player_size))

    def draw_score_text(self) -> None:
        font = pygame.font.Font(None, 36)
        score_text = font.render(
            f'High Score: {self.high_score.get_high_score()}'
            f'{" " * (self.screen_width // self.player_size)}Score: {self.score}',
            True,
            (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def did_player_beat_game(self) -> bool:
        return self.player.get_player_length() >= self.screen_width * self.screen_height

    def player_won_screen(self) -> None:
        display_message_on_screen("YOU WON!!!", self.screen, self.screen_width, self.screen_height, self.text_color)
        sleep(1)
        pygame.display.flip()
        if self.is_score_new_high_score():
            self.high_score.set_high_score(self.score)
            self.display_new_high_score_message()
        else:
            self.display_you_died_screen()
        self.reset_game()

    def update_grid(self) -> None:
        """Updates the grid, and draws out the game on the screen"""
        square_count_x_axis_pointer = 0
        for x in range(0, self.screen_width, self.player_size):
            square_count_y_axis_pointer = 0
            for y in range(0, self.screen_height, self.player_size):
                if self.is_square_in_player_body(square_count_x_axis_pointer, square_count_y_axis_pointer):
                    self.draw_square_in_player_body(x, y)
                elif self.is_square_in_apple(square_count_x_axis_pointer, square_count_y_axis_pointer):
                    self.draw_apple(x, y)
                else:
                    self.draw_background_square(x, y)
                square_count_y_axis_pointer += 1
            square_count_x_axis_pointer += 1

        if self.score > self.high_score.get_high_score():
            self.high_score.set_high_score(self.score)
        self.draw_score_text()
        pygame.display.flip()
        sleep(0.03)

    def is_player_touching_apple(self) -> bool:
        return self.player.main_player == [self.apple_x, self.apple_y]

    def start_game(self) -> None:
        """Starts the game"""
        self.move_apple()
        while not self.player.close_game:
            self.player.handel_player_movement()

            if self.check_if_player_died():
                self.game_over()

            if self.did_player_beat_game():
                self.player_won_screen()

            if self.is_player_touching_apple():
                self.collect_apple()
            self.update_grid()


class Player:
    def __init__(self, screen, screen_width, screen_height, player_size):
        self.player_size = player_size
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.main_player = [(self.screen_width // self.player_size) // 2, (self.screen_height // self.player_size) // 2]
        self.player_body_segments = []
        self.player_previous_position = None
        self.vertical_movement = 0
        self.horizontal_movement = 0

        self.close_game = False

    def get_player_length(self) -> int:
        return len(self.player_body_segments)

    def grow_player(self) -> None:
        """Grows the player. This is for when the player collects an apple"""
        self.player_body_segments.append([self.player_previous_position[0], self.player_previous_position[1]])

    def move_up(self) -> None:
        self.vertical_movement = -1
        self.horizontal_movement = 0

    def move_down(self) -> None:
        self.vertical_movement = 1
        self.horizontal_movement = 0

    def move_left(self) -> None:
        self.horizontal_movement = -1
        self.vertical_movement = 0

    def move_right(self) -> None:
        self.horizontal_movement = 1
        self.vertical_movement = 0

    def update_player_movement_values(self) -> None:
        """Handel user (player) input"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.close_game = True
            elif event.type == pygame.KEYDOWN:
                key = KeyEvent(event.key)
                if key.is_up_key():
                    self.move_up()
                elif key.is_down_key():
                    self.move_down()
                elif key.is_left_key():
                    self.move_left()
                elif key.is_right_key():
                    self.move_right()

    def stop_player_from_going_past_screen(self) -> None:
        """Make Sure The Player Is Not At The Edge Of The Screen. If Player Is At Edge Of Screen (or past the edge),
                "Packman" The Player To The Opposite Edge Of The Screen"""
        number_of_squares_in_grid_height = self.screen_height // self.player_size
        number_of_squares_in_grid_width = self.screen_width // self.player_size

        is_player_past_right_edge = self.main_player[0] > number_of_squares_in_grid_width
        is_player_past_left_edge = self.main_player[0] < 0

        is_player_past_top_edge = self.main_player[1] > number_of_squares_in_grid_height
        is_player_past_bottom_edge = self.main_player[1] < 0

        left_edge_of_screen_coordinate_for_player = [0, self.main_player[1]]
        right_edge_of_screen_coordinate_for_player = [number_of_squares_in_grid_width, self.main_player[1]]
        top_edge_of_screen_coordinate_for_player = [self.main_player[0], 0]
        bottom_edge_of_screen_coordinate_for_player = [self.main_player[0], number_of_squares_in_grid_height]

        if is_player_past_right_edge:
            self.main_player = left_edge_of_screen_coordinate_for_player
        elif is_player_past_left_edge:
            self.main_player = right_edge_of_screen_coordinate_for_player
        if is_player_past_top_edge:
            self.main_player = top_edge_of_screen_coordinate_for_player
        elif is_player_past_bottom_edge:
            self.main_player = bottom_edge_of_screen_coordinate_for_player

    def update_player_position(self) -> None:
        """Move Player"""
        if self.horizontal_movement != 0:
            if self.horizontal_movement > 0:
                self.main_player[0] += 1
            else:
                self.main_player[0] -= 1
        elif self.vertical_movement != 0:
            if self.vertical_movement > 0:
                self.main_player[1] += 1
            else:
                self.main_player[1] -= 1

    def is_player_not_moving(self) -> bool:
        return self.vertical_movement == 0 and self.horizontal_movement == 0

    def has_player_grown_yet(self) -> bool:
        return self.player_previous_position is None or len(self.player_body_segments) < 1

    def update_players_body_segment_positions(self) -> None:
        """Move the players body segments to the next segment in the "chain", and moves the segment next to the
        player head to the player heads previous position."""
        if self.has_player_grown_yet():
            pass
        elif len(self.player_previous_position) == 1:
            self.player_body_segments[0] = [self.player_previous_position[0] + self.horizontal_movement,
                                            self.player_previous_position[1] + self.vertical_movement]
        else:
            len_of_player_body_segments_minus_one = len(self.player_body_segments) - 1
            for index, _ in enumerate(self.player_body_segments):
                the_player_body_segment_we_need = len_of_player_body_segments_minus_one - index

                self.player_body_segments[the_player_body_segment_we_need] = self.player_body_segments[
                    the_player_body_segment_we_need - 1]

            updated_segment_location = [self.player_previous_position[0] + self.horizontal_movement,
                                        self.player_previous_position[1] + self.vertical_movement]
            self.player_body_segments[0] = updated_segment_location

        """I am going to use a tuple here so I cannot accidentally change this values structure"""
        self.player_previous_position = self.main_player[0], self.main_player[1]

    def handel_player_movement(self) -> None:
        """Handles the player movement and user inputs"""
        self.update_player_movement_values()
        self.update_player_position()
        self.stop_player_from_going_past_screen()

        if self.is_player_not_moving():
            return None  # We are done here. No movement is needed

        self.update_players_body_segment_positions()


if __name__ == "__main__":
    game = Game()
    game.set_player_size(20)
    game.start_game()
