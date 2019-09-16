import pandas as pd
import numpy as np


def prepossessing(df):
    df = pd.DataFrame.__deepcopy__(df)
    for (columnName, columnData) in df.iteritems():
        df[columnName].replace('-', 9999999, inplace=True)
        df[columnName] = df[columnName].astype('float')
    return df

def prepossessingXM(df):
    df = pd.DataFrame.__deepcopy__(df)
    for (columnName, columnData) in df.iteritems():
        df[columnName].replace('-', -1, inplace=True)
        df[columnName] = df[columnName].astype('float')
    return df

def min_min(df):
    data = []
    for (columnName, columnData) in df.iteritems():
        indx = df[columnName].loc[df[columnName].idxmin(skipna=True)]
        data.append([indx,'Task '+str(df[df[columnName]==indx].index[0]),df[columnName].name])
    return min(data)

def max_min(df):
    data = []
    for (columnName, columnData) in df.iteritems():
        indx = df[columnName].loc[df[columnName].idxmin(skipna=True)]
        data.append([indx,'Task '+str(df[df[columnName]==indx].index[0]),df[columnName].name])
    return max(data)

def second_smallest(numbers):
    m1, m2 = float('inf'), float('inf')
    for x in numbers:
        if x is np.nan:
            break
        elif x <= m1:
            m1, m2 = x, m1
        elif x < m2:
            m2 = x
    return m2

def sufferagesufferage (df):
    prepossessing(df)
    task_list = []
    data = []
    for iex in df.values:
        indx = (second_smallest(iex)) - min(iex)
        task_list.append(indx)
    cindex= task_list.index(max(task_list))
    Machine_inx = df.iloc[cindex].idxmin()
    Task_inx= df.iloc[cindex].name
    indx = df.T[Task_inx].loc[df.T[Task_inx].idxmin()]
    data.append([indx,'Task ' + str(Task_inx),str(Machine_inx)])

    return min(data)

df = pd.read_csv('Input.csv',
            index_col='Task List',
            header=0,
                )

def min_min_scheduller(df):
    df1 = pd.DataFrame.copy(prepossessing(df))
    for index in range(0,len(df1)):
        data = min_min(df1)
        print(data)
        df1.update(df1[data[2]].apply(lambda x: np.nan if(pd.isnull(x)) else np.nansum([x,data[0]])))
        rowtoremove = int(str(data[1]).strip('Task '))
        df1 = df1.drop([rowtoremove], axis=0)

        #print(df1)

def max_min_scheduller(df):
    df2 =  pd.DataFrame.copy(prepossessingXM(df))
    for index in range(0,len(df2)):
        data = max_min(df2)
        print(data)
        df2.update(df2[data[2]].apply(lambda x: np.nansum([x, data[0]])))
        rowtoremove = int(str(data[1]).strip('Task '))
        df2 = df2.drop([rowtoremove], axis=0)

        #print(df2)

def sufferage_scheduller(df):
    df3 =  pd.DataFrame.copy(prepossessing(df))
    for index in range(0,len(df3)):
        data = sufferagesufferage(df3)
        print(data)
        df3.update(df3[data[2]].apply(lambda x: np.nansum([x, data[0]])))
        rowtoremove = int(str(data[1]).strip('Task '))
        df3 = df3.drop([rowtoremove], axis=0)

        #print(df3)




print("Algorithm Min-Min")
min_min_scheduller(df)
print("-------------------------------")

print("Algorithm Max-Min")
max_min_scheduller(df)
print("-------------------------------")

print("Algorithm Sufferage")
sufferage_scheduller(df)
print("-------------------------------")

