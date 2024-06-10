import serial
import threading
import pygame
import time

pygame.init()
pygame.mixer.init()

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

away_sound = pygame.mixer.Sound("BuzzerSystem/buzz.mp3")
home_sound = pygame.mixer.Sound("BuzzerSystem/TACODING.mp3")

lockout = False
first_to_buzz = None
reset_by_host = False

def read_from_port(port):
    global lockout, first_to_buzz, reset_by_host
    
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        
        while True:
            if ser.in_waiting > 0:
                try:
                    data = ser.readline().decode('utf-8', errors='ignore').rstrip().upper()
                    process_buzzer_press(data)
                except UnicodeDecodeError as e:
                    print(f"Error decoding data from {port}: {e}")

    except serial.SerialException as e:
        print(f"Error opening or reading from serial port {port}: {e}")
    except Exception as e:
        print(f"Unexpected error on {port}: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def process_buzzer_press(data):
    global lockout, first_to_buzz, reset_by_host
    

    if "HOST" in data:
        if not reset_by_host:
            lockout = False
            first_to_buzz = None
            reset_by_host = True
        else:
            reset_by_host = False
        return
    
    if "HOME" in data or "AWAY" in data:
        if lockout:
            return
        
        number = None
        for char in data:
            if char.isdigit():
                number = int(char)
                break
        
        if number is not None:
            if first_to_buzz is None:
                first_to_buzz = f"{data} {number}"
                lockout = True
                if "AWAY" in data:
                    away_sound.play()
                elif "HOME" in data:
                    home_sound.play()
    else:
        print("Unknown Response: 100")

def update_ui(screen):
    global lockout, first_to_buzz
    
    screen.fill(BLACK)
    
    if first_to_buzz is not None:
        text = f"{first_to_buzz} buzzed"
        color = RED 
    else:
        text = "System open for buzzing"
        color = GREEN if not lockout else RED
    
    font = pygame.font.Font(None, 36)
    text_render = font.render(text, True, color)
    
    text_rect = text_render.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    
    screen.blit(text_render, text_rect)
    
    pygame.display.flip()

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Buzzer System")
    
    port1 = '/dev/cu.usbserial-2140'  
    port2 = '/dev/cu.usbserial-2120'  

    thread1 = threading.Thread(target=read_from_port, args=(port1,))
    thread2 = threading.Thread(target=read_from_port, args=(port2,))
    
    thread1.start()
    thread2.start()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        update_ui(screen)
        
        time.sleep(0.1)
    
    pygame.quit()
