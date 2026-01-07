import sys, tty, termios
import threading
import time
import random

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
C_C="\033[36m"

COLOR_LIST=[C_G,C_R,C_Y,C_LR,C_B,C_M,C_C]                             

init_snake = [(20,20), (20,21), (20,22), (20,23), (20,24),(20,25),(20,26)]

# CONFIG 
lines = 30                                      # MAP SIZE LINES
columns = 80                                    # MAP SIZE COLUMNS

# VARIABLES THREAD MODIFIED
key_pressed = "L"                               # USER LAST KEY PRESSED
game_speed = 5
move_delay = 0.1


fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def start_keyboard():

    def read_keyboard():
        global key_pressed, game_speed, move_delay
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
                elif ch1 == '+':
                    if game_speed < 20:
                        game_speed += 1
                        move_delay = max(0.01, move_delay - 0.01)
                elif ch1 == '-':
                    if game_speed > 1:
                        game_speed -= 1
                        move_delay += 0.01
                #para el juego
                elif ch1.lower() == 'p':
                    key_pressed = "P"
                elif ch1.lower() == 'q':
                    key_pressed = "Q" 
                      
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    key_thread = threading.Thread(target=read_keyboard, daemon=True)
    key_thread.start()
    return key_thread


def draw_map():
    print(f"""{C_B }
                                                                                     
▄▄▄▄▄▄▄               ▄▄                   ▄▄▄▄▄▄▄                                  
███▀▀███▄        ██   ██                   █████▀▀▀             ▄▄           
███▄▄███▀ ██ ██ ▀██▀▀ ████▄ ▄███▄ ████▄    ▀████▄  ████▄  ▀▀█▄ ██ ▄█▀ ▄█▀█▄ 
███▀▀▀▀   ██▄██  ██   ██ ██ ██ ██ ██ ██      ▀████ ██ ██ ▄█▀██ ████   ██▄█▀ 
███        ▀██▀  ██   ██ ██ ▀███▀ ██ ██   ███████▀ ██ ██ ▀█▄██ ██ ▀█▄ ▀█▄▄▄ 
            ██                                                                  
          ▀▀▀                                                       DAW 2025                                                                             
{S_R}""")
    print("┌" + "─"*columns + "┐")

    for _ in range(lines):
        print("│" + " "*columns + "│")

    print("└" + "─"*columns + "┘")


    return {"U": 14, "D": 14+lines, "L":2, "R":1+columns}

def move_cursor(line, column):
    print(f"\033[{line};{column}H", end="")

def draw_snake(snake):
    for f,c in snake:
        move_cursor(f,c)
        print(f"{C_G}■{S_R}", end="")


def end_game(jugador=None, puntuacion=None):
    if jugador is not None and puntuacion is not None:
        save_score(jugador, puntuacion)
    print(CLEAR_SCREEN)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    draw_map()
    load_score()
    terminal_restaurar()
    
    
def check_collision(snake, map_limits):
    head = snake[0]
    if head[0] < map_limits["U"]-1 or head[0] >= map_limits["D"]-1 or head[1] < map_limits["L"] or head[1] > map_limits["R"]:
        return True
    if head in snake[1:]:
        return True
    return False

def mov_snake(snake, direction):
    global move_delay
    mov = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    tail = snake.pop()
    head = snake[0]
    head = (head[0] + mov[direction][0], head[1] + mov[direction][1])
    snake.insert(0, head)
    
    move_cursor(*head)
    if(direction=="U" or direction=="D"):
         print(f"{C_G}█{S_R}", end="")
         time.sleep(move_delay * 1.2)
    else:
         print(f"{C_G}■{S_R}", end="")
         time.sleep(move_delay)

    if len(snake) > 2:
        anterior = (snake[1][0] - snake[2][0], snake[1][1] - snake[2][1])
        if anterior != mov[direction]:
            move_cursor(*snake[1])
            print(f"{C_G}▮{S_R}", end="")  
            time.sleep(move_delay)  
    move_cursor(*tail)
    print("  ", end="")

    return tail

def terminal_restaurar():
        move_cursor(14 + lines + 4, 2)
        print(CURSOR_SHOW)
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)



def load_score():
    try:
        with open("score.txt", "r") as f:
            scores = f.readlines()
            scores = [line.strip().split(": ") for line in scores]
            scores_ordenar = []
            for nombre, puntuaciones in scores:
                scores_ordenar.append((int(puntuaciones), nombre))
            scores_ordenar.sort(reverse=True)
            

        move_cursor(20, 30)
        print(f"{C_B} GAME OVER {S_R}")
        for i, score in enumerate(scores_ordenar[:10], start=1):
            move_cursor(21 + i, 30)
            print(f"🤖 {C_B}{score[1]}: {C_Y}{score[0]}{S_R}")
        print(CURSOR_SHOW)

    except FileNotFoundError:
        move_cursor(20, 30)
        print("No hay puntuaciones guardadas")


def save_score(jugador, score):
    with open("score.txt", "a+") as f:
        f.write(f"{jugador}: {score}\n")
    
def draw_fruit(snake, map_limits):
    while True:
        linea = random.randint(map_limits["U"] + 1, map_limits["D"] - 2)
        columna = random.randint(map_limits["L"] + 1, map_limits["R"] - 2)
        
        if (linea, columna) not in snake:
            move_cursor(linea, columna)
            print(f"{random.choice(COLOR_LIST)}⬤{S_R}") 
            return (linea, columna) 
        

def check_eat(snake, fruit_pos, tail, map_limits):

    if snake[0] == fruit_pos:
        snake.append(tail)
        
        move_cursor(*tail)
        print(f"{C_G}■{S_R}", end="")
        
        new_fruit_pos = draw_fruit(snake, map_limits)
        
        current_score = len(snake) - len(init_snake)
        
        return True, new_fruit_pos, current_score
    
    current_score = len(snake) - len(init_snake)
    return False, fruit_pos, current_score
    

def start_game():
    try:
        
        print(CLEAR_SCREEN)
        map_limits = draw_map() 
        
        move_cursor(lines*2 - 15, 0)
        print(f"{C_LR}Para tener la mejor experiencia pon pantalla completa{S_R}")
        nombre = input("Player Name:")
        
        
        
        print(CLEAR_SCREEN)
        draw_map() 
        
        start_keyboard()
        print(CURSOR_HIDE, end="")
        
        snake = init_snake[:]
        draw_snake(snake) 
        
        fruta = draw_fruit(snake, map_limits)
        
        move_cursor(lines*2 - 15, columns-5)
        print("🤖"+nombre.upper())
        
        score = 0
        
        while True:
            move_cursor(lines + 15, 2) 
            
            print(f"Score: {score} \t\t\t   Speed: {game_speed} 🚀   ")
            
            action = key_pressed

            
            if action == "P":
                move_cursor(lines + 15, 2) 
                print(f"Score: {score} \t\t\t   Speed: {C_LR}Stop 🚀{S_R}   ")
                while action == "P":
                    time.sleep(0.1)
                    action = key_pressed
                    if action != "P":
                        break
            if action == "Q":
                end_game(nombre, score)
                break
            
            old_tail = mov_snake(snake, action)
            
            if check_collision(snake, map_limits):
                end_game(nombre, score)
                break
                
        
            comido, fruta, score = check_eat(snake, fruta, old_tail, map_limits)
    except Exception as e:
        print(f"El juego ha terminado ")
        end_game(nombre, score)

try:
    start_game()
except KeyboardInterrupt:
    print(f"El juego ha por interrupcion(Ctrl+C) ")
    end_game()