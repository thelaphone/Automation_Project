import os
import glob
import numpy
from astropy.table import Table, Column 
from subprocess import check_call, Popen, PIPE, TimeoutExpired


def check_files(user_input):   
    """
    Checks to make sure given directory is a valid directory.  
    If directory exists, returns list of .fits files.
    """
    file_ext = ['*.fit*', '*.FIT*']
    data_files = []
    working_dir = os.path.exists(user_input)
    
    if working_dir == True:
        os.chdir(directory)
        for files in file_ext:
            data_files += glob.glob(files)           
        print(data_files)           
        return(data_files)     
    else:
        print('Invalid directory. Please try again.') 
        return False   

while True:   
    directory = input('Enter Directory: ')   
    fits_files = check_files(directory)
    if fits_files != False:
        break

target_data = numpy.loadtxt(fname='/Users/jaredhand/Documents/Automation Project/Automation_Project/target_data.txt',
                            dtype=bytes,
                            delimiter=',')

def bytes_to_str(list_input):
    """
    Converts data type of imported array elements from 
    bytes to string.
    """
    for i in range(len(list_input)):
        x = list_input[i].decode('utf-8')
        list_input[i] = x
    return list_input

target_name = target_data[:,0].tolist()
target_RA = target_data[:,1].tolist()
target_dec = target_data[:,2].tolist()

target_name = bytes_to_str(target_name)
target_RA = bytes_to_str(target_RA)
target_dec = bytes_to_str(target_dec)

def target_dict(name_list,
                val_list):
    """
    Takes list of names and list of values and returns a 
    dictionary with with name_list as dictionary key.
    """
    result = dict(zip(name_list, val_list))
    return result

RA_dict = target_dict(target_name,
                      target_RA)
dec_dict = target_dict(target_name,
                       target_dec)


# In[5]:

get_ipython().magic('debug')
script = 'solve-field --use-sextractor --overwrite --no-plots --ra %s --dec %s --radius 2 "%s"' 

def coord_lookup(file1, dict1):
    """
    Used in script_loop() to relate parsed file name to a given coordinate. Filename is split according to conditional 
    below.
    
    Parameters:
        
        file1: string representing filename that will be compared to keys of dict1
        dict1: dictionary that is used to lookup coordinates via the keyvalue to file1
        
    """
    i = '' #'i' is variable placeholder for file1 after split according to the following conditions:
    
    if 'B_' in file1:
        i = file1.split('B_', 1)[0]
    elif 'V_' in file1:
        i = file1.split('V_', 1)[0]
    elif 'I_' in file1:
        i = file1.split('I_', 1)[0]
    elif 'R_' in file1:
        i = file1.split('R_', 1)[0]
    elif '-' in file1:
        i = file1.split('-', 1)[0]
    elif '_' in file1:
        i = file1.split('_', 1)[0]
    else:
        return(False)
    
    no_whitespace = i.replace(' ','')
    if no_whitespace in dict1.keys():
        try:
            print(no_whitespace)
            coord = dict1.get(no_whitespace)
            print(coord)
            return(coord)
        except:
            return(False)
    elif no_whitespace.upper() in dict1.keys():
        try:
            print(no_whitespace.upper())
            coord = dict1.get(no_whitespace.upper())
            print(coord)
            return(coord)
        except:
            return(False)
    elif no_whitespace.lower() in dict1.keys():
        try:
            print(no_whitespace.lower())
            coord = dict1.get(no_whitespace.lower())
            print(coord)
            return(coord)
        except:
            return(False)
    else:
        return(False)
        

def script_loop(files1, dict1, dict2):
    """
    Prints input list of files.  Loops through reach i in files1 and performs coord_lookup with i 
    with both dict1 and dict2.  From there right ascension is determined by input dict1 and i and 
    declination by dict2 and i.  ra and dec are modified to be used in check_call method that runs 
    astrometry.net with given parameters:
    
        solve-field --use-sextractor --overwrite --downsample <int> --ra <degrees>
        --dec <degrees> --radius <arcminutes> 'filename'
        
    Parameters:
    
        files1: input list of all files in a directory in which to run astrometry.net
        dict1: used as a dictionary to determine ra a file in files1
        dict2: used as a dictionary to determine dec from a file files1
        
    """
    print(files1)
    for i in files1:       
        """
        try:
            proc.communicate(timeout=5)
        except TimeoutExpired:
            proc.kill()
        """
        try:
            #note that ra is returned in hour angles.
            ra = coord_lookup(i,
                              dict1)

            dec = coord_lookup(i, 
                                   dict2)
            
            if ra == False or dec == False:
                print('Coordinate lookup error.  Check to see if target exists in target_data.txt.')
                break

            #ra_rep = ra.replace('.', ':')
            #ra_p1 = ra_rep[0:len(ra)-2]
            #ra_p2 = ra_rep[len(ra)-2:len(ra)]
            """
            Convert ra from str to float to multipy by 15 to give angles in degrees as opposed to hour angles.  
            ra_angles is cast back to str during assignment for consistency with dec_int
            """
            ra_float =float(ra)
            ra_angle = str(ra_float*15.)
            
            print(script %(ra_angle, dec, i)) 

            proc = check_call([script %(ra_angle, dec, i)],
                            shell=True)
            
            print('Success for file '+i)           
        except AttributeError:
            print('AttributeError: Filename: '+i+'. Check to see if target exists in target_data.txt')
            raise
        except KeyboardInterrupt:
            print('Halted')
            break
        except:
            print("ERROR: File name: "+i+"  ra: "+ra_angle+"  dec: "+dec)
        
print(script_loop(fits_files, RA_dict, dec_dict))


# In[4]:

target_table = Table([target_name, target_RA, target_dec], 
                     names = ('name', 'RA', 'dec'))
target_table.show_in_browser()


# In[ ]:



