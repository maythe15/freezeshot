import screeninfo
import mouse
import PIL.ImageGrab as imggrab

mx, my = mouse.get_position()
mnum = -1

for m in screeninfo.get_monitors():
    cx1 = m.x
    cy1 = m.y
    cx2 = m.width + cx1
    cy2 = m.height + cy1
    mnum += 1
    if cx2 > mx > cx1 and cy2 > my > cy1:
        break

img = imggrab.grab((cx1, cy1, cx2, cy2))

import os
os.environ.update({'PYGAME_HIDE_SUPPORT_PROMPT': '1'})
import pygame
pygame.init()
disp = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, display=pygame.display.get_num_displays() - mnum - 1)
pg_image = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

waiting_for_complete = True
selecting_region = False
r_sx = 0
r_xy = 0
r_ex = 0
r_ey = 0

min_size = 10

while waiting_for_complete:
    disp.blit(pg_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                selecting_region = True
                r_sx, r_sy = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                selecting_region = False
                r_ex, r_ey = pygame.mouse.get_pos()
                if min(abs(r_ex - r_sx), abs(r_ey - r_sy)) >= 10:
                    waiting_for_complete = False

    if selecting_region:
        overlay = pygame.Surface(disp.get_size(), pygame.SRCALPHA)
        lx, ly = pygame.mouse.get_pos()
        minsx, maxsx = min(r_sx, lx), max(r_sx, lx)
        minsy, maxsy = min(r_sy, ly), max(r_sy, ly)

        sx, sy = disp.get_size()
        pygame.draw.rect(overlay, (100, 100, 255, 50), (0, 0, sx, minsy))
        pygame.draw.rect(overlay, (100, 100, 255, 50), (0, maxsy, sx, sy - maxsy))
        pygame.draw.rect(overlay, (100, 100, 255, 50), (0, minsy, minsx, maxsy - minsy))
        pygame.draw.rect(overlay, (100, 100, 255, 50), (maxsx, minsy, sx - minsx, maxsy - minsy))
        pygame.draw.rect(overlay, (100, 100, 255, 200), (minsx, minsy, maxsx - minsx, maxsy - minsy), 1)
        disp.blit(overlay, (0, 0))

    pygame.display.update()

region_img = img.crop((min(r_sx, r_ex), min(r_sy, r_ey), max(r_sx, r_ex), max(r_sy, r_ey)))

region_img.save('clip.png')
os.system(f'notify-send "Screenshot saved" "Saved region screenshot" -i "{os.path.dirname(os.path.abspath(__file__))}/clip.png"')
os.system(f'cat clip.png | xclip -selection clipboard -target image/png -i')
os.remove('clip.png')
