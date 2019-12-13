import numpy as np
import matplotlib.pyplot as plt
import json

import os

def disp_connection(ax, con):
    a = {}
    labels = {}
    tick_labels = []

    for d, val in sorted(con.items()):
        tick_labels.append(d)
        for i, q in enumerate(val):
            key = i 
            labels[i] = q['time'][0] + ' ' + q['changes'][0]
            fare = float(q['fare'])

            if key in a.keys():
                a[key].append(fare)
            else:
                a[key] = [fare]

    for k, l in sorted(a.items()):
        ax.plot(l, label=labels[k])

    s = max([len(tick_labels)/7, 1])
    ticks = np.arange(0, len(tick_labels), int(s)) 
    ax.set_xticks(ticks)
    tmp = [tick_labels[i] for i in ticks]
    ax.set_xticklabels(tmp, rotation=0, fontsize=8)
    ax.legend()

def check_dir():
    files = [f for f in os.listdir('.') if f.split('.')[-1] == 'txt']
    return files

def get_con(filename):
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
    connection_filenames = check_dir()
    fig = plt.figure()
    for i, name in enumerate(connection_filenames):
        #ax = fig.add_subplot(len(connection_filenames),1,i+1)
        ax = fig.add_subplot(2, 2 ,i+1)
        connection = get_con(name)

        ax.set_title(name)
        disp_connection(ax, connection)

    plt.show()

if __name__ == '__main__':
    main()
