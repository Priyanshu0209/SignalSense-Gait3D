from typing import List, Dict, Optional
from copy import deepcopy
from app.schemas.processing import ProcessedDeviceState, SignalClassification, SignalTrend

class SimulationEngine:

    def __init__(self):
        self.active_simulation: Optional[str] = None
        
    def start_simulation(self, sim_type: str):
        self.active_simulation = sim_type
        
    def stop_simulation(self):
        self.active_simulation = None

    def apply_simulation(self, real_states: List[ProcessedDeviceState]) -> List[ProcessedDeviceState]:
        if not self.active_simulation:
            return real_states
            
        simulated_states = []
        for state in real_states:
            sim = deepcopy(state)
            sim.twin_mode = "SIMULATION"
            
            if self.active_simulation == "router_failure":
                sim.online_status = False
                sim.health_score = "Critical"
                sim.current_rssi.value = -99
                sim.signal_classification = SignalClassification.DISCONNECTED
                
            elif self.active_simulation == "high_congestion":
                sim.tx_rate = (sim.tx_rate or 0) * 0.1 # Throttle
                sim.rx_rate = (sim.rx_rate or 0) * 0.1
                sim.health_score = "Poor"
                sim.stability_score = max(0, sim.stability_score - 40)
                sim.signal_trend = SignalTrend.FLUCTUATING
                
            simulated_states.append(sim)
            
        return simulated_states

simulation_engine = SimulationEngine()

def get_simulation_engine() -> SimulationEngine:
    return simulation_engine
