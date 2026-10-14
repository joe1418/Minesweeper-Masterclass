import random
import pygame
import time
import sys
from pyvidplayer2 import Video
import Account_SQL as SQL
pygame.init()
screen = pygame.display.set_mode([1000, 600])
width = screen.get_width()
height = screen.get_height()
mid_width = width / 2
mid_height = height / 2
white = (255, 255, 255)
black = (0, 0, 0)
FONT = pygame.font.SysFont("Times New Roman", 24)
message = ""
user = ""
tutorial_completed = False
muted = False
SQL.check_for_db()
controls = {"Pause": pygame.K_ESCAPE}
# Image loading
images = {
    "bomb": pygame.image.load("Sprites/bomb.jpg").convert_alpha(),
    "flag": pygame.image.load("Sprites/Flag.png").convert_alpha(),
    "blank": pygame.image.load("Sprites/blank space.png").convert_alpha(),
    "closed": pygame.image.load("Sprites/closed.png").convert_alpha(),
    "1": pygame.image.load("Sprites/Minesweeper_1.jpg").convert_alpha(),
    "2": pygame.image.load("Sprites/Minesweeper_2.jpg").convert_alpha(),
    "3": pygame.image.load("Sprites/Minesweeper_3.jpg").convert_alpha(),
    "4": pygame.image.load("Sprites/Minesweeper_4.jpg").convert_alpha(),
    "5": pygame.image.load("Sprites/Minesweeper_5.jpg").convert_alpha(),
    "6": pygame.image.load("Sprites/Minesweeper_6.jpg").convert_alpha(),
    "7": pygame.image.load("Sprites/Minesweeper_7.jpg").convert_alpha(),
    "8": pygame.image.load("Sprites/Minesweeper_8.jpg").convert_alpha(),
    "sigma": pygame.image.load("Sprites/download.jpg").convert_alpha(),
    "tut": pygame.image.load("Sprites/Tutorial.png").convert_alpha(),
    "tutf": pygame.image.load("Sprites/Tutorial_flag.png").convert_alpha(),
    "tut_vid_ss": pygame.image.load("Sprites/Tutvid.png").convert_alpha(),
    "tutp": pygame.image.load("Sprites/pause_ss.png").convert_alpha()
}
sounds = {
    "gameover_sfx": pygame.mixer.Sound("Sprites/gameover_sb.wav")
}
videos = {
        "tut_vid": Video("Sprites/Tutvid.mp4")
}
# Setting Icon and Title
pygame.display.set_caption("Minesweeper Masterclass", icontitle="")
pygame.display.set_icon(images["bomb"])

def create_board(mines, h, w):
    board = [[0 for i in range(h)] for j in range(w)]
    closed_board = [[True for i in range(h)] for j in range(w)]
    flag_board = [[False for i in range(h)] for j in range(w)]
    count = 0
    while count < mines:
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        if board[x][y] != -1:
            board[x][y] = -1
            count += 1
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and board[nx][ny] != -1:
                        board[nx][ny] += 1
    return (board, closed_board, flag_board)

def draw_board(board, closed_board, flag_board, difficulty): 
    for x in range(len(board)):
        for y in range(len(board[x])):
            screen.blit(images["blank"], ((x * 20), (y * 20)))
            tile_value = board[x][y]
            if tile_value == -1:
                screen.blit(images["bomb"], ((x * 20), (y * 20)))
            elif 1 <= tile_value <= 8:
                screen.blit(images[f"{tile_value}"], ((x * 20), (y * 20)))
            if closed_board[x][y]: 
                screen.blit(images["closed"], ((x * 20), (y * 20)))
            if flag_board[x][y]: 
                screen.blit(images["flag"], ((x * 20), (y * 20)))            
    if difficulty == "tutorial1":
        create_label(screen,"Remember!", 30, "Times New Roman", 600, 160)
        create_label(screen,"Use right-click to flag tiles when you identify a mine!", 20, "Times New Roman", 600, 220)
        create_label(screen,"You can use middle-click when the tile number matches the", 20, "Times New Roman", 600, 250)
        create_label(screen,"surround flags for faster clearing!", 20, "Times New Roman", 600, 270)
        create_label(screen,"You won't get this reminder in the next practise so make", 20, "Times New Roman", 600, 300)
        create_label(screen,"sure you remember!", 20, "Times New Roman", 600, 320)
    if difficulty == "tutorial2":
        create_label(screen,"Beat this final practise to complete the tutorial!", 20, "Times New Roman", 600, 160)



