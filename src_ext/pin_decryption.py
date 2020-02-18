# Purpose: given user PIN, recover minutiae from the altered data 

import hashlib

def decryption (user_pin, datatable):
    """ create recovered database 
        input:
            user_pin: int
            datatable: altered data that are stored previously as pandas dataframe
        output:
            datatable: with recovered minutiae info
    """

    hash_object = hashlib.sha256(b'%d' %user_pin)
    hash_value = hash_object.hexdigest()

    #print(hash_value)

    # a dictionary: key = hexdecimal value, value = decimal value
    dict_str = hexdict()

    # a dictionary: key = zone, value = (change in x, y, angle) from pin
    pin_dict = {}
    i = 0
    while i < len(hash_value)/8:
        dx, dy, dangle = hash_value[i*8], hash_value[i*8+1], hash_value[i*8+2]
        pin_dict[i] = (dict_str[dx],  dict_str[dy], dict_str[dangle])
        i += 1



    datatable['alter_rc'] = datatable['zone'].map(pin_dict)
    datatable['dx_calc'], datatable['dy_calc'], datatable['dangle_calc'] = datatable.alter_rc.str

    datatable['x_rc'] = datatable['x_alt'] - 3 * datatable['dx_calc']
    datatable['y_rc'] = datatable['y_alt'] - 3 * datatable['dy_calc']
    datatable['angle_rc'] = datatable['angle_alt'] - 10 * datatable['dangle_calc']

    # make sure recovered angle is in (-180, 180]
    datatable['angle_rc_adj'] = datatable['angle_rc'] \
                             - (datatable['angle_rc']//360) * 360 * (datatable['angle_rc']>180) \
                             - (datatable['angle_rc']//360) * 360 * (datatable['angle_rc']<= -180)

    datatable['angle_rc_adj'] -= 360*(datatable['angle_rc_adj']>= 180)
    datatable['angle_rc_adj'] += 360*(datatable['angle_rc_adj']< -180)

    return datatable


def hexdict():
    """ return a dictionary:
        keys: hexidecimal chars
        values: hexidecimal numbers
    """

    str_example = '0123456789abcdef'
    dict_str = {}
    for i in range(len(str_example)):
        dig = str_example[i]
        dict_str[dig] = i

    return dict_str
