import pygame
from auxiliar.functions import game_state


# ATTRIBUTES
# name(name): character's name
# STRENGTH(stg)
# weapon(wpn): damage deal by strength-based attacks
# armor(arm): % damage reduced by each attack
# life(life): character's health. when its reach 0, is defeated
# MAGIC(mgc)
# mana(mna): energy needed to use powers
# spell(spl): damage deal by magic-based attacks
# dodge(ddg): defense to avoid attacks
# SPIRIT(spt)
# speed(spd): number of actions you can do each round
# attack(atk): attack that must hit dodge
# critical(crt): chance to double damage


#iniciar o pygame
pygame.init()

#criar a tela
screen = pygame.display.set_mode((740, 360))

#titulo e icone
pygame.display.set_caption('The Seven Deadly Sins')
icon = pygame.image.load('imagens\icon.png')
pygame.display.set_icon(icon)


# game loop
while True:
    game_state.state_manager()

