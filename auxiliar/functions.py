from time import sleep
from random import randint, choice
import pygame
import sys

# STATUS if not specified, lasts until end of turn
# 1-paralyzed: cant move
# 2-dazed: cant use reactions
# 3-frightened: -50% attack
# 4-stunned: -50% dodge
# 5-weakened: -50% weapon and spell
# 6-vulnerable: armor set to 0%

# 1-focused: +50% attack
# 2-hasted: +50% dodge
# 3-empowered: +25% weapon and spell
# 4-hardened: armor set to 75%
# 5-deadly: critical set to 75%
# 6-hasted: change speed to 5


screen = pygame.display.set_mode((740, 360))

choicemenu = pygame.image.load('imagens\choicemenu.png')
battleground = pygame.image.load('imagens\sbattleground.png').convert_alpha()
background = pygame.image.load('imagens\sbackground.png')

# character selection
meliodas = pygame.image.load('imagens\meliodas-choice.png').convert_alpha()
escanor = pygame.image.load('imagens\escanor-choice.png').convert_alpha()
ban = pygame.image.load('imagens\sban-choice.png').convert_alpha()
king = pygame.image.load('imagens\king-choice.png').convert_alpha()
merlin = pygame.image.load('imagens\merlin-choice.png').convert_alpha()
diane = pygame.image.load('imagens\diane-choice.png').convert_alpha()
button = pygame.image.load('button.png').convert_alpha()
confirm = pygame.image.load('imagens\confirm.png').convert_alpha()

# character image on battleground
meliodasFighter = pygame.image.load('imagens\meliodas_l.png').convert_alpha()
escanorFighter = pygame.image.load('imagens\escanor_l.png').convert_alpha()
banFighter = pygame.image.load('imagens\sban_l.png').convert_alpha()
kingFighter = pygame.image.load('imagens\king_l.png').convert_alpha()
merlinFighter = pygame.image.load('imagens\merlin_l.png').convert_alpha()
dianeFighter = pygame.image.load('imagens\diane_l.png').convert_alpha()

# objects on battleground
healthBar = pygame.image.load('imagens\health_bar.png').convert_alpha()
manaBar = pygame.image.load('imagens\mana_bar.png').convert_alpha()
skip = pygame.image.load('imagens\skip.png').convert_alpha()
temp_msg = ''
action_pile = [['none']]


def draw_temp(text, x, y):
    font = pygame.font.Font('freesansbold.ttf', 20)
    info = font.render(text, True, (255, 255, 255))
    shadow = font.render(text, True, (0, 0, 0))
    if game_state.action_time != 0:
        if game_state.action_time + 2000 > game_state.current_time:
            screen.blit(shadow, (x + 1, y + 1))
            screen.blit(info, (x, y))


