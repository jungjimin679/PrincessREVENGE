#1059줄
import tkinter
import random
import time
import copy
import pygame
pygame.mixer.init()
root = tkinter.Tk()
root.title("중세 게임")

isDie = False
isStart = False
isClear = False

story_script = [0, 0]

stopInput = False

bgm = bgm = pygame.mixer.Sound("DG_BGM.mp3")
eft = pygame.mixer.Sound("damage.mp3")
# 빈칸 : 0 / 벽 : 1 / 포탈 : 2 / 아이템 : 3 / 적 : 4 / 나 : 5
#region 클래스

#이름, 체력, 공격범위, 물리 공격력, 마법 공격력, 방어력, 저항력
class Stat: 

    name = "없음"

    maxHp = 0
    hp = 0

    atk_range = 0 #공격 범위

    str = 0 #물리 공격력
    spr = 0 #마법 공격력

    dep = 0 #방어력
    res = 0 #저항력

    def __init__(self, name, maxHp, atk_range, str, spr, dep, res):
        self.name = name
        self.maxHp = maxHp
        self.hp = maxHp
        self.atk_range = atk_range
        self.str = str
        self.spr = spr
        self.dep = dep
        self.res = res
        

    def hit(self, stat):
        global player

        eft.play()
        ad_damage = stat.str - self.dep if stat.str - self.dep > 0 else 0
        ap_damage = stat.spr - self.res if stat.spr - self.res > 0 else 0

        AddLog(self.name+"(은)는 "+str(ap_damage+ad_damage)+"의 피해를 입었다. "+"남은 체력 "+str(self.hp))
        self.decreaseHp(ad_damage + ap_damage)

    def decreaseHp(self, damage):
        global stopInput
        self.hp -= damage
        if self.hp <= 0 :
            self.hp = 0
            if player.stat == self :
                stopInput = False
                end_game()
                changeBGM("dead.mp3",-1)
            if self.name == "마왕" :
                clear_game()
                changeBGM("EndBgm.mp3",-1)




class Item:

    name = "이름"
    itemType = "타입"
    eft = "효과"
    image_number = 0
    pos = [0,0]

    weaponEffect = [1,1,0,0] # 범위, 물공, 마공, 무게
    weaponEFFect1 = [1,1,3,0]

    def __init__(self,name, itemType, eft, image_number, weaponEffect):
        self.name = name
        self.itemType = itemType
        self.eft = eft
        self.image_number = image_number
        self.weaponEffect = weaponEffect

    def detect(self):
        if stages[curStage][self.pos[1]][self.pos[0]] == 5 : 
            self.use()

    def use(self):
        global player


        if self.itemType == "소모품":
            eft = self.eft.split(':')
            if eft[0] == "회복" :
                if player.stat.hp + int(eft[1]) > player.stat.maxHp : player.stat.hp = player.stat.maxHp
                else : player.stat.hp += int(eft[1])
                AddLog("체력을 회복하여 현재 체력이 "+str(player.stat.hp)+"이 되었다!")
                AddLog(self.name+"(을)를 사용했다!!")
            if eft[0] == "피해" :
                eft = self.eft.split(':')
                player.stat.decreaseHp(int(eft[1]))
                AddLog("윽! 잘못먹은것 같다... ")
            if eft[0] == "근력" :
                AddLog(self.name+"(을)를 사용했다!!")
                AddLog("힘이 강해진 것 같다... ")
                player.stat.str += int(eft[1])
                player.bonus[0] += int(eft[1])
            if eft[0] == "마력" :
                AddLog(self.name+"(을)를 사용했다!!")
                AddLog("지혜로워진 것 같다... ")
                player.stat.spr += int(eft[1])
                player.bonus[1] += int(eft[1])
            if eft[0] == "방어력" :
                AddLog(self.name+"(을)를 사용했다!!")
                AddLog("튼튼해진 것 같다... ")
                player.stat.dep += int(eft[1])
                player.bonus[2] += int(eft[1])
            if eft[0] == "저항력" :
                AddLog(self.name+"(을)를 사용했다!!")
                AddLog("정신이 성숙해진 것 같다... ")
                player.stat.res += int(eft[1])
                player.bonus[3] += int(eft[1])
            if eft[0] == "체력" :
                AddLog(self.name+"(을)를 사용했다!!")
                AddLog("맛있게 먹었다...!")
                player.stat.maxHp += int(eft[1])
                player.stat.hp += int(eft[1])
                player.bonus[3] += int(eft[1])
            DrawEffect(player.pos, image=itemImages[self.image_number][1])

            
        elif self.itemType == "무기":
            player.weapon = self
            player.stat.atk_range = self.weaponEffect[0]
            player.stat.str = self.weaponEffect[1] + player.bonus[0]
            player.stat.spr = self.weaponEffect[2] + player.bonus[1]
            player.weight = self.weaponEffect[3]
            AddLog(self.name+"(을)를 손에 쥐었다.")
            AddLog(player.weapon.eft)
            
        elif self.itemType == "함정":
            eft = self.eft.split(':')
            if eft[0] == "피해" :
                player.stat.decreaseHp(int(eft[1]))
                AddLog(self.name+"(에)게 당했다!!")
        
        curStageItems[curStage].remove(self)

