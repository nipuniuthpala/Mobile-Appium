import json
import logging
import time

from collections import defaultdict

from itertools import combinations
import csv
import os

from alttester import By, altdriver

from pages.base_page import BasePage

from copy import deepcopy

from pages.game_play_page import GamePage
from pages.start_page import StartPage


class GameExpertPage(BasePage):
    def __init__(self, altdriver, appium_driver):
        BasePage.__init__(self, altdriver, appium_driver)
        self.start_page = StartPage(altdriver, appium_driver)

    LOG_FILE = "challenge_scores.log"
    _csv_initialized = False

    def convert_queens_grid_vertical(self, queens_grid, size_x, size_y):
        """
            Converts a vertical-indexed 1D queensGrid to a 2D array and collects 'q' coordinates.

            Returns:
                grid: 2D list of 'q' and 'e'
                queen_positions: List of (row, col) where value == 2
        """
        grid = [['e' for _ in range(size_x)] for _ in range(size_y)]
        queen_positions = []

        for col in range(size_x):
            for row in range(size_y):
                idx = col * size_y + row  # vertical indexing
                # print(f"Checking idx={idx}, val={queens_grid[idx]}")
                if queens_grid[idx] == 2:
                    # print(f"✅ Queen at: ({row}, {col})")
                    grid[row][col] = 'q'
                    queen_positions.append((row, col))
                    # print("=== DEBUG QUEEN GRID CONVERSION ===")
                    # print(f"queens_grid: {queens_grid}")
                    # print(f"Expected total cells: {size_x * size_y}, Actual: {len(queens_grid)}")
                    if len(queens_grid) != size_x * size_y:
                        print("❌ Grid size mismatch!")

        return grid, queen_positions

    def convert_known_queens_grid_vertical(self, queens_grid, size_x, size_y):
        """
            Converts a vertical-indexed 1D queensGrid to a 2D array and collects 'q' coordinates.

            Returns:
                grid: 2D list of 'q' and 'e'
                queen_positions: List of (row, col) where value == 2
        """
        grid = [['e' for _ in range(size_x)] for _ in range(size_y)]
        queen_positions = []

        for col in range(size_x):
            for row in range(size_y):
                idx = col * size_y + row  # vertical indexing
                # print(f"Checking idx={idx}, val={queens_grid[idx]}")
                if queens_grid[idx] == 1:
                    # print(f"✅ Queen at: ({row}, {col})")
                    grid[row][col] = 'q'
                    queen_positions.append((row, col))
                    # print("=== DEBUG QUEEN GRID CONVERSION ===")
                    # print(f"queens_grid: {queens_grid}")
                    # print(f"Expected total cells: {size_x * size_y}, Actual: {len(queens_grid)}")
                    if len(queens_grid) != size_x * size_y:
                        print("❌ Grid size mismatch!")

        return grid, queen_positions

    def get_colors_grids(self, grid_colours, size_x, size_y):
        """
        Groups [row, col] positions by color ID using vertical indexing.

        Returns:
            Dict[str, List[List[int]]]
        """
        color_map = {}

        for col in range(size_x):
            for row in range(size_y):
                idx = col * size_y + row  # vertical indexing
                color = str(grid_colours[idx])

                if color not in color_map:
                    color_map[color] = []

                color_map[color].append([row, col])
                # print(f"colormap:{color_map}")
        return color_map

    @staticmethod
    def get_num_queens_from_grid_colours(grid_colours: str) -> int:
        unique_colors = set(c for c in grid_colours if c != '0')
        return len(unique_colors)

    def grid_color(self, gridColours, size_x, size_y):
        """
            Converts a vertical-indexed 1D queensGrid to a 2D array and collects 'q' coordinates.

            Returns:
                grid: 2D list of 'q' and 'e'
                queen_positions: List of (row, col) where value == 2
        """
        queen_positions = [['0' for _ in range(size_x)] for _ in range(size_y)]

        for col in range(size_x):
            for row in range(size_y):
                idx = col * size_y + row  # vertical indexing

                queen_positions[row][col] = str(gridColours[idx])

        return queen_positions

    def apply_rule_1_and_click(self, current_grid, color_map, queen_colors, queens):
        for queen in queens:
            q_row, q_col = queen
            queen_color = queen_colors[q_row][q_col]
            current_grid = self.apply_rule_1_and_clicks(current_grid, color_map, queen_color)
        return current_grid

    def apply_rule_1_and_clicks(self, current_grid, color_map, color):
        """
        Applies Rule 1 and clicks on affected cells using Selenium.

        - Marks 'x' for empty cells sharing color with a queen.
        - Clicks on 'Paint ✕ Marks' button and each 'x' cell.

        Args:
            driver: Selenium WebDriver
            current_grid: 2D list of ['q', 'e', ...]
            color_map: dict of color_id -> list of [row, col]
        """
        updated_grid = deepcopy(current_grid)
        sizeX = len(current_grid[0])
        sizeY = len(current_grid)
        if color is None:
            # No queen to work with — handle accordingly or skip
            return updated_grid  # or some default

        color_locations = color_map[color]  #
        # Infer grid width
        # color_locations = color_map[color]
        has_queen = False
        new_grid_loc = [['0' for _ in range(sizeX)] for _ in range(sizeY)]
        for location in color_locations:
            r = location[0]
            c = location[1]

            if not has_queen:
                # Check if this color group contains a queen
                has_queen = current_grid[r][c] == 'q'

        for location in color_locations:
            r = location[0]
            c = location[1]

            if has_queen:
                if current_grid[r][c] == 'e':
                    updated_grid[r][c] = 'x'
                    new_grid_loc[r][c] = 'x'

        # print(f"after rule1:{updated_grid}")
        # Click "Paint ✕ Marks" button
        # driver.find_element(By.XPATH, "//*[contains(text(),'Paint ✕ Marks') and @id='markModeBtn']").click()

        # Click all cells that are marked 'x'
        for r in range(len(new_grid_loc)):
            for c in range(len(new_grid_loc[0])):
                if new_grid_loc[r][c] == 'x':
                    vertical_idx = c * sizeY + r
                    self.sleep()
                    partial_name = f"Grid-{vertical_idx}-"

                    element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                    element.click()
                    print(f"🖱️rule 1 Selenium clicked at horizontal_idx={vertical_idx}")

        return updated_grid

    def apply_rule_2_and_click(self, current_grid, queens):
        for queen in queens:
            current_grid = self.apply_rule_2_and_clicks(current_grid, queen)
        return current_grid

    def apply_rule_2_and_clicks(self, current_grid, queen):
        """
        Applies Rule 2: Marks and clicks empty spaces adjacent to any queen ('q').

        Args:
            driver: Selenium WebDriver
            current_grid: 2D list of the grid (from Rule 1), containing 'q', 'e', 'x'
            queen: tuple (row, col) representing the queen's position

        Returns:
            updated_grid: Modified grid after marking 'x' based on adjacency to queens
        """
        if queen is None:
            return current_grid

        rows = len(current_grid)
        cols = len(current_grid[0])  # sizeX derived from input grid
        updated_grid = deepcopy(current_grid)
        new_grid_loc = [['0' for _ in range(cols)] for _ in range(rows)]

        # Directions: 8 neighbors
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        cells_to_click = []

        for r in range(rows):
            for c in range(cols):
                if r == queen[0] and c == queen[1]:
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and updated_grid[nr][nc] == 'e':
                            updated_grid[nr][nc] = 'x'
                            new_grid_loc[nr][nc] = 'x'

                            # Compute AltTester vertical index
                            vertical_idx = nc * rows + nr  # column-first order
                            cells_to_click.append(vertical_idx)

        # ✅ Click adjacent cells using AltTester by partial name
        for vertical_idx in cells_to_click:
            self.sleep()
            partial_name = f"Grid-{vertical_idx}-"  # color part is dynamic
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.click()
            print(f"🖱️Rule 2 AltTester clicked at vertical_idx={vertical_idx} (name starts with {partial_name})")

        return updated_grid

    def apply_rule_3_and_click(self, current_grid, queens):
        for queen in queens:
            current_grid = self.apply_rule_3_and_clicks(current_grid)
        return current_grid

    def apply_rule_3_and_clicks(self, updated_grid):
        """
        Applies Rule 3:
        - Marks 'r' for empty cells in same row or column as any queen.
        - Clicks all 'r' cells using AltTester (partial name match).

        Args:
            driver: Selenium WebDriver (not used now for clicks)
            updated_grid: 2D list from Rule 2 with ['q', 'e', 'x', ...]

        Returns:
            new_grid: updated 2D list with 'r' marks and clicks performed
        """
        new_grid = deepcopy(updated_grid)
        rows = len(new_grid)
        cols = len(new_grid[0])

        # Find all rows and columns that contain queens
        queen_rows = set()
        queen_cols = set()
        for r in range(rows):
            for c in range(cols):
                if new_grid[r][c] == 'q':
                    queen_rows.add(r)
                    queen_cols.add(c)

        # Mark 'r' in empty cells in queen rows and columns
        cells_to_click = []
        for r in range(rows):
            for c in range(cols):
                if new_grid[r][c] == 'e' and (r in queen_rows or c in queen_cols):
                    new_grid[r][c] = 'r'
                    # ✅ Use vertical mapping: column-first order
                    vertical_idx = c * rows + r
                    cells_to_click.append(vertical_idx)

        # ✅ Click all cells marked 'r' using AltTester
        for vertical_idx in cells_to_click:
            self.sleep()
            partial_name = f"Grid-{vertical_idx}-"  # color part is dynamic
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.click()
            print(f"🖱️Rule 3 AltTester clicked at vertical_idx={vertical_idx} (name starts with {partial_name})")

        return new_grid

    def apply_rule_4_and_click(self, updated_grid, color_map, queens_grid):
        new_grid = deepcopy(updated_grid)
        queens_to_click = []
        loc_queen = None

        rows, cols = len(new_grid), len(new_grid[0])

        for color, positions in color_map.items():
            # Skip if this color already has a queen
            if any(new_grid[r][c] == 'q' for r, c in positions):
                continue

            # Candidate = only empty cells in this color group
            candidates = [(r, c) for r, c in positions if new_grid[r][c] == 'e']

            if len(candidates) == 1:
                r, c = candidates[0]
                dom_idx = c * rows + r

                loc_queen = (r, c)

                # Verify against queens_grid
                if str(queens_grid[dom_idx]) in ('1', '2'):
                    new_grid[r][c] = 'q'
                    queens_to_click.append(dom_idx)
                    print(f"✅ Rule 4: Color {color} queen confirmed at ({r},{c}), idx={dom_idx}")
                else:
                    # Not the true queen → revert
                    new_grid[r][c] = 'x'
                    loc_queen = None
                    print(f"❌ Rule 4: Candidate ({r},{c}), idx={dom_idx} rejected (not queen in queens_grid)")

        # ✅ Click queen cells using AltTester
        for idx in queens_to_click:
            try:
                partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                if element:
                    self.sleep()
                    element.click()
                    element.click()
                    print(f"🖱️Rule 4 AltTester clicked at vertical_idx={idx} (partial name: '{partial_name}')")
                else:
                    print(f"⚠️ Element not found for vertical_idx={idx}")
            except Exception as e:
                print(f"❌ Failed to click for vertical_idx={idx}: {e}")

        return new_grid, loc_queen

    '''
    def apply_rule_4_and_click(self, updated_grid, color_map):
        """
        Applies Rule 4:
        - For each color group, if only one cell can be queen (empty 'e'), mark it as 'q'.
        - Click those queen cells using AltTester (vertical index mapping).
        - If after applying Rule 4, there are still 'e' cells left, click the Clear button.

        Args:
            updated_grid: 2D list from Rule 3 with ['q', 'e', 'r', 'x', ...]
            color_map: dict of color_id -> list of (row, col)

        Returns:
            new_grid: updated 2D list with newly assigned queens
            loc_queen: (row, col) of last queen placed or None
        """
        new_grid = deepcopy(updated_grid)
        queens_to_click = []
        loc_queen = None
        rows = len(new_grid)
        cols = len(new_grid[0])

        for color, positions in color_map.items():
            # Skip if this color already has a queen
            if any(new_grid[r][c] == 'q' for r, c in positions):
                continue

            # Candidate cells for a queen in this color group
            candidates = [(r, c) for r, c in positions if new_grid[r][c] not in ('q', 'x', 'r')]

            if len(candidates) == 1:
                r, c = candidates[0]
                new_grid[r][c] = 'q'
                loc_queen = (r, c)

                # ✅ Vertical index mapping: column-first order
                vertical_idx = c * rows + r
                queens_to_click.append(vertical_idx)
                break  # Only place one queen per call

        # ✅ Click queen cells using AltTester
        for vertical_idx in queens_to_click:
            try:
                partial_name = f"Grid-{vertical_idx}-"
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                if element:
                    self.sleep()
                    element.click()
                    element.click()
                    print(f"🖱️ Rule 4 clicked at vertical_idx={vertical_idx} (partial name: '{partial_name}')")
                else:
                    print(f"⚠️ Element not found for vertical_idx={vertical_idx}")
            except Exception as e:
                print(f"❌ Failed to click for vertical_idx={vertical_idx}: {e}")

        # ✅ Check if there are any empty cells ('e') left
        empty_cells_exist = any('e' in row for row in new_grid)

        if empty_cells_exist:
            try:
                print("✅ Empty cells still exist. Clicking Clear button...")
                self.start_page.click_btn_clear()
            except Exception as e:
                print(f"❌ Failed to click Clear button: {e}")
        else:
            print("✅ No empty cells left. Skipping Clear button.")

        return new_grid, loc_queen
    '''

    def apply_rule_5_and_click(self, updated_grid, color_grid):
        updated_grid = deepcopy(updated_grid)
        rows = len(updated_grid)
        cols = len(updated_grid[0]) if rows > 0 else 0

        # Determine if we can apply to both rows and columns
        total_queens = sum(len(v) for v in color_grid.values())
        apply_on_rows = total_queens == rows

        queens_to_click = set()
        queen_positions = []

        def get_data_idx(r, c):
            return c * rows + r

        def check_line(is_row):
            line_count = rows if is_row else cols
            limit = cols if is_row else rows

            for idx in range(line_count):
                color_empty_map = {}
                color_queen_map = {}

                all_other_cells_blocked = True  # Flag to ensure all other cells are 'x' or 'e'

                for i in range(limit):
                    r, c = (idx, i) if is_row else (i, idx)
                    cell = updated_grid[r][c]

                    if cell != 'x' and cell != 'e' and cell != 'q':
                        all_other_cells_blocked = False

                    # Map cell to color
                    for color, positions in color_grid.items():
                        if (r, c) in positions:
                            if cell == 'e':
                                color_empty_map.setdefault(color, []).append((r, c))
                            elif cell == 'q':
                                color_queen_map[color] = True
                            break

                if not all_other_cells_blocked:
                    continue  # Skip this line if there are still non-blocked, non-empty, non-queen cells

                for color, empty_cells in color_empty_map.items():
                    if len(empty_cells) == 1 and not color_queen_map.get(color, False):
                        r, c = empty_cells[0]
                        print(
                            f"👑 Rule 5: One cell of color {color} left in {'row' if is_row else 'column'} {idx}, all others blocked. Placing queen at ({r}, {c})")
                        updated_grid[r][c] = 'q'
                        queens_to_click.add(get_data_idx(r, c))
                        queen_positions.append((r, c))

        # Apply rule on rows if allowed
        if apply_on_rows:
            check_line(is_row=True)

        # Always apply on columns
        check_line(is_row=False)

        if queens_to_click:
            try:
                # driver.find_element(By.XPATH, "//*[contains(text(),'Paint 👑 Queens') and @id='queenModeBtn']").click()
                for idx in sorted(queens_to_click):
                    self.sleep()
                    partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                    element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                    element.tap()
                    element.tap()

            except Exception as e:
                print(f"❌ Error while clicking queens in Rule 5: {e}")

        return updated_grid, queen_positions

    def build_color_matrix(color_grid_dict, rows, cols):
        color_matrix = [[-1 for _ in range(cols)] for _ in range(rows)]  # Fill with dummy color -1
        for color_str, coords in color_grid_dict.items():
            color = int(color_str)
            for r, c in coords:
                color_matrix[r][c] = color
        return color_matrix

    def apply_rule_6_and_click(self, updated_grid, color_grid, num_queens):
        updated_grid = deepcopy(updated_grid)
        rows = len(updated_grid)
        cols = len(updated_grid[0]) if rows > 0 else 0

        # 1. Identify which colors already have queens
        placed_colors = {color for color, positions in color_grid.items()
                         if any(updated_grid[r][c] == 'q' for r, c in positions)}

        # 2. Count empty cells per color
        empty_cells_per_color = {}
        position_to_color = {}
        for r in range(rows):
            for c in range(cols):
                if updated_grid[r][c] == 'e':
                    for color, positions in color_grid.items():
                        if (r, c) in positions:
                            empty_cells_per_color.setdefault(color, []).append((r, c))
                            position_to_color[(r, c)] = color
                            break

        changed = False

        # 3. Check for rows/columns with a single remaining color and no queen
        for r in range(rows):
            empty_positions_in_row = [(c, position_to_color.get((r, c))) for c in range(cols) if
                                      updated_grid[r][c] == 'e' and (r, c) in position_to_color]

            # Check if only one color is present in this row's empty cells
            colors_in_row = {color for _, color in empty_positions_in_row}
            if len(colors_in_row) == 1:
                single_color = next(iter(colors_in_row))
                # The rule only applies if this color doesn't already have a queen.
                if single_color not in placed_colors:
                    # The crucial fix: check if this color has only one total empty cell remaining.
                    if len(empty_cells_per_color.get(single_color, [])) == 1:
                        # Corrected line: use empty_positions_in_row
                        single_cell_pos = empty_positions_in_row[0][0]
                        changed = True
                        print(
                            f"Rule 6: Row {r} has a single empty color {single_color} and no queen. Marking other cells.")

                        # Mark all other cells of this color as 'x'
                        for cell_r, cell_c in empty_cells_per_color[single_color]:
                            if (cell_r, cell_c) != (r, single_cell_pos):
                                if updated_grid[cell_r][cell_c] == 'e':
                                    updated_grid[cell_r][cell_c] = 'x'
                                    data_idx = cell_c * rows + cell_r
                                    self.sleep()
                                    partial_name = f"Grid-{data_idx}-"
                                    element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                                    element.tap()

                                    # Repeat the same logic for columns
        for c in range(cols):
            empty_positions_in_col = [(r, position_to_color.get((r, c))) for r in range(rows) if
                                      updated_grid[r][c] == 'e' and (r, c) in position_to_color]

            colors_in_col = {color for _, color in empty_positions_in_col}
            if len(colors_in_col) == 1:
                single_color = next(iter(colors_in_col))
                if single_color not in placed_colors:
                    if len(empty_cells_per_color.get(single_color, [])) == 1:
                        # Corrected line: use empty_positions_in_col
                        single_cell_pos = empty_positions_in_col[0][0]
                        changed = True
                        print(
                            f"Rule 6: Column {c} has a single empty color {single_color} and no queen. Marking other cells.")

                        for cell_r, cell_c in empty_cells_per_color[single_color]:
                            if (cell_r, cell_c) != (single_cell_pos, c):
                                if updated_grid[cell_r][cell_c] == 'e':
                                    updated_grid[cell_r][cell_c] = 'x'
                                    data_idx = cell_c * rows + cell_r

                                    self.sleep()
                                    partial_name = f"Grid-{data_idx}-"
                                    element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                                    element.tap()

        return updated_grid, changed

    def apply_rule_7_and_click(self, updated_grid, color_map):
        """
                    Rule 5:
                    - For each color, if it appears only in one row or column,
                      mark 'x' in other cells of that row or column that are 'e' and not of that color.

                    Args:
                        driver: Selenium WebDriver
                        updated_grid: 2D list with ['q', 'e', 'r', 'x', ...]
                        color_map: dict of color_id -> list of (row, col)

                    Returns:
                        new_grid: updated 2D list with additional ruled out cells
                """

        new_grid = deepcopy(updated_grid)
        rows = len(new_grid)
        cols = len(new_grid[0])
        cells_to_click = []
        # Update color_map to reflect current grid state (only include 'e' cells)
        updated_color_map = {}
        for color, positions in color_map.items():
            # Only include positions that are still empty ('e') in the current grid
            valid_positions = [(r, c) for r, c in positions if new_grid[r][c] == 'e']
            if valid_positions:
                updated_color_map[color] = valid_positions
        for color, positions in updated_color_map.items():
            # print(f'color{color}-{positions}')

            if not positions:
                continue

            pos_rows = {r for r, _ in positions}
            pos_cols = {c for _, c in positions}

            # Case 1: All positions are in one row
            if len(pos_rows) == 1:
                row = next(iter(pos_rows))
                for col in range(cols):
                    # Only mark if cell is empty 'e' AND NOT part of this color's positions
                    if new_grid[row][col] == 'e' and (row, col) not in positions:
                        new_grid[row][col] = 'x'

                        dom_idx = col * rows + row
                        cells_to_click.append(dom_idx)

            # Case 2: All positions are in one column
            if len(pos_cols) == 1:
                col = next(iter(pos_cols))
                for row in range(rows):
                    if new_grid[row][col] == 'e' and (row, col) not in positions:
                        new_grid[row][col] = 'x'
                        dom_idx = col * rows + row
                        cells_to_click.append(dom_idx)

        # Perform UI clicks if needed
        if cells_to_click:
            self.sleep()
            # driver.find_element(By.XPATH, "//*[contains(text(),'Paint ✕ Marks') and @id='markModeBtn']").click()
            for idx in cells_to_click:
                partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                element.tap()

        return new_grid

    '''
    def apply_rule_8_and_click(self, updated_grid, color_map,queens_cells=None):
        """
        Rule 8: If a non-colored empty cell can see all empty cells of a color
        (via direct lines: top, bottom, left, right, diagonals), it cannot be a queen.

        Args:
            driver: Selenium WebDriver
            updated_grid: 2D grid containing 'e', 'q', 'x', 'r', etc.
            color_map: dict mapping color name -> list of (row, col) positions

        Returns:
            new_grid: grid updated with 'x' marks for ruled out cells
        """
        new_grid = deepcopy(updated_grid)
        rows, cols = len(new_grid), len(new_grid[0])
        cells_to_click = []

        # Pre-filter valid color positions (only empty cells)
        updated_color_map = {
            color: [(r, c) for (r, c) in cells if new_grid[r][c] == 'e']
            for color, cells in color_map.items()
        }

        # Directions: N, S, E, W, NE, NW, SE, SW
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1),
                      (-1, 1), (-1, -1), (1, 1), (1, -1)]

        # For every non-colored empty cell
        for r in range(rows):
            for c in range(cols):
                if new_grid[r][c] != 'e':
                    continue

                if queens_cells and (r, c) in queens_cells:
                    continue

                in_any_color = any((r, c) in positions for positions in color_map.values())
                if in_any_color:
                    continue  # skip colored empty cells

                # Check if this cell can see all empty cells of any one color
                for color, color_positions in updated_color_map.items():
                    if not color_positions or len(color_positions) <= 1:
                        continue  # skip color groups with ≤1 empty cell

                    sees_all = True

                    for (cr, cc) in color_positions:
                        if not self._has_clear_path(new_grid, r, c, cr, cc, directions):
                            sees_all = False
                            break

                    if sees_all:
                        new_grid[r][c] = 'x'
                        dom_idx = c * rows + r
                        cells_to_click.append(dom_idx)
                        print(f"🖱️ rule 8 Selenium clicked at horizontal_idx={dom_idx}")
                        break  # no need to check other colors for this cell

        # Selenium clicks
        if cells_to_click:

            #driver.find_element(By.XPATH, "//*[contains(text(),'Paint ✕ Marks') and @id='markModeBtn']").click()
            for idx in cells_to_click:
                partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                element.tap()

        return new_grid
    '''
    '''
    def apply_rule_8_and_click(self, updated_grid, color_map, size_x, size_y, queens_cells=None, queens_grid=None):
        """
        Rule 8: If a non-colored empty cell can see all empty cells of a color
        (via direct lines: top, bottom, left, right, diagonals), it cannot be a queen.
        """
        new_grid = deepcopy(updated_grid)
        cells_to_click = []


        # Pre-filter valid color positions (only empty cells)
        updated_color_map = {
            color: [(r, c) for (r, c) in cells if new_grid[r][c] == 'e']
            for color, cells in color_map.items()
        }

        # Directions: N, S, E, W, NE, NW, SE, SW
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1),
                      (-1, 1), (-1, -1), (1, 1), (1, -1)]

        for r in range(size_x):
            for c in range(size_y):
                if new_grid[r][c] != 'e':
                    continue  # skip non-empty cells

                # ✅ skip already placed queens
                if queens_cells and (r, c) in queens_cells:
                    continue

                    # ✅ skip if queensGrid says this must be a queen
                if queens_grid:
                    vertical_idx = c * size_x + r  # column-major index
                    value = str(queens_grid[vertical_idx])
                    if value in ('1', '2'):
                        continue

                        # skip colored empty cells
                in_any_color = any((r, c) in positions for positions in color_map.values())
                if in_any_color:
                    continue

                    # Check visibility for each color
                for color, color_positions in updated_color_map.items():
                    if not color_positions or len(color_positions) <= 1:
                        continue

                    if all(self._has_clear_path(new_grid, r, c, cr, cc, directions)
                           for (cr, cc) in color_positions):
                        new_grid[r][c] = 'x'
                        dom_idx = c * size_x + r  # ✅ column-major
                        cells_to_click.append(dom_idx)
                        print(f"🖱️ Rule 8 Selenium clicked at vertical_idx={dom_idx}")
                        break

        # Perform clicks
        for idx in cells_to_click:
            partial_name = f"Grid-{idx}-"
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.tap()

        return new_grid

    def _has_clear_path(self, grid, r1, c1, r2, c2, directions):
        """
        Check if from (r1, c1) to (r2, c2), there's a clear direct path in one direction.
        Only N, S, E, W, NE, NW, SE, SW directions are allowed.
        """
        rows, cols = len(grid), len(grid[0])

        dr = r2 - r1
        dc = c2 - c1

        # Normalize direction
        step_r = (dr > 0) - (dr < 0) if dr != 0 else 0
        step_c = (dc > 0) - (dc < 0) if dc != 0 else 0

        if (step_r, step_c) not in directions:
            return False  # not in direct line

        # Move step by step towards (r2, c2)
        current_r, current_c = r1 + step_r, c1 + step_c
        while (current_r, current_c) != (r2, c2):
            if not (0 <= current_r < rows and 0 <= current_c < cols):
                return False  # out of bounds
            if grid[current_r][current_c] in ('q', 'x', 'r'):
                return False  # blocked
            current_r += step_r
            current_c += step_c

        return True
    '''

    def apply_rule_8_and_click(self, updated_grid, color_map, size_x, size_y, queens_cells=None, queens_grid=None):
        """
        Rule 8: If a non-colored empty cell can see all empty cells of a color
        (via direct lines: top, bottom, left, right, diagonals), it cannot be a queen.
        """

        new_grid = deepcopy(updated_grid)
        cells_to_click = []

        # ✅ Derive actual grid dimensions (safe against swapped inputs)
        rows = len(new_grid)
        cols = len(new_grid[0]) if new_grid else 0

        # ✅ Pre-filter valid color positions (only empty cells)
        updated_color_map = {
            color: [(r, c) for (r, c) in cells if new_grid[r][c] == 'e']
            for color, cells in color_map.items()
        }

        # Directions: N, S, E, W, NE, NW, SE, SW
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1),
                      (-1, 1), (-1, -1), (1, 1), (1, -1)]

        for r in range(rows):
            for c in range(cols):

                # Skip non-empty cells
                if new_grid[r][c] != 'e':
                    continue

                # ✅ Skip already placed queens
                if queens_cells and (r, c) in queens_cells:
                    continue

                # ✅ Skip if queensGrid says 1 or 2 (both treated as queen)
                if queens_grid:
                    vertical_idx = c * rows + r  # column-major index
                    if 0 <= vertical_idx < len(queens_grid):
                        value = str(queens_grid[vertical_idx])
                        if value in ('1', '2'):
                            continue

                # ✅ Skip colored empty cells
                in_any_color = any((r, c) in positions for positions in color_map.values())
                if in_any_color:
                    continue

                # ✅ Check visibility for each color
                for color, color_positions in updated_color_map.items():
                    if not color_positions or len(color_positions) <= 1:
                        continue

                    if all(self._has_clear_path(new_grid, r, c, cr, cc, directions)
                           for (cr, cc) in color_positions):
                        new_grid[r][c] = 'x'
                        dom_idx = c * rows + r  # column-major index
                        cells_to_click.append(dom_idx)
                        logging.info(f"🖱️ Rule 8 Selenium clicked at vertical_idx={dom_idx}")
                        break

        # ✅ Perform clicks
        for idx in cells_to_click:
            partial_name = f"Grid-{idx}-"
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.tap()

        return new_grid

    def _has_clear_path(self, grid, r1, c1, r2, c2, directions):
        """
        Check if from (r1, c1) to (r2, c2), there's a clear direct path in one direction.
        Only N, S, E, W, NE, NW, SE, SW directions are allowed.
        """
        rows, cols = len(grid), len(grid[0])

        dr = r2 - r1
        dc = c2 - c1

        # Normalize direction
        step_r = (dr > 0) - (dr < 0) if dr != 0 else 0
        step_c = (dc > 0) - (dc < 0) if dc != 0 else 0

        if (step_r, step_c) not in directions:
            return False  # not in direct line

        # Move step by step towards (r2, c2)
        current_r, current_c = r1 + step_r, c1 + step_c
        while (current_r, current_c) != (r2, c2):
            if not (0 <= current_r < rows and 0 <= current_c < cols):
                return False  # out of bounds
            if grid[current_r][current_c] in ('q', 'x', 'r'):
                return False  # blocked
            current_r += step_r
            current_c += step_c

        return True

    def apply_rule_9_and_click(self, updated_grid, color_map):
        """
        Rule 7:
        If the remaining positions of two colors are restricted to only two rows or two columns,
        and neither has a queen already placed, then other empty cells in those rows/columns
        can be ruled out.

        Args:
            driver: Selenium WebDriver
            updated_grid: 2D grid with ['e', 'q', 'r', 'x', ...]
            color_map: dict of color_id -> list of (row, col)

        Returns:
            new_grid: updated grid after applying rule
        """
        new_grid = deepcopy(updated_grid)
        rows = len(new_grid)
        cols = len(new_grid[0])
        cells_to_click = []

        for color1, color2 in combinations(color_map.keys(), 2):
            positions1 = color_map[color1]
            positions2 = color_map[color2]

            # Skip if either color already has a Queen
            if any(new_grid[r][c] == 'q' for r, c in positions1 + positions2):
                continue

            remaining1 = [(r, c) for r, c in positions1 if new_grid[r][c] == 'e']
            remaining2 = [(r, c) for r, c in positions2 if new_grid[r][c] == 'e']

            if not remaining1 or not remaining2:
                continue

            combined = remaining1 + remaining2
            combined_rows = {r for r, _ in combined}
            combined_cols = {c for _, c in combined}

            # Case 1: Exactly 2 rows
            if len(combined_rows) == 2:
                for r in combined_rows:
                    for c in range(cols):
                        if new_grid[r][c] == 'e' and (r, c) not in combined:
                            new_grid[r][c] = 'r'
                            dom_idx = c * rows + r
                            cells_to_click.append(dom_idx)

            # Case 2: Exactly 2 columns
            elif len(combined_cols) == 2:
                for c in combined_cols:
                    for r in range(rows):
                        if new_grid[r][c] == 'e' and (r, c) not in combined:
                            new_grid[r][c] = 'r'
                            dom_idx = c * rows + r
                            cells_to_click.append(dom_idx)

        if cells_to_click:
            self.sleep()
            # driver.find_element(By.XPATH, "//*[contains(text(),'Paint ✕ Marks') and @id='markModeBtn']").click()
            for idx in cells_to_click:
                partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                element.tap()

        return new_grid

    def apply_rule_10_and_click(self, updated_grid, color_map):
        """
        Rule 8:
        If the remaining positions of three colors are restricted to only three rows or columns,
        and none of them already has a queen ('q'), we can rule out other empty cells in those rows/columns.

        Args:
            driver: Selenium WebDriver
            updated_grid: 2D grid with ['e', 'q', 'r', 'x', ...]
            color_map: dict of color_id -> list of (row, col)

        Returns:
            new_grid: updated grid after applying rule
        """
        new_grid = deepcopy(updated_grid)
        rows = len(new_grid)
        cols = len(new_grid[0])
        cells_to_click = []

        for color_triplet in combinations(color_map.items(), 3):
            combined = []
            color_names = []
            skip_triplet = False

            # Step 1: Filter colors with existing queens — skip such combinations
            for color, positions in color_triplet:
                color_names.append(color)

                # Skip this color if it already has a queen
                if any(new_grid[r][c] == 'q' for r, c in positions):
                    skip_triplet = True
                    break

                remaining = [(r, c) for r, c in positions if new_grid[r][c] == 'e']
                if not remaining:
                    skip_triplet = True
                    break

                combined.extend(remaining)

            if skip_triplet:
                continue

            combined_rows = {r for r, _ in combined}
            combined_cols = {c for _, c in combined}

            # Case 1: Exactly 3 rows
            if len(combined_rows) == 3:
                for r in combined_rows:
                    for c in range(cols):
                        if new_grid[r][c] == 'e' and (r, c) not in combined:
                            new_grid[r][c] = 'r'
                            dom_idx = c * rows + r
                            cells_to_click.append(dom_idx)

            # Case 2: Exactly 3 columns
            elif len(combined_cols) == 3:
                for c in combined_cols:
                    for r in range(rows):
                        if new_grid[r][c] == 'e' and (r, c) not in combined:
                            new_grid[r][c] = 'r'
                            dom_idx = c * rows + r
                            cells_to_click.append(dom_idx)

        # Perform UI clicks if needed
        if cells_to_click:
            # driver.find_element(By.XPATH, "//*[contains(text(),'Paint ✕ Marks') and @id='markModeBtn']").click()
            for idx in cells_to_click:
                self.sleep()
                partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                element.tap()

        return new_grid

    def extract_queen_positions_from_json(self, queens_grid, size_x, size_y):
        positions = []
        for col in range(size_x):
            for row in range(size_y):
                idx = col * size_y + row  # vertical indexing
                if queens_grid[idx] == 1:
                    positions.append([row, col])
        return positions

    def check_wrong_guess(self, grid, queen_positions):
        """
            Determine if the last guess (an 'x' in grid) conflicts with queens placement.
            Return True if guess was wrong and needs correction.
        """
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        for (r, c) in queen_positions:
            if 0 <= r < rows and 0 <= c < cols:
                if grid[r][c] == 'x':
                    print(f"Conflict: Queen at ({r},{c}) conflicts with 'x' mark")
                    return True
            else:
                print(f"Warning: queen position ({r},{c}) is out of grid bounds")
        return False

    def find_queen_position_to_place(self, grid, queen_positions):
        """
            Given queen_positions (from queensGrid where '1' indicates queen should be),
            find the first position where queen is NOT yet placed on the grid.
        """
        for r, c in queen_positions:
            if grid[r][c] != 'q':  # queen not yet placed here
                return (r, c)
        # If all queens already placed, return first position or None
        if queen_positions:
            return queen_positions[0]
        else:
            return None

    '''
    def apply_rule_11_and_click(self, grid_2d, color_map, queens_grid, size_x, size_y):
        candidates = []
        new_grid = deepcopy(grid_2d)
        loc_queen = None

        # Step 1: Collect colors without queen and count empty cells
        for color, cells in color_map.items():
            empty_cells = []
            has_queen = False

            for row, col in cells:
                if new_grid[row][col] == 'q':
                    has_queen = True
                elif new_grid[row][col] == 'e':
                    empty_cells.append((row, col))

            if not has_queen and empty_cells:
                candidates.append((color, empty_cells, cells))

        # Step 2: Find color group with minimum empty cells (first occurrence wins if tie)
        min_empty = float('inf')
        selected_group = None

        for color, empty_cells, all_cells in candidates:
            if len(empty_cells) < min_empty:
                min_empty = len(empty_cells)
                selected_group = (color, empty_cells, all_cells)

        if selected_group:
            color, empty_cells, all_cells = selected_group
            print(f"🎨 Rule 11 selected color {color} with {min_empty} empty cells.")

            for r in range(size_x):
                for c in range(size_y):
                    vertical_idx_invalid = c * size_y + r
                    if new_grid[r][c] == 'x' and str(queens_grid[vertical_idx_invalid]) == '1':
                        partial_name = f"Grid-{vertical_idx_invalid}-"  # Example: Grid-15-<color>
                        element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                        element.tap()
                        new_grid[r][c] = 'e'
                        print(f"👑 Rule 11: Color {color} already has a queen at ({r},{c}), skipping.")
                        return new_grid, loc_queen

            # Step 3: Find position in vertical-indexed queensGrid
            for row, col in all_cells:
                vertical_idx = col * size_y + row
                if str(queens_grid[vertical_idx]) == '1' and new_grid[row][col] == 'e':
                    new_grid[row][col] = 'q'
                    loc_queen = (row, col)
                    print(f"👑 Rule 11 placed queen at: ({row}, {col}), vertical_idx={vertical_idx}")

                    try:
                        # driver.find_element(By.XPATH,
                        #  "//*[contains(text(),'Paint 👑 Queens') and @id='queenModeBtn']").click()
                        self.sleep()
                        idx = col * size_y + row

                        partial_name = f"Grid-{idx}-"  # Example: Grid-15-<color>
                        element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                        element.tap()
                        element.tap()
                    except Exception as e:
                        print(f"❌ Selenium click failed: {e}")

                    print(f"✅ Grid after Rule 11:\n{new_grid}")
                    return new_grid, loc_queen

            print(f"❌ No valid position for queen found in color {color} group.")
        else:
            print("⚠️ Rule 11: No valid color group found without a queen.")

        print("⚠️ Rule 11: No queen placed.")
        return new_grid, loc_queen
    '''
    '''
    def apply_rule_11_and_click(self, grid_2d, color_map, queens_grid, size_x, size_y):
        candidates = []
        new_grid = deepcopy(grid_2d)
        loc_queen = None

        # Step 1: Collect colors without queen and count empty cells
        for color, cells in color_map.items():
            empty_cells = []
            has_queen = False

            for row, col in cells:
                if new_grid[row][col] == 'q':
                    has_queen = True
                elif new_grid[row][col] == 'e':
                    empty_cells.append((row, col))

            if not has_queen and empty_cells:
                candidates.append((color, empty_cells, cells))

        # Step 2: Pick color with min empty cells
        min_empty = float('inf')
        selected_group = None
        for color, empty_cells, all_cells in candidates:
            if len(empty_cells) < min_empty:
                min_empty = len(empty_cells)
                selected_group = (color, empty_cells, all_cells)

        if selected_group:
            color, empty_cells, all_cells = selected_group
            print(f"🎨 Rule 11 selected color {color} with {min_empty} empty cells.")

            # Step 2a: Fix any invalid X marks where queensGrid says a queen exists
            for r in range(size_x):
                for c in range(size_y):
                    vertical_idx_invalid = c * size_x + r  # ✅ column-major
                    if new_grid[r][c] == 'x' and str(queens_grid[vertical_idx_invalid]) == '1':
                        partial_name = f"Grid-{vertical_idx_invalid}-"
                        element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                        element.tap()
                        new_grid[r][c] = 'e'
                        print(f"👑 Rule 11: Corrected invalid X at ({r},{c}), index={vertical_idx_invalid}")
                        return new_grid, loc_queen

            # Step 3: Place queen
            for row, col in all_cells:
                vertical_idx = col * size_x + row  # ✅ column-major
                if str(queens_grid[vertical_idx]) == '1' and new_grid[row][col] == 'e':
                    new_grid[row][col] = 'q'
                    loc_queen = (row, col)
                    print(f"👑 Rule 11 placed queen at: ({row}, {col}), index={vertical_idx}")

                    try:
                        self.sleep()
                        partial_name = f"Grid-{vertical_idx}-"
                        element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
                        element.tap()
                        element.tap()  # double tap
                    except Exception as e:
                        print(f"❌ Selenium click failed: {e}")

                    print(f"✅ Grid after Rule 11:\n{new_grid}")
                    return new_grid, loc_queen

            print(f"❌ No valid position for queen found in color {color} group.")
        else:
            print("⚠️ Rule 11: No valid color group found without a queen.")

        print("⚠️ Rule 11: No queen placed.")
        return new_grid, loc_queen
    '''

    def apply_rule_11__double_and_click(self, grid_2d, color_map, queens_grid, size_x, size_y):
        """
        Single-rule solver for queens_x2 mode.
        Each call places ONE queen.
        Keep calling until `done == True`.
        """

        new_grid = deepcopy(grid_2d)
        loc_queen = None

        candidates = []
        total_placed = 0

        # ---------- STEP 1: Scan all colors ----------
        for color, cells in color_map.items():
            queen_count = 0
            valid_cells = []

            for r, c in cells:
                if new_grid[r][c] == 'q':
                    queen_count += 1
                    total_placed += 1
                else:
                    idx = c * size_y + r  # column-major
                    if new_grid[r][c] == 'e' and str(queens_grid[idx]) == '1':
                        valid_cells.append((r, c, idx))

            # Need more queens for this color
            if queen_count < 2:
                if not valid_cells:
                    print(f"❌ Dead end: color {color} needs queens but has no valid cells.")
                    return new_grid, None, True  # stop solver

                candidates.append({
                    "color": color,
                    "queen_count": queen_count,
                    "valid_cells": valid_cells
                })

        # ---------- STEP 2: Completion check ----------
        if not candidates:
            print("🏁 All queens placed successfully!")
            return new_grid, None, True  # DONE

        # ---------- STEP 3: Pick most constrained color ----------
        candidates.sort(key=lambda x: len(x["valid_cells"]))
        selected = candidates[0]

        color = selected["color"]
        queen_count = selected["queen_count"]
        valid_cells = selected["valid_cells"]

        print(
            f"🎨 Color {color} | "
            f"Queens {queen_count}/2 | "
            f"Options {len(valid_cells)}"
        )

        # ---------- STEP 4: Place queen ----------
        r, c, idx = valid_cells[0]
        new_grid[r][c] = 'q'
        loc_queen = (r, c)

        try:
            self.sleep()
            partial_name = f"Grid-{idx}-"
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            self.sleep()
            element.tap()
            element.tap()
        except Exception as e:
            print(f"❌ Tap failed at ({r},{c}): {e}")

        print(f"👑 Placed queen at ({r},{c}) index={idx}")

        return new_grid, loc_queen, False  # NOT DONE

    def prepare_and_apply_rule_11(self, grid_2d):
        size_x = len(grid_2d)
        size_y = len(grid_2d[0]) if size_x > 0 else 0

        self.sizeX = size_x
        self.sizeY = size_y

        # Convert grid to queensGrid and color map
        queensGrid = []
        gridColours = []
        color_counter = 1  # or assign based on your logic

        for col in range(size_x):
            for row in range(size_y):
                cell = grid_2d[row][col]
                queensGrid.append(1 if cell == 'q' else 0)
                gridColours.append(color_counter)
            color_counter += 1

        color_map = self.get_colors_grids(gridColours, size_x, size_y)
        queens_cells = self.extract_queen_positions_from_json(queensGrid, size_x, size_y)

        return self.apply_rule_11_and_click(grid_2d, color_map, queensGrid, size_x, size_y)

    def check_whether_cell_can_be_identified(self, current_grid, color_map):
        """
            Checks if a queen can be placed due to only one empty cell left in a color group.

            Args:
                current_grid: 2D list representing the board with 'q', 'e', 'x', etc.
                color_map: dict mapping color_id -> list of (row, col) positions

            Returns:
                (updated_grid, True, (r, c)) if a queen can be placed
                (current_grid, False) otherwise
        """

        updated_grid = deepcopy(current_grid)

        for color, positions in color_map.items():
            empty_cells = [(r, c) for r, c in positions if updated_grid[r][c] == 'e']
            queen_cells = [(r, c) for r, c in positions if updated_grid[r][c] == 'q']

            # If already has a queen, skip
            if queen_cells:
                continue

            if len(empty_cells) == 1:
                r, c = empty_cells[0]
                updated_grid[r][c] = 'q'
                return updated_grid, True, (r, c)

        return current_grid, False

    def apply_guess_for_remaining_colors(self, updated_grid, color_map):
        """
            Attempts guessing when two empty 'e' cells are left for any color.
            Guesses one as queen, checks if solved using validate_status(), else reverts and tries the other.

            Args:
                driver: Selenium WebDriver
                updated_grid: 2D grid with current states ('q', 'e', 'r', etc.)
                color_map: dict of color_id -> list of (row, col)

            Returns:
                new_grid: updated grid after guessing
                loc_queen: (row, col) of confirmed queen if solved, else None
        """
        new_grid = deepcopy(updated_grid)
        rows, cols = len(new_grid), len(new_grid[0])

        for color, positions in color_map.items():
            # Skip color if already has a queen
            if any(new_grid[r][c] == 'q' for r, c in positions):
                continue

            # Find 'e' candidates
            candidates = [(r, c) for r, c in positions if new_grid[r][c] == 'e']
            if len(candidates) != 2:
                continue

            # Click "Paint 👑 Queens" button
            # driver.find_element(By.XPATH, "//*[contains(text(),'Paint 👑 Queens') and @id='queenModeBtn']").click()
            self.sleep()

            # Try first guess
            r1, c1 = candidates[0]
            dom_idx1 = c1 * rows + r1
            self.sleep()
            partial_name = f"Grid-{dom_idx1}-"  # Example: Grid-15-<color>
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.tap()

            if self.wait_for_element_for_2_minutes(self.status):
                if self.validate_status() == '✅ Solved!':
                    new_grid[r1][c1] = 'q'
                    return new_grid, (r1, c1)

            # Revert first guess
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.tap()

            # Try second guess
            r2, c2 = candidates[1]

            dom_idx2 = c2 * rows + r2
            partial_name = f"Grid-{dom_idx2}-"  # Example: Grid-15-<color>
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.click()

            if self.wait_for_element_for_2_minutes(self.status):
                if self.validate_status() == '✅ Solved!':
                    new_grid[r2][c2] = 'q'
                    return new_grid, (r2, c2)

            # Revert second guess
            partial_name = f"Grid-{dom_idx2}-"  # Example: Grid-15-<color>
            element = self.altdriver.find_object_which_contains(By.NAME, partial_name)
            element.tap()

        # No successful guesses
        return new_grid, None

    @staticmethod
    def load_rule_weights(file_name="rule_weights.json"):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go one level up from 'pages/'
        file_path = os.path.join(root_dir, file_name)
        with open(file_path, "r") as f:
            rule_weights = json.load(f)
        return rule_weights

    def log_challenge_score(self, file_name, rule_counts, Difficulty, challenge_score,
                            csv_file="tests/challenge_scores.csv"):
        rule_weights = self.load_rule_weights()
        ordered_rules = list(rule_weights.keys())

        # Determine mode based on whether we've already written the header
        mode = "w" if not GamePage._csv_initialized else "a"

        with open(csv_file, mode=mode, newline="") as f:
            writer = csv.writer(f)

            if not GamePage._csv_initialized:
                header = ["Filename"] + ordered_rules + ["Difficulty"] + ["Challenge Score"]
                writer.writerow(header)
                GamePage._csv_initialized = True

            row = [file_name]
            for rule in ordered_rules:
                row.append(rule_counts.get(rule, 0))
            row.append(f"{float(Difficulty):.4f}")
            row.append(f"{challenge_score:.4f}")
            writer.writerow(row)

    def process_queens_grid(self, queensGrid, gridColours, sizeX, sizeY):

        num_queens = self.get_num_queens_from_grid_colours(gridColours)
        grid_2d, queens_cells = self.convert_queens_grid_vertical(queensGrid, sizeX, sizeY)

        colors_map = self.get_colors_grids(gridColours, sizeX, sizeY)
        queen_colors = self.grid_color(gridColours, sizeX, sizeY)
        rules_count = defaultdict(int)
        # rule_weights = self.load_rule_weights()

        if len(queens_cells) > 1:

            for queen in queens_cells:
                color = queen_colors[queen[0]][queen[1]]
                grid_after_rule_1 = self.apply_rule_1_and_clicks(grid_2d, colors_map, color)
                if grid_after_rule_1 != grid_2d:
                    rules_count["Colour Check"] += 1

                grid_after_rule_2 = self.apply_rule_2_and_clicks(grid_after_rule_1, queen)
                if grid_after_rule_2 != grid_after_rule_1:
                    rules_count["Proximity Check"] += 1

                grid_after_rule_3 = self.apply_rule_3_and_clicks(grid_after_rule_2)
                if grid_after_rule_3 != grid_after_rule_2:
                    rules_count["Row/Column Check"] += 1

                grid_2d = grid_after_rule_3

        i = 0
        while True:
            i += 1
            changed = False
            grid_2d = deepcopy(grid_2d)

            if queens_cells:
                queen_last = queens_cells[-1]
                color = queen_colors[queen_last[0]][queen_last[1]]

            else:
                queen_last = None
                color = None

            grid_after_rule_1 = self.apply_rule_1_and_clicks(grid_2d, colors_map, color)
            if grid_after_rule_1 != grid_2d:
                rules_count["Colour Check"] += 1
                changed = True
            grid_2d = grid_after_rule_1

            grid_after_rule_2 = self.apply_rule_2_and_clicks(grid_2d, queen_last)
            if grid_after_rule_2 != grid_after_rule_1:
                rules_count["Proximity Check"] += 1
                changed = True
            grid_2d = grid_after_rule_2

            grid_after_rule_3 = self.apply_rule_3_and_clicks(grid_2d)
            if grid_after_rule_3 != grid_after_rule_2:
                rules_count["Row/Column Check"] += 1
                changed = True
            grid_2d = grid_after_rule_3

            grid_after_rule_4, loc_queen = self.apply_rule_4_and_click(grid_2d, colors_map,
                                                                       queensGrid)
            if grid_after_rule_4 != grid_after_rule_3:
                rules_count["Naked Single"] += 1

            if loc_queen != None:
                queens_cells.append(loc_queen)
                grid_2d = grid_after_rule_4
                # i = 0
                continue

            grid_after_rule_5, queen_positions = self.apply_rule_5_and_click(grid_2d, colors_map)
            if grid_after_rule_5 != grid_2d:
                rules_count["Forced Queen"] += 1

            if queen_positions:
                queens_cells.extend(queen_positions)
                grid_2d = grid_after_rule_5
                # i = 0
                continue

            grid_after_rule_6, changed_6 = self.apply_rule_6_and_click(grid_2d, colors_map, num_queens)
            if grid_after_rule_6 != grid_after_rule_5:

                if changed_6:
                    rules_count["Forced RuleOut"] += 1
                    changed = True
            grid_2d = grid_after_rule_6

            grid_after_rule_7 = self.apply_rule_7_and_click(grid_2d, colors_map)
            if grid_after_rule_7 != grid_after_rule_6:
                rules_count["Pointing Pairs"] += 1
                changed = True
            grid_2d = grid_after_rule_7

            grid_after_rule_8 = self.apply_rule_8_and_click(grid_2d, colors_map, sizeX, sizeY, queens_cells, queensGrid)
            if grid_after_rule_8 != grid_after_rule_7:
                rules_count["Cell Rule Out"] += 1
                changed = True
            grid_2d = grid_after_rule_8

            grid_after_rule_9 = self.apply_rule_9_and_click(grid_2d, colors_map)
            if grid_after_rule_9 != grid_after_rule_8:
                rules_count["Double Pointing Pairs"] += 1
                changed = True
            grid_2d = grid_after_rule_9

            grid_after_rule_10 = self.apply_rule_10_and_click(grid_2d, colors_map)
            if grid_after_rule_10 != grid_after_rule_9:
                rules_count["Triple Pointing Pairs"] += 1
                changed = True

            grid_2d = grid_after_rule_10
            if changed:
                continue

            grid_after_rule_11, loc_queen_rule_11 = self.apply_rule_11_and_click(grid_2d, colors_map, queensGrid, sizeX,
                                                                                 sizeY)
            if loc_queen_rule_11:  # Check if a queen was actually placed by Rule 11
                rules_count["Fallback"] += 1
                queens_cells.append(loc_queen_rule_11)
                grid_2d = grid_after_rule_11
                continue

                # --- Exit check ---
            any_empty_cells = any("e" in row for row in grid_2d)
            if not any_empty_cells:
                print("✅ No empty 'e' cells left. Puzzle complete.")
                break

            if not changed:
                print("✅ No more progress detected. Exiting loop.")
                break
            # Update main grid_2d with Rule 11's result

            # any_empty_cells_after_rule_10 = any('e' in row for row in grid_after_rule_10)
            # if not any_empty_cells_after_rule_10:
            # print("No empty 'e' cells left. Exiting loop.")
            # break
            # --- Exit check ---

            # if loc_queen_rule_11:  # Check if a queen was actually placed by Rule 11
            # rules_count["Fallback"] += 1
            # queens_cells.append(loc_queen_rule_11)
        # grid_2d = grid_after_rule_11  # Update main grid_2d with Rule 11's result

        # === After all rules are applied, before returning ===

        # Check if all queens have a valid color assigned

        # === Challenge Score Calculation ===
        # challenge_score = sum(rules_count[rule] * rule_weights.get(rule, 1.0) for rule in rules_count)

        print("\nRules used to solve this game:")
        for rule, count in rules_count.items():
            print(f" - {rule}: {count} time(s)")

        # print(f"\nFile: {file_name} — Total Challenge Score: {challenge_score:.2f}")

        # Format rule counts
        rules_summary = "\n".join([f" - {rule}: {count} time(s)" for rule, count in rules_count.items()])
        # Difficulty = self.get_difficulty()

        # Prepare log entry
        '''log_entry = (
               # f"\nFile: {file_name}\n"
                f"{rules_summary}\n"
                f"Difficulty: {float(Difficulty):.4f}\n"
                f"Total Challenge Score: {challenge_score:.4f}\n"
                + "-" * 50 + "\n"
        )'''

        return queens_cells, grid_2d

    def counter_lives_full(self):
        # Get all parent objects with that name
        lives_cells = self.altdriver.find_objects(By.NAME, "Cell-CounterGame-Lives(Clone)")

        if len(lives_cells) < 3:
            raise Exception(f"Expected at least 3 'Cell-CounterGame-Lives(Clone)' objects, found {len(lives_cells)}.")

        first_cell, second_cell, third_cell = lives_cells[:3]

        # Search children of that object for 'Icon-On' or 'Icon-Off' as needed
        icon_on_first = self.altdriver.find_object(
            By.PATH,
            "//Cell-CounterGame-Lives(Clone)/Icon-On"
        )
        icon_on_second = self.altdriver.find_object(
            By.PATH,
            "//Cell-CounterGame-Lives(Clone)[1]/Icon-On"
        )
        icon_on_third = self.altdriver.find_object(
            By.PATH,
            "//Cell-CounterGame-Lives(Clone)[2]/Icon-On"
        )

        # Assert they exist
        assert icon_on_first is not None, "First cell does not have 'Icon-On'."
        assert icon_on_second is not None, "Second cell does not have 'Icon-On'."
        assert icon_on_third is not None, "Third cell does not have 'Icon-On'."

    def counter_lives(self):
        # Get all parent objects with that name
        lives_cells = self.altdriver.find_objects(By.NAME, "Cell-CounterGame-Lives(Clone)")

        if len(lives_cells) < 3:
            raise Exception(f"Expected at least 3 'Cell-CounterGame-Lives(Clone)' objects, found {len(lives_cells)}.")

        first_cell, second_cell, third_cell = lives_cells[:3]

        # Search for child 'Icon-Off' inside first cell
        icon_off_child = self.altdriver.find_object(
            By.PATH, '//Cell-CounterGame-Lives(Clone)/Icon-Off'
        )

        # Search for child 'Icon-On' inside second cell
        icon_on_child = self.altdriver.find_object(
            By.PATH, '//Cell-CounterGame-Lives(Clone)[1]/Icon-On'
        )

        # Search for child 'Icon-On' inside third cell
        icon_on_child2 = self.altdriver.find_object(
            By.PATH, "//Cell-CounterGame-Lives(Clone)[2]/Icon-On"
        )

        # Assertions
        assert icon_off_child is not None, "First cell does not have 'Icon-Off'."
        assert icon_on_child is not None, "Second cell does not have 'Icon-On'."
        assert icon_on_child2 is not None, "Third cell does not have 'Icon-On'."

    def counter_lives_ended(self):
        # Get all parent objects with that name
        lives_cells = self.altdriver.find_objects(By.NAME, "Cell-CounterGame-Lives(Clone)")

        if len(lives_cells) < 3:
            raise Exception(f"Expected at least 3 'Cell-CounterGame-Lives(Clone)' objects, found {len(lives_cells)}.")

        first_cell, second_cell, third_cell = lives_cells[:3]

        # Search for child 'Icon-Off' inside each cell
        icon_off_first = self.altdriver.find_object(
            By.PATH, "//Cell-CounterGame-Lives(Clone)/Icon-Off"
        )
        icon_off_second = self.altdriver.find_object(
            By.PATH, "//Cell-CounterGame-Lives(Clone)[1]/Icon-Off"
        )
        icon_off_third = self.altdriver.find_object(
            By.PATH, "//Cell-CounterGame-Lives(Clone)[2]/Icon-Off"
        )

        # Assertions
        assert icon_off_first is not None, "First cell does not have 'Icon-Off'."
        assert icon_off_second is not None, "Second cell does not have 'Icon-Off'."
        assert icon_off_third is not None, "Third cell does not have 'Icon-Off'."

        print("✅ All three cells have 'Icon-Off'.")

    def counter_lives_full_hard(self):
        # Get all parent objects with that name
        lives_cells = self.altdriver.find_objects(By.NAME, "Cell-CounterGame-Lives(Clone)")

        if len(lives_cells) < 2:
            raise Exception(f"Expected at least 2 'Cell-CounterGame-Lives(Clone)' objects, found {len(lives_cells)}.")

        # Search children of that object for 'Icon-On' or 'Icon-Off' as needed
        icon_on_first = self.altdriver.find_object(
            By.PATH,
            "//Cell-CounterGame-Lives(Clone)/Icon-On"
        )
        icon_on_second = self.altdriver.find_object(
            By.PATH,
            "//Cell-CounterGame-Lives(Clone)[1]/Icon-On"
        )

        # Assert they exist
        assert icon_on_first is not None, "First cell does not have 'Icon-On'."
        assert icon_on_second is not None, "Second cell does not have 'Icon-On'."

    def click_all_queens_from_grid(self, queens_grid, sizeX, sizeY):
        """
        Reads queens_grid (1D list) and double-clicks all queen positions (value == 1)
        """

        queens_found = []

        for idx, val in enumerate(queens_grid):
            if int(val) == 1:
                row = idx % sizeY
                col = idx // sizeY
                queens_found.append((idx, row, col))

        print(f"👑 Total queens found: {len(queens_found)}")

        for idx, r, c in queens_found:
            try:
                partial_name = f"Grid-{idx}-"
                element = self.altdriver.find_object_which_contains(By.NAME, partial_name)

                if element:
                    self.sleep()
                    time.sleep(1.5)
                    element.click()
                    element.click()
                    print(f"🖱️ Queen clicked at (row={r}, col={c}), idx={idx}")
                else:
                    print(f"⚠️ Queen element not found at idx={idx}")

            except Exception as e:
                print(f"❌ Failed clicking queen at idx={idx}: {e}")

        return queens_found
