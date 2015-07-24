import argparse
import json
import logging
import pprint
import requests
import time

from requests.auth import HTTPDigestAuth

class AutomationApiBase:

    def __init__(self, base_url, agent_hostname, group_id, api_user, api_key):
        self.base_url = base_url + "/api/public/v1.0"
        self.agent_hostname = agent_hostname
        self.group_id = group_id
        self.api_user = api_user
        self.api_key = api_key

    def wait_for_goal_state(self):

        count = 0
        while True:
            continue_to_wait = False
            status = self.get_automation_status()
            goal_version = status['goalVersion']

            for process in status['processes']:
                logging.info("Round: %s GoalVersion: %s Process: %s LastVersionAchieved: %s Plan: %s "
                             % (count, goal_version, process['hostname'], process['lastGoalVersionAchieved'], process['plan']))

                if process['lastGoalVersionAchieved'] < goal_version:
                    continue_to_wait = True

            if continue_to_wait:
                time.sleep(1)
            else:
                logging.info("All processes in Goal State. GoalVersionAchieved: %s" % goal_version)
                break

            count += 1

    def get_automation_config(self):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        return self.get(url)

    def get_automation_status(self):
        url = "%s/groups/%s/automationStatus" % (self.base_url, self.group_id)
        return self.get(url)

    def post_monitoring_agent_config(self, file_name):
        url = "%s/groups/%s/automationConfig/monitoringAgentConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def post_backup_agent_config(self, file_name):
        url = "%s/groups/%s/automationConfig/backupAgentConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def post_automation_config(self, file_name):
        url = "%s/groups/%s/automationConfig" % (self.base_url, self.group_id)
        json_body = self.load_config(file_name)
        return self.put(url, json_body)

    def get(self, url):
        logging.info("Executing GET: %s" % url)
        r = requests.get(url, auth=HTTPDigestAuth(self.api_user, self.api_key))
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))
        return r.json()

    def put(self, url, json_body):
        logging.info("Executing PUT: %s" % url)
        headers = {'content-type': 'application/json'}
        r = requests.put(
            url,
            auth=HTTPDigestAuth(self.api_user, self.api_key),
            data=json.dumps(json_body),
            headers=headers
        )
        self.check_response(r)
        logging.debug("%s" % pprint.pformat(r.json()))

        return r

    def check_response(self, r):
        if r.status_code != requests.codes.ok:
            logging.error("Response Error Code: %s Detail: %s" % (r.status_code, r.json()['detail']))
            raise ValueError(r.json()['detail'])

    def load_config(self, file_name):
        data = self.load_json(file_name)

        # Replace the AGENT_HOSTNAME placeholders in the example configs
        # with real value.
        self.replace_agent_hostnames(data)
        self.replace_process_hostnames(data)
        self.replace_kerberos_principals(data)
        return data

    def load_json(self, file_name):
        with open(file_name) as data_file:
            data = json.load(data_file)
        return data

    def replace_agent_hostnames(self, data):
        if 'monitoringVersions' in data:
            for index, mv in enumerate(data['monitoringVersions']):
                data['monitoringVersions'][index]['hostname'] = self.agent_hostname

        if 'backupVersions' in data:
            for index, bv in enumerate(data['backupVersions']):
                data['backupVersions'][index]['hostname'] = self.agent_hostname

    def replace_process_hostnames(self, data):
        if 'processes' in data:
            for index, mv in enumerate(data['processes']):
                data['processes'][index]['hostname'] = self.agent_hostname
                if data['processes'][index].get('alias'):
                    data['processes'][index]['alias'] = self.agent_hostname

    def replace_kerberos_principals(self, data):
        if 'kerberosPrincipal' in data:
            data['kerberosPrincipal'] = data['kerberosPrincipal'].replace('AGENT_HOSTNAME', self.agent_hostname)

        if 'auth' in data:
            if 'autoUser' in data['auth']:
                data['auth']['autoUser'] = data['auth']['autoUser'].replace('AGENT_HOSTNAME', self.agent_hostname)

            for index, user in enumerate(data['auth']['usersWanted']):
                data['auth']['usersWanted'][index]['user'] = \
                    data['auth']['usersWanted'][index]['user'].replace('AGENT_HOSTNAME', self.agent_hostname)
