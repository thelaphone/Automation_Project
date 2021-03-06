import astrometry
import stacking
import sex_auto
import get_files
import config
import target_data
import os
import shutil
import glob

# initialize fits_files variable as a list of fits files at input directory.
while True:
    cwd = config.astrometry_directory
    fits_files = get_files.check_files(cwd)
    no_space = get_files.rm_spaces(fits_files)
    if no_space:
        break

# Instantiate TargetData class.
td = target_data.TargetData()
# All values from target_data are Byte data type.
target_name = td.target_data[:, 0].tolist()
target_RA = td.target_data[:, 1].tolist()
target_dec = td.target_data[:, 2].tolist()
# Converts Byte data in each list to string data type.
target_name = td.bytes_to_str(target_name)
target_RA = td.bytes_to_str(target_RA)
target_dec = td.bytes_to_str(target_dec)
# create dictionaries of RA and dec for each respective target
RA_dict = td.target_dict(target_name, target_RA)
dec_dict = td.target_dict(target_name, target_dec)

os.chdir(config.astrometry_directory)

# Run astronomy.net
astrometry.astro_pipe(fits_files, RA_dict, dec_dict)
# merge wcs header with old fits files
wcs_list = glob.glob('*.wcs')
astrometry.wcs_header_merge(files=fits_files, wcs=wcs_list)

for fits in glob.glob('*.fits'):
    shutil.move(config.astrometry_directory + fits,
                config.stacking_directory + fits)
# move timeout lists
for file in glob.glob('*_timeout.txt*'):
    shutil.move(config.astrometry_directory + file,
                config.pipeline_root + 'timeout_lists/' + file)
# Remove clutter created by astrometry.net
for file in glob.glob('*'):
    os.remove(config.astrometry_directory + file)

# stacked astrometized files
stacking.swarp()

# move stacked fits and delete weights
for stacked in glob.glob('*.fit*'):
    if stacked in glob.glob('*.weight.fit*'):
        os.remove(config.stacking_directory + stacked)
        # shutil.move(config.stacking_directory + stacked,
        #             config.stacking_directory + '/weights/' + stacked)
    elif stacked in glob.glob('*_st.fit*'):
        shutil.move(config.stacking_directory + stacked,
                    config.sex_directory + stacked)
# remove lists used by swarp
for file in glob.glob('*_list.txt*'):
    os.remove(config.stacking_directory + file)
# remove *.new files created by astrometry.net
for file in glob.glob('*.fit*'):
    os.remove(config.stacking_directory + file)

# run SExtractor on stacked files
sex_auto.sex_call()

# move catalogs to catalog directory
for sexed in glob.glob('*.cat'):
    shutil.move(config.sex_directory + sexed,
                config.finished_catalogs + sexed)
# move stacked fits to finished stacked directory
for stacked in glob.glob('*.fit*'):
    shutil.move(config.sex_directory + stacked,
                config.finished_stacked + stacked)
