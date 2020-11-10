import numpy as np
import sys
from conversions import min2decimal, meters2lat, meters2long
# This code usues several functions from conversions.py

# for running the script just to test, these are the file locations
true_file = "tuning_true.csv"
filtered_file = "tuning_test.csv"

# This is how true_path and filtered_path are ordered
SIMP_DTYPES = ['long','lat','bearing','speed']


def csv_to_inputs(csv_file):
    '''
    gets numpy arrays from csv paths

    @param path csv_file: path to csv of simulated rovers path (true or filtered) in [lat_deg, lat_min, long_deg, long_min, bearing, speed]
    @return ndarray path: simulator's true path in numpy array format, no dtype. follows SIMP_DTYPE though
    '''
    old_dtypes = ['longitude_deg', 'longitude_min',
                  'latitude_deg', 'latitude_min', 'bearing_deg','speed']
    path_data = np.genfromtxt(csv_file, delimiter=',',
                              names=old_dtypes, skip_header=1)

    # restructure to merge minutes and degrees
    # I had trouble doing anything to the array once I added in the dtypes so I didn't on these ones. They follow SIMP_DTYPES though.
    path = np.array([min2decimal(path_data['longitude_deg'], path_data['longitude_min']), min2decimal(path_data['latitude_deg'], path_data['latitude_min']),
                    path_data['bearing_deg'],path_data['speed']])
    return path


def evaluate_fit(true_path, filtered_path):
    '''
    assign a number to how good the KF did

    @param true_path: numpy array of the SIMP_DTYPES generaged by the simulater
    @param filtered_path: numpy array of the SIMP_DTYPES from the simulated rovers KF
    @return float: the assesment, which should range from [0,1]
    '''

    # Depends on maximum range
    #lat_range = max(true_path[0]) - min(true_path[0])
    #long_range = max(true_path[1]) - min(true_path[1])
        #speed_range = 10
    #bearing_range = 180  # assuming degrees

    # Depends on predetermined maximum error
    long_range = meters2long(5,true_path[1][0]) #the maximum error is 5 meters.
    lat_range = meters2lat(5)
    speed_range = 1.6 #the maximum error is 1.6m/s
    bearing_range = 30 #the maximum error is 30 degrees

    range_scale = [long_range, lat_range, bearing_range, speed_range]
    diff = abs(true_path - filtered_path)

    scaled_diff = np.divide(diff, np.reshape(range_scale, (4, 1)))
    
    scaled_diff[scaled_diff > 1] = 1

    #default result = 0.10819432899669192
    #speed = .1; everything else = .3; result is 0.09694895559595343
    #speed = .1; bearing = .1; everything else = .3; result is 0.07278779465168708

    return np.average(scaled_diff[0]*0.4+scaled_diff[1]*0.4+scaled_diff[2]*0.1+scaled_diff[3]*0.1)

#for testing
def alter_fit(filtered_path, increment):
    for i in range(4):
        filtered_path[i] += increment[i]
    return filtered_path


if __name__ == "__main__":
    # Get arguments
    if (len(sys.argv) != 3): #3 arguments
        print('Error: Usage from onboard/filter is python3 -m tools.plotter <data_type>')
        sys.exit()

    true_path = csv_to_inputs(sys.argv[1])
    filtered_path = csv_to_inputs(sys.argv[2])
    #Testing cases by altering filtered path
    #for i in range(10):
    #    print(evaluate_fit(true_path, alter_fit(filtered_path, [meters2long(1, true_path[1][0]),
    #                                                            meters2lat(1), 0, 0])))
    print(evaluate_fit(true_path,filtered_path))