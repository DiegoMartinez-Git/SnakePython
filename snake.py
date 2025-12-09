import sys, tty, termios
import threading
import time
 
key_pressed=""
 
 
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
                    key_pressed = "Arriba"
                elif ch1.lower() == 's':   # S = Abajo
                    key_pressed = "Abajo"
                elif ch1.lower() == 'a':   # A = Izquierda
                    key_pressed = "Izquierda"
                elif ch1.lower() == 'd':   # D = Derecha
                    key_pressed = "Derecha"
                    
            # 3. SALIR
                elif ch1.lower() == 'q':
                    key_pressed = "Q" 
                      
                    
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    key_thread = threading.Thread(target=read_keyboard, daemon=True)
    key_thread.start()
    return key_thread
 
 
# EMPEZAR A CAPTURAR TECLADO:
start_keyboard()
try:
    while True:
        if key_pressed == "Q":
            print("Has pulsado la Q, adios.")
            break;
        print(key_pressed)
        time.sleep(0.1)
except KeyboardInterrupt:
    # Esto captura si el usuario hace Ctrl+C a lo bruto
    pass
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print("Terminal restaurada. adios.")


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
 
# CONFIG 
lines = 15                                      # MAP SIZE LINES
columns = 50                                    # MAP SIZE COLUMNS
 
# VARIABLES THREAD MODIFIED
key_pressed = "R"                               # USER LAST KEY PRESSED