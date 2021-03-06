# Script to check edPuzzle grades automatically
#Download all CSVs from EdPuzzle (1/27)
# EP list here: https://docs.google.com/document/d/1rGFqK199RTIh7JK6YA2UedSvFxhvVfKWmETCbvn0u-s/edit?usp=sharing

import pandas as pd
import os
from functools import reduce
import datetime
import numpy as np
import sys
import argparse
import matplotlib.pyplot as plt


advisories = ['BOS', 'SHN', 'BNU-Cats', 'Casa-Amigos']
date = datetime.datetime.now().date()


class edPuzzleCheck(object):

    def __init__(self):
        self.advisories = advisories
        self.today = datetime.datetime.now().date()


    def rename_files(self):
        '''
        Re-organizes file dump in files dir
        Copy input csv files into 
        '''
        for root, dirs, files in os.walk('files', topdown=True):
            print(root, dirs)
            for f in files:
                if '.csv' in f:
                    old_path = os.path.join(root, f)
                    new_file_name = f.replace(' ', '-')
                    new_path = os.path.join(root, new_file_name)
                    os.rename(old_path, new_path)

        self.input_path = os.path.join('.', 'files', f'input-{self.today}')
        if not os.path.isdir(self.input_path):
            os.mkdir(self.input_path)
        # Creating directory for files to be graded
        # Should be all dumped to files dir, this script handles the rest
        for a in self.advisories:
            print(f'Creating folder for {a}')
            self.path2create = os.path.join(self.input_path, a)
            if not os.path.isdir(self.path2create):
                os.mkdir(self.path2create)
            else:
                print('date dir already exists')
                pass

            # Placing input csv files into advisory folders with new name
            for f in os.listdir('files'):
                if a in f and 'csv' in f:
                    os.rename(os.path.join('files', f), os.path.join(self.path2create, f.replace(' ', '-')))
                    print('')

    def convertToSA(self, raw_grade):
        '''
        Converts raw_grade from EdPuzzle completion to appropriate SA HW grade (0, 50, 70, 85, 100)
        '''
        # Grade ranges as keys, scaled SA score as vals
        grade_map = {(0., 25.): 0.,
                     (25.0, 50.0): 50.0,
                     (50., 70.0): 70.0,
                     (70.0, 90.0): 85.0,
                     (90.0, 100.0):100.0}
        bins = list(grade_map.keys())
        for b in bins:
            if b[1] >= raw_grade >= b[0]:
                return grade_map[b]

    def edPuzzleCheck(self, advisory, path):
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
            df = pd.read_csv(os.path.join(path, f))

            # Getting only kids who watched at least 90% of vids
            df = df[df['Video watched (%)'] >=90]

            # print(f'Grades for {f}', df)#, vid.columns)
            list_of_names.append(set(df['First name']))

        # getting intersection of completion logs -- kids who did each video above 90% completion
        u = set.intersection(*list_of_names)
        print(f'Kids who did them all in {advisory}:\n', u)
        print('##############################\n')


    def gradeEdPuzzles(self, advisory, path, save_csv=True):
        '''
        Function to grade edpuzzles over the course of a week
        Returns df with columns for scholar name, Video completion per assignment, and average video completion
        Grades edPuzzle completion for one advisory
        '''
        
        print(f'Grading EdPuzzles for {advisory} on {self.today}...')
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
        df['SA Grade']= df['Average Completion %'].apply(self.convertToSA)

        print(f'{advisory} data for this week:\n', df)
        rounded_avg = round(np.mean(df['SA Grade']), 2)
        std_dev = np.std(df['SA Grade'])
        print(f'{advisory} Class average: {rounded_avg} %')
        print(f'{advisory} Class std dev: {std_dev} %')

        # Saving to a csv in grades folder for this date
        if save_csv:
            grades_folder = f'grades-{self.today}'
            # Creating output folder if needed
            if not (os.path.isdir(os.path.join('grades', grades_folder))):
                os.mkdir(os.path.join('grades', grades_folder))
                print(f'grades folder created! {grades_folder}')
            path_to_output = os.path.join('.', 'grades', grades_folder,f'{advisory}-grades-{self.today}.csv')
            df.to_csv(path_to_output)
        print('###############################################')

        # return df


    def check_all_advisories(self):
        '''
        If all advisories desired, create grades files for each
        '''
        print(f'Checking all advisories grades for {date}...')
        for a in self.advisories:
            path_to_folder = os.path.join(self.input_path, a)
            self.gradeEdPuzzles(a, path_to_folder, True)
            self.populate_export_template(a)

    def one_advisory(self, advisory):
        '''
        Check EdPuzzle grades for ONE advisory
        Pass advisory name as a string
        '''
        path = os.path.join(self.input_path, advisory)
        self.gradeEdPuzzles(advisory, path, True)

    def create_hist(self, df):
        '''
        Create histogram from csv grade file
        '''
        f, (ax1, ax2) = plt.subplots(1,2)

        ax1.hist(df['Average Completion %'])
        ax2.hist(df['SA Grade'])

        ax1.set_xlabel('Average Video Completion %')
        ax2.set_xlabel('Grade')
        plt.show()

    def populate_export_template(self, advisory):
        """
        Creates a copy and populates template grade imports for SIS
        """
        print("Creating SIS import doc...")
        
        grades_path = os.path.join('.', 'grades', f'grades-{self.today}',f'{advisory}-grades-{self.today}.csv')
        grades = pd.read_csv(grades_path)
        template_path = os.path.join('.', 'templates', f'{advisory}-template.csv')
        df = pd.read_csv(template_path)
        print(grades)
        
#         If name cols match (both sorted alphabetically by last name
        if len(df) == len(grades):
            df['Grade'] = grades['SA Grade']
            print(df)
        
#        If a kid logs on with a non-SA account
#        Need to figure out easier system
        else:
            print('Names do not match...')
#            Need to figure out dropping non-SA accounts
#            print(df.where(df.values==grades.values).notna())
        
#        Dumping to csv in export dir
        export_folder = f'export-{self.today}'
        # Creating output folder if needed
        if not (os.path.isdir(os.path.join('export', export_folder))):
            os.mkdir(os.path.join('export', export_folder))
            print(f'export folder created! {export_folder}')
        path_to_output = os.path.join('.', 'export', export_folder,f'{advisory}-grades-{self.today}.csv')
        df.to_csv(path_to_output)
        
        
        


if __name__ == "__main__":
    ep = edPuzzleCheck()
    ep.rename_files() # Putting file dump into proper bins

    args = len(sys.argv) -1
    if args > 0:
#        ep.one_advisory(advisory = sys.argv[1])
        ep.populate_export_template(advisory = sys.argv[1])
    else:
        ep.check_all_advisories()
        




