import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def filter_trace(input_path, output_path):
    "过滤出带static_multistream关键字的行"
    with open(input_path, 'r') as infile:
        with open(output_path, 'w') as outfile:
            for line in infile:
                if "static_multistream" in line:
                    outfile.write(line)


def parse_process(input_path):
    "解析日志文件并创建一个字典，字典的键是frame_id，每个键包含ProcessA和ProcessB的start和end时间。"
    frames = {}
    frames_new = {}
    with open(input_path, 'r') as file:
        for line in file:
            # 分割行以提取各部分信息
            parts = line.strip().split('|')
            frame_id_part = parts[1].split(':')
            process_event_part = parts[4].split(':')
            frame_id = frame_id_part[1]
            process = process_event_part[0][-1]  # 提取A或B
            event = process_event_part[1]  # 提取start或end
            timestamp = int(process_event_part[2])
            if frame_id not in frames:
                frames[frame_id] = {'A_start': '', 'A_end': '', 'B_start': '', 'B_end': ''}
            frames[frame_id][f'{process}_{event}'] = timestamp
    for key, value in frames.items():
        if value['A_start'] and value['A_end'] and value['B_start'] and value['B_end']:
            frames_new[key] = value
            frames_new[key]['A_time'] = value['A_end'] - value['A_start']
            frames_new[key]['B_time'] = value['B_end'] - value['B_start']
            frames_new[key]['valid_time'] = value['B_end'] - value['A_start']
        elif value['A_start'] and value['A_end']:
            frames[key]['A_time'] = value['A_end'] - value['A_start']
            frames[key]['B_time'] = ''
        else:
            frames[key]['A_time'] = ''
            frames[key]['B_time'] = value['B_end'] - value['B_start']
    return frames, frames_new

def calculate_process_times(data):
    "计算各工序的耗时"
    processA_time = []
    processB_time = []
    for id, value in data.items():
        if value['A_time']:
            time_a = int(value['A_time'])
            processA_time.append(time_a)
        if value['B_time']:
            time_b = value['B_time']
            processB_time.append(time_b)
    question1 = {
        'processA': {
            'mean': np.mean(processA_time),
            'p99': np.percentile(processA_time, 99),
            'p90': np.percentile(processA_time, 90)
        },
        'processB': {
            'mean': np.mean(processB_time),
            'p99': np.percentile(processB_time, 99),
            'p90': np.percentile(processB_time, 90)
        },
    }
    return question1

def calculate_throughput(frames):
    "计算系统平均吞吐量以及平均帧"
    times = []
    for key, value in frames.items():
        time = value['valid_time']
        times.append(time)
    #length = len(times)
    #length2 = len(frames)
    que2 = len(frames) / sum(times)
    que3 = sum(times) / len(frames)
    return que2, que3


def show_gantt(frames):
    "绘制甘特图"
    data_A = []
    data_B = []
    for frame_id, value in frames.items():
        if value['A_time']:
            data_A.append({
                'Frame_id': int(frame_id),
                'Process': 'A',
                'start': value['A_start'],
                'time': value['A_time']
            })
        if value['B_time']:
            data_B.append({
                'Frame_id': int(frame_id),
                'Process': 'B',
                'start': value['B_start'],
                'time': value['B_time']
            })
    df_a = pd.DataFrame(data_A)
    df_b = pd.DataFrame(data_B)
    # 初始化绘图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)
    # 设置图表属性
    ax.set_xlabel('时间戳')
    ax.set_ylabel('帧号')
    ax.set_title('调度时序图')
    ax.grid(True)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune='both'))
    frame_ids = df_a['Frame_id'].unique().tolist() + df_b['Frame_id'].unique().tolist()
    frame_ids = sorted(set(frame_ids))  # 去除重复并排序
    yticks = frame_ids[::250]
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks)
    ax.legend(['Process A', 'Process B'])
    plt.barh(y=df_a['Frame_id'], width=df_a['time'], left=df_a['start'], color=['red'])
    plt.barh(y=df_b['Frame_id'], width=df_b['time'], left=df_b['start'], color=['yellow'])
    plt.savefig('gantt.png')
    plt.show()




if __name__ == '__main__':
    filter_trace("E:/pycharm/trace_analysis.log", 'filtered_trace.log')
    frames, frames_new = parse_process('filtered_trace.log')
    que1 = calculate_process_times(frames)
    que2, que3 = calculate_throughput(frames_new)
    result = {}
    result['各工序耗时'] = que1
    result['系统平均吞吐量'] = que2
    result['平均帧时延'] = que3
    path = Path('result.json')
    content = json.dumps(result, ensure_ascii=False, indent=4)
    path.write_text(content, encoding='utf-8')
    show_gantt(frames)
