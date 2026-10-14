# 💣 Minesweeper Masterclass

A feature-rich Minesweeper game built in **Python** with **Pygame**, featuring an interactive tutorial, user accounts, persistent statistics and difficulty-based leaderboards backed by an **SQLite** database.

---

## Features

- **Classic Minesweeper gameplay** with three preset difficulties and a fully custom board mode
- **Interactive tutorial** with images, an embedded video and two guided practice games
- **User accounts**: create an account, log in and log out
- **Persistent stats**: wins, losses, win/loss ratio, average time and account creation date
- **Leaderboards** for each difficulty, filterable by All-time, Monthly and Weekly
- **Pause menu** with remappable pause key
- **Settings**: change controls, revert controls, mute/unmute sound, reset the tutorial
- **Chord clicking** (middle-click) and **flagging** (right-click)
- **First-click safety**: your first click always opens up a blank area, never a mine

---

## Difficulties

| Difficulty    | Board  | Mines |
|---------------|--------|-------|
| Easy          | 9 × 9  | 10    |
| Intermediate  | 16 × 16| 40    |
| Hard          | 30 × 16| 99    |
| Custom        | 9–50 wide, 9–30 high | Up to 35% of the board area |

Only Easy, Intermediate and Hard results are recorded to the leaderboards and win/loss stats. Custom and tutorial games are not.

---

## Controls

| Action                  | Input |
|-------------------------|-------|
| Reveal a tile           | Left-click |
| Flag / unflag a tile    | Right-click |
| Chord (clear neighbours)| Middle-click on a revealed number whose flag count matches |
| Pause                   | `Esc` (remappable in Settings) |
| Navigate the tutorial   | Left / Right arrow keys |

---

## Project Structure

```
.
├── Minesweeper_Masterclass.py   # Main game: UI, game logic, menus, main loop
├── Account_SQL.py               # Database module: accounts, times, leaderboards, sorting
├── accounts.db                  # SQLite database (auto-created if missing)
└── Sprites/                     # Images, sound and tutorial video used by the game
```

---

## Installation & Running

**Requirements:** Python 3.8+

```bash
pip install pygame pyvidplayer2
python Minesweeper_Masterclass.py
```

The `Sprites/` folder must sit next to the script. If `accounts.db` does not exist, it is created automatically on first launch.

---

## Coding Techniques Used

### 1. Data structures: 2D lists

The board is represented by three parallel 2D lists created in `create_board()`:

- `board`: tile values (`-1` for a mine, `0–8` for the count of neighbouring mines)
- `closed_board`: booleans for whether a tile is still hidden
- `flag_board`: booleans for whether a tile is flagged

Separating the *data* (mine positions and counts) from the *state* (hidden and flagged) keeps the logic and rendering simple.

### 2. Board generation with neighbour counting

Mines are placed at random coordinates, with a check so the same tile is never chosen twice. As each mine is placed, a nested `for dx in range(-1, 2)` / `for dy in range(-1, 2)` loop increments all neighbouring tiles. Numbers are therefore calculated incrementally during generation, rather than in a separate pass. Bounds checking (`0 <= nx < w and 0 <= ny < h`) keeps edge tiles safe.

### 3. Iterative flood fill (stack-based)

When a blank (`0`) tile is revealed, `click_handling()` uses a **stack** (`to_reveal` list with `.pop()`) to reveal the surrounding area. Each newly revealed blank tile pushes its own neighbours onto the stack. This is an iterative depth-first flood fill, which avoids Python's recursion limit on large boards such as 30 × 16 or custom 50 × 30.

### 4. Chord clicking

Middle-clicking a revealed number counts the surrounding flags. If the count equals the tile's number, all remaining unflagged neighbours are revealed using the same stack-based expansion. This reproduces the "chording" mechanic from the original game.

### 5. First-click safety by regeneration

`spawn_safety()` checks whether the first clicked tile is a blank (`0`). If it is not, the board is regenerated in a loop until it is. The player therefore always starts with an opening, and the timer starts on the first click rather than when the board is drawn.

### 6. Win detection

`check_win()` scans the board and returns `False` if any non-mine tile is still closed. The win is therefore based on every safe tile being revealed, not on flags being placed correctly.

### 7. Object-oriented programming and inheritance

The UI is built from reusable classes:

| Class            | Purpose |
|------------------|---------|
| `Menu`           | Base class: draws buttons and titles, stores button rectangles and returns the clicked button's label |
| `Menu_with_text` | **Inherits from `Menu`** (`super().__init__()`, `super().create_title()`). Adds text input boxes, password masking (`*`), a 12-character limit and banned keys |
| `Tutorial`       | Handles slide-style navigation with arrow keys |

Each screen (main menu, play, difficulty select, login, settings and so on) is its own object instance, so button state does not leak between screens. This is **encapsulation** and **code reuse** through inheritance.

