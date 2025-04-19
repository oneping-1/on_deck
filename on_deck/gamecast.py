"""
Gamecast module for displaying baseball game information on a screen.
This module is part of the On Deck project, which provides a real-time display
of baseball game statistics and information.
"""
from on_deck.colors import Colors
from on_deck.fonts import Fonts
from on_deck.display_manager import DisplayManager


class Gamecast:
    """
    A class to handle the gamecast display for a baseball game.
    """
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.game: dict = None

        self._ddo = 4 # double digit offset


    def _print_team_names(self, away: dict, home: dict):
        color = Colors.white

        # self.display_manager.clear_section(129, 0, 200, 28)
        self.display_manager.clear_section(129, 0, 200, 28)
        self.display_manager.draw_text(Fonts.ter_u16b, 129, 12, color, away['name'])
        self.display_manager.draw_text(Fonts.ter_u16b, 129, 24, color, home['name'])


    def _print_linescore(self, home: bool, runs: int, hits: int, errors: int, lob: int):
        color = Colors.white
        row_offset = 24 if home else 12

        run_column_offset = 80
        hit_column_offset = 100
        error_column_offset = 116
        lob_column_offset = 132

        if runs is None:
            runs = 0
        if hits is None:
            hits = 0
        if errors is None:
            errors = 0
        if lob is None:
            lob = 0

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


    def _print_linescores(self, away: dict, home: dict):
        self.display_manager.clear_section(200, 0, 275, 24)

        runs = away['runs']
        hits = away['hits']
        errors = away['errors']
        lob = away['left_on_base']
        self._print_linescore(False, runs, hits, errors, lob)

        runs = home['runs']
        hits = home['hits']
        errors = home['errors']
        lob = home['left_on_base']
        self._print_linescore(True, runs, hits, errors, lob)


    def _print_inning(self, inning: int, inning_state: str):
        self.display_manager.clear_section(275, 0, 293, 24)

        column_offset = 128 + 152
        row_offset = 18
        arrow_size = 5

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


    def _print_bases(self, runners: int):
        self.display_manager.clear_section(293, 0, 328, 24)

        second_base_column_offset = 128 + 182
        second_base_row_offset = 8

        base_length = 6
        base_gap = 2
        base_offset = base_length + base_gap

        thickness = 2

        bases = [False, False, False]

        if runners & 1:
            bases[0] = True
        if runners & 2:
            bases[1] = True
        if runners & 4:
            bases[2] = True

        self.display_manager.draw_diamond(second_base_column_offset - base_offset,
            second_base_row_offset + base_offset, base_length, thickness, bases[2], Colors.white)
        self.display_manager.draw_diamond(second_base_column_offset,
            second_base_row_offset, base_length, thickness, bases[1], Colors.white)
        self.display_manager.draw_diamond(second_base_column_offset + base_offset,
            second_base_row_offset + base_offset, base_length, thickness, bases[0], Colors.white)


    def _print_count(self, count: dict):
        self.display_manager.clear_section(328, 0, 370, 24)

        circle_column_offset = 128 + 206
        ball_row_offset = 4
        strike_row_offset = 12
        out_row_offset = 20

        radius = 3
        gap = 1
        thickness = 1
        delta = 2*radius + gap + 1

        balls_int = count.get('balls', None)
        if balls_int is not None:
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


        strikes_int = count.get('strikes', None)
        if strikes_int is not None:
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


        outs_int = count.get('outs', None)
        if outs_int is not None:
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


    def _print_umpire(self, umpire: dict, away: dict, home: dict, pitch_details: dict):
        self.display_manager.clear_section(129, 36, 240, 72)

        column_offset = 129
        row_offset = 48

        umpire_missed_call = pitch_details['umpire_missed_call']
        color = Colors.yellow if umpire_missed_call is True else Colors.white

        num_missed = umpire['num_missed']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'# Miss: {num_missed:2d}')

        row_offset += 12
        favor = umpire['home_favor']
        abv = home['abv']
        if favor < 0:
            abv = away['abv']
            favor *= -1
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'FV: {favor:.2f} {abv}')

        row_offset += 12
        wpa = umpire['home_wpa']
        abv = home['abv']
        if wpa < 0:
            abv = away['abv']
            wpa *= -1
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'WP: {wpa:.1%} {abv}')


    def _print_run_expectancy(self, run_expectancy: dict):
        self.display_manager.clear_section(129, 82, 240, 108)

        column_offset = 129
        row_offset = 96

        color = Colors.white

        re_avg = run_expectancy['average_runs']
        re_ts = run_expectancy['to_score']

        if (re_avg is None) or (re_ts is None):
            return

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'AVG:{re_avg:5.2f}')
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset+12,
            color, f'1+:{re_ts:5.1%}')


    def _print_win_probability(self, win_probability: dict, away: dict, home: dict):
        self.display_manager.clear_section(129, 108, 240, 120)

        column_offset = 129
        row_offset = 120

        color = Colors.white

        wp_away = win_probability['away']
        wp_home = win_probability['home']

        if (wp_away is None) or (wp_home is None):
            return

        if wp_away > wp_home:
            team = away['abv']
            wp = wp_away
        else:
            team = home['abv']
            wp = wp_home

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'WP:{wp:5.1%} {team}')


    def _print_pitch_details(self, pitch_details: dict):
        self.display_manager.clear_section(129, 132, 240+24, 180)

        column_offset = 129
        row_offset = 144

        color = Colors.white

        pitch_type = pitch_details['type']
        if pitch_type is None:
            return
        if pitch_type == 'Four-Seam Fastball':
            pitch_type = 'Four-Seam'

        pitch_colors = {
            'Four-Seam': Colors.red,
            'Sinker': Colors.pink,
            'Cutter': Colors.pink,
            'Curveball': Colors.blue,
            'Slider': Colors.light_blue,
            'Sweeper': Colors.light_blue,
            'Changeup': Colors.green,
            'Splitter': Colors.yellow,
        }
        pitch_color = pitch_colors.get(pitch_type, Colors.white)
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            pitch_color, f'{pitch_type}')

        pitch_speed = pitch_details['speed']
        if pitch_speed is None:
            return
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            pitch_color, f'{pitch_speed:.1f}')
        self.display_manager.draw_text(Fonts.ter_u12b, column_offset+38, row_offset,
            pitch_color, 'MPH')

        pitch_hand = pitch_details['pitch_hand']
        is_rhp = True if pitch_hand == 'R' else False
        break_horizontal = pitch_details['break_horizontal']
        break_direction = 'A' if (is_rhp ^ (break_horizontal < 0)) else 'G'
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset+64, row_offset,
            color, f'{abs(break_horizontal):5.1f}')
        self.display_manager.draw_text(Fonts.ter_u12b, column_offset+104, row_offset,
            color, break_direction)


        row_offset += 12
        pitch_zone = pitch_details['zone']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, 'Zone:')
        color = Colors.red
        if pitch_zone > 9:
            color = Colors.green
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset+40, row_offset,
            color, f'{pitch_zone:2d}')

        color = Colors.white
        break_vertical_induced = pitch_details['break_vertical_induced']
        break_direction = 'U' if break_vertical_induced > 0 else 'D'
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset+64, row_offset,
            color, f'{abs(break_vertical_induced):5.1f}')
        self.display_manager.draw_text(Fonts.ter_u12b, column_offset+104, row_offset,
            color, break_direction)


    def _print_hit_details(self, hit_details: dict):
        self.display_manager.clear_section(129, 180, 240, 216)

        column_offset = 129
        row_offset = 192

        color = Colors.white

        if hit_details['distance'] is None:
            self.display_manager.clear_section(column_offset, row_offset,
                column_offset+128, row_offset+24)
            return

        exit_velo = hit_details['exit_velo']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{exit_velo:5.1f} MPH')

        launch_angle = hit_details['launch_angle']
        xslg = f'{hit_details["xslg"]:.3f}'
        xslg = f' {xslg[1:]}' if xslg[0] == '0' else xslg
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{launch_angle:5.1f}°  {xslg}')

        distance = hit_details['distance']
        xba = f'{hit_details["xba"]:.3f}'
        xba = f' {xba[1:]}' if xba[0] == '0' else xba
        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            color, f'{distance:5.1f} ft{xba}')

        # row_offset += 12
        # self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
        #     color, f'{xba} {xslg}')


    def _print_batting_order(self, batting_order: dict):
        row_offset = 36
        column_offset = 240

        # self.display_manager.draw_box(240, 36, 386, 146, Colors.white)
        self.display_manager.clear_section(240, 36, 386, 146)

        at_bat_index = batting_order['at_bat_index']
        batting_order = batting_order['batting_order']

        if batting_order is None:
            return

        for i, batter in enumerate(batting_order):
            color = Colors.white
            if at_bat_index == i+1:
                color = Colors.yellow

            row_offset += 12
            name = batter['last_name']
            slg = batter['slg']
            position = batter['position']
            self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
                color, rf'{position:>2s} {name[:10]:10s}{slg:>5s}')


    def _print_pitcher(self, matchup: dict):
        row_offset = 168
        column_offset = 240

        # self.display_manager.draw_box(240, 156, 384, 204, Colors.white)
        self.display_manager.clear_section(240, 156, 384, 204)

        pitcher = matchup['pitcher']

        if (pitcher is None) or (pitcher['name'] is None):
            return

        pitcher_name = f' P {pitcher["name"][:10]:10s}{pitcher["era"]:>5s}'
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            Colors.white, pitcher_name)

        row_offset += 12
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            Colors.white, ' IP H R K BB  S/P')

        row_offset += 12
        pitch_count = f'{pitcher["strikes"]:2d}/{pitcher["pitches"]:<2d}'
        innings_pitched = pitcher['innings_pitched']
        hits = pitcher['hits_allowed']
        runs = pitcher['runs_allowed']
        strike_outs = pitcher['strike_outs']
        walks = pitcher['walks']
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset, row_offset,
            Colors.white, f'{innings_pitched}{hits:>2d}{runs:>2d} {strike_outs:<2d}{walks:>2d} {pitch_count}')


    def print_game(self, game: dict):
        """
        Print the game information to the screen.
        This function is called when the gamecast is updated.

        Args:
            game (dict): The game information to print.
                The game information is a dictionary with the following keys:
                - away: The away team information (dict)
                - home: The home team information (dict)
                - inning: The current inning (int)
                - inning_state: The current inning state (str)
                - runners: The runners on base (int)
                - count: The current count (dict)
                - umpire: The umpire information (dict)
                - run_expectancy: The run expectancy information (dict)
                - win_probability: The win probability information (dict)
                - pitch_details: The pitch details information (dict)
                - hit_details: The hit details information (dict)
                - batting_order: The batting order information (dict)
                - matchup: The matchup information (dict)
        """
        self._print_team_names(game['away'], game['home'])
        self._print_linescores(game['away'], game['home'])
        self._print_inning(game['inning'], game['inning_state'])
        self._print_bases(game['runners'])
        self._print_count(game['count'])
        self._print_umpire(game['umpire'], game['away'], game['home'], game['pitch_details'])
        self._print_run_expectancy(game['run_expectancy'])
        self._print_win_probability(game['win_probability'], game['away'], game['home'])
        self._print_pitch_details(game['pitch_details'])
        self._print_hit_details(game['hit_details'])
        self._print_batting_order(game['batting_order'])
        self._print_pitcher(game['matchup'])
        self.display_manager.swap_frame()


if __name__ == '__main__':
    print('wrong module dummy')
