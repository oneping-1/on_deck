from typing import Union

from on_deck.colors import Colors
from on_deck.fonts import Fonts
from on_deck.display_manager import DisplayManager

class Gamecast:
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.game: dict = None

        self._ddo = 4 # double digit offset

    def _print_team_names(self, game: dict):
        color = Colors.white

        self.display_manager.clear_section(129, 0, 200, 28)
        self.display_manager.draw_text(Fonts.ter_u16b, 129, 12, color, game['away']['name'])
        self.display_manager.draw_text(Fonts.ter_u16b, 129, 24, color, game['home']['name'])

    def _print_linescore(self, home: bool, runs: int, hits: int, errors: int, lob: int):
        color = Colors.white
        row_offset = 24 if home else 12

        run_column_offset = 80
        hit_column_offset = 100
        error_column_offset = 116
        lob_column_offset = 132

        run_column_offset -= self._ddo if runs >= 10 else 0
        hit_column_offset -= self._ddo if hits >= 10 else 0
        lob_column_offset -= self._ddo if lob >= 10 else 0

        if runs >= 10:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + run_column_offset,
                row_offset, Colors.yellow, f'{runs}')
        else:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + run_column_offset,
                row_offset, Colors.yellow, f'{runs}')

        if hits >= 10:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + hit_column_offset,
                row_offset, color, f'{hits}')
        else:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + hit_column_offset,
                row_offset, color, f'{hits}')

        self.display_manager.draw_text(Fonts.ter_u16b, 128 + error_column_offset,
            row_offset, color, f'{errors}')

        if lob >= 10:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + lob_column_offset,
                row_offset, color, f'{lob}')
        else:
            self.display_manager.draw_text(Fonts.ter_u16b, 128 + lob_column_offset,
                row_offset, color, f'{lob}')

    def _print_linescores(self, game: dict):
        self.display_manager.clear_section(200, 0, 275, 24)

        runs = game['away']['runs']
        hits = game['away']['hits']
        errors = game['away']['errors']
        lob = game['away']['left_on_base']
        self._print_linescore(False, runs, hits, errors, lob)

        runs = game['home']['runs']
        hits = game['home']['hits']
        errors = game['home']['errors']
        lob = game['home']['left_on_base']
        self._print_linescore(True, runs, hits, errors, lob)

    def _print_inning(self, game: dict):
        self.display_manager.clear_section(275, 0, 293, 24)

        column_offset = 128 + 152
        row_offset = 18
        arrow_size = 5

        inning = game['inning']
        inning_state = game['inning_state']

        color = Colors.white

        if inning >= 10:
            self.display_manager.draw_text(Fonts.ter_u16b, column_offset - self._ddo,
                row_offset, color, f'{inning}')
        else:
            self.display_manager.draw_text(Fonts.ter_u16b, column_offset,
                row_offset, color, f'{inning}')

        if inning_state == 'T':
            self.display_manager.draw_inning_arrow(column_offset+3, row_offset-12,
                arrow_size, True, color)
        elif inning_state == 'B':
            self.display_manager.draw_inning_arrow(column_offset+3, row_offset+1,
                arrow_size, False, color)

    def _print_bases(self, game: dict):
        self.display_manager.clear_section(293, 0, 328, 24)

        second_base_column_offset = 128 + 182
        second_base_row_offset = 8

        base_length = 6
        base_gap = 2
        base_offset = base_length + base_gap

        thickness = 2

        bases = [False, False, False]

        if game['runners'] & 1:
            bases[0] = True
        if game['runners'] & 2:
            bases[1] = True
        if game['runners'] & 4:
            bases[2] = True

        self.display_manager.draw_diamond(second_base_column_offset - base_offset,
            second_base_row_offset + base_offset, base_length, thickness, bases[2], Colors.white)
        self.display_manager.draw_diamond(second_base_column_offset,
            second_base_row_offset, base_length, thickness, bases[1], Colors.white)
        self.display_manager.draw_diamond(second_base_column_offset + base_offset,
            second_base_row_offset + base_offset, base_length, thickness, bases[0], Colors.white)

    def _print_count(self, game: dict):
        self.display_manager.clear_section(328, 0, 370, 24)

        circle_column_offset = 128 + 206
        ball_row_offset = 4
        strike_row_offset = 12
        out_row_offset = 20

        radius = 3
        gap = 1
        thickness = 1
        delta = 2*radius + gap + 1

        balls_int = game['count']['balls']
        balls = [False, False, False, False]
        if balls_int >= 1:
            balls[0] = True
        if balls_int >= 2:
            balls[1] = True
        if balls_int >= 3:
            balls[2] = True
        if balls_int >= 4:
            balls[3] = True

        self.display_manager.draw_circle(circle_column_offset + 0*delta,
            ball_row_offset, radius, thickness, balls[0], Colors.green)
        self.display_manager.draw_circle(circle_column_offset + 1*delta,
            ball_row_offset, radius, thickness, balls[1], Colors.green)
        self.display_manager.draw_circle(circle_column_offset + 2*delta,
            ball_row_offset, radius, thickness, balls[2], Colors.green)
        self.display_manager.draw_circle(circle_column_offset + 3*delta,
            ball_row_offset, radius, thickness, balls[3], Colors.green)


        strikes_int = game['count']['strikes']
        strikes = [False, False, False]
        if strikes_int >= 1:
            strikes[0] = True
        if strikes_int >= 2:
            strikes[1] = True
        if strikes_int >= 3:
            strikes[2] = True

        self.display_manager.draw_circle(circle_column_offset + 0*delta,
            strike_row_offset, radius, thickness, strikes[0], Colors.red)
        self.display_manager.draw_circle(circle_column_offset + 1*delta,
            strike_row_offset, radius, thickness, strikes[1], Colors.red)
        self.display_manager.draw_circle(circle_column_offset + 2*delta,
            strike_row_offset, radius, thickness, strikes[2], Colors.red)


        outs_int = game['count']['outs']
        outs = [False, False, False]
        if outs_int >= 1:
            outs[0] = True
        if outs_int >= 2:
            outs[1] = True
        if outs_int >= 3:
            outs[2] = True

        self.display_manager.draw_circle(circle_column_offset + 0*delta,
            out_row_offset, radius, thickness, outs[0], Colors.white)
        self.display_manager.draw_circle(circle_column_offset + 1*delta,
            out_row_offset, radius, thickness, outs[1], Colors.white)
        self.display_manager.draw_circle(circle_column_offset + 2*delta,
            out_row_offset, radius, thickness, outs[2], Colors.white)

    def _print_umpire(self, game: dict):
        self.display_manager.clear_section(129, 36, 240, 72)

        column_offset = 129
        row_offset = 48

        color = Colors.white

        num_missed = game['umpire']['num_missed']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'# Miss: {num_missed:2d}')

        row_offset += 12
        favor = game['umpire']['home_favor']
        abv = game['home']['abv']
        if favor < 0:
            abv = game['away']['abv']
            favor *= -1
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'FV: {favor:.2f} {abv}')

        row_offset += 12
        wpa = game['umpire']['home_wpa']
        abv = game['home']['abv']
        if wpa < 0:
            abv = game['away']['abv']
            wpa *= -1
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'WP: {wpa*100:.1f}% {abv}')

    def _print_run_expectancy(self, game: dict):
        self.display_manager.clear_section(129, 82, 240, 108)

        column_offset = 129
        row_offset = 96

        color = Colors.white

        re_avg = game['run_expectancy']['average_runs']
        re_ts = game['run_expectancy']['to_score']

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'AVG:{re_avg:5.2f}')
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset+12,
            color, f'1+:{re_ts*100:5.1f}%')

    def _print_win_probability(self, game: dict):
        self.display_manager.clear_section(129, 108, 240, 120)

        column_offset = 129
        row_offset = 120

        color = Colors.white

        wp_away = game['win_probability']['away']
        wp_home = game['win_probability']['home']

        if wp_away > wp_home:
            team = game['away']['abv']
            wp = wp_away
        else:
            team = game['home']['abv']
            wp = wp_home

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'WP:{wp*100:5.1f}% {team}')

    def _print_pitch_details(self, game: dict):
        self.display_manager.clear_section(129, 132, 240, 168)

        column_offset = 129
        row_offset = 144

        color = Colors.white

        pitch_type = game['pitch_details']['type']
        if pitch_type == 'Four-Seam Fastball':
            pitch_type = 'Four-Seam'
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{pitch_type}')

        pitch_speed = game['pitch_details']['speed']
        if pitch_speed is None:
            return
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{pitch_speed:.1f} MPH')

        row_offset += 12
        pitch_zone = game['pitch_details']['zone']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, 'Zone:')
        color = Colors.red
        if pitch_zone > 9:
            color = Colors.green
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset+48, row_offset,
            color, f'{pitch_zone:2d}')

    def _print_hit_details(self, game: dict):
        self.display_manager.clear_section(129, 180, 240, 216)

        column_offset = 129
        row_offset = 192

        color = Colors.white

        if game['hit_details']['distance'] is None:
            self.display_manager.clear_section(column_offset, row_offset,
                column_offset+128, row_offset+24)
            return

        distance = game['hit_details']['distance']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{distance:5.1f} ft')

        exit_velo = game['hit_details']['exit_velo']
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{exit_velo:5.1f} MPH')

        launch_angle = game['hit_details']['launch_angle']
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{launch_angle:5.1f}°')

    def print_game(self, new_data: Union[dict, None] = None, game: Union[dict, None] = None):
        print(new_data)
        print()
        # self.display_manager.clear_section(128, 0, 384, 256)

        away = new_data.get('away', None)
        home = new_data.get('home', None)
        if (away is not None) or (home is not None):
            self._print_team_names(game)
            self._print_linescores(game)

        inning = new_data.get('inning', None)
        inning_state = new_data.get('inning_state', None)
        if (inning is not None) or (inning_state is not None):
            self._print_inning(game)

        runners = new_data.get('runners', None)
        if (runners is not None):
            self._print_bases(game)

        count = new_data.get('count', None)
        if (count is not None):
            self._print_count(game)

        umpire = new_data.get('umpire', None)
        if (umpire is not None):
            self._print_umpire(game)

        re = new_data.get('run_expectancy', None)
        if (re is not None):
            self._print_run_expectancy(game)

        wp = new_data.get('win_probability', None)
        if (wp is not None):
            self._print_win_probability(game)

        pitch = new_data.get('pitch_details', None)
        if pitch is not None:
            self._print_pitch_details(game)

        hit = new_data.get('hit_details', None)
        if hit is not None:
            self._print_hit_details(game)

        self.display_manager.swap_frame()

if __name__ == '__main__':
    print('wrong module dummy')