class Player:
    
    stat = Stat("용사",3,1,1,1,1,1) # 초기 세팅
    
    bonus = [0,0,0,0] # 물리 마법 방어 저항

    dir = 0

    weapon = Item("주먹","없음","없음",-1,[1,1,0,0])
    armor = Item("천 옷","없음","없음",-1,[0,0,0,0])

    weight = 0
    pos = [0,0] # 내 위치

    def __init__(self,stat):
        self.stat = stat

    #죽음
    def die(self):
        return
    def reset(self):
        self.stat.hp = self.stat.maxHp

    def move_attack(self):
        dirX = 0
        dirY = 0
        if self.dir < 2 : 
           dirX =  -1 if self.dir == 0 else  1
        else :
            dirY =  -1 if self.dir == 2 else  1
            #16 + curX*32 , 16 + curY*32
        for i in range(5, 0, -1):
            canvas.coords("Player", 
                          16 + self.pos[0] * 32 + i * 1 * dirX, 
                          16 + self.pos[1] * 32 + i * 1 * dirY)
            canvas.update()
            time.sleep(0.05)

    #공격 시도
    def try_attack(self):
        for i in range(self.pos[1]-self.stat.atk_range, self.pos[1]+self.stat.atk_range+1): # 본인 기준 범위에 해당하는 y값 차례로 검사
            
            if i < 0 or i > 14 : continue # 맵의 크기보다 크면 넘어가기
            
            for j in range(self.pos[0]-self.stat.atk_range, self.pos[0]+self.stat.atk_range+1): # 해당 y값의 x값 차례로 검사
                
                if j < 0 or j > 24 : continue # 맵의 크기보다 크면 넘어가기
               
                if stages[curStage][i][j] == 4 : # 검사하는 위치에 적이 있으면, 위치 받아서 공격. 위치로 적 데이터 찾아내는 것
                  
                    self.targetPos = [j,i]
                    self.attack()
    def attack(self):
        
        for i in curStageEnemies[curStage] : # 현재 스테이지의 적들이 담겨있는 배열 검사
            if i.pos == self.targetPos : # 그 적의 위치가 현재 검사한 타겟에 해당하는지 검사
               self.move_attack()

               AddLog(self.stat.name+"(은)는 "+self.weapon.name+"(으)로 "+i.stat.name+"(을)를 공격!")
               i.stat.hit(self.stat)
               i.die()
               if self.weapon.image_number == -1 : DrawEffect(self.targetPos, image=tkinter.PhotoImage(file="item_bow1_e.png"))
               else : DrawEffect(self.targetPos, image=itemImages[self.weapon.image_number][1])
 
