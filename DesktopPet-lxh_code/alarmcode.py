import time
import pygame
import win32api,win32con
import eyed3

close_alarm = 1
musicposition = 0.0
play = 0

def play_music():
    print("播放音乐")
    global musicposition,close_alarm,play
    play = 0
    while close_alarm == 0:
        if play:
            with open('./information.txt', 'r', encoding='utf-8') as f:
                data_pre = f.read()
            beg = data_pre.find('\n', 0) + 1
            end = data_pre.find('.mp3', beg) + 4
            path = data_pre[beg:end]

            if path != "" and path.endswith(".mp3"):
                musicperiod = eyed3.load(path).info.time_secs
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1,start=musicposition)

                time1 = time.time()
                win32api.MessageBox(0, "清醒了", "提示", win32con.MB_OK)
                time2 = time.time()

                print(time2-time1)

                musicposition1 = musicposition + time2-time1
                if musicposition >= musicperiod:
                    musicposition1 = musicposition1 - musicperiod

                pygame.mixer.music.stop()
                musicposition = musicposition1
            else:
                win32api.MessageBox(0, "请先选择闹铃", "提示", win32con.MB_OK)
    pygame.mixer.music.stop()

