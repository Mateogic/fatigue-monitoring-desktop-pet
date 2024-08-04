# 疲劳驾驶6.0
# -*- coding: utf-8 -*-
import numpy as np
from scipy.spatial import distance as dist  # 计算欧氏距离
import dlib
import cv2

import alarmcode
import gesture_recognition

import time

# ==============获取图像内的左眼、右眼对应的关键点集==============


def getEYE(image, rect):
    landmarks = predictor(image, rect)
    # 关键点处理为(x,y)形式
    shape = np.matrix([[p.x, p.y] for p in landmarks.parts()])
    # 计算左眼、右眼
    leftEye = shape[42:48]  # 左眼，关键点索引从42到47（不包含48）
    rightEye = shape[36:42]  # 右眼，关键点索引从36到41（不包含42）
    return leftEye, rightEye

# ============计算眼睛的纵横比（小于0.3太小是闭眼或眨眼、超过0.3是睁眼）==========


def eye_aspect_ratio(eye):
    # 眼睛用6个点表示。上下各两个，左右一个，结构如下所示：
    # ---------------------------------------------
    #      1    2
    # 0             3      <----这是眼睛的6个关键点
    #      5    4
    # ---------------------------------------------
    # 欧氏距离（垂直方向上的两个距离1和5、 2和4）
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # 欧氏距离（水平距离0和3）
    C = dist.euclidean(eye[0], eye[3])
    # 纵横比
    ear = (A + B) / (2.0 * C)
    return ear

# ================计算两眼的纵横比均值========================


def earMean(leftEye, rightEye):
    # 计算左眼纵横比leftEAR、右眼纵横比rightEAR
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    # 均值处理
    ear = (leftEAR + rightEAR) / 2.0
    return ear

# ==============绘制眼框（眼眶的包围框）=======================


def drawEye(eye):
    # 把眼睛圈起来1：convexHull，获取凸包
    eyeHull = cv2.convexHull(eye)
    # 把眼睛圈起来2：drawContours,绘制凸包对应的轮廓
    cv2.drawContours(frame, [eyeHull], -1, (0, 255, 0), 1)

    # 计数器
COUNTER = 0
# 眼睛纵横比的阈值0.3，默认高宽比大于0.3，再小就是闭眼（眨眼）
RationTresh = 0.25
# 定义闭眼帧数的阈值设定为50，超过该阈值，判定为闭眼而不是眨眼
ClosedThresh = 50
# ============模型初始化====================
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


close1 = 1
musicposition = 0.0
RelaxTimeSecondsThresh = 5  # 变量阈值 超过5s没有检测到人脸表示用户已经去休息
WorkTimeSecondsThresh = 10  # 提示休息间隔 为了方便测试这里设置为10s 表示每10s提醒用户（goToRelax赋值为1）去休一次（5s）
goToRelax = 0  # 用户在镜头前10s后赋值为1
ret = False
frame = []
# 主调函数
close2 = 1

def opencv1_func():
    # ==================使用到的变量==========================
    global musicposition, close1,close2

    global goToRelax,time_work_sum
    global detector, cap, predictor, frame, boxes
    global COUNTER, RationTresh, ClosedThresh
    global frame,ret
    # =========初始化摄像头============
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    begin_relax = 0
    time_realx_start = 0.0
    begin_work = 0
    time_sample = time.time()  # work
    time_work_sum = 0.0
    # cap = cv2.VideoCapture(0)
    # ===========读取摄像头视频，逐帧处理=============
    while True:
        # 读取摄像头内的帧
        ret, frame = cap.read()
        frame = cv2.flip(frame,1)   #沿着y轴转换下方向

        if close1 == 0:
            # 获取人脸
            boxes = detector(frame, 0)

            # 休息是单次总计时，工作是间断的合计时
            if len(boxes) == 0 and begin_relax == 0:  # 人消失开始计时
                time_realx_start = time.time()
                begin_relax = 1
            if begin_relax:
                if len(boxes) == 0:  # 计时判断
                    if time.time()-time_realx_start >= RelaxTimeSecondsThresh:  # 如果人消失时间足够长（这里设置为5s），认为在休息，就把工作重置
                        begin_work_count = 0
                        time_work_sum = 0.0
                        begin_work = 0  # 重新计时
                        time_work_sum = 0

            time_sample_division = time.time()-time_sample
            time_sample = time.time()

            # print(time_sample_division)

            # 循环遍历每一个boxes内对象
            for b in boxes:
                # print("aaa")
                leftEye, rightEye = getEYE(frame, b)  # 获取左眼、右眼
                ear = earMean(leftEye, rightEye)  # 计算左眼、右眼的纵横比均值

                if begin_work == 0:  # 第一眼看到人开始计时
                    begin_work = 1
                    goToRelax = 0  # 重新回来工作
                if begin_work == 1:  # 计时中的判断
                    time_work_sum += time_sample_division
                    if time_work_sum > WorkTimeSecondsThresh:  # 工作时长超过阈值
                        goToRelax = 1  # 去休息
                print(time_work_sum, goToRelax)  # 用户在镜头前的时间和是否提示用户去休息

                # 判断眼睛的高宽比（纵横比，ear),小于0.3（EYE_AR_THRESH），认为闭眼了
                # 闭眼可能是正常眨眼，也可能是疲劳了，继续计算闭眼的时长
                if ear < RationTresh:
                    COUNTER += 1  # 没检测到一次，将【计数器】加1
                    # 【计数器】足够大，说明闭眼时间足够长 ，认为疲劳了
                    if COUNTER >= ClosedThresh:
                        goToRelax = 0  # 判定为疲劳后重新计时   既然大于10 又疲劳
                        alarmcode.play = 1
                        # 显示警告warn
                        cv2.putText(frame, "!!!!WARN!!!!", (50, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                # 否则（对应宽高比大于0.3），计数器清零、解除疲劳标志
                else:
                    alarmcode.play = 0
                    COUNTER = 0  # 【计数器】清零
                # 绘制眼框（眼睛的包围框）
                drawEye(leftEye)
                drawEye(rightEye)
                # 显示EAR值（eye_aspect_ratio)
                cv2.putText(frame, "EAR: {:.2f}".format(ear), (250, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        ret, frame = gesture_recognition.opencv2_func(ret,frame,close2)


        # 显示处理结果
        cv2.imshow("Frame", frame)
        # 按下Esc键，退出。ESC键的ASCII码为27
        if cv2.waitKey(1) == 27 or (close1 and close2) :
            break
    cv2.destroyAllWindows()
    cap.release()