class Enemy:
    
    stat = Stat("-",0,0,0,0,0,0)

    id = -1

    dir = 0

    speed = 0 # 속도값, 3이면 3턴에 한 번 행동
    cool = 0 # 속도값에 맞게 남은 턴을 세주는 용도의 쿨타임 변수
    detect_range = 0

    effect_number = 0

    pos = [0,0]
    targetPos = [-1,-1] # 타겟이 없을 때 => [-1, -1]

    image_number = 0
    
    def __init__(self, image_number, speed, detect_range, effect_number, stat):
        self.image_number = image_number
        self.speed = speed
        self.cool = random.randint(0,speed)
        self.detect_range = detect_range
        self.effect_number = effect_number
        self.stat = stat

    def detect(self): # Player의 공격 함수와 거의 동일

        self.targetPos = [-1,-1]

        for i in range(self.pos[1]-self.detect_range, self.pos[1]+self.detect_range+1):

            if i < 0 or i > 14 : continue

            for j in range(self.pos[0]-self.detect_range, self.pos[0]+self.detect_range+1):

                if j < 0 or j > 24 : continue

                if stages[curStage][i][j] == 5 : # 타겟으로 지정되면, 타겟의 위치를 targetPos에 담는다
                    self.targetPos = [j,i]

        self.act_pos() # 몬스터의 행동
        
    def act_pos(self):

        if(self.cool > 0) : # 쿨타임일 경우 행동하지 않음
            self.cool -= 1
            return
        else :
            self.cool = self.speed

        #

        stages[curStage][self.pos[1]][self.pos[0]] = 0 # 이동할 경우를 대비하여 현재 위치 비우기

        #

        if self.targetPos[0] == -1 and self.targetPos[1] == -1 : # 타겟이 없는 경우 무작위 위치로 이동

            x = random.randint(-1,1)
            y = random.randint(-1,1)

            if y == 1 : self.dir = 3
            elif y == -1 : self.dir = 2

            if x == 1 : self.dir = 1
            elif x == -1 : self.dir = 0

            if (self.pos[1]+y >= 0 and self.pos[1]+y <= 14) and (self.pos[0]+x >= 0 and self.pos[0]+x <= 24) :  # 이동하려는 위치가 맵 바깥이면 그냥 리턴
                if ( stages[curStage][self.pos[1]+y][self.pos[0]+x] == 0 ) : # 이동하려는 위치가 비어있는지 확인
                    self.pos[0] += x
                    self.pos[1] += y
        else: # 타겟이 있는 경우

            #공격 범위 안에 있는 경우
            if self.targetPos[0] - self.pos[0] >= -self.stat.atk_range and self.targetPos[0] - self.pos[0] <= self.stat.atk_range and self.targetPos[1] - self.pos[1] >= -self.stat.atk_range and self.targetPos[1] - self.pos[1] <= self.stat.atk_range :
                self.attack()
            else: #공격 범위 밖에 있는 경우, 해당 방향으로 이동
                if self.targetPos[0] - self.pos[0] < -self.stat.atk_range and stages[curStage][self.pos[1]][self.pos[0]-1] == 0 : #타겟이 왼쪽
                    self.pos[0] -= 1
                    self.dir = 0
                elif self.targetPos[0] - self.pos[0] > self.stat.atk_range and stages[curStage][self.pos[1]][self.pos[0]+1] == 0 : #타겟이 오른쪽
                    self.pos[0] += 1
                    self.dir = 1
                if self.targetPos[1] - self.pos[1] < -self.stat.atk_range and stages[curStage][self.pos[1]-1][self.pos[0]] == 0 : #타겟이 위
                    self.pos[1] -= 1
                elif self.targetPos[1] - self.pos[1] > self.stat.atk_range and stages[curStage][self.pos[1]+1][self.pos[0]] == 0 : #타겟이 아래
                    self.pos[1] += 1
        stages[curStage][self.pos[1]][self.pos[0]] = 4 #갱신된 위치 적용

    def move_attack(self):
        dirX = 0
        dirY = 0

        id = curStageEnemies[curStage].index(self)
            
        if self.dir < 2 : 
           dirX =  -1 if self.dir == 0 else  1
        else :
            dirY =  -1 if self.dir == 2 else  1
            #16 + curX*32 , 16 + curY*32
        for i in range(5, 0, -1):
            canvas.coords(curStageEnemiesCanvas[curStage][id], 
                          16 + self.pos[0] * 32 + i * 1 * dirX, 
                          16 + self.pos[1] * 32 + i * 1 * dirY)
            canvas.update()
            time.sleep(0.05)
            
    def attack(self):
        global player
        DrawEffect(player.pos, image=enemyEffectImages[self.effect_number])
        AddLog(self.stat.name+"(은)는 "+player.stat.name+"(을)를 공격!")
        self.move_attack()
        if player.stat.hit(self.stat) : 
            player.die()

    def die(self):
        if(self.stat.hp > 0) : return
        stages[curStage][self.pos[1]][self.pos[0]] = 0 
        id = curStageEnemies[curStage].index(self)
        curStageEnemiesCanvas[curStage].pop(id)
        curStageEnemies[curStage].remove(self)
        AddLog(self.stat.name+"(은)는 죽었다...")
        move_enemis()

#endregion

#region 스테이지

#초기화용
stagesForReset = [ 
    [#마을
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,1,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,0,1],
    
    [1,0,0,0,1 ,0,0,1,0,0 ,0,0,0,1,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,1,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,1,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,1,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    ],[#가는길
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,0,0,0,0 ,0,0,0,1,0 ,0,0,0,0,0 ,0,0,1,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,1,0 ,0,0,0,0,0 ,0,0,1,0,0 ,0,0,0,0,1],
    
    [1,0,0,0,1 ,0,0,0,1,0 ,0,0,0,1,0 ,0,0,1,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,1,0,1,0 ,0,0,0,0,0 ,0,0,0,1,0 ,0,0,0,0,1],
    [1,0,0,1,0 ,0,0,0,1,0 ,0,0,0,0,1 ,0,0,0,1,0 ,0,1,0,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    ],[#입구
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,1,1,1,1],
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,1,1,1,1],
    
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,1,0 ,0,0,0,0,0 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,0,0 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,0,0 ,2,2,2,2,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,1,0 ,0,0,1,0,0],
    
    [0,0,0,0,0 ,0,0,1,0,1 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,0,0,1,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,1,0,0 ,0,1,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    ],[#성 내부
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,1,0,0 ,0,1,0,0,0 ,0,1,0,0,1 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,0,0,1 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,2],
    
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,1 ,0,0,0,0,1],
    [0,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,1],
    [0,0,0,0,0 ,0,0,1,0,0 ,0,0,0,0,0 ,0,1,0,0,1 ,0,0,0,0,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    ],[#마왕이 있는 곳
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,1,0,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,1,1],
    [1,1,0,0,0 ,0,0,0,0,1 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    
    [1,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,1,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,1,0,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,1,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],]
]

