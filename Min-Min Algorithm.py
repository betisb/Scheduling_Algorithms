import pandas as pd
import numpy as np


def prepossessing(df):
    for (columnName, columnData) in df.iteritems():
        df[columnName].replace('-', np.nan, inplace=True)
        df[columnName] = df[columnName].astype('float')
    return df

def min_min(df):
    data = []
    for (columnName, columnData) in df.iteritems():
        indx = df[columnName].loc[df[columnName].idxmin()]
        data.append([indx,'Task '+str(df[df[columnName]==indx].index[0]),df[columnName].name])
    return min(data)

def max_min(df):
    data = []
    for (columnName, columnData) in df.iteritems():
        indx = df[columnName].loc[df[columnName].idxmin()]
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
    for (columnName, columnData) in df.iteritems():
        inx = task_list.index(min(task_list))
        Cname = df.idxmin(axis=1)
        Task = df.loc[:, :].min(axis=1)
        data.append([Task[inx],'Task '+str(inx),Cname[inx]])
    return min(data)

df = pd.read_csv('Input.csv',
            index_col='Task List',
            header=0,
                )

def min_min_scheduller(df):
    df = prepossessing(df)
    for index in range(0,len(df)):
        data = min_min(df)
        print(data)
        rowtoremove = int(str(data[1]).strip('Task '))
        df = df.drop([rowtoremove], axis=0)
        df.update(df[data[2]].apply(lambda x: np.nansum([x,data[0]])))
        print(df)

def max_min_scheduller(df):
    df = prepossessing(df)
    for index in range(0,len(df)):
        data = max_min(df)
        print(data)
        rowtoremove = int(str(data[1]).strip('Task '))
        df = df.drop([rowtoremove], axis=0)
        df.update(df[data[2]].apply(lambda x: np.nansum([x,data[0]])))
        print(df)

def sufferage_scheduller(df):
    df = prepossessing(df)
    for index in range(0,len(df)):
        data = sufferagesufferage(df)
        print(data)
        rowtoremove = int(str(data[1]).strip('Task '))
        df = df.drop([rowtoremove], axis=0)
        df.update(df[data[2]].apply(lambda x: np.nansum([x,data[0]])))
        print(df)

#min_min_scheduller(df)
#max_min_scheduller(df)
sufferage_scheduller(df)
# data = (min_min(df))
# print(data)
#
# data2 = min_min(df)
# rowtoremove= int(str(data[1]).strip('Task '))
# df.update(df[data2[2]].apply(lambda x: int(x)+data2[0]))
#
# print(df)
# print(max_min(df))





#df.columns = [x.strip().replace(' ', '_') for x in df.columns]
# for idx, colidx in df.iteritems():
#     if df.iat[colidx,idx] == '-':
#         df.iat[colidx,idx] = 999
#     print(df.iat[colidx,idx])
#df.columns = [df.columns].str.replace('-','999').astype('float')

#print(df)

#print(df['Machine 2'].loc[df['Machine 2'].idxmin()])

#prepossessing(df)
#print(df.loc[df.idxmin()])
# for each in range(0,len(df)):
#     if df.iat[each, 2] == '-':
#         df.iat[each,2] = 999
#     print(df.iat[each,2])
    #print(df.get(each))
    #,
     #       dtype= {'Machine 0': np.float64,'Machine 1': np.float64,'Machine 2': np.float64,'Machine 3': np.float64,'Machine 4': np.float64,'Machine 5': np.float64,'Machine 6': np.float64})
    #,
     #       names=['Task List','Machine 0','Machine 1','Machine 2','Machine 3','Machine 4','Machine 5','Machine 6'])

#print(next(df.iterrows())[1].get('Machine 0'))

#print(next(df.iterrows())[1].get('Machine 1'))
#print(next(df.iterrows())[1].get('Machine 2'))
#print(next(df.iterrows())[1].get('Machine 3'))
#print(next(df.iterrows())[1].get('Machine 4'))
#df_T = df.T
#for each in (next(df_T.iterrows())[1].index):

#    print(df_T[each].get(each))
