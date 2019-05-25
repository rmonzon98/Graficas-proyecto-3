"""
Raúl Alejandro Monzon Solís
17014
Universidad del Valle de Guatemala
Proyecto 3: Raycaster
"""

import sys, os, pygame, time
from pygame.locals import *
from math import *  

#Colores
map_color     = (192,192,192)
floor_color   = (34,155,70)
ceiling_color = (34,42,155)


#Sprites y bmps
path = os.path.join(os.path.split(__file__)[0], 'data')
texture = pygame.image.load(os.path.join(path, 'pared.bmp'))

player_v={
    "x":70,
    "y":70,
    "a":pi/3,
    "fov":pi/3
    }
    
WIDTH    = 1360
HEIGHT   = 768
map_size = int((WIDTH / 680) * 64)
FPS      = 60
rotate_speed   = 0.01
move_speed     = 0.05
strafe_speed   = 0.04
wall_height    = 1.27
resolution     = 6


pygame.init()

screen   = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
pygame.display.set_caption("Proyecto 3 Graficas Raul Monzon")
pygame.mouse.set_visible(False)

texWidth  = texture.get_width()
texHeight = texture.get_height()
texArray  = pygame.PixelArray(texture)

old = 0


#Crear nivel, a partir del Level.txt
def create_level(file):
    f = open(os.path.join(path, file), 'r')
    file = f.readlines()

    for i, line in enumerate(file):
        file[i] = list(line.rstrip('\n'))
        for j, char in enumerate(file[i]):
            if char == ' ':
                file[i][j] = 0
            else:
                file[i][j] = int(char)
    f.close()

    mapBoundX  = len(file)
    mapBoundY  = len(file[0])
    mapGrid    = []

    for i, line in enumerate(file):
        mapGrid.append([])
        for j, char in enumerate(file[i]):
            if char != 0:
                mapGrid[i].append(char)
            else:
                mapGrid[i].append(0)

    return mapBoundX, mapBoundY, mapGrid

#Funcion para salir
def Quit():
    pygame.quit()
    sys.exit()



