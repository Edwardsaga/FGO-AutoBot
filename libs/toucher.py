"""
The screen touch module.
:author: @Edwardsaga
"""
import win32gui, win32ui, win32con,win32api
import cv2 as cv
import numpy as np
import time
from pathlib import Path
import logging
logger = logging.getLogger('touch_manager')

class touch_manager(object):
    """
    A class of the touch manager.
    """
    def __init__(self,
                 window_name: str = "雷电模拟器",
                 root_path: str = "D:/games/FGO/FGO_bot/images/",
                 transport_path: str = "D:/games/FGO/FGO_bot/images/transport/",
                 friends_path: str = "D:/games/FGO/FGO_bot/images/friends/",
                 skills_path: str = "D:/games/FGO/FGO_bot/images/skills/",
                 use_main = False
                 ):
        """
        Initial

        Args:
            window_name: The simulator window name.
            root_path: The path of main images.
            transport_path: The path of mission images.
            friends_path: The path of friends images.
            skills_path: The path of skill images.
        """
        # 窗口名
        # 获取后台窗口的句柄，注意后台窗口不能最小化

        hWnd = win32gui.FindWindow(0, window_name)  # 窗口的类名可以用Visual Studio的SPY++工具获取
        child=[]
        if not use_main:
            # 获取渲染窗口句柄
            def winfun(hwnd, param):
                """Get the render window‘s handler

                Args:
                    hwnd: The parent window handler.
                """
                s = win32gui.GetWindowText(hwnd)
                if len(s) > 3:
                    child.append(hwnd)
                    print("winfun, child_hwnd: %d   txt: %s" % (hwnd, s))
                return 1
            win32gui.EnumChildWindows(hWnd, winfun, None)
            hWnd=child[0]

        # 获取句柄窗口的大小信息
        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        left, top, right, bot = win32gui.GetWindowRect(hWnd)
        self.hWndDC = win32gui.GetWindowDC(hWnd)
        # 创建设备描述表
        self.mfcDC = win32ui.CreateDCFromHandle(self.hWndDC)
        # 创建内存设备描述表
        self.saveDC = self.mfcDC.CreateCompatibleDC()

        #Windows handler
        self.hWnd=hWnd
        self.width = right - left
        self.height = bot - top
        #Pathes
        self.root_path = root_path
        self.transport_path = transport_path
        self.friends_path = friends_path
        self.skills_path = skills_path
        #Screen related
        self.images = {}
        self.tap_positions = {}
        self.ranges = {}
        self.sizes = {}

        logger.debug('Touch manager initialized.')

    def __del__(self):
        """
        Clear the tables
        """
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hWnd, self.hWndDC)

    def loadImage(self,image_path,key):
        """
        Load an image and its key

        Args:
            image_path: The load path.
            key: The image key.
        """
        print(image_path)
        self.images[key] = cv.imread(str(image_path))

    def load_images(self,im_dir):
        """
        Load template images from directory.

        Args:
            im_dir: The load directory.
        """
        for im in im_dir.glob('*.png'):
            self.loadImage(im,im.name[:-4])


    def doClick(self,cx, cy, pause_time=0.5, Not_release=False):  # 点击坐标
        """
        Do click at cx,cy

        Args:
            cx: The start point.
            cy: The end point.
            pause_time: The sleeping time after touched the point.
        """
        # print('点击',cx,cy,'坐标')
        long_position = win32api.MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
        win32api.SendMessage(self.hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)  # 模拟鼠标按下
        time.sleep(pause_time)
        if not Not_release:
            win32api.SendMessage(self.hWnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)  # 模拟鼠标弹起
            time.sleep(pause_time)

    def moveMouse_release(self,cx, cy, release_time=5):  # 点击坐标
        """
        Move mouse to cx,cy

        Args:
            cx: The start point.
            cy: The end point.
            pause_time: The sleeping time after touched the point.
        """
        long_position = win32api.MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
        win32gui.SendMessage(self.hWnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, long_position)  # 移动到终点
        time.sleep(release_time)
        win32gui.SendMessage(self.hWnd, win32con.WM_LBUTTONUP, long_position)


    def doSlide(self,point_start, point_end, step=5, push_time=0.1):
        """
        Do slide from point_start to point_end

        Args:
            point_start: The start point.
            point_end: The end point.
            step: The whole slide sometimes need to be devided into smaller steps.
        """
        point_start = np.array(point_start)
        point_end = np.array(point_end)
        # print('滑动',point_start[0],"到",point_end[0],'x坐标')
        point1 = win32api.MAKELONG(point_start[0], point_start[1])  # 模拟鼠标指针 传送到指定坐标

        win32gui.SendMessage(self.hWnd, win32con.WM_LBUTTONUP, point1)
        win32gui.SendMessage(self.hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point1)  # 起始点按住
        time.sleep(push_time)
        for i in range(step):
            point2 = np.array(point_start + (point_end - point_start) * (i) / step, dtype=int)
            point2_win32 = win32api.MAKELONG(point2[0], point2[1])  # 模拟鼠标指针 传送到指定坐标
            win32gui.SendMessage(self.hWnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point2_win32)  # 移动到终点
            time.sleep(0.1)
        win32gui.SendMessage(self.hWnd, win32con.WM_LBUTTONUP, point2_win32)  # 松开    time.sleep(1)

    def get_screen(self):
        """
        Catch current screen image
        """
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.width, self.height)
        # 将截图保存到saveBitMap中
        self.saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        self.saveDC.BitBlt((0, 0), (self.width, self.height), self.mfcDC, (0, 0), win32con.SRCCOPY)
        ##opencv+numpy保存
        ###获取位图信息
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        ###PrintWindow成功，保存到文件，显示到屏幕
        im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
        im_opencv.shape = (self.height, self.width, 4)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        return im_opencv[:self.height, :self.width, :3]

    def save_screen(self, path):
        img = self.get_screen()
        cv.imwrite(path, img)

    def get_screen_part(self,width,height,pos_x,pos_y):
        """
        Catch part of current screen image
        Args:
            width: The range width.
            height: The range height.
            pos_x: The range start x.
            pos_y: The range start y.
        """
        # 创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        saveBitMap.CreateCompatibleBitmap(self.mfcDC, width, height)
        # 将截图保存到saveBitMap中
        self.saveDC.SelectObject(saveBitMap)
        # 保存bitmap到内存设备描述表
        self.saveDC.BitBlt((0, 0), (width, height), self.mfcDC, (pos_x, pos_y), win32con.SRCCOPY)
        ##opencv+numpy保存
        ###获取位图信息
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        ###PrintWindow成功，保存到文件，显示到屏幕
        im_opencv = np.frombuffer(signedIntsArray, dtype='uint8')
        im_opencv.shape = (height, width, 4)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        return im_opencv[:height, :width, :3]

    # 检查模板是否存在
    def if_exist(self,name,threshold=0.96):
        """
        Check if an template is exist at the image

        Args:
            img: The check image(current screen).
            threshold: The match threshold.
            name: The template name.
        Returns:
            If the template is in the image.
        """
        img = self.get_screen()
        res = cv.matchTemplate(img, self.images[name], cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > threshold:
            return True
        else:
            return False
    def if_exist_part(self,img, threshold, name):
        """
        Check if an template is exist at the part image

        Args:
            img: The check image(current screen).
            threshold: The match threshold.
            name: The template name.
        Returns:
            If the template is in the image.
        """
        range_a = self.ranges[name]
        size = self.sizes[name]
        detect_range = img[range_a[1]:range_a[1] + size[1], range_a[0]:range_a[0] + size[0]]
        res = cv.matchTemplate(detect_range, self.images[name], cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > threshold:
            return True,max_val
        else:
            return False,max_val
    def exist_prob(self,img, name):
        """
        Get the match probability of target image

        Args:
            img: The check image(current screen).
            name: The template name.
        Returns:
            If the template is in the image.
        """
        res = cv.matchTemplate(img, self.images[name], cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        return max_val
    def find_and_tap(self,input, threshold=0.9, pause_time=0.2, Not_release=False):
        """
        Find the template and tap the position

        Args:
            input: The template image name.
            threshold: The match threshold.
            pause_time: The waiting time after the touch.
        Returns:
            If the template is in the image.
        """
        img = self.get_screen()
        input=self.images[input]
        template_x = input.shape[1]
        template_y = input.shape[0]
        res = cv.matchTemplate(img, input, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > threshold:
            cx = max_loc[0] + template_x / 2
            cy = max_loc[1] + template_y / 2
            # print(cx, cy)
            self.doClick(int(cx), int(cy), 0.01, Not_release)
            time.sleep(pause_time)
            return True
        else:
            logger.debug(f"未找到点击目标")
            return False

    def find_and_tap_part(self,input,x,y, threshold=0.9, pause_time=0.2):
        """
        Find the template and tap the position in part img

        Args:
            input: The template image name.
            threshold: The match threshold.
            pause_time: The waiting time after the touch.
            x: x range
            y: y range
        Returns:
            If the template is in the image.
        """
        img = self.get_screen_part(x[1]-x[0],y[1]-y[0],x[0],y[0])
        cv.imwrite("test_part.png",img)
        input=self.images[input]

        template_x = input.shape[1]
        template_y = input.shape[0]
        res = cv.matchTemplate(img, input, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        if max_val > threshold:
            cx = max_loc[0] +x[0]+ template_x / 2
            cy = max_loc[1] +y[0]+ template_y / 2
            # print(cx, cy)
            self.doClick(int(cx), int(cy), 0.01)
            time.sleep(pause_time)
            return True
        else:
            logger.debug(f"未找到点击目标")
            return False




