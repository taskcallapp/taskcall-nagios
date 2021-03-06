#!/usr/bin/env python3
# This file contains the code to send alerts from Nagios to TaskCall.

import argparse
import json
import logging
import requests


NAGIOS_SERVER = 'default'
INTEGRATION_KEY = ''
TOTAL_TIME = 60
config_parameters = {
    'integration_key': INTEGRATION_KEY,
    'log_path': '/var/log/taskcall-nagios/send_to_taskcall.log',
    'nagios_server': NAGIOS_SERVER,
    'nagios_to_taskcall.logger': 'warning',
    'taskcall.api.url': 'https://integrations.taskcallapp.com/nagios/',
    'nagios_to_taskcall.http.proxy.enabled': 'false',
    'nagios_to_taskcall.http.proxy.port': '1111',
    'nagios_to_taskcall.http.proxy.host': 'localhost',
    'nagios_to_taskcall.http.proxy.protocol': 'http',
    'nagios_to_taskcall.http.proxy.username': '',
    'nagios_to_taskcall.http.proxy.password': ''
}
config_path = '/home/taskcall-nagios/nagios_to_taskcall.conf'
cmd_line_arguments = dict()


def override_config_parameters():
    '''
    Reads parameters from the configuration file and override the parameters in the dictionary.
    '''
    try:
        file_reader = open(config_path, 'r')
        file_lines = file_reader.readlines()
        for line in file_lines:
            line = line.strip()
            if '#' not in line and line != '' and len(line) != 0:
                line_split = line.split('=')
                key, value = line_split[0].strip(), line_split[1].strip()
                if key == 'nagios_to_taskcall.timeout':
                    value = int(value)
                config_parameters[key] = value
        file_reader.close()
    except (IOError, ValueError) as e:
        logging.exception(str(e))


def log_config_parameters():
    '''
    Log the configuration parameters.
    '''
    logging.info('Configurations...')
    for item in config_parameters:
        logging.info(item + '=' + config_parameters[item])


