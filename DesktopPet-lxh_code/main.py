import os
import sys
import random

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from tkinter.filedialog import askopenfilename
from tkinter import Tk
import win32api,win32con
from threading import *

import alarmcode# 警告模块
import cvcode# 疲劳检测模块
import gesture_recognition# 石头剪刀布游戏模块

#桌面宠物类的定义
class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        # 窗体初始化
        self.init()
        # 托盘化初始
        self.initPall()
        # 宠物静态gif图加载
        self.initPetImage()
        # 宠物正常待机，实现随机切换动作
        self.petNormalAction()

        #标志位属性定义及初始化
        self.game_begin = 0 # 宠物出拳已定表示游戏开始（检测到用户出拳后宠物才会随机出拳）1表示宠物出石头，2表示宠物出剪刀，3表示宠物出布
        self.flag1 = 0 # 0表示宠物出拳动画的第一张gif图（动图），1表示宠物出拳动画的第二章gif图（静态） 用于解决QMovie.start()只能循环播放的问题
        self.flag2 = 0 # 为了保持宠物出拳动画正常播放，逻辑应该是①先播放宠物出拳动图②展示宠物出拳结果（静态）③展示宠物胜负结果 为了避免出现result后直接跳到③，所以在①之后令self.flag1=1，再在②前通过判断self.falg1==1赋值self.flag2=1 最终在②之后通过判断self.flag2==1得出游戏胜负才进入③


    # 窗体初始化
    def init(self):
        # 初始化
        # 设置窗口属性:窗口无标题栏且固定在最前面
        # FrameWindowHint:无边框窗口
        # WindowStaysOnTopHint: 窗口总显示在最上面
        # SubWindow: 新窗口部件是一个子窗口，而无论窗口部件是否有父窗口部件
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        # setAutoFillBackground(True)表示的是自动填充背景,False为透明背景
        self.setAutoFillBackground(False)
        # 窗口透明，窗体空间不透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 重绘组件、刷新
        self.repaint()

    # 托盘化设置初始化
    def initPall(self):
        # 导入准备在托盘化显示上使用的图标
        icons = os.path.join('lxh.png')
        # 设置右键显示最小化的菜单项
        #菜单项切换音乐，点击后调用changemusic_func函数
        changemusic = QAction('切换音乐', self, triggered=self.changemusic_func)
        #菜单项开启提醒，点击后调用remind_func1函数
        remind_on = QAction('开启提醒', self, triggered=self.remind_func1)
        #菜单项关闭提醒，点击后调用remind_func2函数
        remind_off = QAction('关闭提醒', self, triggered=self.remind_func2)
        #菜单项开始游戏，点击后调用game_func1函数
        game_on = QAction('开启游戏', self, triggered=self.game_func1)
        #菜单项关闭提醒，点击后调用game_func2函数
        game_off = QAction('关闭游戏', self, triggered=self.game_func2)
        # 菜单项显示，点击后调用showing_func函数
        showing = QAction('显示', self, triggered=self.showing_func)
        # 菜单项隐藏，点击后调用hide_func函数
        hide = QAction('隐藏', self, triggered=self.hide_func)
        # 菜单项退出，点击后调用quit函数
        quit_action = QAction('退出', self, triggered=self.quit_func)

        # 新建一个菜单项控件
        self.tray_icon_menu = QMenu(self)
        # 在菜单栏添加一个无子菜单的菜单项‘切换音乐’
        self.tray_icon_menu.addAction(changemusic)
        # 在菜单栏添加一个无子菜单的菜单项‘开启提醒’
        self.tray_icon_menu.addAction(remind_on)
        # 在菜单栏添加一个无子菜单的菜单项‘关闭提醒’
        self.tray_icon_menu.addAction(remind_off)
        # 在菜单栏添加一个无子菜单的菜单项‘开启游戏’
        self.tray_icon_menu.addAction(game_on)
        # 在菜单栏添加一个无子菜单的菜单项‘关闭游戏’
        self.tray_icon_menu.addAction(game_off)
        # 在菜单栏添加一个无子菜单的菜单项‘显示’
        self.tray_icon_menu.addAction(showing)
        # 在菜单栏添加一个无子菜单的菜单项‘隐藏’
        self.tray_icon_menu.addAction(hide)
        # 在菜单栏添加一个无子菜单的菜单项‘退出’
        self.tray_icon_menu.addAction(quit_action)
        # QSystemTrayIcon类为应用程序在系统托盘中提供一个图标
        self.tray_icon = QSystemTrayIcon(self)
        # 设置托盘化图标
        self.tray_icon.setIcon(QIcon(icons))
        # 设置托盘化菜单项
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        # 展示
        self.tray_icon.show()

    # 宠物静态gif图加载
    def initPetImage(self):
        # 对话框定义
        self.talkLabel = QLabel(self)
        # 对话框样式设计
        self.talkLabel.setStyleSheet("font:15pt '楷体';border-width: 1px;color:blue;")
        # 定义显示图片部分
        self.image = QLabel(self)
        # QMovie是一个可以存放动态视频的类，一般是配合QLabel使用的,可以用来存放GIF动态图
        self.movie = QMovie("normal/normal1.gif")
        # 设置标签大小
        self.movie.setScaledSize(QSize(200, 200))
        # 将Qmovie在定义的image中显示
        self.image.setMovie(self.movie)
        self.movie.start()
        self.resize(1024, 1024)
        # 调用自定义的randomPosition，会使得宠物出现位置随机
        self.randomPosition()
        # 展示
        self.show()

        # 将宠物正常待机状态的动图放入pet1中
        self.pet1 = []
        for i in os.listdir("normal"):
            self.pet1.append("normal/" + i)

        #将石头状态的动图和静止图放入process1中
        self.process1 = []
        for i in os.listdir("process1"):
            self.process1.append("process1/" + i)

        #将剪刀状态的动图和静止图放入process2中
        self.process2 = []
        for i in os.listdir("process2"):
            self.process2.append("process2/" + i)

        #将布状态的动图和静止图放入process3中
        self.process3 = []
        for i in os.listdir("process3"):
            self.process3.append("process3/" + i)

        # 将宠物正常待机状态的对话放入dialog中
        self.dialog = []
        # 读取目录下dialog文件
        with open("dialog.txt", "r") as f:
            text = f.read()
            # 以\n 即换行符为分隔符，分割放进dialog中
            self.dialog = text.split("\n")

    # 宠物正常待机动作
    def petNormalAction(self):
        # 每隔一段时间做个动作
        # 定时器设置
        self.timer = QTimer()
        # 时间到了自动执行
        self.timer.timeout.connect(self.randomAct)
        # 动作时间切换设置
        self.timer.start(4000)
        # 宠物状态设置为正常
        self.condition = 0
        # 每隔一段时间切换对话
        self.talkTimer = QTimer()
        self.talkTimer.timeout.connect(self.talk)
        self.talkTimer.start(4000)
        # 对话状态设置为常态
        self.talk_condition = 0
        # 游戏是否进行中
        self.game_state = 0
        # 1用户胜利 2用户平局 3用户失败
        self.result = 0
        # 宠物对话框
        self.talk()

    # 随机动作切换
    def randomAct(self):
        # condition记录宠物状态，宠物状态为0时，代表正常待机
        if self.condition == 0 and alarmcode.play==0:
            # 随机选择装载在pet1里面的gif图进行展示，实现随机切换
            self.movie = QMovie(random.choice(self.pet1))
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        #当被判定为疲劳时，remind.gif与音乐同时播放
        # 这里可以通过else-if语句往下拓展做更多的交互功能
        if alarmcode.play==1:
            self.movie = QMovie("./remind/remind1.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            # 宠物状态设置为正常待机
            self.condition = 0
            self.talk_condition = 0
        # condition不为0，转为切换特有的动作，实现宠物的点击反馈
        if self.condition==1 and alarmcode.play==0:
            # 读取特殊状态图片路径
            self.movie = QMovie("./others/click.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            # 宠物状态设置为正常待机
            self.condition = 0
            self.talk_condition = 0
        if gesture_recognition.result == 'none' and self.game_begin != 0:#已经点击开启游戏但是用户没有出拳
            print(gesture_recognition.result)
            # 读取特殊状态图片路径
            self.movie = QMovie("./others/ready.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # #随机数j==1，表示宠物出石头
        if self.game_begin ==1 and gesture_recognition.result!='none' and self.result==0:
            self.movie = QMovie(self.process1[self.flag1])
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            if self.flag1 ==1:
                self.flag2=1
            # 开始播放动画
            self.movie.start()
            self.flag1 = 1
            if self.flag2 ==1  and self.result ==0:
                if gesture_recognition.result == 'stone':   #两次播放动画后才进入判断出结果  出结果后不再进入判断
                    print("本局平局")
                    self.result=2
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:石头"
                                           "小黑出拳:石头", "本局平局", win32con.MB_OK)
                if gesture_recognition.result == 'scissors':
                    print("本局失败")
                    self.result=3
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:剪刀"
                                           "小黑出拳:石头", "本局失败", win32con.MB_OK)
                if gesture_recognition.result == 'cloth':
                    print("本局胜利")
                    self.result=1
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:布"
                                           "小黑出拳:石头", "本局胜利", win32con.MB_OK)
        #随机数==2，表示宠物出剪刀
        if self.game_begin ==2 and gesture_recognition.result!='none'and self.result==0:
            self.movie = QMovie(self.process2[self.flag1])
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            if self.flag1 ==1:
                self.flag2=1
            # 开始播放动画
            self.movie.start()
            self.flag1 = 1
            if self.flag2 ==1:#只显示一次结果
                if gesture_recognition.result == 'stone':   #两次播放动画后才进入判断出结果  出结果后不再进入判断
                    print("本局胜利")
                    self.result=1
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:石头"
                                           "小黑出拳:剪刀", "本局胜利", win32con.MB_OK)
                if gesture_recognition.result == 'scissors':
                    print("本局平局")
                    self.result=2
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:剪刀"
                                           "小黑出拳:剪刀", "本局平局", win32con.MB_OK)
                if gesture_recognition.result == 'cloth':
                    print("本局失败")
                    self.result=3
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:布"
                                           "小黑出拳:剪刀", "本局失败", win32con.MB_OK)
        #随机数j==3，表示宠物出布
        if self.game_begin ==3 and gesture_recognition.result!='none'and self.result==0:
            self.movie = QMovie(self.process3[self.flag1])
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            if self.flag1 ==1:
                self.flag2=1
            # 开始播放动画
            self.movie.start()
            self.flag1 = 1
            if self.flag2 ==1  and self.result ==0:
                if gesture_recognition.result == 'stone': #两次播放动画后才进入判断出结果  出结果后不再进入判断
                    print("本局失败")
                    self.result=3
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:石头"
                                           "小黑出拳:布", "本局失败", win32con.MB_OK)
                if gesture_recognition.result == 'scissors':
                    print("本局胜利")
                    self.result=1
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:剪刀"
                                           "小黑出拳:布", "本局胜利", win32con.MB_OK)
                if gesture_recognition.result == 'cloth':
                    print("本局平局")
                    self.result=2
                    self.flag2 = 0
                    win32api.MessageBox(0, "您出拳:布"
                                           "小黑出拳:布", "本局平局", win32con.MB_OK)
        # 用户胜利
        if self.result == 1:
            # 读取特殊状态图片路径
            self.movie = QMovie("./result/result1.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # 平局
        if self.result == 2:
            # 读取特殊状态图片路径
            self.movie = QMovie("./result/result2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # 用户失败
        if self.result == 3:
            # 读取特殊状态图片路径
            self.movie = QMovie("./result/result3.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()

        if cvcode.goToRelax == 1 and alarmcode.play==0:
            # 读取特殊状态图片路径
            self.movie = QMovie("./remind/remind2.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()

    # 宠物对话框行为处理
    def talk(self):
        if self.talk_condition == 0 and alarmcode.play==0 and self.game_state == 0:
            # talk_condition为0则选取加载在dialog中的语句
            self.talkLabel.setText(random.choice(self.dialog))
            # 设置样式
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            # 根据内容自适应大小
            self.talkLabel.adjustSize()
        if alarmcode.play == 1 and self.game_state == 0:
            # 当被判定为疲劳时，显示为别睡啦，这里同样可以通过if-else-if来拓展对应的行为
            self.talkLabel.setText("别睡啦")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0
        if self.talk_condition==1 and alarmcode.play==0 and self.game_state == 0:
            # talk_condition为1显示为别戳我
            self.talkLabel.setText("别戳我")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if (gesture_recognition.result == 'none'  and self.game_state==1 and self.result == 0):
            # 开启游戏但未检测到用户出拳，并且结果未出 提示放马过来
            self.talkLabel.setText("          放马过来吧!")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if (gesture_recognition.result != 'none'  and self.game_state==1 and self.result == 0):
            # 检测到用户出拳，并且结果未出 宠物出拳动画加载中 显示 石头剪刀布~~
            self.talkLabel.setText("石头剪刀布~~")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if (self.result == 1):
            # 检测到用户出拳，并且结果未出 宠物出拳动画加载中 显示 石头剪刀布~~
            self.talkLabel.setText("55555")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if (self.result == 2):
            # 检测到用户出拳，并且结果未出 宠物出拳动画加载中 显示 石头剪刀布~~
            self.talkLabel.setText("平局诶嘿嘿")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if (self.result == 3):
            # 检测到用户出拳，并且结果未出 宠物出拳动画加载中 显示 石头剪刀布~~
            self.talkLabel.setText("我赢啦呜呼！")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

        if cvcode.goToRelax == 1 and alarmcode.play==0:
            self.talkLabel.setText("快起来活动活动!")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

    # 宠物随机位置
    def randomPosition(self):
        # screenGeometry（）函数提供有关可用屏幕几何的信息
        screen_geo = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        pet_geo = self.geometry()
        width = (screen_geo.width() - pet_geo.width()) * random.random()
        height = (screen_geo.height() - pet_geo.height()) * random.random()
        self.move(width, height)

    # 鼠标左键按下时, 宠物将和鼠标位置绑定
    def mousePressEvent(self, event):
        # 更改宠物状态为点击
        self.condition = 1
        # 更改宠物对话状态
        self.talk_condition = 1
        # 即可调用对话状态改变
        self.talk()
        # 即刻加载宠物点击动画
        self.randomAct()
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
        # globalPos() 事件触发点相对于桌面的位置
        # pos() 程序相对于桌面左上角的位置，实际是窗口的左上角坐标
        self.mouse_drag_pos = event.globalPos() - self.pos()
        event.accept()
        # 拖动时鼠标图形的设置
        self.setCursor(QCursor(Qt.OpenHandCursor))

    # 鼠标移动时调用，实现宠物随鼠标移动
    def mouseMoveEvent(self, event):
        # 如果鼠标左键按下，且处于绑定状态
        if Qt.LeftButton and self.is_follow_mouse:
            # 宠物随鼠标进行移动
            self.move(event.globalPos() - self.mouse_drag_pos)
        event.accept()

    # 鼠标释放调用，取消绑定
    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        # 鼠标图形设置为箭头
        self.setCursor(QCursor(Qt.ArrowCursor))

    # 鼠标移进时调用
    def enterEvent(self, event):
        # 设置鼠标形状 Qt.ClosedHandCursor   非指向手
        self.setCursor(Qt.ClosedHandCursor)

    # 切换音乐
    def changemusic_func(self):
        print("切换音乐")
        Tk().withdraw()
        filename = askopenfilename()
        if filename.endswith(".mp3"):
            with open('./information.txt', 'w', encoding='utf-8') as f:
                f.write(filename)
        else:
            if filename != '':
                win32api.MessageBox(0, "选中的文件不是.mp3文件，请重新选择", "提示", win32con.MB_OK)

    # 开启提醒
    def remind_func1(self):
        print("开启提醒")
        cvcode.close1 = 0
        alarmcode.close_alarm = 0
        if cvcode.close2:
            Thread(target=cvcode.opencv1_func).start()

        Thread(target=alarmcode.play_music).start()

    # 关闭提醒
    def remind_func2(self):
        print("关闭提醒")
        cvcode.goToRelax = 0
        cvcode.time_work_sum = 0
        cvcode.begin_work = 0
        cvcode.close1 = 1
        alarmcode.close_alarm = 1


    # 开启游戏
    def game_func1(self):
        global j
        self.flag1 = 0#flag1逻辑:用于解决qmovie只能循环播放的问题，先令flag1==0时播放动图，之后令flag1==1播放动图的最后一帧gif图片
        self.result = 0
        self.game_state = 1
        print("开启游戏")
        #game.opencv2_func()
        cvcode.close2 = 0
        if cvcode.close1:
            Thread(target=cvcode.opencv1_func).start()
        # Thread(target=gesture_recognition.opencv2_func).start()#与上者区别
        numbers = [1,2,3]
        j=random.choice(numbers)
        self.game_begin = j#根据j的数值决定宠物随机出拳的结果

    # 关闭游戏
    def game_func2(self):
        print("关闭游戏")
        # gesture_recognition.close2 = 1#关闭窗口
        cvcode.close2 = 1
        self.game_begin = 0#清空宠物出拳状态
        self.flag1 = 0
        self.flag2 = 0
        self.j = 0
        self.result = 0
        self.game_state = 0

    # 显示宠物
    def showing_func(self):
        # setWindowOpacity（）设置窗体的透明度，通过调整窗体透明度实现宠物的展示和隐藏
        self.setWindowOpacity(1)

    # 隐藏宠物
    def hide_func(self):
        # setWindowOpacity()设置窗体的透明度，通过调整窗体透明度实现宠物的展示和隐藏
        self.setWindowOpacity(0)

    # 退出操作，关闭程序
    def quit_func(self):
        cvcode.close1 = 1
        gesture_recognition.close2 = 1
        alarmcode.close_alarm = 1
        self.close()
        sys.exit()

#主程序
if __name__ == '__main__':
    # 创建了一个QApplication对象，对象名为app，带两个参数argc,argv
    # 所有的PyQt5应用必须创建一个应用（Application）对象。sys.argv参数是一个来自命令行的参数列表。
    app = QApplication(sys.argv)
    # 窗口组件初始化
    pet = DesktopPet()
    # 1. 进入时间循环；
    # 2. wait，直到响应app可能的输入；
    # 3. QT接收和处理用户及系统交代的事件（消息），并传递到各个窗口；
    # 4. 程序遇到exit()退出时，机会返回exec()的值。
    sys.exit(app.exec_())
