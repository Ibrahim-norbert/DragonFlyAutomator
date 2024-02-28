import ProjectRoot
name = "ProjectRoot"

def Go():
	change_wd_to_project_root()
	
def change_wd_to_project_root():
    """
    Helper function for jupyter notebook usage
    This methode goes recursively upwards from the current file directory
    and searches for the .root_dir file, if found it changes the working directory to that folder
    """
    import glob
    import os
    print('search for root_dir and set working directory')
    root = glob.glob(os.path.join(os.getcwd(), '.root_dir'))
    counter = 0
    
    while len(root) == 0 and counter <= 5:

        # go upwards and search for .root_dir file
        os.chdir('../')
        root = glob.glob(os.path.join(os.getcwd(), '.root_dir'))

    print('Working directory set to: {}'.format(os.getcwd()))
    
