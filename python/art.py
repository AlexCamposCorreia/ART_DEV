import common.yaml_lib as yaml_lib
import run_modules.mohid as mohid
import run_modules.ww3 as ww3
import run_modules.wrf as wrf

import common.constants as static
import common.config as cfg
import common.logger
import datetime
import os.path
import sys


def validate_path(path):
    return os.path.exists(path)


def main():

    yaml = yaml_lib.open_yaml_file(sys.argv[1])

    #yaml_lib.validate_yaml_file(yaml)
    #yaml_lib.validate_date(yaml)
    validate_path(yaml['artconfig']['mainPath'])

    artconfig_keys = yaml['artconfig'].keys()

    # ALEX
    global static
    if 'logFileName' in artconfig_keys:
        static.logger = common.logger.ArtLogger("MOHID", yaml['artconfig']['logFileName'])
    else:
        static.logger = common.logger.ArtLogger("MOHID", "log.txt")


    running_mode(yaml)
            
    module = yaml['artconfig']['module']
    if module == "mohid" or module == "Mohid":
        mohid.execute(yaml)
    elif module == "WW3":
        ww3.execute(yaml)
    elif module == "WRF":
        wrf.execute(yaml)
    else:
        raise ValueError("No valid simulation module given.")
    
    static.logger.info("------------- ART RUN FINISHED -------------")
    print("------------- ART RUN FINISHED -------------")


def running_mode(yaml):
    if yaml['artconfig']['operationalMode']:
        static.logger.debug("Running in Operational Mode")
        today = datetime.datetime.today()
        cfg.global_initial_date = today + datetime.timedelta(days=yaml['artconfig']['refDayToStart'])
        cfg.global_final_date = (today + datetime.timedelta(days=yaml['artconfig']['numberOfRuns'])
                                    + datetime.timedelta(days=yaml['artconfig']['daysPerRun'] - 1))
        cfg.number_of_runs = yaml['artconfig']['numberOfRuns']
        initial_date = cfg.global_initial_date
        final_date = initial_date + datetime.timedelta(days=yaml['artconfig']['daysPerRun'])
        static.logger.debug("Initial Date : " + initial_date.strftime(static.DATE_FORMAT))
        static.logger.debug("Final Date: " + final_date.strftime(static.DATE_FORMAT))
        static.logger.debug("Number of runs : " + str(cfg.number_of_runs))
    elif not (yaml['artconfig']['operationalMode']):
        try:
            static.logger.debug("Running in Normal Mode")
            cfg.global_initial_date = datetime.datetime.strptime(yaml['artconfig']['startDate'],
                                                                    static.DATE_FORMAT)
            cfg.global_final_date = datetime.datetime.strptime(yaml['artconfig']['endDate'], static.DATE_FORMAT)

            difference = cfg.global_final_date - cfg.global_initial_date
            cfg.number_of_runs = difference.days
        except KeyError:
            static.logger.warning("KeyError")
            cfg.number_of_runs = 1
            global_initial_date = datetime.datetime.today()
            global_final_date = global_initial_date + datetime.timedelta(days=yaml['artconfig']['daysPerRun'])
            cfg.global_initial_date = datetime.datetime.strftime(datetime.datetime.today(), static.DATE_FORMAT)
            cfg.global_final_date = datetime.datetime.strftime(global_final_date, static.DATE_FORMAT)
        finally:
            static.logger.debug("Global Initial Date : " + cfg.global_initial_date.strftime(static.DATE_FORMAT))
            static.logger.debug("Global Final Date : " + cfg.global_final_date.strftime(static.DATE_FORMAT))
            static.logger.debug("Number of runs : " + str(cfg.number_of_runs))
    else:
        raise ValueError("artconfig: forecastMode value needs to be either a number or true/false")


if __name__ == "__main__":
    main()