stages = [ 
    [#마을
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,1,0,0,0,1],
    
    [1,0,0,0,0 ,1,0,0,1,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,0,0,1,0 ,0,0,0,0,0 ,0,0,0,0,1 ,0,0,0,0,0 ,0,0,0,1,1],
    [1,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    ],[#가는길
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    ],[#입구
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    ],[#성 내부
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,2],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    ],[#마왕이 있는 곳
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1 ,1,1,1,1,1],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],
    [0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0 ,0,0,0,0,0],]
]

def CopyStage() :
    for y in range(5):
        for x in range(15):
            for z in range(25):
                stages[y][x][z] = stagesForReset[y][x][z]

#endregion

#region 이미지 리소스

backGroundImages = [ tkinter.PhotoImage(file="map_0.png"), 
                     tkinter.PhotoImage(file="map_1.png"), 
                     tkinter.PhotoImage(file="map_2.png"), 
                     tkinter.PhotoImage(file="map_3.png"), 
                     tkinter.PhotoImage(file="map_4.png"), 
                     tkinter.PhotoImage(file="map_5.png")] # 게이트

# 해골병사 해골기사 해골마법사 마왕 난민1 난민2 난민3 : 7
enemyImages = [
    [tkinter.PhotoImage(file="unit_skull_l.png"),
                  tkinter.PhotoImage(file="unit_skull_r.png"),
                  tkinter.PhotoImage(file="unit_skull_b.png"),
                  tkinter.PhotoImage(file="unit_skull_f.png")],
    [tkinter.PhotoImage(file="unit_skullk_l.png"),
                  tkinter.PhotoImage(file="unit_skullk_r.png"),
                  tkinter.PhotoImage(file="unit_skullk_b.png"),
                  tkinter.PhotoImage(file="unit_skullk_f.png")],
    [tkinter.PhotoImage(file="unit_skullm_l.png"),
                  tkinter.PhotoImage(file="unit_skullm_r.png"),
                  tkinter.PhotoImage(file="unit_skullm_b.png"),
                  tkinter.PhotoImage(file="unit_skullm_f.png")],
    [tkinter.PhotoImage(file="unit_devil_l.png"),
                  tkinter.PhotoImage(file="unit_devil_r.png"),
                  tkinter.PhotoImage(file="unit_devil_b.png"),
                  tkinter.PhotoImage(file="unit_devil_f.png")],
    [tkinter.PhotoImage(file="unit_npc_l.png"),
                  tkinter.PhotoImage(file="unit_npc_r.png"),
                  tkinter.PhotoImage(file="unit_npc_b.png"),
                  tkinter.PhotoImage(file="unit_npc_f.png")],
    [tkinter.PhotoImage(file="unit_npc1_l.png"),
                  tkinter.PhotoImage(file="unit_npc1_r.png"),
                  tkinter.PhotoImage(file="unit_npc1_b.png"),
                  tkinter.PhotoImage(file="unit_npc1_f.png")],
    [tkinter.PhotoImage(file="unit_npc2_l.png"),
                  tkinter.PhotoImage(file="unit_npc2_r.png"),
                  tkinter.PhotoImage(file="unit_npc2_b.png"),
                  tkinter.PhotoImage(file="unit_npc2_f.png")],
    [tkinter.PhotoImage(file="unit_prs.png"), 
                    tkinter.PhotoImage(file="unit_prs.png"), 
                    tkinter.PhotoImage(file="unit_prs.png"), 
                    tkinter.PhotoImage(file="unit_prs.png")]
                  ]

enemyEffectImages = [ [tkinter.PhotoImage(file="item_mace1_e.png")],
                     [tkinter.PhotoImage(file="item_sword1_e.png")],
                      [tkinter.PhotoImage(file="item_mace2_e.png")],
                       [tkinter.PhotoImage(file="item_mace3_e.png")],
                        [tkinter.PhotoImage(file="item_mace1_e.png")],
                         [tkinter.PhotoImage(file="item_mace1_e.png")],
                          [tkinter.PhotoImage(file="item_mace1_e.png")],
                          [tkinter.PhotoImage(file="item_mace1_e.png")] ]

npcImages = [ tkinter.PhotoImage(file="knight1.png"), 
                    tkinter.PhotoImage(file="knight2.png"), 
                    tkinter.PhotoImage(file="unit_prs.png"), 
]

playerImage = [ tkinter.PhotoImage(file="player_left.png"), 
                tkinter.PhotoImage(file="player_right.png"), 
                tkinter.PhotoImage(file="player_up.png"), 
                tkinter.PhotoImage(file="player_down.png")]

