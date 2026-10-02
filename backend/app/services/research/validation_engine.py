from app.services.research.research_manager import get_research_manager

class ValidationEngine:
    def __init__(self):
        self.research_manager = get_research_manager()

    def run_diagnostics(self) -> list:
        warnings = []
        experiments = self.research_manager.get_all_experiments()
        
        if not experiments:
            warnings.append({
                "level": "Warning",
                "message": "No experiments found. Run a training cycle to generate research data."
            })
            return warnings
            
        for exp in experiments:
            metrics = exp.get("metrics", {})
            if not metrics:
                warnings.append({
                    "level": "Critical",
                    "message": f"Experiment {exp['id']} is missing evaluation metrics."
                })
            elif metrics.get("MAE", 0) > 5.0:
                warnings.append({
                    "level": "Warning",
                    "message": f"Experiment {exp['id']} has an unusually high MAE (> 5.0m)."
                })
                
            note = self.research_manager.get_note(exp['id'])
            if len(note) < 50:
                warnings.append({
                    "level": "Info",
                    "message": f"Experiment {exp['id']} has very short notes. Consider expanding for reproducibility."
                })
                
        return warnings

validation_engine = ValidationEngine()

def get_validation_engine() -> ValidationEngine:
    return validation_engine
