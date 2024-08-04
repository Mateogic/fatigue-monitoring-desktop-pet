# 疲劳监测桌宠

## 介绍
​	针对需要线上办公学习乃至需要虚拟同伴的广大互联网用户群体，该项目将借助虚拟形象建模、动画特效渲染等技术打造用户独一无二的桌面宠物，并利用基于卷积神经网络的深度学习和计算机视觉算法打破虚拟与现实之间的屏障。该程序主要功能是在监测到用户处于疲劳困倦状态时指令桌宠提醒用户及时调整状态，专心投入到学习工作中。此外，它还可以在用户休闲时间根据识别到用户的不同动作进行实时互动，给予用户温馨陪伴。

## 封面
![Poster](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/Poster.png)

## 功能介绍

### 桌宠基础功能

#### 功能介绍及展示

1. **随机切换动画**

将想要随机切换的动画放置在normal文件夹下

![CartoonChange](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/CartoonChange.png)

2. **随机切换话语**

将想要随机切换的话语放置在dialog文本文件中

![DialogChange](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/DialogChange.png)

> 注意：末尾不要留有空行，否则可能会显示空白

3. **可拖拽至屏幕任意位置**

4. **鼠标点击动画和话语**

![ClickEffect](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/ClickEffect.png)

5. **可选择隐藏或显示**

![ShowOrHide](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/ShowOrHide.png)

6. **可自定义更换提醒音乐**

![MusicChange](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/MusicChange.png)

### 疲劳检测功能

#### 公式-计算眼睛纵横比

![FormulaDerivation](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/FormulaDerivation.png)

#### 原理及实现功能介绍

1. 根据眼睛纵横比数值大小判断当前眼睛睁闭状态，并对视频中用户连续闭眼帧数计数

2. 若当前帧眼睛为闭合状态，计数器+1，若当前帧眼睛为睁开状态，计数器清零
3. 若计数器值大于阈值(48),认为眼睛闭合时间过长，判定为疲劳状态。此时显示WARN，宠物切换到相应gif动画并播放提醒音乐

> 左上为睁眼状态，眼睛纵横比约为0.3，即大于等于0.3认为眼睛睁开
>
> 右上为闭眼状态，眼睛纵横比约为0，即小于0.3认为眼睛闭合

#### 实现效果

1. **常态（非疲劳状态）**

![NotTired](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/NotTired.png)

2. **疲劳状态**

![Tired](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/Tired.png)

### 久坐检测功能

#### 原理及实现功能介绍

主要在cvcode.py中完成该功能的编写，整体思路:

从摄像头第一次检测到人眼，则通过赋值begin_work=1开启计时状态

计时状态下，持续检测到人眼时长time_work_num自增

判断time_work_num若大于30，则开启久坐提醒状态，小黑显示对应动画

久坐提醒状态下，若摄像头超过5s没用检测到人眼，则认为用户已完成休息

再次检测到人眼之后计时清零再重新开始计时

#### 实现效果

1. 终端打印摄像头持续检测到人眼时间和是否久坐（0为非久坐，1为久坐）

![Terminal](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/Terminal.png)

2. 若判定用户久坐，小黑会作相应提醒

![SedentaryReminder](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/SedentaryReminder.png)

### 游戏功能-石头剪刀布

#### 原理及实现功能介绍

1. **小黑出拳结果**:通过random.choice()函数随机选出
2. **用户出拳结果**:通过计算机视觉分析得出(代码中有详细注释)
3. **游戏胜负判定**:根据剪刀石头布规则通过条件判断枚举列出

#### 实现效果

1. **小黑出拳**

![SelectHei](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/SelectHei.png)

2. **用户出拳**

![SelectUser](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/SelectUser.png)

3. **胜负判定**

结局弹窗

![ResultPopup](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/ResultPopup.png)

小黑显示效果

![ResultHei](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/ResultHei.png)

## 二次开发说明

### 形象更换

该程序可能显示的全部小黑gif形象分类存放在以下几个文件夹中

![ImageFolders](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/ImageFolders.png)

GIF动画的调用方式大致有两种

1. 首先将每个文件夹下的图片通append()函数添加到一个单独的数组中，再通过random.choice()函数随机选择数组中的图片并用QMovie()播放
2. 根据标志变量的判断切换到特定GIF动画

> 话语的显示与之类似，通过代码中的注释是容易理解的

### 功能修改与增加

1. 石头剪刀布功能:该功能开启目前只支持单次游戏后再次点击开始，其实也可以通过win32api.MessageBox()增加"再来一局"按钮
2. 无论是疲劳检测还是石头剪刀布，简化其过程都可以看作通过开发者实现功能产生的标志变量调用宠物切换到特定的动画和话语

> 开发者也可以采用类似的做法

![FunctionAdd](https://raw.githubusercontent.com/Mateogic/fatigue-monitoring-desktop-pet/main/ReadmeImage/FunctionAdd.png)

## [演示视频](https://www.bilibili.com/video/BV1uc41177Vf)
## [可执行文件及所需资源百度网盘](https://pan.baidu.com/s/1-L1iQJ95HZMLwrOQBhvWCQ?pwd=9999)