def click_handling(event, board, closed_board, flag_board, first_click):
    game_over = False
    blank = False
    mx, my = pygame.mouse.get_pos()
    x, y = mx // 20, my // 20
    try:
        if event.button == 1:  # Left-click
            if closed_board[x][y] and not flag_board[x][y]:
                closed_board[x][y] = False
                if board[x][y] == -1:
                    game_over = True
                elif board[x][y] == 0:
                    blank = True
                    surrounding_tiles = []
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            cx, cy = x + dx, y + dy
                            if 0 <= cx < len(board[0]) and 0 <= cy < len(board[0]) and not (dx == 0 and dy == 0):
                                surrounding_tiles.append((cx, cy))
                    to_reveal = list(surrounding_tiles)
                    while to_reveal:
                        cx, cy = to_reveal.pop()
                        if closed_board[cx][cy] and not flag_board[cx][cy]:
                            closed_board[cx][cy] = False
                            if board[cx][cy] == -1:
                                game_over = True
                            elif board[cx][cy] == 0:
                                for dx in range(-1, 2):
                                    for dy in range(-1, 2):
                                        nx, ny = cx + dx, cy + dy
                                        if 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                                            to_reveal.append((nx, ny))
        
        if first_click or blank:
            event.button = 2
        elif event.button == 3 and not first_click:  # Right-click
            if closed_board[x][y]:
                flag_board[x][y] = not flag_board[x][y]
        if event.button == 2 and closed_board[x][y] == False:  # Middle-click
            surrounding_flags = 0
            surrounding_tiles = []

            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    cx, cy = x + dx, y + dy
                    if 0 <= cx < len(board) and 0 <= cy < len(board[0]) and not (dx == 0 and dy == 0):
                        surrounding_tiles.append((cx, cy))
                        if flag_board[cx][cy]:
                            surrounding_flags += 1

            if surrounding_flags == board[x][y]:
                to_reveal = list(surrounding_tiles)
                while to_reveal:
                    cx, cy = to_reveal.pop()
                    if closed_board[cx][cy] and not flag_board[cx][cy]:
                        closed_board[cx][cy] = False
                        if board[cx][cy] == -1:
                            game_over = True
                        elif board[cx][cy] == 0:
                            for dx in range(-1, 2):
                                for dy in range(-1, 2):
                                    nx, ny = cx + dx, cy + dy
                                    if 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                                        to_reveal.append((nx, ny))
    except:
        return
    return game_over

def spawn_safety(event, board):
    mx, my = pygame.mouse.get_pos()
    x, y = mx // 20, my // 20
    regenerate = False
    if event.button == 1:
        if board[x][y] != 0:
            regenerate = True
            return regenerate
    return regenerate

def is_in_range(event, board):
    mx, my = pygame.mouse.get_pos()
    x, y = mx // 20, my // 20
    try:
        if event.button == 1 or event.button == 2 or event.button == 3:
            board[x][y] == board[x][y]
            return True
    except:
        return False
    
def check_win(board, closed_board):
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] != -1 and closed_board[x][y]:
                return False
    return True

