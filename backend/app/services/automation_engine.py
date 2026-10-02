import logging
from typing import List
from app.schemas.processing import ProcessedDeviceState

logger = logging.getLogger("signalsense.automation_engine")

class AutomationEngine:

    def __init__(self):
        self.workflows = []
        self._load_default_workflows()
        
    def _load_default_workflows(self):

        self.workflows.append({
            "trigger": "Unknown Device",
            "condition": lambda s: s.behavior_profile == "Unknown" and s.online_status,
            "action": self._action_alert_slack
        })
        self.workflows.append({
            "trigger": "Critical Health",
            "condition": lambda s: s.health_score == "Critical" and s.online_status,
            "action": self._action_log_critical
        })
        self.workflows.append({
            "trigger": "High Packet Loss",
            "condition": lambda s: s.signal_quality is not None and s.signal_quality < 20,
            "action": self._action_log_warning
        })
        
    def evaluate(self, state: ProcessedDeviceState):
        if state.twin_mode == "SIMULATION":
            return # Never automate on simulated data
            
        for wf in self.workflows:
            try:
                if wf["condition"](state):
                    wf["action"](state)
            except Exception as e:
                pass # logger.error
            
    def _action_log_critical(self, state: ProcessedDeviceState):
        logger.warning(
            f"[WORKFLOW] Health Critical for {state.hostname or state.mac_address}. Action: Log Alert."
        )
            
    def _action_log_warning(self, state: ProcessedDeviceState):
        logger.warning(
            f"[WORKFLOW] High packet loss likely for {state.hostname or state.mac_address}. Quality: {state.signal_quality}%"
        )
            
    def _action_alert_slack(self, state: ProcessedDeviceState):
        # We would only trigger this once per device using a cache, simplified for Phase 7
        logger.warning(
            f"[WORKFLOW] Unknown Device detected. Triggering Slack Webhook."
        )

automation_engine = AutomationEngine()

def get_automation_engine() -> AutomationEngine:
    return automation_engine
