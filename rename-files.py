# Script to get rid of spaces in edPuzzle filenames
# Removes spaces from csv file names for pandas read-in

import os
import glob
import datetime

advisories = ['BOS', 'SHN', 'BNU-Cats', 'Casa-Amigos']
date = datetime.datetime.now().date()



for root, dirs, files in os.walk('files', topdown=True):
	print(root, dirs)
	for f in files:
		if '.csv' in f:
			old_path = os.path.join(root, f)
			new_file_name = f.replace(' ', '-')
			new_path = os.path.join(root, new_file_name)
			os.rename(old_path, new_path)

# Creating directory for files to be graded
# Should be all dumped to files dir, this script handles the rest
for a in advisories:
	path2create = os.path.join('files', f'input{a}-{date}')
	if not os.path.isdir(path2create):
		os.mkdir(path2create)
	else:
		print('date dir already exists')
		pass

	for f in os.listdir('files'):
		if a in f and 'csv' in f:
			os.rename(os.path.join('files', f), os.path.join(path2create, f.replace(' ', '-')))
print(os.path.isdir('./files'))