### 8. Event-driven programming

The game is built around Pygame's event loop. Mouse clicks, key presses and window close events are handled with `pygame.event.get()`. Hit-testing uses `Rect.collidepoint()` for buttons, and integer division on mouse coordinates (`mx // 20, my // 20`) converts pixels to grid positions.

### 9. State-machine style menu navigation

Navigation is driven by string state variables (`choice`, `play_choice`, `select_choice`, `account_choice` and others). Nested `while` loops each represent one screen, and setting a variable to `""` returns to the previous screen. Functions such as `gameplay()` and `win_menu()` return strings like `"play_again"`, `"return_menu"` or `"next_practise"`, which the caller uses to decide what happens next.

### 10. Recursion in game flow

`gameplay()` calls itself to restart a game ("Play Again") or to move between tutorial practice boards. After a loss in the tutorial, the player is sent back to the same practice board.

### 11. Relational database design (SQLite)

`Account_SQL.py` defines two related tables:

- **`accounts`**: `username` (primary key, unique), hashed `password`, `tutorial` flag, `date_created`, `wins`, `losses`, `winloss`
- **`times`**: auto-incrementing `timeID` primary key, `time`, `difficulty`, `obtain_date` and `username` as a **foreign key** referencing `accounts`

The `get_average()` query uses a `JOIN` with the `AVG()` aggregate function to calculate a player's mean solve time. Tables are created with `CREATE TABLE IF NOT EXISTS`, so the database sets itself up on first run.

### 12. Parameterised SQL queries

Every query uses **named placeholders** (`:user`, `:difficulty` and so on) with a dictionary of values, never string concatenation. This protects the database against **SQL injection**.

```python
cursor.execute("SELECT * FROM accounts WHERE username=:user", {"user": user})
```

### 13. Password hashing

Passwords are never stored in plain text. They are hashed with `hashlib.sha224` before being saved, and login compares the hash of the entered password against the stored hash.

### 14. Merge sort (recursive divide and conquer)

`sort_leaderboard()` is a hand-written **recursive merge sort**. It splits the list of `(time, timeID, username)` tuples in half, sorts each half, then merges them by comparing the time at index `[0]` of each tuple. Fastest times appear first, and the top 10 are displayed. Merge sort runs in O(n log n) and sorts the tuples in place.

### 15. Date and time handling

The `datetime` module is used to stamp account creation, record when each time was set, and calculate rolling date windows (`timedelta(weeks=1)` and `timedelta(days=30)`). The leaderboard query then filters with `obtain_date >= :last_date`, giving **Weekly** and **Monthly** boards from a single table.

### 16. Win/loss ratio logic

`increment()` updates wins or losses, then recalculates the ratio. It handles the **divide-by-zero** case, so a player with no losses has a ratio equal to their wins.

### 17. Input validation and error handling

- Usernames need at least 3 characters.
- Passwords need at least 3 characters and at least one digit.
- Passwords must match their confirmation, and usernames must be unique.
- Custom boards are checked for non-numeric input (`try`/`except` around `int()`), zero mines, size limits (min 9, max 50 × 30) and a maximum mine density of 35%.
- Out-of-range clicks are handled safely with `try`/`except` and an `is_in_range()` helper.
- Error messages are displayed in red on screen.

### 18. Dictionaries for configuration and asset management

Images, sounds and video are loaded once at start-up into dictionaries (`images`, `sounds`, `videos`) and accessed by key. This avoids reloading files every frame. Sprites for numbered tiles are looked up with an f-string key: `images[f"{tile_value}"]`. Key bindings live in a `controls` dictionary, which is what makes the **remappable pause key** possible, including a check (`is_control_taken()`) that stops two actions sharing a key.

### 19. Multimedia

Pygame handles rendering (`blit`, `draw.rect`), fonts and sound effects, and `pyvidplayer2` plays the tutorial video inside the game window. A mute setting scales the game-over sound volume to zero.

### 20. User progress tied to the account

The tutorial completion flag is stored per account, so returning players skip straight to the game. Logging out resets the session state, and the tutorial can be reset from Settings.

---

## Possible Future Improvements

- Add a **salt** and use a stronger password-hashing function (such as `bcrypt` or `hashlib.pbkdf2_hmac`) in place of unsalted SHA-224
- Close database connections explicitly, or use `with sqlite3.connect(...)` context managers
- Enable `PRAGMA foreign_keys = ON` so SQLite enforces the `times → accounts` relationship
- Replace bare `except:` blocks with specific exceptions
- Replace global state with a game-state class
- Refactor the duplicated flood-fill code in `click_handling()` into a shared helper function
- Add more remappable controls and a "best time per difficulty" view

---

## Author

Created by **Leo McBride**.
