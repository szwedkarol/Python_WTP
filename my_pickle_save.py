# Karol Szwed
# 17.02.2024 r.
# Python programming course
# Data analysis of the public bus transit in Warsaw
# My helper functions for saving and loading objects as pickle files.

import pickle

"""
 * INPUT:
    - "pickle_filename" - string with the name of the pickle file where the object will be saved;
    - "obj_to_save" - the object that will be saved in the pickle file.
 * FUNCTION: Save an object to a pickle file.
 * OUTPUT: None; function has side effect of creating a pickle file with the saved object.
"""
def save_obj_as_pickle_file(pickle_filename, obj_to_save):
    with open(pickle_filename, 'wb') as f:
        pickle.dump(obj_to_save, f)


"""
 * INPUT:
    - "pickle_filename" - string with the name of the pickle file from which the object will be loaded;
    - "obj_to_load" - the object that will be loaded from the pickle file.
 * FUNCTION: Load an object from a pickle file.
 * OUTPUT: The object loaded from the pickle file.
"""
def load_obj_from_pickle_file(pickle_filename):
    with open(pickle_filename, 'rb') as f:
        return pickle.load(f)