# 검 메이스 채찍 활 체력 독 힘 마법 방어 저항 사과 고기 함정
itemImages = [ 
              [tkinter.PhotoImage(file="item_sword1.png"), tkinter.PhotoImage(file="item_sword1_e.png")] , 
              [tkinter.PhotoImage(file="item_sword2.png"), tkinter.PhotoImage(file="item_sword2_e.png")], 
              [tkinter.PhotoImage(file="item_sword3.png"), tkinter.PhotoImage(file="item_sword3_e.png")], 
              [tkinter.PhotoImage(file="item_mace1.png"), tkinter.PhotoImage(file="item_mace1_e.png")], 
              [tkinter.PhotoImage(file="item_mace2.png"), tkinter.PhotoImage(file="item_mace2_e.png")], 
              [tkinter.PhotoImage(file="item_mace3.png"), tkinter.PhotoImage(file="item_mace3_e.png")], 
              [tkinter.PhotoImage(file="item_whip1.png"), tkinter.PhotoImage(file="item_whip1_e.png")], 
              [tkinter.PhotoImage(file="item_whip2.png"), tkinter.PhotoImage(file="item_whip2_e.png")], 
              [tkinter.PhotoImage(file="item_whip3.png"), tkinter.PhotoImage(file="item_whip3_e.png")],
              [tkinter.PhotoImage(file="item_bow1.png"), tkinter.PhotoImage(file="item_bow1_e.png")],
              [tkinter.PhotoImage(file="item_bow2.png"), tkinter.PhotoImage(file="item_bow2_e.png")], 
              [tkinter.PhotoImage(file="item_bow3.png"), tkinter.PhotoImage(file="item_bow3_e.png")], 
              [tkinter.PhotoImage(file="item_heal.png"), tkinter.PhotoImage(file="item_heal_e.png")], 
              [tkinter.PhotoImage(file="item_poison.png"), tkinter.PhotoImage(file="item_poison_e.png")], 
              [tkinter.PhotoImage(file="item_power.png"), tkinter.PhotoImage(file="item_power_e.png")], 
              [tkinter.PhotoImage(file="item_magic.png"), tkinter.PhotoImage(file="item_magic_e.png")], 
              [tkinter.PhotoImage(file="item_shield.png"), tkinter.PhotoImage(file="item_shield_e.png")], 
              [tkinter.PhotoImage(file="item_resist.png"), tkinter.PhotoImage(file="item_resist_e.png")], 
              [tkinter.PhotoImage(file="item_apple.png"), tkinter.PhotoImage(file="item_apple_e.png")], 
              [tkinter.PhotoImage(file="item_meat.png"), tkinter.PhotoImage(file="item_meat_e.png")], 
              [tkinter.PhotoImage(file="item_trap.png"), tkinter.PhotoImage(file="item_bow1_e.png")]
               ]

uiImages = [ tkinter.PhotoImage(file="playerStat.png"), tkinter.PhotoImage(file="InfoUI.png"), 
            tkinter.PhotoImage(file="portrait.png") ]

img_title = [tkinter.PhotoImage(file="Title.png"),tkinter.PhotoImage(file="GameOver.png"),tkinter.PhotoImage(file="End.png")]

script_image = [tkinter.PhotoImage(file="script_0.png"), tkinter.PhotoImage(file="script_1.png"), tkinter.PhotoImage(file="script_2.png")]

#endregion

#region 데이터

enemyDatas = [ #데이터 속 이미지 인덱스, 속도, 감지범위, 공격 이펙트 이미지 인덱스, 스텟 / 이름, 체력, 공격범위, 물리 공격력, 마법 공격력, 방어력, 저항력
    Enemy(0, 3, 3, 0, Stat("해골 병사", 5, 1, 2, 0, 0, 0)),
    Enemy(1, 1, 4, 1, Stat("해골 기사", 12, 1, 3, 1, 0, 0)),
    Enemy(2, 4, 7, 2, Stat("해골 마법사", 10, 3, 0, 3, 0, 0)),
    Enemy(3, 2, 10, 3, Stat("마왕", 20, 2, 3, 3, 2, 2)),
    Enemy(4, 6, 1, 4, Stat("난민1", 5, 0, 0, 0, 0, 0)),
    Enemy(5, 5, 1, 5, Stat("난민2", 10, 0, 0, 0, 0, 0)),
    Enemy(6, 4, 1, 6, Stat("난민3", 20, 0, 0, 0, 0, 0)),
    Enemy(7, 10, 0, 7, Stat("공주", 10, 0, 0, 0, 0, 0))
    ]

