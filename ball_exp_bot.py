"""
自动搓丸子 bot.
原则上仅是本人自用脚本
如需使用，运行前请务必保证：
1、友情池免费一抽用过
2、礼装强化对象选择中筛选仅显示1、2星礼装，按稀有度倒序
3、礼装强化素材选择中筛选仅显示1、2星礼装，按稀有度倒序
4、所有从者均上锁
5、将所有需要保留的金银芙芙和高级经验值收入灵基保管室或上锁
6、商店灵基变还中，筛选显示从者、芙芙、经验值，按稀有度升序
7、将游戏置于主界面（迦勒底亚斯
8、灵基保管室中筛选仅显示1、2星礼装礼装，按等级倒序
:author: @Edwardsaga
"""
import logging
import time
import random
import json
from pathlib import Path
from libs.toucher import touch_manager
logger = logging.getLogger('exp_bot')

window_name= "命运-冠位指定 - MuMu模拟器"
# window_name= "雷电模拟器"

#将'./images/'设置为root_path
root_path="D:/games/FGO/FGO_bot/images/"
transport_path=root_path+"transport/"
friends_path=root_path+"friends/"
skills_path=root_path+"skills/"
ballexp_path = root_path+"ballexp/"

use_main = False
toucher = touch_manager(window_name, root_path, transport_path, friends_path, skills_path, use_main)
im_dir = Path(ballexp_path)
toucher.load_images(im_dir)
logger.debug('Images Loaded.')
toucher.save_screen("nox_test.png")

def swipe():
    """
    Swipe in given track.
    """
    toucher.doSlide([1000, 800], [1000, 400])
    wait(0.2)

def wait(t=0.4):
    """
    Sleep with random time.
    """
    time.sleep(t + 0.2 * t * random.random())

def wait_until(im: str, addition_wait=0.0, not_appear=False):
    """
    Wait until the given image appears. Useful when try to use skills, etc.
    """
    logger.debug("Wait until image '{}' appears.".format(im))
    while toucher.if_exist(im, 0.95) is not_appear:
        wait(0.05)
    wait(addition_wait)

def wait_until_tap(im: str, addition_wait=0.0):
    """
    Wait until the given image appears. Useful when try to use skills, etc.
    """
    logger.debug("Wait until image '{}' appears in battle.".format(im))
    while not toucher.if_exist(im, 0.99):
        toucher.doClick(1550, 850, 0.02)
    wait(addition_wait)
def select_swipe(im, release_time=0.5):
    """
    select cards by slide mouse.
    """
    toucher.find_and_tap(im,pause_time=1, Not_release=True)
    toucher.moveMouse_release(1200,850,release_time)

def select_swipe_pos(x,y, release_time=0.5):
    toucher.doClick(x,y,pause_time=1,Not_release=True)
    toucher.moveMouse_release(1200,850,release_time)


def gacha_prepare():
    """
        gacha in friend points pool until full.
    """
    wait_until("gacha")
    toucher.find_and_tap("gacha",pause_time=0.2)
    wait(0.3)
    while(1):
        if toucher.if_exist("gacha_full", 0.95):
            return
        wait_until("decide")
        toucher.find_and_tap("decide")
        wait_until("gacha_continue",not_appear= True)
        wait_until_tap("gacha_continue")
        toucher.find_and_tap("gacha_continue", pause_time=0.2)
        wait(0.3)

def sold_out():
    """
        sell servants.
    """
    if not toucher.if_exist("equip_full"):
        toucher.find_and_tap("sold",pause_time=0.5)
        wait_until("niu")
        select_swipe("niu", 40)
        wait(1)
        toucher.find_and_tap("decide_sold",pause_time=0.5)
        wait_until("destroy")
        toucher.find_and_tap("destroy", pause_time=0.5)
        wait_until("close")
        toucher.find_and_tap("close", pause_time=0.5)
        toucher.find_and_tap("close_menu", pause_time=0.5)
        return True
    else:
        toucher.find_and_tap("quick_enhance_port",pause_time=0.5)
        return False

