import argparse
import logging

from automation_api_base import AutomationApiBase

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

class TestAutomationApi(AutomationApiBase):

    def __init__(self, base_url, agent_hostname, group_id, api_user, api_key):
        AutomationApiBase.__init__(self, base_url, agent_hostname, group_id, api_user, api_key)

    def clean(self):
        self.post_automation_config("configs/api_0_clean.json")

    def run(self):
        self.post_automation_config("configs/api_0_clean.json")
        self.wait_for_goal_state()
        
        self.post_automation_config("configs/api_1_define_versions.json")
        self.wait_for_goal_state()

        self.post_automation_config("configs/api_2_install_other_agents.json")
        self.wait_for_goal_state()

        self.post_automation_config("configs/api_3_create_replica_set.json")
        self.wait_for_goal_state()

        self.post_automation_config("configs/api_4_upgrade_replica_set.json")
        self.wait_for_goal_state()

        self.post_automation_config("configs/api_5_replica_set_to_cluster.json")
        self.wait_for_goal_state()

        self.post_automation_config("configs/api_6_enable_auth.json")
        self.wait_for_goal_state()


if __name__ == '__main__':

    # python test_automation_api.py http://mms.example.com:8080 mongo-01.example.com 54b5e4df9436322466a89a3e apple@johnandcailin.com 063fc60e-c5eb-4426-85c1-1e650d6228c6
    parser = argparse.ArgumentParser(description='Automation API Demo')
    parser.add_argument('base_url', help="Base URL")
    parser.add_argument('agent_hostname', help="Agent Hostname")
    parser.add_argument('group_id', help="Group ID")
    parser.add_argument('api_user', help="API User")
    parser.add_argument('api_key', help="API Key")
    parser.add_argument('--clean', action='store_true', required=False)
    args = parser.parse_args()

    test = TestAutomationApi(args.base_url, args.agent_hostname, args.group_id, args.api_user, args.api_key)
    if args.clean:
        test.clean()
    else:
        test.run()