itemDatas = [
    Item("검","무기", "균형잡힌 검을 주웠다.",0 ,[1,3,0,2]),
    Item("불검","무기", "타오르는 검을 손에 쥐었다...!",1 ,[2,3,3,2]),
    Item("성검","무기", "성검을 마주했다...신성한 힘이 몸에 흐른다...!",2 ,[2,6,6,2]),
    Item("철퇴","무기", "묵직한 철퇴를 주웠다.",3 ,[3,5,0,3]),
    Item("마법 철퇴","무기", "마법적인 기운을 뿜어내는 철퇴가 함께하게 되었다...!",4 ,[3,4,4,3]),
    Item("악마 철퇴","무기", "나도모르게 악마 철퇴를 들었고, 악마들을 박살내고 싶어진다...",5 ,[3,8,8,3]),
    Item("채찍","무기", "가벼운 가죽채찍을 주웠다.",6 ,[3,2,0,2]),
    Item("녹슨 사슬","무기", "많이 녹슬어 맞으면 중독될 것 같은 사슬을 쥐었다...!",7 ,[3,2,2,2]),
    Item("신의 징벌","무기", "빛나는 채찍을 들어올리자 악한 것들을 심판하고 싶어진다...",8 ,[3,3,5,1]),
    Item("활","무기", "튼튼한 활을 얻었다.",9 ,[4,1,0,1]),
    Item("번개 활","무기", "짜릿한 번개 활이 내 것이 되었다...!",10 ,[5,1,2,1]),
    Item("성스러운 활","무기", "성스러운 기운이 악을 처단하라고 말한다...!",11 ,[5,1,4,1]),
    Item("체력 물약", "소모품", "회복:5", 12, [0,0,0,0]),
    Item("독 물약", "소모품", "피해:3", 13, [0,0,0,0]),
    Item("힘 물약", "소모품", "근력:2", 14, [0,0,0,0]),
    Item("마법 물약", "소모품", "마력:2", 15, [0,0,0,0]),
    Item("보호 물약", "소모품", "방어력:3", 16, [0,0,0,0]),
    Item("저항 물약", "소모품", "저항력:3", 17, [0,0,0,0]),
    Item("사과", "소모품", "체력:1", 18, [0,0,0,0]),
    Item("고기", "소모품", "체력:5", 19, [0,0,0,0]),
    Item("가시","함정","피해:3", 20, [0,0,0,0])]

#endregion

#region 키 입력
key = ""

def key_down(e):
    global key, player, turn, isDie, isStart, stopInput, isClear
    key = e.keysym 

    if(isClear) :
        canvas.create_image(400,240,image=img_title[2], tag = "Script")
        if(story_script[1] == 0) : 
            story_script[1] += 1
            return
        else :
            quit()

    if(stopInput) : return

    #초반 스토리
    if story_script[0] < 2 :
        canvas.delete("ALL")
        story_script[0] += 1
        if story_script[0] == 1 :
            canvas.create_image(400,240,image=script_image[0], tag = "Script")
        elif story_script[0] == 2 :
            canvas.create_image(400,240, image=backGroundImages[0], tag = "Background")
            canvas.create_image(368,276,image=npcImages[0], tag = "Script")
            canvas.create_image(432,276,image=npcImages[1], tag = "Script")
            canvas.create_image(400,320,image=npcImages[2], tag = "Script")
            canvas.create_image(400,440,image=playerImage[3], tag = "ScriptPlayer")
            stopInput = True
            for i in range(30, 0, -1):
                canvas.coords("ScriptPlayer",  400 , 440 + i * -2)
                canvas.update()
                time.sleep(0.05)
            canvas.create_image(400,240,image=script_image[1], tag = "Script")
            stopInput = False
        return

    #시작 화면
    if isStart == False and key == "Return" : 
        isStart = True
        changeBGM("battle_BGM.mp3", -1)
        reset()

    #죽은 경우
    if isDie == True : 
        if key == "Return" :
                reset()
        return
        
    if key != "Up" and key != "Down" and key != "Left" and key != "Right" and key != "space" : return 
    if(turn) : return
    turn = True

    
    stopInput = True
    if key == "space" : player.try_attack()
    else : move_player()

    r = 0
    while(r <= player.weight) :
        r += 1
        after_turn()

    stopInput = False
    

def key_up(e):
    global key
    key = ""
   
#endregion

#region 턴

def move_player():
    global curX, curY, curStage, idx, player

    stages[curStage][curY][curX] = 0

    # 빈칸 : 0 / 벽 : 1 / 포탈 : 2 / 아이템 : 3 / 적 : 4 / 나 : 5 / 이전 포탈 : 6

    if key == "Up" and ( stages[curStage][curY-1][curX] == 0 or stages[curStage][curY-1][curX] == 2 
                        or stages[curStage][curY-1][curX]==3): # 통과할 수 있는 것 설정...
        curY = curY - 1
        player.dir = 2
    if key == "Down" and ( stages[curStage][curY+1][curX] == 0 or stages[curStage][curY+1][curX] == 2 
                          or stages[curStage][curY+1][curX] == 3 ):
        curY = curY + 1
        player.dir = 3
    if key == "Left" and ( stages[curStage][curY][curX-1] == 0 or stages[curStage][curY][curX-1] == 2 
                          or stages[curStage][curY][curX-1] == 3 ):
        curX = curX - 1
        player.dir = 0
    if key == "Right" and ( stages[curStage][curY][curX+1] == 0 or stages[curStage][curY][curX+1] == 2 
                           or stages[curStage][curY][curX+1] == 3 ):
        curX = curX + 1
        player.dir = 1

    
    if player.stat.hp <= 0: # 플레이어 체력이 계속 떨어지지 않도록 설정
        player.stat.hp = 0

    if stages[curStage][curY][curX] == 2:
        curStage += 1
        curX = 2  # 플레이어 위치
        curY = 8
        #stages[curStage][curY][curX] = 6
        stages[curStage] = copy.deepcopy(stages[curStage])
        canvas.delete("ALL")

        draw_stage()
        set_stage()

    canvas.delete("Player")
    canvas.create_image(16 + curX*32 , 16 + curY*32 , image=playerImage[player.dir], tag= "Player")

    stages[curStage][curY][curX] = 5

    player.pos = [curX, curY]

    canvas.coords("Player", 16 + curX*32, 16 + curY*32)