def enter_enhance():
    """
        enter enhance hall.
    """
    toucher.find_and_tap("menu", pause_time=0.5)
    toucher.find_and_tap("enhance_port", pause_time=1)
    toucher.find_and_tap("enhance_craft", pause_time=0.5)
    wait_until("enhance_hall",addition_wait=0.1)

def enter_gacha():
    """
        enter friend points gacha pool.
    """
    print("enter_gacha")
    toucher.find_and_tap("menu", pause_time=0.5)
    toucher.find_and_tap("gacha_port", pause_time=0.5)
    wait_until("main_pool",addition_wait=0.2)
    toucher.doClick(100,450,pause_time=0.5) #切友情池
    wait_until("gacha",addition_wait=0.1)


def tap_slider_bottom():
    toucher.doClick(1270,865,pause_time=0.2)

def enhance_ball():
    """
        enhance ball.
    """
    print('enter enhance.')
    wait_until_tap("enhance_hall",addition_wait=0.1)
    toucher.doClick(200,450,pause_time=0.2) #左侧选择
    wait_until("equip_select_hall",addition_wait=0.5)

    tap_slider_bottom()
    if not toucher.if_exist("ball_base",threshold=0.95):
        toucher.find_and_tap("close_menu", pause_time=0.2)
        return False
    toucher.find_and_tap("ball_base", pause_time=0.2)
    wait_until("enhance_hall",addition_wait=0.1)
    toucher.doClick(1000,400,pause_time=0.2) #右侧选择
    wait_until("equip_select_hall",addition_wait=0.5)

    tap_slider_bottom()
    wait(0.2)
    if not toucher.if_exist("ball_for_up",threshold=0.95):
        toucher.find_and_tap("close_menu", pause_time=0.2)
        return False
    toucher.find_and_tap("ball_for_up", pause_time=0.2)
    toucher.find_and_tap("decide_sold", pause_time=0.2)
    wait_until("enhance_hall",addition_wait=0.1)

    toucher.doClick(1500,850,pause_time=0.2) #强化按钮
    wait_until("decide_equip")
    toucher.find_and_tap("decide_equip", pause_time=0.2)
    wait_until("enhance_hall", not_appear=True)
    wait_until_tap("enhance_hall",addition_wait=0.1)

    toucher.doClick(1000,400,pause_time=0.3) #右侧选择
    wait_until("equip_select_hall",addition_wait=0.5)

    if toucher.if_exist("main_ball_dark",threshold=0.98):
        toucher.find_and_tap("close_menu", pause_time=0.2)
        return False
    select_swipe_pos(200,300,release_time=0.5)
    toucher.find_and_tap("decide_sold",pause_time=0.2)
    wait(0.5)
    wait_until_tap("enhance_hall",addition_wait=0.1)

    toucher.doClick(1500,850,pause_time=0.2) #强化按钮
    wait_until("decide_equip")
    toucher.find_and_tap("decide_equip", pause_time=0.2)
    wait(0.5)

    return True

