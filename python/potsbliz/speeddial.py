import re
import potsbliz.config as config
from potsbliz.logger import Logger


def convert(number):
    with Logger(__name__ + '.convert') as log:

        # read speeddial numbers from config
        speeddial_numbers = config.get_speeddial_numbers()
        
        for entry in speeddial_numbers:
            if (entry[0] == number):
                # remove non-digit characters
                expanded_number = re.sub('[^0-9]+', '', entry[1])                
                log.debug('Speeddial number found: ' + number + ' => ' + expanded_number)
                return expanded_number
            
        # no speeddial number found
        return number
