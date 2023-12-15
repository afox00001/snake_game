from time import sleep
import numpy
import pygame
import sys

def number_of_duplicates_in_iterable(list_object: iter) -> int:
    """Returns the number of elements in an iterable: "list_object" that are the same"""
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


def display_message_on_screen(text: str, screen, screen_width, screen_height, text_color) -> None:
    """displays text on the screen"""
    large_text = pygame.font.Font('freesansbold.ttf', 115)
    text_surface, text_rectangle = text_objects(text, large_text, text_color)
    text_rectangle.center = ((screen_width / 2), (screen_height / 2))
    screen.blit(text_surface, text_rectangle)

    pygame.display.update()
    sleep(2)


class Game:
    def __init__(self) -> None:
        """NOTE: The text color must be in (R,G,B) (0-255, 0-255, 0-255) format, the player_color, background_color,
        and apple_color can either be a string or in the same (R,G,B) format as the text color is in
        """
        pygame.init()
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

        self.move_apple()

    def set_player_size(self, player_size: int) -> None:
        """Changes the size of the player, and the size of the grid and apple"""
        self.player_size = player_size
        self.player.player_size = player_size

    def move_apple(self) -> None:
        """Moves the apple to a random position on the screen"""

        number_of_squares_in_grid_height = self.screen_height // self.player_size
        number_of_squares_in_grid_width = self.screen_width // self.player_size

        percentage_of_screen_we_can_spawn_apple = 0.80

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

    def game_over(self) -> None:
        self.score = 0
        self.player.player_body_segments = []
        self.player.main_player = [(self.screen_width // self.player_size) // 2,
                                   (self.screen_height // self.player_size) // 2]
        display_message_on_screen("YOU DIED", self.screen, self.screen_width, self.screen_height, self.text_color)

    def update_grid(self) -> None:
        """Updates the grid, and draws out the game on the screen"""
        square_count_x_axis_pointer = 0
        for x in range(0, self.screen_width, self.player_size):
            square_count_y_axis_pointer = 0
            for y in range(0, self.screen_height, self.player_size):
                """Check if our current square we are rendering:
                 [square_count_x_axis_pointer, square_count_y_axis_pointer] is either in the array of body segments
                 or is equal to the players "head" (self.main_player)"""
                if [square_count_x_axis_pointer, square_count_y_axis_pointer] in self.player.player_body_segments or [
                        square_count_x_axis_pointer, square_count_y_axis_pointer] == self.player.main_player:
                    "Draw snake body"
                    pygame.draw.rect(self.screen, self.player_color,
                                     pygame.Rect(x, y, self.player_size, self.player_size))
                elif square_count_x_axis_pointer == self.apple_x and square_count_y_axis_pointer == self.apple_y:
                    "Draw the apple"
                    pygame.draw.rect(self.screen, self.apple_color,
                                     pygame.Rect(x, y, self.player_size, self.player_size))
                else:
                    "Draw the background"
                    pygame.draw.rect(self.screen, self.background_color,
                                     pygame.Rect(x, y, self.player_size, self.player_size))
                square_count_y_axis_pointer += 1
            square_count_x_axis_pointer += 1

        "Draw the score text"
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()
        sleep(0.03)

    def start_game(self) -> None:
        """Starts the game"""
        while not self.player.close_game:
            self.player.handel_player_movement()

            "Check if player has died, if so: game over"
            if self.check_if_player_died():
                self.game_over()

            "Check if player is touching the apple, if so, collect the apple"
            if self.player.main_player == [self.apple_x, self.apple_y]:
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

    def grow_player(self) -> None:
        """Grows the player. This is for when the player collects an apple"""
        self.player_body_segments.append([self.player_previous_position[0], self.player_previous_position[1]])

    def handel_player_movement(self) -> None:
        """Handles the player movement and user inputs"""

        """Handel user (player) input"""
        events = pygame.event.get()
        for event in events:
            # This allows the user to close the game
            if event.type == pygame.QUIT:
                self.close_game = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.vertical_movement = -1
                    self.horizontal_movement = 0
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.vertical_movement = 1
                    self.horizontal_movement = 0
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.horizontal_movement = -1
                    self.vertical_movement = 0
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.horizontal_movement = 1
                    self.vertical_movement = 0

        """Check if player is not moving"""
        if self.vertical_movement == 0 and self.horizontal_movement == 0:
            return  # We are done here. No movement is needed

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

        """Move the players body segments to the next segment in the "chain", and moves the segment next to the 
        player head to the player heads previous position."""
        if self.player_previous_position is None or len(self.player_body_segments) < 1:
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


if __name__ == "__main__":
    game = Game()
    game.set_player_size(20)
    game.start_game()