def initial_main_ball():
    """
        initial a main ball.
    """
    wait_until_tap("enhance_hall",addition_wait=0.1)
    print('initial main ball.')

    toucher.doClick(200,450,pause_time=0.2) #左侧选择
    wait_until("equip_select_hall",addition_wait=0.5)

    tap_slider_bottom()
    toucher.find_and_tap("ball_base", pause_time=0.2)
    wait_until("enhance_hall",addition_wait=0.1)
    toucher.doClick(1000,400,pause_time=0.2) #右侧选择
    wait_until("equip_select_hall",addition_wait=0.5)

    tap_slider_bottom()
    for i in range(4):
        toucher.find_and_tap("ball_for_up", pause_time=0.2)
    toucher.find_and_tap("decide_sold", pause_time=0.2)
    wait_until("enhance_hall",addition_wait=0.1)

    toucher.doClick(1500,850,pause_time=0.2) #强化按钮
    wait_until("decide_equip")
    toucher.find_and_tap("decide_equip", pause_time=0.2)
    wait(0.5)
    wait_until_tap("enhance_hall",addition_wait=0.1)

    toucher.doClick(1000, 400, pause_time=0.2)  # 右侧选择
    wait_until("equip_select_hall", addition_wait=0.5)

    select_swipe_pos(200,300,release_time=0.5)
    toucher.find_and_tap("decide_sold",pause_time=0.2)
    wait(0.5)
    wait_until_tap("enhance_hall",addition_wait=0.1)

    toucher.doClick(1500,850,pause_time=0.2) #强化按钮
    wait_until("decide_equip")
    toucher.find_and_tap("decide_equip", pause_time=0.2)
    wait(0.5)
    wait_until_tap("enhance_hall",addition_wait=0.1)

    toucher.doClick(200,450,pause_time=0.2) #左侧选择
    wait_until("equip_select_hall",addition_wait=0.5)
    #上锁
    toucher.find_and_tap("lock", pause_time=0.2)
    toucher.doClick(200,300,pause_time=0.2) #强化按钮
    toucher.find_and_tap("close_menu", pause_time=0.2)
    wait_until("enhance_hall",addition_wait=0.1)

def enhance_main_ball():
    """
        enhance main ball.
    """
    print('enhance main ball.')
    toucher.doClick(200,450,pause_time=0.2) #左侧选择
    wait_until("equip_select_hall",addition_wait=0.5)
    while not toucher.if_exist("main_ball",threshold=0.98):
        swipe()
        wait(0.5)
    toucher.find_and_tap("main_ball")
    wait_until("enhance_hall",addition_wait=0.1)
    while(1):
        toucher.doClick(1000,400,pause_time=0.2) #右侧选择
        wait_until("equip_select_hall",addition_wait=0.5)

        if not toucher.if_exist("ball_up_1", threshold=0.999):
            toucher.find_and_tap("close_menu", pause_time=0.2)
            wait_until("enhance_hall", addition_wait=0.1)
            return False
        select_swipe_pos(200, 300, release_time=0.5)
        toucher.find_and_tap("decide_sold", pause_time=0.2)
        wait(0.5)
        wait_until_tap("enhance_hall", addition_wait=0.1)

        toucher.doClick(1500,850,pause_time=0.2) #强化按钮
        wait_until("decide_equip")
        toucher.find_and_tap("decide_equip", pause_time=0.2)
        wait(0.5)
        wait_until_tap("enhance_hall",addition_wait=0.1)
        if toucher.if_exist("full_exp",threshold=0.99):
            return False

def save_main_ball():
    """
        save main ball.
    """
    print('save main ball.')
    toucher.find_and_tap("close_menu", pause_time=1)
    toucher.find_and_tap("menu", pause_time=0.5)
    toucher.find_and_tap("teamwork", pause_time=1)
    toucher.find_and_tap("save_room", pause_time=0.5)
    wait(0.5)
    toucher.find_and_tap("equip_page", pause_time=0.5)
    wait(0.5)
    toucher.doClick(200,300,pause_time=0.2)
    toucher.find_and_tap("decide_sold", pause_time=0.5)
    toucher.find_and_tap("excute", pause_time=1)
    toucher.find_and_tap("close", pause_time=0.5)
    toucher.find_and_tap("close_menu", pause_time=1)

if __name__ == '__main__':

    for i in range(16):
        has_main_ball=False
        # if(i==0):
        #     has_main_ball=True
        while(1):
            print("已经搓了"+str(i)+"个丸子")
            enter_gacha()
            gacha_prepare()
            wait(1)
            if sold_out():
                enter_enhance()
            if not has_main_ball:
                initial_main_ball()
                has_main_ball=True
            while(enhance_ball()):
                wait(0.1)
            wait_until("enhance_hall",addition_wait=0.1)
            enhance_main_ball()
            if toucher.if_exist("full_exp",threshold=0.99):
                break
            else:
                toucher.find_and_tap("close_menu", pause_time=1)
        save_main_ball()


