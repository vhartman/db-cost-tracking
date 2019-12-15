import numpy as np
import matplotlib.pyplot as plt

import datetime
import time

import json
import os


def disp_connection(ax, con):
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    a = {}
    labels = {}
    tick_labels = []

    for d, val in sorted(con.items()):
        if len(val) > 0:
            tick_labels.append(d)
        for i, q in enumerate(val):
            key = i 
            labels[i] = q['time'][0] + ' ' + q['changes'][0]
            fare = float(q['fare'])

            if key in a.keys():
                a[key].append(fare)
            else:
                a[key] = [fare]

    # compute tick label stuff
    # 11/20/2019, 19:00:04
    t0 = datetime.datetime.strptime('01/01/1900, 00:00:00', "%m/%d/%Y, %H:%M:%S")
    t = [datetime.datetime.strptime(q, "%m/%d/%Y, %H:%M:%S") for q in tick_labels]
    t = [(q - t0).total_seconds() for q in t]

    for k, l in sorted(a.items()):
        name = labels[k]
        name = name[:-2] + ':' + name[-2:]
        name = name[:2] + ':' + name[2:]

        m = 'v'
        if name[-1] == '0':
            m = 'o'
            name = r'\textbf{'+name+'}'

        t_seg = [t[0]]
        l_seg = [l[0]]
        flag = False
        for i in range(len(t)-1):
            if t[i+1] - t[i] > 60*60*2:
                if not flag:
                    ax.plot(t_seg, l_seg, label=name, color=colors[k])
                    flag = True
                else:
                    ax.plot(t_seg, l_seg, color=colors[k])
                
                ax.plot([t[i], t[i+1]], [l[i], l[i+1]], ':', color=colors[k])

                t_seg = []
                l_seg = []

            t_seg.append(t[i+1])
            l_seg.append(l[i+1])

        ax.plot(t_seg, l_seg, color=colors[k])

        #ax.plot(t, l, label=name)
        #ax.scatter(t, l, marker=m, label=name, s=4)

    s = max([len(tick_labels)/4, 1])
    ticks = np.arange(0, len(tick_labels), int(s)) 
    ax.set_xticks([t[a] for a in ticks])
    
    tmp = [tick_labels[i].split(',')[0] for i in ticks]
    ax.set_xticklabels(tmp, rotation=0, fontsize=8)

    ax.legend(title='Changes')

    ax.grid(axis='y')

    ax.spines['left'].set_position(('outward', 10))
    ax.spines['bottom'].set_position(('outward', 10))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    return tmp


def check_dir():
    files = [f for f in os.listdir('.') if f.split('.')[-1] == 'txt']
    return files


def read_connection_data(filename):
    d = {}
    with open(filename) as f:
        for line in f:
            s = line.split('[')
            date_time = s[0][:-2]

            conn = '[' + '['.join(s[1:])
            conn_json = json.loads(conn)

            d[date_time] = conn_json

        return d


def main():
    plt.rc('text', usetex=True)

    connection_filenames = check_dir()
    fig = plt.figure()

    axes = []
    min_price = 100
    max_price = 0

    groups = {}
    for name in connection_filenames:
        iternary = ' '.join(name.split('_')[:2])
        
        if iternary in groups:
            groups[iternary].append(name)
        else:
            groups[iternary] = [name]

    num_connections = len(groups)
    max_days = max([len(v) for _, v in groups.items()])

    max_xticks = [0, 1]
    max_xticklabels = None

    cnt = 0
    for iternary_name, names in sorted(groups.items()):
        for i, name in enumerate(sorted(names)):
            #ax = fig.add_subplot(len(connection_filenames),1,i+1)
            if cnt > 0 or i > 0:
                ax = fig.add_subplot(max_days, num_connections, 1 + i*num_connections + cnt, sharex=axes[0])
            else:
                ax = fig.add_subplot(max_days, num_connections, 1 + i*num_connections + cnt)

            connection = read_connection_data(name)

            if i == 0:
                ax.set_title(iternary_name)

            ax.text(-.15, 0.5, name.split('.')[0].split('_')[-1],
                    fontsize=12,
                    rotation=90,
                    verticalalignment='center',
                    transform=ax.transAxes)

            ax.set_ylabel("Price [Euro]")
            if i == len(names)-1:
                ax.set_xlabel("Time of retrieval")

            labels = disp_connection(ax, connection)

            lb, ub = ax.get_ylim()
            
            min_price = min([lb, min_price])
            max_price = max([ub, max_price])

            xticks = ax.get_xticks()
            if max_xticks[-1] - max_xticks[0] < xticks[-1] - xticks[0]:
                max_xticks = xticks
                max_xticklabels = labels

            axes.append(ax)

        cnt += 1

    for ax in axes:
        ax.set_ylim(min_price, max_price)
        ax.set_xticks(max_xticks)
        ax.set_xticklabels(max_xticklabels)

    plt.show()

if __name__ == '__main__':
    main()