def after_turn():
    global turn, isDie
    if(isDie) : return

    print(66)

    for i in curStageEnemies[curStage]:
        i.detect()
    for i in curStageItems[curStage]:
        i.detect()
    move_enemis()
    item_check()
    restore_playerInfo()

    turn = False
    
#endregion

#region 적 행동

def item_check():
    if(isDie) : return
    canvas.delete("Item")
    for i in curStageItems[curStage]:
        canvas.create_image(16 + i.pos[0]*32 , 16 + i.pos[1]*32 , image=itemImages[i.image_number][0], tag="Item") 
    
def move_enemis():
    if(isDie) : return
    print(15)
    canvas.delete("Enemy")
    canvas.delete("Enemy_Info")
    for enemy in curStageEnemies[curStage]: # 추가부분 적 데이터에 따른 적의 이름 출력
        image = canvas.create_image(16 + enemy.pos[0]*32, 16 + enemy.pos[1]*32, image=enemyImages[enemy.image_number][enemy.dir], tag="Enemy")
        curStageEnemiesCanvas[curStage].append(image)  

        canvas.create_text(16 + enemy.pos[0]*32, 16 + enemy.pos[1]*32 + 24, text=enemy.stat.name, fill="white", font=("Sam3KRFont", 8, "bold"), tag="Enemy_Info")
        
#endregion

#region 스테이지 세팅

stageEnemyKind = [ [4,6], [0,1], [0,1], [1,2], [1,2] ]
stageDropCounts = [ [1,2], [2,2], [2,3], [2,4], [2,2] ] # 스테이지별로 드랍되는 [ 아이템 수, 적 수 ]
curStageItems = [[],[],[],[],[]]
curStageEnemies = [[],[],[],[],[]]
curStageEnemiesCanvas = [[],[],[],[],[]]

def set_stage():
    if(isDie) : return
    if(curStage == 4) : set_devil()
    set_enemy()
    set_item()
    draw_ui()

def set_enemy():
    global curStageItems, stages
    for i in range( stageDropCounts[curStage][1] ) :
        pos = [ random.randint(0,24), random.randint(0,14) ] # 무작위 위치 지정

        while(True): # 비어있는 위치를 찾을 때까지 반복
            if stages[curStage][pos[1]][pos[0]] == 0: 
                stages[curStage][pos[1]][pos[0]] = 4
                break
            else :
                pos = [random.randint(1,23), random.randint(1,13)]
        
        enemy = copy.deepcopy(enemyDatas[random.randint(stageEnemyKind[curStage][0],stageEnemyKind[curStage][1])])
        
        enemy.pos = pos
        curStageEnemies[curStage].append( enemy )
        image = canvas.create_image(16 + pos[0]*32 , 16 + pos[1]*32 , image=enemyImages[enemy.image_number][3], tag="Enemy") 
        curStageEnemiesCanvas[curStage].append( image )

def set_devil( ) :
    enemy = copy.deepcopy(enemyDatas[3])

    pos = [23,9]

    enemy.pos = pos
    curStageEnemies[curStage].append( enemy )
    image = canvas.create_image(16 + pos[0]*32 , 16 + pos[1]*32 , image=enemyImages[enemy.image_number][3], tag="Enemy") 
    curStageEnemiesCanvas[curStage].append( image )

    enemy = copy.deepcopy(enemyDatas[7])
    pos = [23,8]

    enemy.pos = pos
    curStageEnemies[curStage].append( enemy )
    image = canvas.create_image(16 + pos[0]*32 , 16 + pos[1]*32 , image=enemyImages[enemy.image_number][3], tag="Enemy") 
    curStageEnemiesCanvas[curStage].append( image )


def set_item():
    global curStageItems, stages

    #위치
    for i in range(stageDropCounts[curStage][0]) :
        pos = [random.randint(0,24), random.randint(0,14)]

        while(True):
            if stages[curStage][pos[1]][pos[0]] == 0: 
                stages[curStage][pos[1]][pos[0]] = 3
                break
            else :
                pos = [random.randint(1,23), random.randint(1,13)]

        #세팅
        item = copy.deepcopy(random.choice(itemDatas))
        item.pos = pos
        curStageItems[curStage].append( item )
        canvas.create_image(16 + pos[0]*32 , 16 + pos[1]*32 , image=itemImages[item.image_number][0], tag="Item") 