def pause_menu(difficulty):
    running = True
    while running:
        menu_width = 400
        menu_height = 200
        menu_rect = pygame.Rect(mid_width - menu_width // 2, mid_height - menu_height // 2, menu_width, menu_height)


        pygame.draw.rect(screen, white, menu_rect)
        pygame.draw.rect(screen, black, menu_rect, 3)

        create_label(screen, "Paused", 24, "Times New Roman", 500, 370)
        
        if difficulty == "tutorial1" or difficulty == "tutorial2":
            resume_button = create_button(screen, "Resume", mid_width - 100, mid_height)
        else:
            resume_button = create_button(screen, "Resume", mid_width - 100, mid_height - 20)
        if difficulty != "tutorial1" and difficulty != "tutorial2":
            quit_button = create_button(screen, "Back to Menu", mid_width - 100, mid_height + 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    return "resume"
                elif difficulty != "tutorial1" and difficulty != "tutorial2":
                    if quit_button.collidepoint(event.pos):
                        return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == controls["Pause"]:
                    return "resume"

    return "quit"

def win_menu(elapsed_time, difficulty):
    running = True
    if user != "" and difficulty != "custom" and difficulty != "tutorial1" and difficulty != "tutorial2":
        SQL.insert_time(user,elapsed_time,difficulty)
        SQL.increment(user,"w")
    while running:
        menu_width = 400
        menu_height = 200
        menu_rect = pygame.Rect(mid_width - menu_width // 2, mid_height - menu_height // 2, menu_width, menu_height)
        pygame.draw.rect(screen, white, menu_rect)
        pygame.draw.rect(screen, black, menu_rect, 3)
        title_text = FONT.render("You Win!", True, black)
        screen.blit(title_text, (mid_width - title_text.get_width() // 2, mid_height - 100))
        time_text = FONT.render(f"Time: {elapsed_time:.2f} seconds", True, black)
        screen.blit(time_text, (mid_width - time_text.get_width() // 2, mid_height - 70))
        if difficulty == "tutorial1":
            play_again_button = create_button(screen, "Next Practise", mid_width - 100, mid_height)
        elif difficulty == "tutorial2":
            play_again_button = create_button(screen, "Finish", mid_width - 100, mid_height)
        else:
            play_again_button = create_button(screen, "Play Again", mid_width - 100, mid_height - 20)
        if difficulty != "tutorial1" and difficulty != "tutorial2":
            return_menu_button = create_button(screen, "Return to Menu", mid_width - 100, mid_height + 40)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    if difficulty == "tutorial1":
                        return "next_practise"
                    elif difficulty == "tutorial2":
                        return "tutorial_complete"
                    else:
                        return "play_again"
                elif difficulty != "tutorial1" and difficulty != "tutorial2":
                    if return_menu_button.collidepoint(event.pos):
                        return "return_menu"
    return "quit"

def gameplay(mines, height, width, difficulty): #main gameplay subroutine
    board = create_board(mines, height,  width)
    game_over = False
    timer_started = False
    start_time = 0
    is_paused = False
    first_click = True
    regenerate = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not event.button == 3 and not event.button == 2 and not game_over and not is_paused and first_click and is_in_range(event, board[0]):
                if not timer_started:
                    start_time = time.time()
                    timer_started = True
                    regenerate = spawn_safety(event, board[0])
                while regenerate == True:
                    board = create_board(mines, height, width)
                    timer_started = False
                    start_time = 0
                    regenerate = spawn_safety(event, board[0])
                game_over = click_handling(event, board[0], board[1], board[2], first_click)
                start_time = time.time()
                first_click = False
                timer_started = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not is_paused and not first_click and is_in_range(event, board[0]):
                game_over = click_handling(event, board[0], board[1], board[2], first_click)
            elif event.type == pygame.KEYDOWN:
                if event.key == controls["Pause"]:
                    is_paused = True 
        
        if is_paused:
            pause_choice = pause_menu(difficulty)
            if pause_choice == "resume":
                is_paused = False 
            elif pause_choice == "quit":
                return

        if not is_paused:
            screen.fill(white)
            draw_board(board[0], board[1], board[2], difficulty) 
            if timer_started and check_win(board[0], board[1]):
                elapsed_time = time.time() - start_time
                result = win_menu(elapsed_time, difficulty)
                if result == "play_again":
                        return gameplay(mines,height,width, difficulty)
                elif result == "return_menu":
                    return
                elif result == "next_practise":
                    return gameplay(10,9,9,"tutorial2")
                elif result == "tutorial_complete":
                    global tutorial_completed
                    tutorial_completed = True
                    if user != "":
                        SQL.update_tutorial(user)
                    return

        pygame.display.flip()
    if game_over and difficulty == "tutorial1":
        return gameplay(mines,height,width, difficulty)
    elif game_over and difficulty == "tutorial2":
        return gameplay(10,9,9,"tutorial1")
    if game_over:
        sounds["gameover_sfx"].play()
        if user != "" and difficulty != "tutorial1" and difficulty != "tutorial2" and difficulty != "custom":
            SQL.increment(user, "l")
    while game_over:
        sounds["gameover_sfx"].set_volume(1.0) if not muted else sounds["gameover_sfx"].set_volume(0.0)
        screen.blit(images["sigma"], (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                sounds["gameover_sfx"].stop()
                game_over = False
    return

def create_button(screen, text, x, y, width=200, height=50, font=FONT, text_color=white, bg_color=black):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_color, button_rect)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect

def create_label(screen,title, size, font, x, y):
    title_font = pygame.font.SysFont(f"{font}", size)
    title_text = title_font.render(f"{title}", True, black)
    screen.blit(title_text, (x - title_text.get_width() // 2, y - 150))
    return

class Menu:
    def __init__(self):
        self.boxes = []
        self.texts = []
    
    def create_button(self, screen, text, x, y, width=200, height=50, font=FONT, text_color=white, bg_color=black, outline=0):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, bg_color, button_rect, outline)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        self.boxes.append(button_rect)
        self.texts.append(text)
        return button_rect
    
    def create_title(self, screen, title, size, font, x, y, clear):
        if clear:
            screen.fill(white)
        title_font = pygame.font.SysFont(f"{font}", size)
        title_text = title_font.render(f"{title}", True, black)
        screen.blit(title_text, (x - title_text.get_width() // 2, y - 150))
        return
    
    def menu_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range (len(self.boxes)):
                    if self.boxes[i].collidepoint(event.pos):
                        return f"{self.texts[i]}"
        self.boxes = []
        self.texts = []
        return

class Menu_with_text(Menu):
    def __init__(self):
        super().__init__()
        self.input_active = []
        self.terms = []
        self.terms_check = []
        self.pointer = 0
        self.banned_char = [pygame.K_ESCAPE,pygame.K_TAB,pygame.K_DELETE,pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE]
    
    def create_heading(self, screen, title, x, y):
        super().create_title(screen, title, 24, "Times New Roman", x, y, False)
    
    def create_box(self, screen, x, y):
        if self.pointer == 0:
            self.pointer = len(self.boxes)
        super().create_button(screen, text="", x=x, y=y, width=300, height=40, font=FONT, text_color=black, bg_color=white)
        self.input_active.append(False)
        self.terms.append("")
        self.terms_check.append(False)
    
    def draw_box(self, screen):
        for i in range(0, self.pointer):
            pygame.draw.rect(screen, black, rect = self.boxes[i])
            text_surface = FONT.render(self.texts[i], True, white)
            text_rect = text_surface.get_rect(center=self.boxes[i].center)
            screen.blit(text_surface, text_rect)
        for i in range (self.pointer, len(self.boxes)):
            k = i - self.pointer
            if self.input_active[k]:
                pygame.draw.rect(screen, black, self.boxes[i], 2)
            else:
                pygame.draw.rect(screen, black, self.boxes[i], 1)
    
    def text_menu_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range (self.pointer, len(self.boxes)):
                    k = i - self.pointer
                    if self.boxes[i].collidepoint(event.pos):
                        for j in range(len(self.input_active)):
                            self.input_active[j] = False
                        self.input_active[k] = True   
                for i in range(0,self.pointer):
                    if self.boxes[i].collidepoint(event.pos):
                        return f"{self.texts[i]}"
            elif event.type == pygame.KEYDOWN:
                for i in range (len(self.input_active)):
                    if self.input_active[i]:
                        if event.key == pygame.K_BACKSPACE:
                            self.terms[i] = self.terms[i][:-1]
                        elif event.key not in self.banned_char:
                            if len(self.terms[i]) < 12:    
                                self.terms[i] += event.unicode
        return 
    
    def draw_text(self, screen, is_hidden):
        for i in range (len(self.terms)):
            if not is_hidden[i]:
                word = FONT.render(self.terms[i], True, black)
                screen.blit(word, (self.boxes[i+(self.pointer)].x + 10, self.boxes[i+(self.pointer)].y + 4))
            elif is_hidden[i]:
                word = FONT.render("*" * len(self.terms[i]), True, black)
                screen.blit(word, (self.boxes[i+(self.pointer)].x + 10, self.boxes[i+(self.pointer)].y + 4))        
    
    def return_values(self):
        return self.terms
    
    def clear_boxes(self):
        for i in range (0, (len(self.boxes)-self.pointer)):
            self.terms[i] = ""
            self.input_active[i] = False
        return

class Tutorial:
    def create_image(self, screen, image, x, y):
        screen.fill(white)
        screen.blit(image, (x,y))
        return
    
    def create_label(self, screen,title, size, font, x, y):
        title_font = pygame.font.SysFont(f"{font}", size)
        title_text = title_font.render(f"{title}", True, black)
        screen.blit(title_text, (x - title_text.get_width() // 2, y - 150))
        return
    
    def tutorial_handling(self):
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                return "forward"
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                return "back"
        return False

def control_display(control):
    button_name = pygame.key.name(control)
    return button_name

def is_control_taken(control):
    return control in controls.values()

def change_control():
    wait = True
    screen.fill(white)
    prompt_text = FONT.render("Press a key to change control", True, (255, 0, 0))
    screen.blit(prompt_text, (mid_width - prompt_text.get_width() // 2, 350))
    pygame.display.flip()
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not is_control_taken(event.key):
                    new_key = event.key
                    return new_key
                else:
                    error_text = FONT.render("Key already in use", True, (255, 0, 0))
                    screen.blit(error_text, (mid_width - error_text.get_width() // 2, 450))
                    pygame.display.flip()

def is_valid_username(username):
    return len(username.strip()) >= 3

def is_valid_password(password):
    return len(password.strip()) >= 3 and any(char.isdigit() for char in password)

# Game loop
running = True
c_first = True
ca_first = True
l_first = True
main_menu = Menu()
play_screen = Menu()
Guide = Tutorial()
select_screen = Menu()
custom_screen = Menu_with_text()
leaderboards_screen = Menu()
leaderboard_difficulty = ""
leaderboard_time = ""
account_screen = Menu()
create_account_screen = Menu_with_text()
login_screen = Menu_with_text()
logged_account_screen = Menu()
view_account_screen = Menu()
settings_screen = Menu()
controls_screen = Menu_with_text()
logout_screen = Menu()
while running:
    main_menu.create_title(screen, "Minesweeper Masterclass", 70, "Times New Roman", 500, 300, True)
    main_menu.create_button(screen, "Play", mid_width - 100, mid_height - 20)
    main_menu.create_button(screen, "Account", mid_width - 100, mid_height + 40)
    main_menu.create_button(screen, "Settings", mid_width - 100, mid_height + 100)
    main_menu.create_button(screen, "Quit", mid_width - 100, mid_height + 160)
    pygame.display.flip()
    choice = main_menu.menu_handling()
    while choice == "Play" and tutorial_completed:
        play_screen.create_title(screen, "Minesweeper Masterclass", 70, "Times New Roman", 500, 300, True)
        play_screen.create_button(screen, "Classic", mid_width - 100, mid_height - 20)
        play_screen.create_button(screen, "Leaderboards", mid_width - 100, mid_height + 40)
        play_screen.create_button(screen, "Return", mid_width - 100, mid_height + 100)
        pygame.display.flip()
        play_choice = play_screen.menu_handling()
        if play_choice == "Return":
            choice = ""
        while play_choice == "Classic":
            select_screen.create_title(screen, "Select Difficulty", 70, "Times New Roman", 500, 300, True)
            select_screen.create_button(screen, "Easy", mid_width - 100, mid_height - 20)
            select_screen.create_button(screen, "Intermediate", mid_width - 100, mid_height + 40)
            select_screen.create_button(screen, "Hard", mid_width - 100, mid_height + 100)
            select_screen.create_button(screen, "Custom", mid_width - 100, mid_height + 160)
            select_screen.create_button(screen, "Return", mid_width - 100, mid_height + 220)
            pygame.display.flip()
            select_choice = select_screen.menu_handling()
            if select_choice == "Easy":
                play_choice = ""
                choice = ""
                gameplay(10,9,9,"Easy")
            elif select_choice == "Intermediate":
                play_choice = ""
                choice = ""
                gameplay(40,16,16, "Intermediate")
            elif select_choice == "Hard":
                play_choice = ""
                choice = ""
                gameplay(99,16,30, "Hard")
            if select_choice == "Custom" and c_first:
                custom_screen.create_button(screen, "Return", mid_width - 150, 500, 120, 40)
                custom_screen.create_button(screen, "Submit", mid_width + 30, 500, 120, 40)
                custom_screen.create_box(screen, 350, 150)
                custom_screen.create_box(screen, 350, 220)
                custom_screen.create_box(screen, 350, 290)
            while select_choice == "Custom":
                custom_screen.create_title(screen, "Customise board", 24, "Times New Roman", 500, 200, True)
                custom_screen.create_heading(screen, "Height", 316, 305)
                custom_screen.create_heading(screen, "Width", 319, 375)
                custom_screen.create_heading(screen, "Mines", 319, 445)
                custom_screen.create_heading(screen, "Max height 30", 721, 305)
                custom_screen.create_heading(screen, "Max width 50", 718, 375)
                custom_screen.create_heading(screen, f"Max mines 35% of board area", 797, 445)
                custom_screen.draw_box(screen)
                custom_screen.draw_text(screen, [False, False, False])
                if message:
                    message_text = FONT.render(message, True, (255, 0, 0))
                    screen.blit(message_text, (mid_width - message_text.get_width() // 2, 350))
                pygame.display.flip()
                custom_choice = custom_screen.text_menu_handling()
                while custom_choice == "Submit":
                    message = ""
                    custom_game = custom_screen.return_values()
                    try:
                        heightc = int(custom_game[0])
                        widthc = int(custom_game[1])
                        minesc = int(custom_game[2])
                    except:
                        message = "Invalid characters entered"
                        custom_choice = ""
                    else:
                        if minesc == 0:
                            message = "Cannot have 0 mines"
                            custom_choice = ""
                        elif widthc > 50 or heightc > 30:
                            message = "Board size too big"
                            custom_choice = ""
                        elif widthc < 9 or heightc < 9:
                            message = "Board size too small"
                            custom_choice = ""
                        elif minesc > (heightc*widthc*0.35):
                            message = "Too many mines"
                            custom_choice = ""
                        elif widthc <= 50 and heightc <= 30 and minesc <= (heightc*widthc*0.35):
                            custom_choice = ""
                            select_choice = ""
                            play_choice = ""
                            choice = ""
                            c_first = False
                            custom_screen.clear_boxes()
                            gameplay(minesc, heightc, widthc, "custom")
                if custom_choice == "Return":
                    custom_screen.clear_boxes()
                    message = ""
                    select_choice = ""
                    c_first = False
            if select_choice == "Return":
                play_choice = ""
        while play_choice == "Leaderboards":
            leaderboards_screen.create_title(screen, "Leaderboards", 70, "Times New Roman", 500, 150, True)
            leaderboards_screen.create_button(screen, "Easy", mid_width - 420, 220, 140, 40)
            leaderboards_screen.create_button(screen, "Intermediate", mid_width - 420, 280, 140, 40)
            leaderboards_screen.create_button(screen, "Hard", mid_width - 420, 340, 140, 40)
            leaderboards_screen.create_button(screen, "All-time", mid_width - 270, 220, 140, 40)
            leaderboards_screen.create_button(screen, "Monthly", mid_width - 270, 280, 140, 40)
            leaderboards_screen.create_button(screen, "Weekly", mid_width - 270, 340, 140, 40)
            leaderboards_screen.create_button(screen, "Return", mid_width - 100, mid_height + 220)
            if leaderboard_difficulty != "" and leaderboard_time != "":
                leaderboard = SQL.get_leaderboard(leaderboard_difficulty, leaderboard_time)
                SQL.sort_leaderboard(leaderboard)
                if len(leaderboard) < 10:
                    for i in range (len(leaderboard)):
                        leaderboards_screen.create_title(screen, str((i+1)) + ". " + leaderboard[i][2], 30, "Times New Roman", 600 , 300 + (35 * i), False)
                        leaderboards_screen.create_title(screen, str(round(leaderboard[i][0],2)), 30, "Times New Roman", 800 , 300 + (35 * i), False)
                else:
                    for i in range (10):
                        leaderboards_screen.create_title(screen, str((i+1)) + ". " + leaderboard[i][2], 30, "Times New Roman", 600 , 300 + (35 * i), False)
                        leaderboards_screen.create_title(screen, str(round(leaderboard[i][0],2)), 30, "Times New Roman", 800 , 300 + (35 * i), False)
            pygame.display.flip()
            leaderboards_choice = leaderboards_screen.menu_handling()
            if leaderboards_choice in ["Easy", "Intermediate", "Hard"]:
                leaderboard_difficulty = leaderboards_choice
            elif leaderboards_choice in ["All-time", "Monthly", "Weekly"]:
                leaderboard_time = leaderboards_choice
            if leaderboards_choice == "Return":
                leaderboard_time = ""
                leaderboard_difficulty = ""
                play_choice = ""
            
    while choice == "Play" and not tutorial_completed:
        screen.fill(white)
        Guide.create_label(screen, "Welcome to Minesweeper Masterclass", 40, "Times New Roman", 500, 210)
        Guide.create_label(screen, "In this tutorial we aim to teach the fundamentals of Minesweeper to you.", 30, "Times New Roman", 500, 510)
        Guide.create_label(screen, "Navigate the tutorial using the left and right arrow keys.", 30, "Times New Roman", 500, 550)
        Guide_Next = Guide.tutorial_handling()
        if tutorial_completed:
            break
        while Guide_Next == "forward":
            Guide.create_image(screen, images["tut"], 351, 135)
            Guide.create_label(screen, "Introduction", 40, "Times New Roman", 500, 210)
            Guide.create_label(screen, "Numbered tiles numbers correlate to the amount of mines in the surrounging area.", 30, "Times New Roman", 500, 510)
            Guide.create_label(screen, "This tile surrounded by 1's contains a mine.", 30, "Times New Roman", 500, 550)
            Guide_Next_1 = Guide.tutorial_handling()
            if tutorial_completed:
                break
            if Guide_Next_1 == "back":
                Guide_Next = ""
            while Guide_Next_1 == "forward":
                Guide.create_image(screen, images["tutf"], 351, 135)
                Guide.create_label(screen, "Flagging", 40, "Times New Roman", 500, 210)
                Guide.create_label(screen, "Right-click to flag a tile.", 30, "Times New Roman", 500, 510)
                Guide.create_label(screen, "This will mark the tile and ensure you cannot incorrectly click it.", 30, "Times New Roman", 500, 550)
                Guide.create_label(screen, "Middle-clicking a tile that has the same number of flags in its surrounding", 30, "Times New Roman", 500, 590)
                Guide.create_label(screen, "will clear all the non-flagged tiles in its surrounding.", 30, "Times New Roman", 500, 630)
                Guide_Next_2 = Guide.tutorial_handling()
                if tutorial_completed:
                    break
                if Guide_Next_2 == "back":
                    Guide_Next_1 = ""
                while Guide_Next_2 == "forward":
                    Guide.create_image(screen, images["tut_vid_ss"], 222, 133)
                    videos["tut_vid"].draw(screen, (235, 135), force_draw = True)
                    videos["tut_vid"].resume()
                    Guide.create_label(screen, "Middle-Click (Chord) Example", 40, "Times New Roman", 500, 210)
                    Guide.create_label(screen, "Whenever a blank tile is revealed it automatically does the same thing", 30, "Times New Roman", 500, 510)
                    Guide.create_label(screen, "as middle-clicking.", 30, "Times New Roman", 500, 550)
                    Guide_Next_3 = Guide.tutorial_handling()
                    if tutorial_completed:
                        break
                    if Guide_Next_3 == "back":
                        videos["tut_vid"].pause()
                        Guide_Next_2 = ""
                    while Guide_Next_3 == "forward":
                        videos["tut_vid"].pause()
                        Guide.create_image(screen, images["tutp"], 260, 146)
                        Guide.create_label(screen, "Pausing", 40, "Times New Roman", 500, 210)
                        Guide.create_label(screen, "Clicking the 'esc' key at anytime during gameplay brings up the pause menu.", 30, "Times New Roman", 500, 256)
                        Guide.create_label(screen, "Clicking 'Resume' takes you back to your board", 30, "Times New Roman", 500, 580)
                        Guide.create_label(screen, "Clicking 'Back to Menu' brings you back to the main menu", 30, "Times New Roman", 500, 620)
                        Guide_Next_4 = Guide.tutorial_handling()
                        if tutorial_completed:
                            break
                        if Guide_Next_4 == "back":
                            videos["tut_vid"].resume()
                            Guide_Next_3 = ""
                        while Guide_Next_4 == "forward":
                            screen.fill(white)
                            Guide.create_label(screen, "Practise Time!", 40, "Times New Roman", 500, 210)
                            Guide.create_label(screen, "You will now play some practise games.", 30, "Times New Roman", 500, 510)
                            Guide.create_label(screen, "Be sure you understand the tutorial before clicking", 30, "Times New Roman", 500, 550)
                            Guide.create_label(screen, "ahead as you can't come back!", 30, "Times New Roman", 500, 590)
                            Guide_Next_5 = Guide.tutorial_handling()
                            if tutorial_completed:
                                break
                            if Guide_Next_5 == "back":
                                Guide_Next_4 = ""
                            if Guide_Next_5 == "forward":
                                gameplay(10,9,9,"tutorial1")
                                                                
    while choice == "Account" and user == "":
        account_screen.create_title(screen, "Account", 70, "Times New Roman", 500, 300, True)
        account_screen.create_button(screen, "Create Account", mid_width - 100, mid_height - 20)
        account_screen.create_button(screen, "Login", mid_width - 100, mid_height + 40)
        account_screen.create_button(screen, "Return", mid_width - 100, mid_height + 100)
        pygame.display.flip()
        account_choice = account_screen.menu_handling()
        if account_choice == "Create Account" and ca_first:
            create_account_screen.create_button(screen, "Return", mid_width - 150, 500, 120, 40)
            create_account_screen.create_button(screen, "Submit", mid_width + 30, 500, 120, 40)
            create_account_screen.create_box(screen, 350, 150)
            create_account_screen.create_box(screen, 350, 220)
            create_account_screen.create_box(screen, 350, 290)
        while account_choice == "Create Account":
            create_account_screen.create_title(screen, "Create Account", 24, "Times New Roman", 500, 200, True)
            create_account_screen.create_heading(screen, "Username", 301, 305)
            create_account_screen.create_heading(screen, "Min 3 characters", 732, 305)
            create_account_screen.create_heading(screen, "Password", 304, 375)
            create_account_screen.create_heading(screen, "Min 3 characters & a number", 794, 375)
            create_account_screen.create_heading(screen, "Confirm Password", 260, 445)
            create_account_screen.create_heading(screen, "Must match password", 757, 445)
            create_account_screen.draw_box(screen)
            create_account_screen.draw_text(screen, [False, True, True])
            if message:
                message_text = FONT.render(message, True, (255, 0, 0))
                screen.blit(message_text, (mid_width - message_text.get_width() // 2, 350))
            pygame.display.flip()
            create_account_choice = create_account_screen.text_menu_handling()      
            while create_account_choice == "Submit":
                message = ""
                new_account = create_account_screen.return_values()
                if SQL.check_for_username(new_account[0]) == []:
                    pass
                else:
                    message = "Username taken"
                    create_account_choice = ""
                if is_valid_password(new_account[1]):
                    pass
                else:
                    message = "Invalid Password"
                    create_account_choice = ""
                if new_account[1] == new_account[2]:
                    pass
                else:
                    message = "Passwords do not match"
                    create_account_choice = ""
                if is_valid_username(new_account[0]):
                    pass
                else:
                    message = "Invalid Username"
                    create_account_choice = ""
                if create_account_choice == "Submit":
                    SQL.insert_account(new_account[0], new_account[1], tutorial_completed)
                    account = SQL.get_user(new_account[0])
                    user = account[0]
                    tutorial_completed = account[2]
                    create_account_choice = "Return"
            if create_account_choice == "Return":
                create_account_screen.clear_boxes()
                message = ""
                account_choice = ""
                ca_first = False
        if account_choice == "Login" and l_first:
            login_screen.create_button(screen, "Return", mid_width - 150, 400, 120, 40)
            login_screen.create_button(screen, "Submit", mid_width + 30, 400, 120, 40)
            login_screen.create_box(screen, 350, 150)
            login_screen.create_box(screen, 350, 220)
        while account_choice == "Login":
            login_screen.create_title(screen, "Login", 24, "Times New Roman", 500, 200, True)
            login_screen.create_heading(screen, "Username", 301, 305)
            login_screen.create_heading(screen, "Password", 304, 375)
            login_screen.draw_box(screen)
            login_screen.draw_text(screen, [False, True])
            if message:
                message_text = FONT.render(message, True, (255, 0, 0))
                screen.blit(message_text, (mid_width - message_text.get_width() // 2, 350))
            pygame.display.flip()
            login_choice = login_screen.text_menu_handling()
            while login_choice == "Submit":
                message = ""
                logged_account = login_screen.return_values()
                if SQL.check_password(logged_account[0], logged_account[1]):
                    pass
                elif SQL.check_password(logged_account[0], logged_account[1]) == "error":
                    login_choice = ""
                else:
                    message = "Username/Password does not match"
                    login_choice = ""
                if is_valid_password(logged_account[1]):
                    pass
                else:
                    message = "Invalid Password"
                    login_choice = ""
                if SQL.check_for_username(logged_account[0]) != []:
                    pass
                else:
                    message = "Invalid Username"
                    login_choice = ""
                if is_valid_username(logged_account[0]):
                    pass
                else:
                    message = "Invalid Username"
                    login_choice = ""
                if login_choice == "Submit":
                    account = SQL.get_user(logged_account[0])
                    user = account[0]
                    tutorial_completed = account[2]
                    login_choice = "Return"
            if login_choice == "Return":
                login_screen.clear_boxes()
                message = ""
                account_choice = ""
                l_first = False
        if account_choice == "Return":
            choice = ""
    
    while choice == "Account" and user != "":
        logged_account_screen.create_title(screen, "Account", 70, "Times New Roman", 500, 300, True)
        logged_account_screen.create_button(screen, "View Account", mid_width - 100, mid_height - 20)
        logged_account_screen.create_button(screen, "Logout", mid_width - 100, mid_height + 40)
        logged_account_screen.create_button(screen, "Return", mid_width - 100, mid_height + 100)
        pygame.display.flip()
        logged_account_choice = logged_account_screen.menu_handling()
        if logged_account_choice == "View Account":
            account = SQL.get_user(user)
            winloss = round(account[6], 1)
            avg = SQL.get_average(user)
            try:
                average = round(avg[0], 2)
            except:
                average = "no scores yet"
        while logged_account_choice == "View Account":
            view_account_screen.create_title(screen, "Hello " + user, 70, "Times New Roman", 500, 200, True)
            view_account_screen.create_title(screen, "Total wins: " + str(account[4]) , 30, "Times New Roman", 500, 400, False) 
            view_account_screen.create_title(screen, "Total losses: " + str(account[5]) , 30, "Times New Roman", 500, 440, False)
            view_account_screen.create_title(screen, "Winloss: " + str(winloss) , 30, "Times New Roman", 500, 480, False)
            view_account_screen.create_title(screen, "Average time: " + str(average) , 30, "Times New Roman", 500, 520, False)
            view_account_screen.create_title(screen, "Created: " + account[3] , 30, "Times New Roman", 500, 600, False)
            view_account_screen.create_button(screen, "Return", mid_width - 100, mid_height + 200)
            pygame.display.flip()
            view_account_choice = view_account_screen.menu_handling()
            if view_account_choice == "Return":
                logged_account_choice = ""
        while logged_account_choice == "Logout":
            logout_screen.create_title(screen, "Are you sure?", 70, "Times New Roman", 500, 300, True)
            logout_screen.create_button(screen, "Return", mid_width - 150, 400, 120, 40)
            logout_screen.create_button(screen, "Logout", mid_width + 30, 400, 120, 40)
            pygame.display.flip()
            logout_screen_choice = logout_screen.menu_handling()
            if logout_screen_choice == "Return":
                logged_account_choice = ""
            elif logout_screen_choice == "Logout":
                user = ""
                tutorial_completed = False 
                logged_account_choice = ""
        if logged_account_choice == "Return":
            choice = ""
    
    while choice == "Settings":
        settings_screen.create_title(screen, "Settings", 70, "Times New Roman", 500, 300, True)
        settings_screen.create_button(screen, "Change controls", mid_width - 100, mid_height - 20)
        settings_screen.create_button(screen, "Revert controls", mid_width - 100, mid_height + 40)
        settings_screen.create_button(screen, "Unmute" if muted else "Mute", mid_width - 100, mid_height + 100)
        settings_screen.create_button(screen, "Reset Tutorial", mid_width - 100, mid_height + 160)
        settings_screen.create_button(screen, "Return", mid_width - 100, mid_height + 220)
        pygame.display.flip()
        settings_choice = settings_screen.menu_handling()
        while settings_choice == "Change controls":
            controls_screen.create_title(screen, "Change controls", 24, "Times New Roman", 500, 200, True)
            controls_screen.create_heading(screen, "Current: " + control_display(controls.get("Pause")), 600, 378)
            controls_screen.create_button(screen, "Pause", mid_width - 150, 220, 140, 40)
            controls_screen.create_button(screen, "Return", mid_width - 100, mid_height + 220)
            pygame.display.flip()
            controls_choice = controls_screen.menu_handling()
            while controls_choice == "Pause":
                controls["Pause"] = change_control()
                controls_choice = ""
            if controls_choice == "Return":
                settings_choice = ""
        if settings_choice == "Revert controls":
            controls = {"Pause": pygame.K_ESCAPE}
        if settings_choice == "Mute" or settings_choice == "Unmute":
            muted = not muted
        if settings_choice == "Reset Tutorial":
            tutorial_completed = False
        if settings_choice == "Return":
            choice = ""
        
    if choice == "Quit":
        pygame.quit()
        sys.exit()
    pygame.display.flip()