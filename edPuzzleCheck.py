# Script to check edPuzzle grades automatically
#Download all CSVs from EdPuzzle (1/27)
# EP list here: https://docs.google.com/document/d/1rGFqK199RTIh7JK6YA2UedSvFxhvVfKWmETCbvn0u-s/edit?usp=sharing

import pandas as pd
import os
from functools import reduce
import datetime
import numpy as np


advisories = ['BOS', 'SHN', 'BNU-Cats', 'Casa-Amigos']
date = datetime.datetime.now().date()

def convertToSA(raw_grade):
    '''
    Converts raw_grade from EdPuzzle completion to appropriate SA HW grade (0, 50, 70, 85, 100)
    '''

    if raw_grade < 25.:
        return 0.

    elif 50. > raw_grade >= 25.:
        return 50.

    elif 70. > raw_grade >= 50.:
        return 70.

    elif 90. > raw_grade >= 70.:
        return 85.

    elif 100. >= raw_grade >= 90.:
        return 100.

def edPuzzleCheck(advisory, path):
    '''
    This function checks all of the edpuzzle videos for one homeroom
    Returns a DF with column for scholar name, and a column of completion for each EP in the list
    advisory - str, name of advisory to check, should matchdirectory name
    path - path to folder with csvs
    '''
    print(f'Getting EdPuzzle completion data for {advisory}, {path}')
    list_of_names = []
    
    # Going through each file in folder
    for f in os.listdir(path):
        df= pd.read_csv(os.path.join(path, f))

        # Getting only kids who watched at least 90% of vids
        df = df[df['Video watched (%)'] >=90]

        # print(f'Grades for {f}', df)#, vid.columns)
        list_of_names.append(set(df['First name']))

    # getting intersection of completion logs -- kids who did each video above 90% completion
    u = set.intersection(*list_of_names)
    print(f'Kids who did them all in {advisory}:\n', u)
    print('##############################\n')


def gradeEdPuzzles(advisory, path, save_csv=True):
    '''
    Function to grade edpuzzles over the course of a week
    Returns df with columns for scholar name, Video completion per assignment, and average video completion
    '''
    
    print(f'Grading EdPuzzles for {advisory} on ')
    dfs = []
    n = 1
    for f in os.listdir(path):
        assignment_name = f.replace('.csv', '')
        dat = pd.read_csv(os.path.join(path, f))

        # Dropping unneeded columns
        dat = dat.drop(['Role', 'Username', 'Time spent', 'Last watched', 'Time turned in', 'On time?'], axis=1)
        # grade and Correct answers may change #s based on video
        for col in dat.columns:
            if 'Correct answers' in col or 'Grade' in col:
                dat = dat.drop(col, axis=1)

        # Renaming columns for assignment
        dat = dat.rename(columns={'Video watched (%)': f'Video-{n} % Watched'})

        dat['Scholar Name'] = dat['First name'] + ' ' + dat['Last name'] 
        dat = dat.drop(['Last name', 'First name'], axis=1)
        dat = dat.set_index('Scholar Name')
        dfs.append(dat)

        n += 1

    # Concatenating previous dfs
    df = pd.concat(dfs, axis=1)
    df = df.loc[:,~df.columns.duplicated()] # Dropping duplicated Scholar Name columns
    n_cols = len(df.columns)

    df['Average Completion %'] = df.mean(axis=1)
    df['SA Grade']= df['Average Completion %'].apply(convertToSA)

    print(f'{advisory} data for this week:\n', df)
    print(f'{advisory} Class average:', np.mean(df['SA Grade']))


    if save_csv:
        # Saving to a csv in grades folder for this date
        grades_folder = f'grades-{date}'
        if not (os.path.join('grades', grades_folder)):
            os.mkdir(os.path.join('grades', grades_folder))
            print(f'grades folder created! {grades_folder}')
        path_to_output = os.path.join('.', 'grades', grades_folder,f'{advisory}-grades-{date}.csv')
        df.to_csv(path_to_output)

    return df


def check_all_advisories():
    '''
    If all advisories desired, create grades files for each
    '''
    print(f'Checking all advisories grades for {date}...')
    # 
    for a in advisories:
        path_to_folder = os.path.join('.', 'files', f'input{a}-{date}')
        gradeEdPuzzles(a, path_to_folder, True)

def one_advisory(advisory):
    '''
    Check EdPuzzle grades for ONE adviusry
    '''

    path = os.path.join('.', 'files', advisory)
    gradeEdPuzzles(advisory, path, True)



if __name__ == "__main__":
    check_all_advisories()