#endregion

#region UI

def draw_stage():
    canvas.create_image(400,240, image=backGroundImages[curStage+1], tag = "Background")

def draw_ui():
    #canvas.create_image(64 , 48 , image=uiImages[0], tag="UI")
    #canvas.create_image(32*25-64 , 48 , image=uiImages[0], tag="UI")
    canvas.create_image(400 , 48 , image=uiImages[1], tag="UI")
    canvas.create_image(48 , 48 , image=uiImages[2], tag="UI")
    restore_playerInfo()
    AddLog("모험 시작")

def draw_txt(txt,x,y,siz,col):
    fnt = ("Times New Roman",siz,"bold")
    canvas.create_text(x+2,y+2,text=txt,fill="black",font=fnt,tag ="screen")
    canvas.create_text(x,y,text=txt,fill=col,font=fnt,tag="screen")

def restore_playerInfo():
    global player
    if(isDie) : return
    canvas.delete("PlayerInfo")
    fnt = ("Sam3KRFont",12)
    canvas.create_text(100,12,text="용사 "+"체력 "+str(player.stat.hp)+'/'+str(player.stat.maxHp) +
                       " 무게 "+str(player.weight),fill="white",font=fnt,tag ="PlayerInfo",anchor="w")
    canvas.create_text(100,36,text= "무기 "+player.weapon.name+"   범위 "+str(player.weapon.weaponEffect[0]),
                       fill="white",font=fnt,tag ="PlayerInfo",anchor="w")
    
    
    canvas.create_text(100,66,text="공격력 [물리/마법] "+'['+str(player.stat.str)+'/'+str(player.stat.spr)+']',
                       fill="white",font=fnt,tag ="PlayerInfo",anchor="w")
    #canvas.create_text(100,76,text="방어력 [물리/마법] "+'['+str(player.stat.dep)+'/'+str(player.stat.res)+']',
    #                   fill="white",font=fnt,tag ="PlayerInfo",anchor="w")

def AddLog(text):
    global logText
    logText.place(x=300, y=11)
    logText.insert(tkinter.END, text+'\n')
    logText.yview(tkinter.END)
    


def DrawEffect(targetPos, image) :
    canvas.create_image(16 + targetPos[0]*32 , 16 + targetPos[1]*32 ,image=image, tag="Effect")
    canvas.update()
    time.sleep(0.2)
    canvas.delete("Effect")
    canvas.update()


#endregion

#region 리셋

def clear_game():
    global stopInput, isClear
    #draw_txt("STAGE CLEAR!",360,270,40,"violet")
    stopInput = True
    isClear = True
    logText.destroy()
    canvas.delete("ALL")
    canvas.create_image(400,240, image=script_image[2], tag ="ending")

def end_game():
    global turn, isDie, canvas
    turn = True
    isDie = True
    #reset_game()
    #draw_txt("GAME OVER",370,350,40,"red")

    logText.destroy()
    canvas.delete("ALL")
    canvas.create_image(400,240, image=img_title[1], tag = "title")
    
        
def reset_game():
    #draw_txt("Press ENTER",400,350,40,"yellow")
    canvas.create_image(400,240,image=img_title[0])

def reset():
    global turn, curStage, isDie, logText
    isDie = False
    turn = False
    curStage = 0
    canvas.delete("ALL")

    #0번 검은 화면에 
    logText = tkinter.Text(width=58, height=5, font=("Sam3KRFont", 12),bg="black", fg="white")
    changeBGM("battle_BGM.mp3", -1)
    CopyStage()
    draw_stage()
    reset_data()
    set_stage()
    move_player()
    restore_playerInfo()

def reset_data():
    global player,  curStageItems, curStageEnemies, curStageEnemiesCanvas, curX, curY
    player = Player(Stat("용사",20,1,1,1,1,1))
    player.pos = [2,8]
    curX = 2
    curY = 8
    curStageItems = [[],[],[],[],[]]
    curStageEnemies = [[],[],[],[],[]]
    curStageEnemiesCanvas = [[],[],[],[],[]]
   
#endregion


def changeBGM(name,loop):
    global bgm
    bgm.stop()
    bgm = bgm = pygame.mixer.Sound(name)
    bgm.play(loop)

#effect

#현재 위치

turn = False
tmr = 0
idx = 0

player = Player(Stat("용사",1,1,1,1,1,1))
player.pos = [2,8]

curX = player.pos[0]
curY = player.pos[1]
curStage = ""

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

canvas = tkinter.Canvas(width=800, height=480, bg="white")
canvas.pack()
bgm.play()
reset_game()
root.mainloop()
