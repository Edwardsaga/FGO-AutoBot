# FGO AutoBot
 根据Win32 API编写的高效自动化战斗脚本以及搓丸子脚本  
 框架参考[@will7101/fgo-bot](https://github.com/will7101/fgo-bot)

# 原理及特性
- 通过Win32 API获取模拟器窗口内容，并模拟鼠标点击、滑动等操作，**支持后台运行，不支持窗口最小化**
- Win32 API响应速度很快，甚至可以制作实时游戏的脚本
- 使用opencv模板匹配进行图片识别和定位
- 按用户自定义策略进行自动战斗
- 针对快速进本机制和陈宫/大英雄队伍进行优化，对屏幕进行自动连点
- 自动判断技能是否cd、宝具卡是否可用、xjbd选卡优先级，提高低配队伍刷本稳定性
- 支持换人服使用
- 总结机械流程实现搓丸子的自动操作
- 可根据`touch_manager`模块自行编写其他通用脚本
# 安装
```
pip install opencv-python numpy pywin32
```
# 使用准备
## 战斗脚本
- 使用模拟器进行游戏，调整分辨率为1600x900，推荐使用MuMu/雷电模拟器
- 构筑所需队伍，并将队伍名截图保存至./images/ 或./images/friends/ 
![chengong](./images/friends/chengong.png)
- 将需要的关卡截图保存至 ./images/transport  
![hetao](./images/transport/hetao_free.png)
- 将需要的助战截图保存至 ./images/friends/ 
![caber](./images/friends/caber.png)
- 在战斗菜单中关闭“技能使用确认”和“宝具匀速”，打开“缩短敌人消失时间”
- 在选择指令卡界面调整游戏速度为2倍速
- 将可能出现的指令卡头像截图保存至 ./images/friends/  
![card_chengong](./images/friends/card_chengong.png) ![card_chengong](./images/friends/card_simayi.png) ![card_caber3](./images/friends/card_caber3.png) ![card_caber2](./images/friends/card_caber2.png) ![card_kongming](./images/friends/card_kongming.png)  
- 将游戏置于进入副本前状态
- 参照注释修改脚本
- 运行bot_example.py
## 搓丸子脚本
**请一定确保以下步骤在运行脚本前均已完成，否则后果自负**  
- 使用过友情池的免费一抽
- 礼装强化对象选择中筛选**仅显示1、2星礼装，按稀有度倒序**
- 礼装强化素材选择中筛选**仅显示1、2星礼装，按稀有度倒序**
- **将所有需要保留的从者均上锁或收入灵基保管室**
- **将所有需要保留的金银芙芙和高级经验值收入灵基保管室或上锁**
- 商店灵基变还中，筛选显示从者、芙芙、经验值，按稀有度升序
- 灵基保管室中筛选**仅显示1、2星礼装礼装，按等级倒序**
- 将游戏置于主界面（迦勒底亚斯
- 运行ball_exp_bot.py
# 战斗脚本的修改
## 编写/修改步骤
在任意目录下创建一个python源文件，从`./libs/mission_bot.py`中导入`automatic_bot`这个模块。

automatic_bot类提供了`@at_stage()`装饰器，只需要在你自己的python源文件中实例化一个`bot`，然后将函数注册到对应的战斗阶段，接着运行`bot.run()`，就可以实现自动战斗。

具体例子可以参考项目根目录下的`./bot_example.py`
- bot实例化中各图片参数修改
- 各面打法自定义修改
## 简要API参考

**`automatic_bot.use_skill(servant, skill, obj=None)`**  
使用（从左往右）第`servant`个从者的第`skill`个技能，施放对象为第`obj`个从者（如果是指向性） 

**`automatic_bot.use_master_skill(skill, obj=None, obj2=None)`**  
使用第`skill`个御主技能，作用对象为从者`obj`（如果是指向性）。  
如果`skill`等于4，则使用换人服技能，对象为`obj`号从者与`obj2`号从者     

**`automatic_bot.attack(cards)`**  
选取指令卡并攻击。 
`cards`需要为有三个整数作为元素的list，按照顺序表示出的卡。6~8表示从左往右的宝具卡, 对于1~5数字会自动按照xjbd优先级进行选卡  
例如[6, 1, 2]表示先使用从者1的宝具卡，再按xjbd优先级选择两张卡。
# 自定义脚本
## 编写/修改步骤
在任意目录下创建一个python源文件，从`./libs/toucher.py`中导入`touch_manager`这个模块。  
`touch_manager`提供点击指定位置、匹配图片并点击、检查是否存在图片、区域性识别和点击等接口  
总结机械步骤后进行编写即可

具体例子可以参考项目根目录下的`./ball_exp_bot.py` 
## API参考
参考`./libs/toucher.py`中各函数名及注释即可
