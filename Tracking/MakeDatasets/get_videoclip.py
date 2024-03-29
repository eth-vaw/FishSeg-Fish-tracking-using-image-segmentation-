"""
FishSeg
Make Datasets

Copyright (c) 2023 ETH Zurich
BAUG, Laboratory of Hydraulics, Hydrology and Glaciology (VAW), Prof. Robert Boes
License under the 3-clause BSD License (see LICENSE for details)
"""

# "MakeDatasets" consists of 4 main scripts:
# （1） StartTime.py: Correct the manually recorded start time (from 25 fps to 20 fps),
# specially setup for VAW fisheye camera system;
# （2）get_videoclip.py: get video clips where fish actually show up and do MOG2
# background subtraction in the meantime;
# （3）concatenate_clips.py: concatenate all the video clips together;
# （4）datasets.py: check annotation datasets and reorganize datasets;  

#%% Read before you start
# This script is written for getting video clips where fish are present in the shooting range of the camera
    #  to avoid unnecessary time spent in finding the fish when doing annotations.
# Two sets of outputs are obtained as the outputs, which are folders of "Temp clips_eel" and "BGS clips_eel".
    # "Temp clips_eel" saves video clips in the un-preprocessed way.
    # "BGS clips_eel" saves video clips after background subtraction. 
# In the "DatasetClips_eel_1.txt", the start and end time for each experiment set are 
    # arranged in the sequence of "name - start time of cam0 - end time of cam0 - start time of cam1 - ... end time of cam4"
    # Example: 205_2020_24_09_16_19 00:08 00:38 00:13 00:30 03:00 03:20 03:30 03:50 05:30 05:45
    
# Three main sections are included in the script.
# (1) Functions needed for the script ("get_videoclips")
# (2) batch process for multiple video clips
# (3) get a video clip from single video
# Always run section(1) first, and then select to run section(2) or (3) depending on your needs.
# Check the file and folder path before you run section (2) or (3) according to the annotations.

#%%

import os
import cv2
import numpy as np
from moviepy.editor import *

def get_videoclips(videoinpath, videotemppath, videooutpath, start_time, end_time):
    base_name = os.path.splitext(os.path.basename(videoinpath))[0]
    folder_name = videoinpath[3:23]+'_temp'
    videotemppath = os.path.join(videotemppath, folder_name)
    if not os.path.exists(videotemppath):
        os.mkdir(videotemppath)
    videotemppath = os.path.join(videotemppath,base_name.replace('final','temp')+'.avi')
    
    def min_sec(timecode):
        t = timecode.split(':')
        min = int(t[0])
        sec = int(t[1])
        return min,sec
    
    start_min, start_sec = min_sec(start_time)
    end_min, end_sec = min_sec(end_time)
    
    video_clip = VideoFileClip(videoinpath).subclip((start_min,start_sec),(end_min,end_sec))
    video_clip.write_videofile(videotemppath,codec="libx264")
    
    cap = cv2.VideoCapture(videotemppath)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(width),int(height))    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    folder_name = videoinpath[3:23]+'_bgs'
    videooutpath = os.path.join(videooutpath, folder_name)
    if not os.path.exists(videooutpath):
        os.mkdir(videooutpath)
    videooutpath = os.path.join(videooutpath,base_name.replace('final','cut_2')+'.avi')
    vidout = cv2.VideoWriter(videooutpath,fourcc,fps,size,0)
    
    fgbg = cv2.createBackgroundSubtractorMOG2()
    while cap.isOpened():
        ret,frame = cap.read()
        if not ret:
            print('Finishing BGS of video' + videooutpath)
            cap.release()
            vidout.release()
            continue
        fgmask = fgbg.apply(frame)
        vidout.write(fgmask)
        
    return True

#%% batch process for multiple video clips

videoinpath = 'Y:\\' # video path for experimental videos
videotemppath = 'D:\FishSeg_Results\VideoClips\\Temp clips_eel' # folder for un-processed video clips
videooutpath = 'D:\FishSeg_Results\VideoClips\\BGS clips_eel' # folder for video clips after backgroundSubtractorMOG2
timePeriods = 'D:\FishSeg_Results\VideoClips\\DatasetClips_eel_1.txt' # text doc with folder names, as well as start and end time of intended video clips
    # Note that 'DatasetClips_eel_1.txt' is based on 'DatasetClips_eel.xlsx'
    # Such video clips can be obtained simultaneously with specified folder names


f = open(timePeriods)
lines = f.readlines()
runIDs = []
starts_0 = []
ends_0 = []
starts_1 = []
ends_1 = []
starts_2 = []
ends_2 = []
starts_3 = []
ends_3 = []
starts_4 = []
ends_4 = []
folders_cam0 = []
folders_cam1 = []
folders_cam2 = []
folders_cam3 = []
folders_cam4 = []
for i in range(len(lines)):
    runIDs.append(lines[i][0:20])
    starts_0.append(lines[i][21:26])
    ends_0.append(lines[i][27:32])
    starts_1.append(lines[i][33:38])
    ends_1.append(lines[i][39:44])
    starts_2.append(lines[i][45:50])
    ends_2.append(lines[i][51:56])
    starts_3.append(lines[i][57:62])
    ends_3.append(lines[i][63:68])
    starts_4.append(lines[i][69:74])
    ends_4.append(lines[i][75:80])
    folders_cam0.append(os.path.join(videoinpath,runIDs[i],'Cam_0_final.avi'))
    folders_cam1.append(os.path.join(videoinpath,runIDs[i],'Cam_1_final.avi'))
    folders_cam2.append(os.path.join(videoinpath,runIDs[i],'Cam_2_final.avi'))
    folders_cam3.append(os.path.join(videoinpath,runIDs[i],'Cam_3_final.avi'))
    folders_cam4.append(os.path.join(videoinpath,runIDs[i],'Cam_4_final.avi'))

for i in range(len(folders_cam0)):
    get_videoclips(folders_cam0[i], videotemppath, videooutpath, starts_0[i], ends_0[i])
    get_videoclips(folders_cam1[i], videotemppath, videooutpath, starts_1[i], ends_1[i])
    get_videoclips(folders_cam2[i], videotemppath, videooutpath, starts_2[i], ends_2[i])
    get_videoclips(folders_cam3[i], videotemppath, videooutpath, starts_3[i], ends_3[i])
    get_videoclips(folders_cam4[i], videotemppath, videooutpath, starts_4[i], ends_4[i])

#%% get a video clip from single video

videoinpath = 'Y:\\244_2020_05_10_10_07\\Cam_4_final.avi' # video path
videotemppath = 'D:\FishSeg_Results\VideoClips\\Temp clips_eel' # folder for un-processed video clips
videooutpath = 'D:\FishSeg_Results\VideoClips\\BGS clips_eel'# folder for video clips after backgroundSubtractorMOG2
start_time = '02:05' # Start time for specific video clip
end_time = '02:11' # End time for specific video clip

get_videoclips(videoinpath, videotemppath, videooutpath, start_time, end_time)

