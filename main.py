import os
import re
import numpy as np
import yaml

def matching_func_err(ans_list, out_list):
    # 총 11개 point
    err = 0
    for idx, (i, j) in enumerate(zip(ans_list, out_list)):
        if idx == 4: # angle
            err += abs(round(i,1) - round(j,1))*10
        else:
            err += abs(i-j)

    return err

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


answer_dictionary = {}
output_dictionary = {}

with open(config['answer_path'], "r") as file:
    b = file.readlines()
    for line in b:
        str_line = line.strip("\n")
        list_line = re.split(",", str_line)
        frame_number = int(list_line[0])
        center_x = int(list_line[1])
        center_y = int(list_line[2])
        width = int(list_line[3])
        height = int(list_line[4])
        angle = float(list_line[5])
        nose_x = int(list_line[6])
        nose_y = int(list_line[7])
        neck_x = int(list_line[8])
        neck_y = int(list_line[9])
        tail_x = int(list_line[10])
        tail_y = int(list_line[11])
        track_number = int(list_line[12])

        if not answer_dictionary.get(frame_number):
            answer_dictionary[frame_number] = {}
        
        answer_dictionary[frame_number][track_number] = [center_x, center_y, width, height, angle, nose_x, nose_y, neck_x, neck_y, tail_x, tail_y]

with open(config['answer_path'], "r") as file:
    b = file.readlines()
    for line in b:
        str_line = line.strip("\n")
        list_line = re.split(",", str_line)
        frame_number = int(list_line[0])
        center_x = int(list_line[1])
        center_y = int(list_line[2])
        width = int(list_line[3])
        height = int(list_line[4])
        angle = float(list_line[5])
        nose_x = int(list_line[6])
        nose_y = int(list_line[7])
        neck_x = int(list_line[8])
        neck_y = int(list_line[9])
        tail_x = int(list_line[10])
        tail_y = int(list_line[11])
        track_number = int(list_line[12])

        if output_dictionary.get(frame_number):
            pass
        else:
            output_dictionary[frame_number] = {}
        
        output_dictionary[frame_number][track_number] = [center_x, center_y, width, height, angle, nose_x, nose_y, neck_x, neck_y, tail_x, tail_y]

frame_matching = {}
remain_object = {}

for frame, val in answer_dictionary.items():

    frame_output_sheet = output_dictionary[frame]
    for ans_trk_num, ans_det in val.items():
        # object detection 잔여 정답
        if not remain_object.get(ans_trk_num):
            remain_object[ans_trk_num] = 1
        else:
            remain_object[ans_trk_num] += 1

        # 정답 매칭 코드
        # if frame == 599 and ans_trk_num == 5:
        #     print("error")
        min_err = 9999
        best_trk = None
        for trk_num, det in frame_output_sheet.items():
            # if matching_func(ans_det, det):
            err = matching_func_err(ans_det, det)
            if err < min_err and err < 50:
                min_err = err
                best_trk = trk_num
        # 정답 매칭 key값 init
        if not frame_matching.get(ans_trk_num):
            frame_matching[ans_trk_num] = []
        if best_trk != None:
            frame_matching[ans_trk_num].append(best_trk)

    print("{} | {}".format(frame, len(answer_dictionary.keys())))


tracking_TP = 0
switching = 0

total_sum = 0
no_matching = 0
swtiching_mismatch = 0

for ans_trk, out_trk_list in frame_matching.items():
    # print("{} track frame : {} | {}".format(ans_trk, len(out_trk_list), remain_object[ans_trk]))

    total_sum += len(out_trk_list)
    no_matching += abs(len(out_trk_list) - remain_object[ans_trk])
    if out_trk_list[0] == np.mean(np.array(out_trk_list)):
        tracking_TP += 1
    else:
        switching += len(set(out_trk_list))
        swtiching_mismatch += len(out_trk_list) - out_trk_list.count(out_trk_list[0])
        # print("[CHANGE] {} : {}".format(ans_trk, set(out_trk_list)))

print("---------------------------------------------------")
print("Track Model : {}".format(re.split("[.]",config['answer_path'])[0]))
print("object num : {}".format(len(frame_matching.keys())))
print("total sum : {} | no_matching : {} | switching_mismatch : {}".format(total_sum, no_matching, swtiching_mismatch))
print("My MOTA Score : {}".format(1-(no_matching+swtiching_mismatch)/total_sum))