class Fighter:
    def __init__(self, image, name, nick, mgc, stg, spt):
        self.image = image
        self.name = name
        self.nick = nick
        self.mgc = mgc
        self.spl = randint((mgc * 1), (mgc * 4))
        self.ddg = int(50 + mgc * 2.5)
        self.mna = 200 + (mgc * 10)
        self.stg = stg
        self.wpn = randint((stg * 2), (stg * 3))
        self.full_life = 400 + (stg * 20)
        self.full_mana = 200 + (mgc * 10)
        self.arm = int(stg / 2)
        self.spt = spt
        self.atk = 100 + spt * 2
        self.spd = int(spt / 9)
        self.crt = int(spt / 2)
        # 0 = none; 1 = melee; 2 = ranged; 3 = reaction; 4 = move; 5 = ult; 6 = spell; 7 = stance; 256 = ult, spell, ranged
        # 14 = move, melee; 26 = ranged, spell; 16 = melee, spell; 31 = reaction, melee; 34 = move, reaction; 32 = reaction, melee
        # 16 = ult, melee
        self.act = 0
        self.player = 1
        self.position = 1
        self.health_bar = healthBar
        self.mana_bar = manaBar
        self.damage_take = 0
        self.life = 400 + (stg * 20)
        self.full_lifebar = 336
        self.full_manabar = 336
        self.atkRoll = randint(1, 100)
        self.ngt_stt = []
        self.pst_stt = []
        self.paralyzed = False
        self.dazed = False
        self.info1 = (f'    {mgc}                                              {stg}'
                      f'                                           {spt}                                 {400 + (stg * 20)}')
        self.info2 = (f'{int(mgc * 1)} - {int(mgc * 4)}'
                      f'                                     {stg * 2} - {stg * 3}'
                      f'                                      {spt // 2}%                                  {int(50 + mgc * 2.5)}')
        self.info3 = (f' {200 + (mgc * 10)}                                      {100 + spt * 2}'
                      f'                                               {spt // 9}                                          {stg // 2}%')

    def spend_mana(self, cost):
        if self.mna >= cost and cost > 0:
            self.mna -= cost
            percent_spend = (cost * 100) / self.full_mana
            bar_change = int(percent_spend * 3.4)
            if percent_spend > 0:
                self.full_manabar -= bar_change
                self.spd -= 1
                if self.full_manabar <= 0:
                    self.full_manabar = 1
        elif cost < 0:
            bar_change = 34
            if self.mna > self.full_mana:
                self.mna = self.full_mana
            self.full_manabar += bar_change
            if self.full_manabar >= 336:
                self.full_manabar = 336

    def status(self):
        global temp_msg
        if 1 in self.ngt_stt:
            # paralyzed: cant move
            self.paralyzed = True
            temp_msg = 'Enemy got paralyzed'
        elif 2 in self.ngt_stt:
            # dazed: cant use reactions
            self.dazed = True
            temp_msg = 'Enemy got dazed'
        elif 3 in self.ngt_stt:
            # frightened: -50% attack
            self.atk = int(self.atk // 2)
            temp_msg = 'Enemy got frightened'
        elif 4 in self.ngt_stt:
            # stunned: -50% dodge
            self.ddg = int(self.ddg // 2)
            temp_msg = 'Enemy got stunned'
        elif 5 in self.ngt_stt:
            # weakened: -50% weapon and spell
            self.wpn = int(self.wpn // 2)
            self.spl = int(self.spl // 2)
            temp_msg = 'Enemy got weakened'
        elif 6 in self.ngt_stt:
            # vulnerable: armor set to 0
            self.arm = 0
            temp_msg = 'Enemy got vulnerable'
        elif 7 in self.ngt_stt:
            # petrified: speed set to 0
            self.spd = 0
            temp_msg = 'Enemy got petrified'
        elif 1 in self.pst_stt:
            # focused: +50% attack
            self.atk = int(self.atk * 1.5)
            temp_msg = 'You got focused'
        elif 2 in self.pst_stt:
            # empowered: +50% weapon and spell
            self.wpn = int(self.wpn * 1.5)
            self.spl = int(self.spl * 1.5)
            temp_msg = 'You got empowered'
        elif 3 in self.pst_stt:
            # elusive: +50% dodge
            self.ddg = int(self.ddg * 1.5)
            temp_msg = 'You got elusive'
        elif 4 in self.pst_stt:
            # hardened: armor set to 75%
            self.arm = 75
            temp_msg = 'You got elusive'
        elif 5 in self.pst_stt:
            # deadly: critical set to 75%
            self.crt = 75
            temp_msg = 'You got deadly'
        elif 6 in self.pst_stt:
            # hasted: speed set to 5
            full_speed = self.spd // 9
            current_speed = self.spd
            actions_take = full_speed - current_speed
            self.spd = 5 - actions_take
            temp_msg = 'You got hasted'
        draw_temp(temp_msg, 300, 150)

    def critical(self):
        if self.atkRoll >= 100 - self.crt:
            self.wpn *= 2
            self.spl *= 2
            return True
        return False

    def hitChance(self, defense):
        ofense = self.atk
        hit = ofense / defense
        if defense <= ofense:
            res = 100 - (100 / hit * 2 ** (-hit))
            if res > 95:
                res = 95
        else:
            hit = -(defense / ofense)
            res = 100 / 2 ** (-hit)
            if res < 5:
                res = 5
        return int(res)

    def action_reroll(self):
        self.pst_stt = []
        self.act = 0
        self.atk = 100 + self.spt * 2
        self.atkRoll = randint(1, 100)
        self.spl = randint((self.mgc * 1), (self.mgc * 4))
        self.wpn = randint((self.stg * 2), (self.stg * 3))

    def draw_fighter(self):
        if player1.position > 0:
            if self.player == 1:
                screen.blit(self.image, (-100, 0))
            elif self.player == 2:
                flipped = pygame.transform.flip(self.image, True, False)
                screen.blit(flipped, (458, 0))
        else:
            if self.player == 1:
                screen.blit(self.image, (0, 0))
            elif self.player == 2:
                flipped = pygame.transform.flip(self.image, True, False)
                screen.blit(flipped, (358, 0))

    def draw_info(self):
        font = pygame.font.Font('freesansbold.ttf', 20)
        font_act = pygame.font.Font('freesansbold.ttf', 30)
        info = font.render(self.nick, True, (255, 255, 255))
        act_point = font_act.render(str(self.spd), True, (255, 255, 255))
        if self.player == 1:
            screen.blit(info, (10, 192))
            screen.blit(act_point, (16, 12))
        elif self.player == 2:
            screen.blit(info, (500, 192))
            screen.blit(act_point, (706, 12))

    def draw_bar(self):
        life_change = pygame.transform.scale(self.health_bar, (self.full_lifebar, 10))
        mana_change = pygame.transform.scale(self.mana_bar, (self.full_manabar, 10))
        font = pygame.font.Font('freesansbold.ttf', 10)
        health_value = font.render(str(self.life), True, (255, 255, 255))
        mana_value = font.render(str(self.mna), True, (255, 255, 255))
        if self.player == 1:
            screen.blit(mana_change, (6, 225))
            screen.blit(mana_value, (9, 225))
            screen.blit(life_change, (6, 212))
            screen.blit(health_value, (9, 212))
        elif self.player == 2:
            screen.blit(mana_change, (397, 225))
            screen.blit(mana_value, (400, 225))
            screen.blit(life_change, (397, 212))
            screen.blit(health_value, (400, 212))


def turn_reroll(player: Fighter):
    player.pst_stt = []
    player.ngt_stt = []
    player.paralyzed = False
    player.dazed = False
    player.spd = int(player.spt / 9)
    player.atk = 100 + player.spt * 2
    player.spl = randint((player.mgc * 1), (player.mgc * 4))
    player.wpn = randint((player.stg * 2), (player.stg * 3))
    player.melee_ddg = int(50 + player.mgc * 2.5)
    player.ranged_ddg = int(50 + player.mgc * 2.5)
    player.arm = int(player.stg / 2)
    player.crt = int(player.spt / 2)


def life_change(player: Fighter, change):
    player.damage_take = change
    player.life -= player.damage_take
    percent_dam = (player.damage_take * 100) / player.full_life
    bar_change = int(percent_dam * 3.4)
    if 1 > bar_change > 0:
        bar_change = 1
    if bar_change < 0:
        player.full_lifebar -= bar_change
    elif bar_change > 0:
        player.full_lifebar -= bar_change
        if player.full_lifebar <= 0:
            player.full_lifebar = 1


def action_attack(title, p1: Fighter, p2: Fighter, cost, damage, number, spell, melee, bonus1, bonus2, onus, ifhit, ult):
    global temp_msg
    temp_msg = ''
    if ifhit is False:
        p2.ngt_stt.append(onus)
    if ult is True and p1.life > (p1.full_life // 2):
        temp_msg = "YOU CAN'T USE IT NOW!"
    elif ult is True and p1.life <= (p1.full_life // 2) or ult is False:
        if p1.mna >= cost and p1.spd > 0:
            p1.spend_mana(cost)
            # number of attacks
            for attacks in range(0, number):
                p1.pst_stt.append(bonus1)
                p1.pst_stt.append(bonus2)
                p1.action_reroll()
                # attack deals spell damage
                if spell == True:
                    dmg = p1.spl
                else:
                    dmg = p1.wpn
                dmg *= damage
                dmg = int(dmg - (dmg * (p2.arm / 100)))
                hit_chance = p1.hitChance(p2.ddg)
                print(f'Hit chance: {hit_chance}%, {p1.nick}: {p1.atk} x {p2.nick}: {p2.ddg}')
                if melee == True:
                    if player1.position > 0:
                        temp_msg = 'Out of reach!'
                    else:
                        if p1.atkRoll > 100 - hit_chance:
                            if ifhit == True and p1.critical():
                                p2.ngt_stt.append(onus)
                                temp_msg = 'Critical hit!'
                                print(f'{p1.nick} hit a {title} and deal {dmg}!')
                                life_change(p2, dmg)
                            else:
                                p2.ngt_stt.append(onus)
                                print(f'{p1.nick} hit a {title} and deal {dmg}!')
                                life_change(p2, dmg)
                            print(p2.status())
                        else:
                            temp_msg = 'You miss!'
                else:
                    if p1.atkRoll > 100 - hit_chance:
                        if ifhit == True and p1.critical():
                            p2.ngt_stt.append(onus)
                            temp_msg = 'Critical hit!'
                            print(f'{p1.nick} hit a {title} and deal {dmg}!')
                            life_change(p2, dmg)
                        else:
                            p2.ngt_stt.append(onus)
                            print(f'{p1.nick} hit a {title} and deal {dmg}!')
                            life_change(p2, dmg)
                        print(p2.status())
                    else:
                        temp_msg = 'You miss!'
                sleep(0.1)
    print(f'{p1.nick} make a {title}')


def action_reaction(title, p1: Fighter, p2: Fighter, cost, counter, retaliation, move, distance, bonus1, bonus2, ult):
    global temp_msg
    if ult is True and p1.life > (p1.full_life // 2):
        temp_msg = "YOU CAN'T USE IT NOW!"
    elif ult is True and p1.life <= (p1.full_life // 2) or ult is False:
        if p1.mna >= cost and p1.spd > 0:
            p1.spend_mana(cost)
            p1.pst_stt.append(bonus1)
            p1.pst_stt.append(bonus2)
            if move == True:
                player1.position += distance
                if player1.position < 0:
                    player1.position = 0
                if distance < 0:
                    temp_msg = 'You are close!'
                else:
                    temp_msg = 'You are away!'
            elif counter == True:
                p2.act = 0
                temp_msg = 'You counter a power!'
            elif retaliation == True:
                p2.act = 0
                counterattack = 0
                p1.action_reroll()
    #        return counterattack
    print(f'{p1.nick} make a {title}')


def action_move(title, p1: Fighter, cost, move):
    global temp_msg
    if title == 'skip':
        temp_msg = 'Enemy Skip'
    elif p1.mna >= cost and p1.spd > 0:
        p1.spend_mana(cost)
        player1.position += move
        if player1.position < 0:
            player1.position = 0
        if move < 0:
            if player1.position == 0:
                temp_msg = 'You are close!'
            else:
                temp_msg = 'You still far!'
        else:
            temp_msg = 'You are away!'
        p1.action_reroll()
    print(f'{p1.nick} make a {title}')


def action_stance(title, p1: Fighter, p2: Fighter, cost, powerup, heal, bonus1, bonus2, bonus3, onus1, onus2, ult):
    global temp_msg
    if ult is True and p1.life > (p1.full_life // 2):
        temp_msg = "YOU CAN'T USE IT NOW!"
    elif ult is True and p1.life <= (p1.full_life // 2) or ult is False:
        if p1.mna >= cost and p1.spd > 0:
            p1.spend_mana(cost)
            p1.pst_stt.append(bonus1)
            p1.pst_stt.append(bonus2)
            p1.pst_stt.append(bonus3)
            p2.ngt_stt.append(onus1)
            p2.ngt_stt.append(onus2)
            if heal > 0:
                lifegain = int(-(p1.full_life * (heal / 10)))
                life_change(p1, lifegain)
            elif powerup == True:
                life_loss = int(p1.full_life * 0.05)
                life_change(p1, life_loss)
                mana_gain = int(p1.full_mana * 0.1)
                p1.mna += mana_gain
                p1.spend_mana(-mana_gain)
            temp_msg = f'{p1.nick} activate {title}!'
            p1.action_reroll()
    print(f'{p1.nick} make a {title}')


class Button():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(self.x - 53, self.y - 53, self.w, self.h)
        self.click = False
        self.choice = 0

    def draw_image(self, image):
        action = False
        pos = pygame.mouse.get_pos()
        button_rect = image.get_rect(center=(self.x, self.y))
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                self.click = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False
        screen.blit(image, button_rect)
        return action

    def draw_text(self, title, act, gray=False):
        action = False
        player1.act = act
        unleash = title.lower().replace(" ", "_")
        color = (255, 255, 255)
        if gray == True:
            color = (198, 198, 198)
        pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, color, (self.x-53, self.y-53, self.w, self.h), 0)
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render(title, True, (0, 0, 0))
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.click == False:
                self.click = True
                action = True
                add_pile(unleash)
                sleep(0.5)
        if pygame.mouse.get_pressed()[0] == 0:
            self.click = False
        screen.blit(text, (self.x - 53, self.y - 53))
        return action

    def hover(self, image, caps, text1, text2, text3):
        current_image = True
        fontTitle = pygame.font.Font('freesansbold.ttf', 20)
        font = pygame.font.Font('freesansbold.ttf', 16)
        hover_rect = self.rect
        if hover_rect.collidepoint(pygame.mouse.get_pos()):
            current_image = False

        if current_image is not True:
            screen.blit(image, (0, 0, 740, 360))
            title = fontTitle.render(caps, True, (255, 255, 255))
            info1 = font.render(text1, True, (0, 0, 0))
            info2 = font.render(text2, True, (0, 0, 0))
            info3 = font.render(text3, True, (0, 0, 0))
            screen.blit(info1, (60, 283))
            screen.blit(info2, (60, 308))
            screen.blit(info3, (60, 333))
            screen.blit(title, (10, 253))


# BUTTONS
meliodasButton = Button(444, 66, 105, 105)
escanorButton = Button(559, 66, 105, 105)
banButton = Button(668, 66, 105, 105)
kingButton = Button(444, 181, 105, 105)
merlinButton = Button(559, 181, 105, 105)
dianeButton = Button(668, 181, 105, 105)
skip_turn = Button(700, 320, 100, 20)

players = [0, 0]

choice1 = Fighter(meliodasFighter, "Meliodas, Dragon's Sin of Wrath", 'Meliodas', 41, 64, 45)
choice2 = Fighter(escanorFighter, "Escanor, Lion's Sin of Pride", 'Escanor', 20, 100, 30)
choice3 = Fighter(banFighter, "Ban, Fox's Sin of Greed", 'Ban', 45, 41, 64)
choice4 = Fighter(kingFighter, "Harlequinn, Grizzly's Sin of Sloth", 'Harlequinn', 90, 4, 56)
choice5 = Fighter(merlinFighter, "Merlin, Boar's Sin of Glutonny", 'Merlin', 100, 5, 45)
choice6 = Fighter(dianeFighter, "Diane, Serpent's Sin of Envy", 'Diane', 30, 84, 36)


def mouse_over():
    meliodasButton.hover(meliodas, choice1.name, choice1.info1, choice1.info2, choice1.info3)
    escanorButton.hover(escanor, choice2.name, choice2.info1, choice2.info2, choice2.info3)
    banButton.hover(ban, choice3.name, choice3.info1, choice3.info2, choice3.info3)
    kingButton.hover(king, choice4.name, choice4.info1, choice4.info2, choice4.info3)
    merlinButton.hover(merlin, choice5.name, choice5.info1, choice5.info2, choice5.info3)
    dianeButton.hover(diane, choice6.name, choice6.info1, choice6.info2, choice6.info3)


def player_choice():
    if meliodasButton.draw_image(button):
        if players[0] == 0:
            players[0] = 1
        elif players[1] == 0 and players[0] != 1:
            players[1] = 1
    elif escanorButton.draw_image(button):
        if players[0] == 0:
            players[0] = 2
        elif players[1] == 0 and players[0] != 2:
            players[1] = 2
    elif banButton.draw_image(button):
        if players[0] == 0:
            players[0] = 3
        elif players[1] == 0 and players[0] != 3:
            players[1] = 3
    elif kingButton.draw_image(button):
        if players[0] == 0:
            players[0] = 4
        elif players[1] == 0 and players[0] != 4:
            players[1] = 4
    elif merlinButton.draw_image(button):
        if players[0] == 0:
            players[0] = 5
        elif players[1] == 0 and players[0] != 5:
            players[1] = 5
    elif dianeButton.draw_image(button):
        if players[0] == 0:
            players[0] = 6
        elif players[1] == 0 and players[0] != 6:
            players[1] = 6
    global player1, player2
    player1 = Fighter(confirm, 'Fullname', 'Player 1', 0, 0, 0)
    player2 = Fighter(confirm, 'Fullname', 'Player 2', 0, 0, 0)
    if players[0] == 1:
        player1 = choice1
        player1.player = 1
    elif players[0] == 2:
        player1 = choice2
        player1.player = 1
    elif players[0] == 3:
        player1 = choice3
        player1.player = 1
    elif players[0] == 4:
        player1 = choice4
        player1.player = 1
    elif players[0] == 5:
        player1 = choice5
        player1.player = 1
    elif players[0] == 6:
        player1 = choice6
        player1.player = 1
    if players[1] == 1 and players[0] != 1:
        player2 = choice1
        player2.player = 2
    elif players[1] == 2 and players[0] != 2:
        player2 = choice2
        player2.player = 2
    elif players[1] == 3 and players[0] != 3:
        player2 = choice3
        player2.player = 2
    elif players[1] == 4 and players[0] != 4:
        player2 = choice4
        player2.player = 2
    elif players[1] == 5 and players[0] != 5:
        player2 = choice5
        player2.player = 2
    elif players[1] == 6 and players[0] != 6:
        player2 = choice6
        player2.player = 2
    if players[0] != 0 and players[1] == 0:
        num = 1
        nick = player1.nick
        draw_temp(f'Player {num} choose {nick}', 410, 240)
    elif player1.nick != 'Player 1' and player2.nick != 'Player 2':
        num = 2
        nick = player2.nick
        draw_temp(f'Player {num} choose {nick}', 410, 240)


# ACTIONS
def resolve_actions(title):
    p1 = player1
    p2 = player2
    if p2.act != 0:
        p1 = player2
        p2 = player1
    # attacks: title, cost, damage, number, spell, melee, bonus1, bonus2, onus, ult
    if title == 'strike':
        action_attack('Strike', p1, p2, 10, 1, 1, False, True, 0, 0, 2, True, False)
    elif title == 'thousand_cuts':
        action_attack('Thousand Cuts', p1, p2, 50, 0.3, 10, False, True, 5, 0, 0, False, False)
    elif title == 'hell_blaze':
        action_attack('Hell Blaze', p1, p2, 100, 6, 1, True, False, 0, 0, 3, False, False)
    elif title == 'trillion_darkness':
        action_attack('Trillion Darkness', p1, p2, 200, 0.15, 60, True, False, 1, 5, 0, False, True)
    elif title == 'super_slash':
        action_attack('Super Slash', p1, p2, 50, 2.5, 1, False, True, 1, 0, 1, True, False)
    elif title == 'divine_sword':
        action_attack('Divine Sword', p1, p2, 100, 4.5, 1, False, True, 5, 0, 3, False, False)
    elif title == 'grim_sun':
        action_attack('Grim Sun', p1, p2, 150, 15, 1, True, False, 1, 0, 4, False, True)
    elif title == 'blast':
        action_attack('Blast', p1, p2, 30, 1, 1, True, False, 0, 0, 5, True, False)
    elif title == 'sunflower':
        action_attack('Sunflower', p1, p2, 150, 2.5, 1, True, False, 5, 0, 5, False, False)
    elif title == 'increase':
        action_attack('Increase', p1, p2, 300, 0.2, 30, True, False, 1, 0, 6, False, False)
    elif title == 'petrification':
        action_attack('Petrification', p1, p2, 400, 5, 1, True, False, 1, 0, 7, True, True)
    # counters: title, cost, counter, retaliation, move, distance, bonus1, bonus2, ult
    elif title == 'block':
        action_reaction('Block', p1, p2, 40, False, False, False, 0, 4, 0, False)
    elif title == 'evade':
        action_reaction('Evade', p1, p2, 50, False, False, False, 0, 3, 0, False)
    elif title == 'blink':
        action_reaction('Blink', p1, p2, 100, True, False, False, 0, 0, 0, False)
    elif title == 'full_counter':
        action_reaction('Full Counter', p1, p2, 150, True, True, False, 0, 1, 0, False)
    elif title == 'dash':
        action_reaction('Dash', p1, p2, 30, False, False, True, -2, 0, 0, False)
    elif title == 'teleport':
        action_reaction('Teleport', p1, p2, 75, False, False, True, 2, 0, 0, False)
    # moves: title, mana cost, distance
    elif title == 'walk':
        action_move('Walk', p1, 10, -1)
    elif title == 'fly':
        action_move('Fly', p1, 20, 1)
    elif title == 'charge':
        action_move('Charge', p1, 40, -2)
        action_attack('Attack', p1, p2, 0, 1.5, 1, False, True, 0, 0, 6, False, False)
    # stances: title, cost, powerup, bonus1, bonus2, bonus3, onus1, onus2, ult
    elif title == 'power_up':
        action_stance('Power Up', p1, p2, 10, True, 0, 0, 0, 0, 0, 0, False)
    elif title == 'assault_mode':
        action_stance('Assault Mode', p1, p2, 150, False, 0, 2, 4, 5, 0, 0, True)
    elif title == 'pollen_garden':
        action_stance('Pollen Garden', p1, p2, 350, False, 3, 3, 4, 0, 0, 0, True)
    elif title == 'the_one':
        action_stance('The One', p1, p2, 100, False, 0, 1, 2, 6, 0, 0, True)
    elif title == 'skip':
        action_move('skip', p1, 0, 0)


# x, y, w, h
def meliodas_buttons():
    attack1 = Button(173, 299, 100, 20)
    attack2 = Button(313, 299, 100, 20)
    attack3 = Button(453, 299, 100, 20)
    attack4 = Button(593, 299, 100, 20)
    reaction1 = Button(173, 328, 100, 20)
    reaction2 = Button(313, 328, 100, 20)
    move1 = Button(173, 358, 100, 20)
    move2 = Button(313, 358, 100, 20)
    stance1 = Button(173, 386, 100, 20)
    stance2 = Button(313, 386, 100, 20)
    attack1.draw_text('Strike', 1)
    attack2.draw_text('Thousand Cuts', 1)
    attack3.draw_text('Hell Blaze', 26)
    attack4.draw_text('Trillion Darkness', 256)
    reaction1.draw_text('Block', 3, True)
    reaction2.draw_text('Full Counter', 3, True)
    move1.draw_text('Walk', 4)
    move2.draw_text('Dash', 4)
    stance1.draw_text('Power Up', 7, True)
    stance2.draw_text('Assault Mode', 7, True)

def escanor_buttons():
    attack1 = Button(173, 299, 100, 20)
    attack2 = Button(313, 299, 100, 20)
    attack3 = Button(453, 299, 100, 20)
    attack4 = Button(593, 299, 100, 20)
    reaction1 = Button(173, 328, 100, 20)
    move1 = Button(173, 358, 100, 20)
    move2 = Button(313, 358, 100, 20)
    move3 = Button(453, 358, 100, 20)
    stance1 = Button(173, 386, 100, 20)
    stance2 = Button(313, 386, 100, 20)
    attack1.draw_text('Strike', 1)
    attack2.draw_text('Super Slash', 1)
    attack3.draw_text('Divine Sword', 1)
    attack4.draw_text('Grim Sun', 256)
    reaction1.draw_text('Block', 3, True)
    move1.draw_text('Walk', 4)
    move2.draw_text('Charge', 14)
    move3.draw_text('Dash', 4)
    stance1.draw_text('Power Up', 7, True)
    stance2.draw_text('The One', 7, True)

def harlequinn_buttons():
    attack1 = Button(173, 299, 100, 20)
    attack2 = Button(313, 299, 100, 20)
    attack3 = Button(453, 299, 100, 20)
    attack4 = Button(593, 299, 100, 20)
    reaction1 = Button(173, 328, 100, 20)
    reaction2 = Button(313, 328, 100, 20)
    move1 = Button(173, 358, 100, 20)
    move2 = Button(313, 358, 100, 20)
    stance1 = Button(173, 386, 100, 20)
    stance2 = Button(313, 386, 100, 20)
    attack1.draw_text('Blast', 1)
    attack2.draw_text('Sunflower', 1)
    attack3.draw_text('Increase', 26)
    attack4.draw_text('Petrification', 256)
    reaction1.draw_text('Evade', 3, True)
    reaction2.draw_text('Blink', 3, True)
    move1.draw_text('Fly', 4)
    move2.draw_text('Teleport', 4)
    stance1.draw_text('Power Up', 7, True)
    stance2.draw_text('Pollen Garden', 7, True)


def add_pile(title):
    global temp_msg, enemy
    if action_pile[0][0] != 'none' and player1.spd != 0 and player1.act != 0:
        action_pile.append(title)
        resolve_actions(action_pile[1])
        resolve_actions(action_pile[0])
        temp_msg = f'{title}!'
    elif action_pile[0][0] != 'none' and player2.spd != 0 and player1.act == 0:
        action_pile.append(enemy)
        resolve_actions(action_pile[1])
        resolve_actions(action_pile[0])
        temp_msg = f'{enemy}!'
    elif action_pile[0][0] == 'none' and player1.spd != 0 and player1.act != 0:
        action_pile.pop()
        action_pile.append(title)
        temp_msg = f'{title}!'
    elif action_pile[0][0] == 'none' and player2.spd != 0 and player1.act == 0:
        action_pile.pop()
        action_pile.append(enemy)
        temp_msg = f'{enemy}!'
    draw_temp(temp_msg, 300, 150)
    print(action_pile, player1.act)


def enemy_actions(char):
    # list of  AI actions
    melee = []
    ranged = []
    reactions = []
    ults = []
    enemy = ''
    if char == 'Meliodas':
        melee = ['strike', 'thousand_cuts', 'hell_blaze']
        ranged = ['hell_blaze', 'walk', 'dash']
        reactions = ['block', 'full_counter']
        ults = ['trillion_darkness', 'assault_mode']
    elif char == 'Escanor':
        melee = ['strike', 'super_slash', 'divine_sword']
        ranged = ['walk', 'charge', 'dash']
        reactions = ['block']
        ults = ['grim_sun', 'the_one']
    elif char == 'Harlequinn':
        melee = ['fly', 'blink', 'teleport']
        ranged = ['blast', 'sunflower', 'increase']
        reactions = ['evade', 'blink']
        ults = ['pollen_garden', 'petrification']
    # 0 = none; 100 = melee; 200 = ranged; 300 = reaction; 400 = move; 500 = ult; 600 = spell; 700 = stance;
    # 256 = ult, spell, ranged; 140 = move, melee; 260 = ranged, spell; 160 = melee, spell; 310 = reaction, melee;
    # 340 = move, reaction; 320 = reaction, melee; 150 = ult, melee
    if player2.spd > 0:
        if player2.mna <= (player2.full_mana // 4):
            enemy = 'power_up'
        elif player2.mna <= (player2.full_mana // 2) or player2.life <= (player2.full_life // 2):
            enemy = choice(ults)
        elif action_pile[0][0] != 'none' and 100 <= player1.act <= 199:
            if player1.life <= (player1.full_life // 2):
                enemy = choice(reactions)
            else:
                enemy = 'skip'
        elif action_pile[0][0] == 'none' and player1.position == 0:
            enemy = choice(melee)
        elif action_pile[0][0] == 'none' and player1.position != 0:
            enemy = choice(ranged)
    else:
        enemy = 'skip'
    return enemy


def turn():
    running = True
    while running:
        if player1.spd == 0 and player2.spd == 0:
            turn_reroll(player1)
            turn_reroll(player2)
            running = False
        else:
            enemy_actions()


class GameState():
    def __init__(self):
        self.state = 'choice_menu'
        self.current_time = 0
        self.action_time = 0
        self.clock = pygame.time.Clock()

    def choice_menu(self):
        screen.blit(choicemenu, (0, 0))
        # info appears when mouse over button
        mouse_over()
        # when player selected a character, appears on window
        player_choice()

        if player1.nick != 'Player 1' and player2.nick != 'Player 2':
            if self.action_time + 2000 < self.current_time:
                self.state = 'main_game'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.action_time = pygame.time.get_ticks()

        self.current_time = pygame.time.get_ticks()

        pygame.display.flip()
        self.clock.tick(60)

    def main_game(self):
        screen.blit(background, (0, 0))
        player1.draw_fighter()
        player2.draw_fighter()
        # life and mana bars
        player1.draw_bar()
        player2.draw_bar()

        screen.blit(battleground, (0, 0))
        player1.draw_info()
        player2.draw_info()
        if player1.nick == 'Meliodas':
            meliodas_buttons()
        elif player1.nick == 'Harlequinn':
            harlequinn_buttons()
        elif player1.nick != 'Harlequinn' and player1.nick != 'Meliodas':
            escanor_buttons()
        skip_turn.draw_image(skip)

        # empty pile
        if len(action_pile) == 2:
            action_pile.pop()
            action_pile.pop()
            action_pile.append(['none'])

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.action_time = pygame.time.get_ticks()

        self.current_time = pygame.time.get_ticks()

        pygame.display.flip()
        self.clock.tick(60)

    def state_manager(self):
        if self.state == 'choice_menu':
            self.choice_menu()
        if self.state == 'main_game':
            self.main_game()


global game_state
game_state = GameState()
