"""
An example of fgo mission bot.
:author: @Edwardsaga
"""
from libs.mission_bot import automatic_bot
import logging

# 指定日志的输出等级（DEBUG / INFO / WARNING / ERROR）
logging.basicConfig(level=logging.DEBUG)
# 实例化一个bot
bot = automatic_bot(

    # 要打的关卡截图为'hetao_free.png'，放在./images/transport下
    target_mission="hetao_free",

    # 需要的助战截图为'caber.png'，放在./images/friends下
    # 如果可以接受的助战有多个，可以传入一个list，例如：friend=['caber.png', 'caber_qp.png]
    # 当前无指定助战时，会自动下滑和刷新
    friends="caber",
    # 助战职介为caster, 支持七职介小写英文和all、extra
    friends_work="caster",
    # 使用队伍名截图为'chengong.png', 放在./images下
    team='chengong',

    # XJBD时的优先选卡顺序, 为保证稳定需对队伍中可能出现的指令卡头像进行截图，放在./images/friends下
    prim_cards=["card_chengong","card_simayi","card_caber3","card_caber2","card_kongming"],
    # AP策略为：当体力耗尽时，优先吃银苹果，再吃金苹果
    # 如果不指定ap参数，则当体力耗尽时停止运行
    ap_strategy=['sliver_apple','gold_apple'],
    # 要打的关卡有3面
    stage_count=3,
    # 关卡图像识别的阈值为0.95
    # 如果设的过低会导致进错本，太高会导致无法进本，请根据实际情况调整
    quest_threshold=0.95,

    # 助战图像识别的阈值为0.99
    # 如果设的过低会导致选择错误的助战，太高会导致选不到助战，请根据实际情况调整
    friend_threshold=0.99,

    # 仅当ap参数为'wait_ap'时用来计算等待体力回复时间，其余情况可以无视
    ap_cost=20,
)
#将'./images/'设置为root_path
root_path="D:/games/FGO/FGO_bot/images/"
transport_path=root_path+"transport/"
friends_path=root_path+"friends/"
skill_path=root_path+"skills/"
#图片路径设置和tm初始化
#window_name 根据不同模拟器调整：
# 雷电模拟器：'雷电模拟器'
# MUMU: '命运-冠位指定 - MuMu模拟器'
bot.set_touch_manager(window_name = "雷电模拟器",
                 root_path = root_path,
                 transport_path = transport_path,
                 friends_path = friends_path,
                 skills_path = skill_path)
# 为了方便，使用了简写
s = bot.use_skill
m = bot.use_master_skill
a = bot.attack

# 第一面的打法
@bot.at_stage(1)
def stage_1():
    # s(1, 2, 2)表示使用1号从者的技能2, 目标为2
    s(1, 2, 2)
    s(1, 3, 2)
    s(1, 1)
    # (a[7, 2, 3])表示出卡顺序为：7号卡（2号从者宝具卡），按xjbd优先级选剩余两张卡
    a([7, 2, 3])


# 第二面的打法
@bot.at_stage(2)
def stage_2():
    s(1, 2)
    s(1, 3)
    s(2, 2)
    a([7, 2, 3])


# 第三面的打法
@bot.at_stage(3)
def stage_3():
    s(3, 2, 2)
    s(3, 3, 2)
    s(3, 1)
    # m(2, 2)表示使用御主技能2，对象为2号从者
    # m(4, 1, 5)表示使用换人技能，对象为1号位和5号位
    m(2, 2)
    a([7,2,3])

# 程序的入口点
# 使用时，可以直接在命令行运行'python bot_example.py'
if __name__ == '__main__':

    # 启动bot，最多打5次
    bot.run(max_loops=1)
