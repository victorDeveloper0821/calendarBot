import configparser
import os

#config.sections()
# get current configs
def getConfigs():
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(dir_path+'/config.ini')
    return config;


if __name__=='__main__' :
    testConfig = getConfigs();
    print('testConfig: ',testConfig['Google']['calendarId'])
    print('testConfig: ',type(testConfig['Google']))