#Main
def main():
    mapBoundX, mapBoundY, mapGrid = create_level('Level.txt')
    pygame.mixer.music.load(os.path.join(path, 'music.mp3'))
    pygame.mixer.music.play(2,0.0)

    posX = 8.5
    posY = 10.5
    dirX = 1.0
    dirY = 0.0
    planeX = 0.0
    planeY = 0.66

    non_players =[
        {
            "x": 100,
            "y": 200,
            "texture": pygame.image.load(os.path.join(path,'sprite1.png'))
        },
        {
            "x": 280,
            "y": 190,
            "texture": pygame.image.load(os.path.join(path,'sprite2.png'))
        },
        {
            "x": 225,
            "y": 340,
            "texture": pygame.image.load(os.path.join(path,'sprite3.png'))
        }
    ]

    
    sprite1=[
        {
            "x":100,
            "y":200,
            "texture":pygame.image.load(os.path.join(path,'sprite1.png'))
        }
    ]
    zBuffer    = []
    zbuffer = [-float('inf') for z in range(0, 500)]

    
    
    while True:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                Quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Quit()
                    return

        #Techo y piso
        pygame.draw.rect(screen,ceiling_color,(0,0, WIDTH,(HEIGHT - map_size)/2))
        pygame.draw.rect(screen,floor_color,(0,(HEIGHT-map_size)/2,WIDTH,(HEIGHT-map_size)/2))

        for x in range(0, WIDTH, resolution):
            #Situación inicial
            cameraX = 2*x/WIDTH-1
            rayPosX = posX
            rayPosY = posY
            rayDirX = dirX+planeX*cameraX+0.000000000000001
            rayDirY = dirY+planeY*cameraX+0.000000000000001

            
            mapX = int(rayPosX)
            mapY = int(rayPosY)

            
            deltaDistX = sqrt(1 + rayDirY ** 2 / rayDirX ** 2)
            deltaDistY = sqrt(1 + rayDirX ** 2 / rayDirY ** 2)
            

            #Calcular pasos
            if rayDirX < 0:
                stepX = -1
                sideDistX = (rayPosX - mapX) * deltaDistX
            else:
                stepX = 1
                sideDistX = (mapX + 1 - rayPosX) * deltaDistX

            if rayDirY < 0:
                stepY = -1
                sideDistY = (rayPosY - mapY) * deltaDistY
            else:
                stepY = 1
                sideDistY = (mapY + 1 - rayPosY) * deltaDistY

            #Analizador diferencial digital
            while True:
                if sideDistX < sideDistY:
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = 0
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = 1
                if mapX >= mapBoundX or mapY >= mapBoundY or mapX < 0 or mapY < 0 or mapGrid[mapX][mapY] > 0:
                    break
                
            if side == 0:
                rayLength = (mapX - rayPosX + (1 - stepX) / 2) / rayDirX
            else:
                rayLength = (mapY - rayPosY + (1 - stepY) / 2) / rayDirY

            #Calcular la longitud de la linea para dibujar en la pantalla
            lineHeight = (HEIGHT / rayLength) * wall_height

            drawStart  = -lineHeight / 2 + (HEIGHT - map_size) / 2
            drawEnd    =  lineHeight / 2 + (HEIGHT - map_size) / 2

            if side == 0:
                wallX = rayPosY + rayLength * rayDirY
            else:
                wallX = rayPosX + rayLength * rayDirX
            wallX = abs((wallX - floor(wallX)) - 1)
            
            texX = int(wallX * texWidth)
            if side == 0 and rayDirX > 0:
                texX = texWidth - texX - 1
            if side == 1 and rayDirY < 0:
                texX = texWidth - texX - 1
            
            for y in range(texHeight):
                
                if drawStart + (lineHeight / texHeight) * (y + 1) < 0:
                    continue
                if drawStart + (lineHeight / texHeight) * y > HEIGHT - map_size:
                    break
                
                color = pygame.Color(texArray[texX][y])
                pygame.draw.line(screen, color, (x, drawStart + (lineHeight / texHeight) * y), (x, drawStart + (lineHeight / texHeight) * (y + 1)), resolution)

        #Renderizar barra de Abajo
        HUD = pygame.image.load(os.path.join(path, 'HUD.png'))
        HUD = pygame.transform.scale(HUD, (int(HUD.get_width() * (map_size / 64)), int(HUD.get_height() * (map_size / 64))))
        hand = pygame.image.load(os.path.join(path, 'player2.png'))
        screen.blit(HUD, (0, HEIGHT - map_size))

        """
        #Renderizar sprites
        for non_player in non_players:
            screen.set_at((non_player["x"], non_player["y"]), (0,0,0))

            sprite_a = atan2(non_player["y"] - player_v["y"], non_player["x"] - player_v["x"])
            sprite_d = ((player_v["x"] - non_player["x"])**2 + (player_v["y"] - non_player["y"])**2)**0.5
            sprite_size = (500/sprite_d) * 70

            sprite_x = 500 + (sprite_a - player_v["a"])*500/player_v["fov"] + 250 - sprite_size/2
            sprite_y = 250 - sprite_size/2
    
            sprite_x = int(sprite_x)
            sprite_y = int(sprite_y)
            sprite_size = int(sprite_size)
    
            for x in range(sprite_x, sprite_x + sprite_size):
                for y in range(sprite_y, sprite_y + sprite_size):
                    if 500 < x < 1000 and zbuffer[x - 500] >= sprite_d:
                        tx = int((x - sprite_x) * 128/sprite_size)
                        ty = int((y - sprite_y) * 128/sprite_size)
                        c = non_player["texture"].get_at((tx, ty))
                        if c != (152, 0, 136, 255):
                            screen.set_at((124, 124), c)
                            #zBuffer[x-500] = sprite_d
        
        

        screen.set_at((sprite1[0]["x"], sprite1[0]["y"]), (0,0,0))
        sprite_a = atan2(sprite1[0]["y"] - player_v["y"], sprite1[0]["x"] - player_v["x"])
        sprite_d = ((player_v["x"] - sprite1[0]["x"])**2 + (player_v["y"] - sprite1[0]["y"])**2)**0.5
        sprite_size = (500/sprite_d) * 70

        sprite_x = 500 + (sprite_a - player_v["a"])*500/player_v["fov"] + 250 - sprite_size/2
        
        sprite_y = 250 - sprite_size/2
        

        sprite_x = int(sprite_x)
        sprite_y = int(sprite_y)
        sprite_size = int(sprite_size)
        

        for x in range(sprite_x, sprite_x + sprite_size):
            for y in range(sprite_y, sprite_y + sprite_size):
                if 500 < x < 1000 and zbuffer[x - 500] >= sprite_d:
                    tx = int((x - sprite_x) * 128/sprite_size)
                    ty = int((y - sprite_y) * 128/sprite_size)
                    c = sprite1["texture"].get_at((tx, ty))
                    if c != (152, 0, 136, 255):
                        screen.set_at((x,y), c)
                        #zBuffer[x-500] = sprite_d
        """
        #Personaje
        for x_hand in range(616,872):
            for y_hand in range (244,500):
                tx=int ((x_hand - 616) * 32/256)
                ty=int ((y_hand - 244) * 32/256)
                c=hand.get_at((tx,ty))
                if c!=(152, 0, 136, 255):
                    screen.set_at((x_hand,y_hand),c)

        #Mini mapa            
        for x in range(mapBoundX):
            for y in range(mapBoundY):
                if mapGrid[y][x] != 0:
                    pygame.draw.rect(screen, map_color, ((x * (map_size / mapBoundX) + WIDTH) - map_size, y * (map_size / mapBoundY) + HEIGHT - map_size, (map_size / mapBoundX), (map_size / mapBoundY)))

        pos_on_map = (posY * (map_size / mapBoundY) + WIDTH - map_size, posX * (map_size / mapBoundX) + HEIGHT - map_size)

        #Triangulo que representa la vista en el mini mapa
        pygame.draw.rect(screen, (  0, 255,   0), pos_on_map + (2, 2))
        pygame.draw.line(screen, (255,   0, 127), pos_on_map, ((dirY + posY + planeY) * (map_size / mapBoundY) + WIDTH - map_size, (dirX + posX + planeX) * (map_size / mapBoundX) + HEIGHT - map_size))
        pygame.draw.line(screen, (255,   0, 127), pos_on_map, ((dirY + posY - planeY) * (map_size / mapBoundY) + WIDTH - map_size, (dirX + posX - planeX) * (map_size / mapBoundY) + HEIGHT - map_size))
        pygame.draw.line(screen, (255,   0, 127), ((dirY + posY + planeY) * (map_size / mapBoundY) + WIDTH - map_size, (dirX + posX + planeX) * (map_size / mapBoundX) + HEIGHT - map_size), ((dirY + posY - planeY) * (map_size / mapBoundY) + WIDTH - map_size, (dirX + posX - planeX) * (map_size / mapBoundY) + HEIGHT - map_size))

        #Teclas para mover al personaje
        keys = pygame.key.get_pressed()

        #Mover hacia adelante
        if keys[K_w]:
            if not mapGrid[int(posX + dirX * move_speed)][int(posY)]:
                posX += dirX * move_speed
            if not mapGrid[int(posX)][int(posY + dirY * move_speed)]:
                posY += dirY * move_speed

        #Mover a la derecha
        if keys[K_a]:
            if not mapGrid[int(posX + dirY * strafe_speed)][int(posY)]:
                posX += dirY * strafe_speed
            if not mapGrid[int(posX)][int(posY - dirX * strafe_speed)]:
                posY -= dirX * strafe_speed

        #Mover hacia atras
        if keys[K_s]:
            if not mapGrid[int(posX - dirX * move_speed)][int(posY)]:
                posX -= dirX * move_speed
            if not mapGrid[int(posX)][int(posY - dirY * move_speed)]:
                posY -= dirY * move_speed

        #Mover a la izquierda
        if keys[K_d]:
            if not mapGrid[int(posX - dirY * strafe_speed)][int(posY)]:
                posX -= dirY * strafe_speed
            if not mapGrid[int(posX)][int(posY + dirX * strafe_speed)]:
                posY += dirX * strafe_speed

        #Ver hacia la izquierda y derecha con la letra q y e
        difference = pygame.mouse.get_pos()[0] - (WIDTH / 2)
        
        if keys[K_q]:
            difference = -5
        if keys[K_e]:
            difference = 5
        
        pygame.mouse.set_pos([WIDTH / 2, HEIGHT / 2])

        #Vector de rotacion
        if difference != 0:
            cosrot = cos(difference * rotate_speed)
            sinrot = sin(difference * rotate_speed)
            old    = dirX
            dirX   = dirX * cosrot - dirY * sinrot
            dirY   = old  * sinrot + dirY * cosrot
            old    = planeX
            planeX = planeX * cosrot - planeY * sinrot
            planeY = old    * sinrot + planeY * cosrot

        pygame.display.update()

if __name__=="__main__": main()