def send_post_request():
    '''
    Send a HTTP post request to TaskCall's server to process alerts generated by Nagios.
    '''
    succeeded = False
    attempts = 0

    if cmd_line_arguments['entity_type'] == 'host':
        logging.info('Processing request for - HostName: ' + cmd_line_arguments['host_name'] +
                     ', HostState: ' + cmd_line_arguments['host_state'])
    else:
        logging.info('Processing request for - HostName: ' + cmd_line_arguments['host_name'] +
                     ', ServiceDesc: ' + cmd_line_arguments['service_desc'] + ', ServiceState: ' +
                     cmd_line_arguments['service_state'] + ']')

    while not succeeded and attempts <= 3:
        try:
            attempts += 1
            logging.info('Attempt ' + str(attempts))

            url = config_parameters['taskcall.api.url'] + cmd_line_arguments['integration_key']
            header_params = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Accept-Language': 'en'
            }
            response = requests.post(url, headers=header_params, data=json.dumps(cmd_line_arguments),
                                     timeout=TOTAL_TIME)

            if response.status_code == 200:
                succeeded = True
                logging.info('Succeeded')
            else:
                logging.error('Failed - Error code ' + str(response.status_code))
                logging.error(response.json())
        except Exception as e:
            logging.exception(str(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='send events from Nagios to TaskCall')

    parser.add_argument('-integKey', help='Integration key issued by TaskCall')
    parser.add_argument('-nagiosServer', default=config_parameters['nagios_server'], help='Nagios server')
    parser.add_argument('-logPath', default=config_parameters['log_path'], help='LOGPATH')
    parser.add_argument('-entityType')
    parser.add_argument('-ntt', help='NOTIFICATIONTYPE')
    parser.add_argument('-ldt', help='LONGDATETIME')

    # host related arguments
    parser.add_argument('-hn', help='HOSTNAME')
    parser.add_argument('-hdn', help='HOSTDISPLAYNAME')
    parser.add_argument('-hal', help='HOSTALIAS')
    parser.add_argument('-haddr', help='HOSTADDRESS')
    parser.add_argument('-hs', help='HOSTSTATE', default=None)
    parser.add_argument('-hsi', help='HOSTSTATEID', default=None)
    parser.add_argument('-lhs', help='LASTHOSTSTATE', default=None)
    parser.add_argument('-lhsi', help='LASTHOSTSTATEID', default=None)
    parser.add_argument('-hst', help='HOSTSTATETYPE', default=None)
    parser.add_argument('-ha', help='HOSTATTEMPT', default=None)
    parser.add_argument('-mha', help='MAXHOSTATTEMPTS', default=None)
    parser.add_argument('-hei', help='HOSTEVENTID', default=None)
    parser.add_argument('-lhei', help='LASTHOSTEVENTID', default=None)
    parser.add_argument('-hpi', help='HOSTPROBLEMID', default=None)
    parser.add_argument('-lhpi', help='LASTHOSTPROBLEMID', default=None)
    parser.add_argument('-hl', help='HOSTLATENCY', default=None)
    parser.add_argument('-het', help='HOSTEXECUTIONTIME', default=None)
    parser.add_argument('-hd', help='HOSTDURATION', default=None)
    parser.add_argument('-hds', help='HOSTDURATIONSEC', default=None)
    parser.add_argument('-hdt', help='HOSTDOWNTIME', default=None)
    parser.add_argument('-hpc', help='HOSTPERCENTCHANGE', default=None)
    parser.add_argument('-hgn', help='HOSTGROUPNAME', default=None)
    parser.add_argument('-hgns', help='HOSTGROUPNAMES', default=None)
    parser.add_argument('-lhc', help='LASTHOSTCHECK', default=None)
    parser.add_argument('-lhsc', help='LASTHOSTSTATECHANGE', default=None)
    parser.add_argument('-lhu', help='LASTHOSTUP', default=None)
    parser.add_argument('-lhd', help='LASTHOSTDOWN', default=None)
    parser.add_argument('-lhur', help='LASTHOSTUNREACHABLE', default=None)
    parser.add_argument('-ho', help='HOSTOUTPUT', default=None)
    parser.add_argument('-lho', help='LONGHOSTOUTPUT', default=None)
    parser.add_argument('-hnu', help='HOSTNOTESURL', default=None)
    parser.add_argument('-hpd', help='HOSTPERFDATA', default=None)

    # service related arguments
    parser.add_argument('-s', help='SERVICEDESC', default=None)
    parser.add_argument('-sdn', help='SERVICEDISPLAYNAME', default=None)
    parser.add_argument('-ss', help='SERVICESTATE', default=None)
    parser.add_argument('-ssi', help='SERVICESTATEID', default=None)
    parser.add_argument('-lss', help='LASTSERVICESTATE', default=None)
    parser.add_argument('-lssi', help='LASTSERVICESTATEID', default=None)
    parser.add_argument('-sst', help='SERVICESTATETYPE', default=None)
    parser.add_argument('-sa', help='SERVICEATTEMPT', default=None)
    parser.add_argument('-msa', help='MAXSERVICEATTEMPTS', default=None)
    parser.add_argument('-siv', help='SERVICEISVOLATILE', default=None)
    parser.add_argument('-sei', help='SERVICEEVENTID', default=None)
    parser.add_argument('-lsei', help='LASTSERVICEEVENTID', default=None)
    parser.add_argument('-spi', help='SERVICEPROBLEMID', default=None)
    parser.add_argument('-lspi', help='LASTSERVICEPROBLEMID', default=None)
    parser.add_argument('-sl', help='SERVICELATENCY', default=None)
    parser.add_argument('-set', help='SERVICEEXECUTIONTIME', default=None)
    parser.add_argument('-sd', help='SERVICEDURATION', default=None)
    parser.add_argument('-sds', help='SERVICEDURATIONSEC', default=None)
    parser.add_argument('-sdt', help='SERVICEDOWNTIME', default=None)
    parser.add_argument('-spc', help='SERVICEPERCENTCHANGE', default=None)
    parser.add_argument('-sgn', help='SERVICEGROUPNAME', default=None)
    parser.add_argument('-sgns', help='SERVICEGROUPNAMES', default=None)
    parser.add_argument('-lsch', help='LASTSERVICECHECK', default=None)
    parser.add_argument('-lssc', help='LASTSERVICESTATECHANGE', default=None)
    parser.add_argument('-lsok', help='LASTSERVICEOK', default=None)
    parser.add_argument('-lsw', help='LASTSERVICEWARNING', default=None)
    parser.add_argument('-lsu', help='LASTSERVICEUNKNOWN', default=None)
    parser.add_argument('-lsc', help='LASTSERVICECRITICAL', default=None)
    parser.add_argument('-so', help='SERVICEOUTPUT', default=None)
    parser.add_argument('-lso', help='LONGSERVICEOUTPUT', default=None)
    parser.add_argument('-snu', help='SERVICENOTESURL', default=None)
    parser.add_argument('-spd', help='SERVICEPERFDATA', default=None)

    # parse the arguments
    args = parser.parse_args()

    cmd_line_arguments['integration_key'] = args.integKey
    cmd_line_arguments['nagios_server'] = args.nagiosServer
    cmd_line_arguments['log_path'] = args.logPath
    cmd_line_arguments['entity_type'] = args.entityType
    cmd_line_arguments['notification_type'] = args.ntt
    cmd_line_arguments['long_date_time'] = args.ldt

    cmd_line_arguments['host_name'] = args.hn
    cmd_line_arguments['host_display_name'] = args.hdn
    cmd_line_arguments['host_alias'] = args.hal
    cmd_line_arguments['host_address'] = args.haddr
    cmd_line_arguments['host_state'] = args.hs
    cmd_line_arguments['host_state_id'] = args.hsi
    cmd_line_arguments['last_host_state'] = args.lhs
    cmd_line_arguments['last_host_state_id'] = args.lhsi
    cmd_line_arguments['host_state_type'] = args.hst
    cmd_line_arguments['host_attempt'] = args.ha
    cmd_line_arguments['max_host_attempts'] = args.mha
    cmd_line_arguments['host_event_id'] = args.hei
    cmd_line_arguments['last_host_event_id'] = args.lhei
    cmd_line_arguments['host_problem_id'] = args.hpi
    cmd_line_arguments['last_host_problem_id'] = args.lhpi
    cmd_line_arguments['host_latency'] = args.hl
    cmd_line_arguments['host_execution_time'] = args.het
    cmd_line_arguments['host_duration'] = args.hd
    cmd_line_arguments['host_duration_sec'] = args.hds
    cmd_line_arguments['host_down_time'] = args.hdt
    cmd_line_arguments['host_percent_change'] = args.hpc
    cmd_line_arguments['host_group_name'] = args.hgn
    cmd_line_arguments['host_group_names'] = args.hgns
    cmd_line_arguments['last_host_check'] = args.lhc
    cmd_line_arguments['last_host_state_change'] = args.lhsc
    cmd_line_arguments['last_host_up'] = args.lhu
    cmd_line_arguments['last_host_down'] = args.lhd
    cmd_line_arguments['last_host_unreachable'] = args.lhur
    cmd_line_arguments['host_output'] = args.ho
    cmd_line_arguments['long_host_output'] = args.lho
    cmd_line_arguments['host_notes_url'] = args.hnu
    cmd_line_arguments['host_perf_data'] = args.hpd

    cmd_line_arguments['service_desc'] = args.s
    cmd_line_arguments['service_display_name'] = args.sdn
    cmd_line_arguments['service_state'] = args.ss
    cmd_line_arguments['service_state_id'] = args.ssi
    cmd_line_arguments['last_service_state'] = args.lss
    cmd_line_arguments['last_service_state_id'] = args.lssi
    cmd_line_arguments['service_state_type'] = args.sst
    cmd_line_arguments['service_attempt'] = args.sa
    cmd_line_arguments['max_service_attempts'] = args.msa
    cmd_line_arguments['service_is_volatile'] = args.siv
    cmd_line_arguments['service_event_id'] = args.sei
    cmd_line_arguments['last_service_event_id'] = args.lsei
    cmd_line_arguments['service_problem_id'] = args.spi
    cmd_line_arguments['last_service_problem_id'] = args.lspi
    cmd_line_arguments['service_latency'] = args.sl
    cmd_line_arguments['service_execution_time'] = args.set
    cmd_line_arguments['service_duration'] = args.sd
    cmd_line_arguments['service_duration_sec'] = args.sds
    cmd_line_arguments['service_down_time'] = args.sdt
    cmd_line_arguments['service_percent_change'] = args.spc
    cmd_line_arguments['service_group_name'] = args.sgn
    cmd_line_arguments['service_group_names'] = args.sgns
    cmd_line_arguments['last_service_check'] = args.lsch
    cmd_line_arguments['last_service_state_change'] = args.lssc
    cmd_line_arguments['last_service_ok'] = args.lsok
    cmd_line_arguments['last_service_warning'] = args.lsw
    cmd_line_arguments['last_service_unknown'] = args.lsu
    cmd_line_arguments['last_service_critical'] = args.lsc
    cmd_line_arguments['service_output'] = args.so
    cmd_line_arguments['long_service_output'] = args.lso
    cmd_line_arguments['service_notes_url'] = args.snu
    cmd_line_arguments['service_perf_data'] = args.spd

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

    # Override the configuration parameters
    override_config_parameters()

    # Log the configurations
    log_config_parameters()

    if cmd_line_arguments['notification_type'] is None or cmd_line_arguments['notification_type'] == '':
        logging.error('Nagios NOTIFICATIONTYPE parameter is missing. Aborting process.')
    else:
        send_post_request()
