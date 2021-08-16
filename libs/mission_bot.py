"""
The automatic bot.
:author: @Edwardsaga
"""
import logging
import time
import random
import json
from pathlib import Path
from libs.toucher import touch_manager
from typing import Tuple, List, Union,Dict, Any, Callable
logger = logging.getLogger('mission_bot')


class automatic_bot(object):
    """
    A class of the automatic bot.
    """
    def __init__(self,
                 transport_ways: Union[str, List[str]] = ["daily_port","daily_port2"],
                 target_mission: str = "sword_pai",
                 friends: Union[str, List[str]] = "cba_wucha",
                 friends_work: str="caster",
                 team: str = "jiban",
                 prim_cards:List[str]=["card_extra_lin", "card_simayi", "card_kongming"],
                 stage_count=3,
                 ap_strategy: List[str] = ["wait_ap"],
                 quest_threshold: float = 0.97,
                 friend_threshold: float = 0.98,
                 ap_cost=40,
                 ):
        """
        Initial

        Args:
            transport_ways: The touch templates from start to target mission.
            target_mission: The touch template of target mission.
            friends: The touch templates of usable 助战.
            friends_path: The path of friends images.
            friends_work: The class of friends servant (saber/lancer/.....)
            team: 需要的队伍名截图
            prim_cards: XJBD时的优先选卡策略
            stage_count: stage nums (1-3)
            ap_strategy: 可选的体力使用策略 wait_ap: 自回体 gold_apple: 金苹果
            quest_threshold: The threshold of mission teamplate match
            friend_threshold: The threshold of friend teamplate match
        """
        self.transport_ways=transport_ways
        self.target_mission=target_mission
        if isinstance(friends, str):
            friends = [friends]
        self.friends=friends
        self.prim_cards=prim_cards
        self.stage_handlers = {}

        self.friend_work=friends_work
        self.team = team
        self.stage_count=stage_count
        self.ap_strategy=ap_strategy
        self.quest_threshold=quest_threshold
        self.friend_threshold=friend_threshold
        self.ap_cost=ap_cost
        # Load button coords from config
        btn_path = Path.cwd() / 'config' / 'buttons.json'
        with open(btn_path) as f:
            self.buttons = json.load(f)

        self.friend_refresh= "refresh"
        logger.debug('Automatic bot initialized.')

    def __add_stage_handler(self, stage: int, f: Callable):
        """
        Register a handler function to a given stage of the battle.

        :param stage: the stage number
        :param f: the handler function
        """
        assert not self.stage_handlers.get(stage), 'Cannot register multiple function to a single stage.'
        logger.debug('Function {} registered to stage {}'.format(f.__name__, stage))
        self.stage_handlers[stage] = f
    def __wait(self,t=0.4):
        """
        Sleep with random time.
        """
        time.sleep(t+0.2*t*random.random())
    def __wait_until(self, im: str,is_attack=False):
        """
        Wait until the given image appears. Useful when try to use skills, etc.
        """
        logger.debug("Wait until image '{}' appears.".format(im))
        while not self.toucher.if_exist(im,0.95):
            self.__wait(0.08)

    def __wait_until_battale(self, im: str):
        """
        Wait until the given image appears. Useful when try to use skills, etc.
        """
        logger.debug("Wait until image '{}' appears in battle.".format(im))
        while not self.toucher.if_exist(im,0.95):
            self.toucher.doClick(800,450,0.1)
    def __get_current_stage(self) -> int:
        """
        Get the current stage in battle.

        :return: current stage. Return -1 if error occurs.
        """
        print('getting stage')
        self.__wait_until_battale('attack')
        max_prob, max_stage = 0.8, -1
        for stage in range(1, self.stage_count + 1):
            im = '{}_{}'.format(stage, self.stage_count)
            prob = self.toucher.exist_prob(self.toucher.get_screen(),im)
            if prob > max_prob:
                max_prob, max_stage = prob, stage

        if max_stage == -1:
            logger.error('Failed to get current stage.')
        else:
            logger.debug('Got current stage: {}'.format(max_stage))

        return max_stage

    def __find_friend(self) -> str:
        """
        Refresh the ui until target friend appeared.

        :return: the finded template.
        """
        self.__wait_until(self.friend_refresh)
        self.toucher.find_and_tap(self.friend_work,0.85)
        finded=False
        count=0
        find_img=[]
        while not finded:
            for fid in range(len(self.friends)):
                im = self.friends[fid]
                finded=self.toucher.if_exist(im,0.95)
                if(finded):
                    return im
                self.__wait(0.2)
            self.__swipe()
            self.__wait(0.2)
            count+=1
            if(count>=2):
                self.__wait_until(self.friend_refresh)
                self.toucher.find_and_tap(self.friend_refresh,pause_time=0.2)
                self.__wait(0.2)
                self.toucher.find_and_tap('yes')
                self.__wait(1)
                count=0

    def __prim_attack_single(self):
        count=0
        for card in self.prim_cards:
            if self.toucher.if_exist(card,0.95):
                self.toucher.find_and_tap_part(card,[0,1600],[300,900], pause_time=0.2)
                return True
        return False
    def __swipe(self):
        """
        Swipe in given track.
        """
        self.toucher.doSlide([1000,800],[1000,400])
        self.__wait(0.2)
    def __ap_charge(self):
        # no enough AP
        if self.toucher.if_exist('ap_regen'):
            print("ap need charge")
            if not self.ap_strategy:
                return False
            else:
                ok = False
                for ap_item in self.ap_strategy:
                    if self.toucher.find_and_tap(ap_item):
                        self.__wait(1)
                        if ap_item == 'wait_ap':
                            logger.debug('Sleep {} minutes.'.format(self.ap_cost * 5))
                            localtime = time.asctime(time.localtime(time.time()))
                            print("休眠时时间为 :", localtime)
                            time.sleep(self.ap_cost * 5 * 60 + 30)
                            while not self.toucher.find_and_tap(self.target_mission, threshold=self.quest_threshold):
                                self.__swipe()
                            self.__wait(0.5)
                            ok = True
                            break
                        if self.toucher.find_and_tap('decide'):
                            self.__wait_until(self.friend_refresh)
                            ok = True
                            break
                return ok
        else:
            return True
    def __enter_battle(self) -> bool:
        """
        Enter the battle.

        :return: whether successful.
        """
        quick_continue=False
        while not self.toucher.if_exist("menu"):
            if self.toucher.if_exist("continue_mission"):
                self.toucher.find_and_tap("continue_mission")
                quick_continue=True
                break
            self.__wait(0.5)
        if not quick_continue:
            while not self.toucher.find_and_tap(self.target_mission, threshold=self.quest_threshold):
                self.__swipe()
            self.__wait(0.5)
        self.__wait(1)
        if not self.__ap_charge():
            return False
        # look for friend servant
        find_img=self.__find_friend()
        self.toucher.find_and_tap(find_img)
        self.__wait(0.5)
        if not quick_continue:
            self.__wait_until('start_quest')
            while (True):
                if self.toucher.if_exist(self.team):
                    break
                else:
                    #TODO:test the touch position
                    self.toucher.doClick((int)(1250*1.25),(int)(360*1.25))
                    self.__wait(0.2)
            self.toucher.find_and_tap('start_quest')
        self.__wait_until_battale('attack')
        return True

    def __button(self, btn):
        """
        Return the __button coords and size.

        :param btn: the name of __button
        :return: (x, y, w, h)
        """
        btn = self.buttons[btn]
        return btn['x'], btn['y'], btn['w'], btn['h']

    def __play_battle(self) -> int:
        """
        Play the battle.

        :return: count of rounds.
        """
        rounds = 0
        while True:
            stage = self.__get_current_stage()
            if stage == -1:
                logger.error("Failed to get current stage. Leaving battle...")
                return rounds

            rounds += 1
            logger.info('At stage {}/{}, round {}, calling handler function...'
                        .format(stage, self.stage_count, rounds))
            self.stage_handlers[stage]()

            while True:
                self.__wait(0.2)
                if self.toucher.if_exist('bond') or self.toucher.if_exist('bond_up') or self.toucher.if_exist('next_step'):
                    logger.info("'与从者的羁绊' detected. Leaving battle...")
                    return rounds
                elif self.toucher.if_exist('attack'):
                    logger.info("'Attack' detected. Continuing loop...")
                    break
                elif self.toucher.if_exist('in_battle'):
                    logger.info('指令卡未正常点击，按优先级XJBD以退出')
                    for i in range(3):
                        self.__prim_attack_single()
                self.toucher.doClick(800, 450, 0.1)
                self.__wait(0.1)

    def __end_battle(self):
        # self.__find_and_tap('bond')
        # self.__wait(INTERVAL_SHORT)
        # self.__wait_until('gain_exp')
        # self.__find_and_tap('gain_exp')
        # self.__wait(INTERVAL_SHORT)
        self.__wait(0.5)
        while not self.toucher.if_exist('next_step'):
            self.toucher.doClick((int)(640*1.25+50**1.25), (int)(360*1.25+50*1.25))
            self.__wait(0.5)

        self.toucher.find_and_tap('next_step')
        self.__wait(0.5)

        # quest first-complete reward
        if self.toucher.if_exist('please_tap'):
            self.toucher.find_and_tap('please_tap')
            self.__wait(0.2)

        # not send friend application
        if self.toucher.if_exist('not_apply'):
            self.toucher.find_and_tap('not_apply')

        if self.toucher.if_exist('complete'):
            self.toucher.find_and_tap('please_tap')
        self.__wait(0.5)

    def set_touch_manager(self,window_name: str = "雷电模拟器",
                 root_path: str = "D:/games/FGO/FGO_bot/images/",
                 transport_path: str = "D:/games/FGO/FGO_bot/images/transport/",
                 friends_path: str = "D:/games/FGO/FGO_bot/images/friends/",
                 skills_path: str = "D:/games/FGO/FGO_bot/images/skills/",
                 ):
        """
        Set the touch manager and load images

        Args:
            window_name: The simulator window name.
            root_path: The path of main images.
            transport_path: The path of mission images.
            friends_path: The path of friends images.
            skills_path: The path of skill images.
        """
        # self.toucher=touch_manager(window_name,root_path,transport_path,friends_path,skills_path)
        # for i in range(len(self.transport_ways)):
        #     self.toucher.loadImage(transport_path + self.transport_ways[i] + ".png",self.transport_ways[i])
        # for i in range(len(self.friends)):
        #     self.toucher.loadImage(friends_path + self.friends[i] + ".png",self.friends[i])
        # self.toucher.loadImage(transport_path + self.target_mission + ".png", self.target_mission)
        #
        # self.toucher.loadImage(friends_path + "refresh.png", "refresh")
        # self.toucher.loadImage(friends_path + self.friend_work+".png", self.friend_work)
        # self.toucher.loadImage(friends_path + self.team+".png", self.team)
        # self.toucher.loadImage(root_path + "gold_apple.png", "gold_apple")
        # self.toucher.loadImage(root_path + "yes.png", "yes")
        self.toucher=touch_manager(window_name,root_path,transport_path,friends_path,skills_path)
        im_dir = Path(root_path)
        self.toucher.load_images(im_dir)
        im_dir = Path(skills_path)
        self.toucher.load_images(im_dir)
        im_dir = Path(transport_path)
        self.toucher.load_images(im_dir)
        im_dir = Path(friends_path)
        self.toucher.load_images(im_dir)
        logger.debug('Images Loaded.')

    def at_stage(self, stage: int):
        """
        A decorator that is used to register a handler function to a given stage of the battle.

        :param stage: the stage number
        """

        def decorator(f):
            self.__add_stage_handler(stage, f)
            return f

        return decorator

    def use_skill(self, servant: int, skill: int, obj=None):
        """
        Use a skill.

        :param servant: the servant id.
        :param skill: the skill id.
        :param obj: the object of skill, if required.
        """
        print('using skill')
        self.__wait_until_battale('attack')
        x, y, w, h = self.__button('skill')
        x += self.buttons['servant_distance'] * (servant - 1)
        x += self.buttons['skill_distance'] * (skill - 1)

        screen=self.toucher.get_screen()
        # cv.line(screen,(319,0),(319,719),(0,0,255),5)
        # cv.line(screen,(319*2,0),(319*2,719),(0,0,255),5)
        # cv.line(screen,(319*3,0),(319*3,719),(0,0,255),5)
        # cv.imshow('screen',screen)
        # cv.waitKey(0)
        x_b=[int(560*1.25),int(620*1.25)]
        y_b=[int(((servant-1)*319+(skill-1)*90+24)*1.25),int(((servant-1)*319+(skill-1)*90+84)*1.25)]
        prob = self.toucher.exist_prob(screen[x_b[0]:x_b[1],y_b[0]:y_b[1],:], 'skill_cd')
        if prob>0.8:
            print('从者'+str(servant)+'技能'+str(skill)+'冷却中')
            return True


        self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
        logger.debug('Used skill ({}, {})'.format(servant, skill))
        self.__wait(0.2)

        if self.toucher.if_exist('servant_state'):
            self.toucher.find_and_tap('close')

        if obj is not None:
            if self.toucher.if_exist('choose_object'):
                x, y, w, h = self.__button('choose_object')
                x += self.buttons['choose_object_distance'] * (obj - 1)
                self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25),pause_time=0.2)
                logger.debug('Chose skill object {}.'.format(obj))

        if self.toucher.if_exist('servant_state'):
            self.toucher.find_and_tap('close')

        self.__wait(0.2)




    def use_master_skill(self, skill: int, obj=None, obj2=None):
        """
        Use a master skill.
        Param `obj` is needed if the skill requires a object.
        Param `obj2` is needed if the skill requires another object (Order Change).

        :param skill: the skill id.
        :param obj: the object of skill, if required.
        :param obj2: the second object of skill, if required.
        """
        if skill<=3:
            print('using master_skill')
            self.__wait_until_battale('attack')

            x, y, w, h = self.__button('master_skill_menu')
            self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
            self.__wait(0.2)

            x_b = [int(310 * 1.25), int(365 * 1.25)]
            y_b = [int(((skill-1)*94+855) * 1.25),
                   int(((skill-1)*94+925) * 1.25)]
            screen=self.toucher.get_screen()
            prob = self.toucher.exist_prob(screen[x_b[0]:x_b[1], y_b[0]:y_b[1], :], 'master_skill_cd')

            if prob>0.8:
                print('御主技能'+str(skill)+'冷却中')
                return True

            x, y, w, h = self.__button('master_skill')
            x += self.buttons['master_skill_distance'] * (skill - 1)
            self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
            logger.debug('Used master skill {}'.format(skill))
            self.__wait(0.2)

            if obj is not None:
                if self.toucher.if_exist('choose_object'):
                    x, y, w, h = self.__button('choose_object')
                    x += self.buttons['choose_object_distance'] * (obj - 1)
                    self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
                    logger.debug('Chose master skill object {}.'.format(obj))

            self.__wait(0.2)

        if skill==4:
            print('using exchange_skill')
            self.__wait_until_battale('attack')

            x, y, w, h = self.__button('master_skill_menu')
            self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
            self.__wait(0.2)

            x_b = [int(310 * 1.25), int(365 * 1.25)]
            y_b = [int(((skill - 2) * 94 + 855) * 1.25),
                   int(((skill - 2) * 94 + 925) * 1.25)]
            screen = self.toucher.get_screen()
            prob = self.toucher.exist_prob(screen[x_b[0]:x_b[1], y_b[0]:y_b[1], :], 'master_skill_cd')

            if prob > 0.8:
                print('御主技能' + str(skill) + '冷却中')
                return True


            x, y, w, h = self.__button('master_skill')
            x += self.buttons['master_skill_distance'] * (skill - 2)
            self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25))
            logger.debug('Used master skill {}'.format(skill))
            self.__wait(0.2)

            x, y, w, h = self.__button('swap')
            x += self.buttons['swap_distance'] * (obj - 1)
            self.toucher.doClick((int)((x)*1.25), (int)((y)*1.25))
            self.__wait(0.2)
            x, y, w, h = self.__button('swap')
            x += self.buttons['swap_distance'] * (obj2 - 1)
            self.toucher.doClick((int)((x)*1.25), (int)((y)*1.25))
            self.__wait(0.2)

            self.toucher.find_and_tap("confirm_swap")

            print('exchanged')

            self.__wait(0.2)

    def attack(self, cards: list):
        """
        Tap attack __button and choose three cards.

        1 ~ 5 stands for normal cards, 6 ~ 8 stands for noble phantasm cards.

        :param cards: the cards id, as a list

        """
        assert len(cards) == 3, 'Number of cards must be 3.'
        assert len(set(cards)) == 3, 'Cards must be distinct.'
        print('attacking')
        self.__wait_until_battale('attack')
        self.__wait(0.8)

        while not self.toucher.if_exist('in_battle'):
            self.toucher.find_and_tap('attack')
            self.__wait(0.3)

        self.__wait(1)
        for card in cards:
            if 1 <= card <= 5:
                self.__prim_attack_single()
            elif 6 <= card <= 8:
                # template = self.toucher.images['noble_filled']
                # screen=self.toucher.get_screen()
                # x_b = [int(650 * 1.25), int(700 * 1.25)]
                # y_b = [int(((card-6)*319) * 1.25),
                #        int(((card-5)*319) * 1.25)]
                # prob = self.toucher.exist_prob(screen[x_b[0]:x_b[1], y_b[0]:y_b[1], :], 'noble_filled')
                #
                # if prob<0.8:
                #     print('从者'+str(card-5)+'宝具卡'+'未充满')
                #     x, y, w, h = self.__button('card')
                #     x += self.buttons['card_distance'] * (card - 4)
                #     self.toucher.doClick((int)(x*1.25+w*1.25/2), (int)(y*1.25+h*1.25/2),0.5)
                #     continue

                x, y, w, h = self.__button('noble_card')
                x += self.buttons['card_distance'] * (card - 6)
                self.toucher.doClick((int)((x+w/2)*1.25), (int)((y+h/2)*1.25),0.25)
            else:
                logger.error('Card number must be in range [1, 8]')

    def run(self, max_loops: int = 10):
        """
        Start the bot.

        :param max_loops: the max number of loops.
        """
        count = 0
        for n_loop in range(max_loops):
            print('第'+str(n_loop)+'次进入副本')
            logger.info('Entering battle...')
            if not self.__enter_battle():
                logger.info('AP runs out. Quiting...')
                break
            rounds = self.__play_battle()
            self.__end_battle()
            count += 1
            logger.info('{}-th Battle complete. {} rounds played.'.format(count, rounds))

        logger.info('{} Battles played in total. Good bye!'.format(count))




