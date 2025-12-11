import sys, tty, termios
import threading
import time
 
#Variables Globales:
# COLORS AND CURSOR
CURSOR_HIDE="\033[?25l"                         # HIDE CURSOR
CURSOR_SHOW="\033[?25h"                         # SHOW CURSOR
CLEAR_SCREEN="\033c"                            # CLEAR SCREEN
S_R="\033[0m"                                   # STYLE RESET
S_D="\033[2m"                                   # STYLE DIM
S_B="\033[1m"                                   # STYLE BOLD
R_L="\033[2K"                                   # REMOVE LINE
M_U="\033[A"                                    # MOVE UP 1 LINE
C_G="\033[32m"                                  # COLOR GREEN
C_LG="\033[92m"                                 # COLOR LIGHT GREEN
C_R="\033[31m"                                  # COLOR RED
C_Y="\033[33m"                                  # COLOR YELLOW
C_LR="\033[91m"                                 # COLOR LIGHT RED
C_B="\033[34m"                                  # COLOR BLUE
C_M="\033[35m"                                  # COLOR MAGENTA
C_C="\033[36m"                                  # COLOR CYAN

init_snake = [(5,5), (5,6), (5,7), (5,8), (5,9)]
 
# CONFIG 
lines = 15                                      # MAP SIZE LINES
columns = 50                                    # MAP SIZE COLUMNS
 
# VARIABLES THREAD MODIFIED
key_pressed = "R"                               # USER LAST KEY PRESSED
 
 
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def start_keyboard():
    """
    Capture keystrokes in background using threads:
        Q, P, UP, DOWN, LEFT, RIGHT: save key value in {key_pressed} variable
        +, -: modify {speed} variable in 0.05 steeps
 
    GLOBAL VARIABLES MODIFIED
      {key_pressed}
    """
    def read_keyboard():
        global key_pressed
        try:
            tty.setcbreak(fd)
            #Si la tecla pulsada no es la "q" compruba cual es
            while key_pressed != "q":
                ch1 = sys.stdin.read(1)
                if ch1 == '\x1b':  
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    k = ch1 + ch2 + ch3
                    if k == '\x1b[A':
                        key_pressed = "Arriba"   
                    elif k == '\x1b[B':
                        key_pressed = "Abajo"
                    elif k == '\x1b[C':
                        key_pressed = "Izquierda"
                    elif k == '\x1b[D':
                        key_pressed = "Derecha" 
                #Si en vez de flechas quiere usar "w-a-s-d tambien puede"
                elif ch1.lower() == 'w':   # W = Arriba
                    key_pressed = "U"
                elif ch1.lower() == 's':   # S = Abajo
                    key_pressed = "D"
                elif ch1.lower() == 'a':   # A = Izquierda
                    key_pressed = "L"
                elif ch1.lower() == 'd':   # D = Derecha
                    key_pressed = "R"
                    
            # 3. SALIR
                elif ch1.lower() == 'q':
                    key_pressed = "Q" 
                      
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    key_thread = threading.Thread(target=read_keyboard, daemon=True)
    key_thread.start()
    return key_thread
 

def draw_map():
    print(""" ███████████              █████    █████                              █████████                       █████              
░░███░░░░░███            ░░███    ░░███                              ███░░░░░███                     ░░███               
 ░███    ░███ █████ ████ ███████   ░███████    ██████  ████████     ░███    ░░░  ████████    ██████   ░███ █████  ██████ 
 ░██████████ ░░███ ░███ ░░░███░    ░███░░███  ███░░███░░███░░███    ░░█████████ ░░███░░███  ░░░░░███  ░███░░███  ███░░███
 ░███░░░░░░   ░███ ░███   ░███     ░███ ░███ ░███ ░███ ░███ ░███     ░░░░░░░░███ ░███ ░███   ███████  ░██████░  ░███████ 
 ░███         ░███ ░███   ░███ ███ ░███ ░███ ░███ ░███ ░███ ░███     ███    ░███ ░███ ░███  ███░░███  ░███░░███ ░███░░░  
 █████        ░░███████   ░░█████  ████ █████░░██████  ████ █████   ░░█████████  ████ █████░░████████ ████ █████░░██████ 
░░░░░          ░░░░░███    ░░░░░  ░░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░     ░░░░░░░░░  ░░░░ ░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░  
               ███ ░███                                                                                                  
              ░░██████                                                                                                   
               ░░░░░░                                                                                                    """)
    print("r", "-"*columns, "r")

    for _ in range(lines):
        print("|" + " "*columns + "|")
    print("r", "-"*columns, "r")

    return {"U": 5, "D": 5+lines, "L":2, "R":1+columns}

def move_cursor(line, column):
    """
    Move cursor to specified terminal line and column
    """
    print(f"\033[{line};{column}H", end="")
 
def draw_snake(snake):
    for f,c in snake:
        move_cursor(f,c)
        #CAMBIAR 0 POR CARACTER PARA LA SERPIENTE
        print(f"{C_G}■{S_R}", end="")


def end_game():
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    move_cursor(lines+2, 1)
    print("Game Over")
def check_collision(snake, map_limits):
    head = snake[0]
    if head[0] < map_limits["U"] or head[0] > map_limits["D"] or head[1] < map_limits["L"] or head[1] > map_limits["R"]:
        return True
    if head in head[1:]:
        return True
    return False

def mov_snake(snake, direction):
    mov = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    tail = snake.pop()
    head = snake[0]
    head = (head[0] + mov[direction][0], head[1] + mov[direction][1])
    snake.insert(0, head)
    
    move_cursor(*head)
    print(f"{C_G}■{S_R}", end="")

    move_cursor(*tail)
    print(" ")

# EMPEZAR A CAPTURAR TECLADO:
def start_game():
    start_keyboard()
    print(CURSOR_HIDE, end="")
    #Pinta el mapa y te devuelve los limites y asi se lo podrás pasar a otras funciones
    map_limits = draw_map()
    snake = init_snake[:]
    draw_snake(snake)

    while True:
        time.sleep(0.1)
        action = key_pressed
        mov_snake(snake, action)
        if check_collision(snake, map_limits):
            end_game()
            break

        
        #print(action)
        #Si ponemos mas tiempo el juego irá mas lento
        

    end_game()

start_game()

    

#mover serpiente es añadir una cabeza y quitar la cola