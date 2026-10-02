from typing import List, Dict, Any, Tuple
from collections import deque
import statistics
import math

class TimeSeriesMath:

    @staticmethod
    def _get_timestamp_value(point: Dict[str, Any]) -> Tuple[float, float]:

        # Assume timestamp is datetime or unix
        x = point["timestamp"].timestamp() if hasattr(point["timestamp"], "timestamp") else point["timestamp"]
        # Look for the primary value key in the dict
        # Typically it's 'value' for raw, or 'avg_value' for aggregates
        y = point.get("value", point.get("avg_value", 0.0))
        return x, y

    @staticmethod
    def lttb_downsample(data: List[Dict[str, Any]], target_points: int) -> List[Dict[str, Any]]:

        if target_points <= 2 or len(data) <= target_points:
            return data

        sampled = []
        # Bucket size
        every = (len(data) - 2) / (target_points - 2)
        
        # Always include the first point
        sampled.append(data[0])
        
        a = 0  # index of current selected point
        
        for i in range(target_points - 2):
            # Calculate bucket ranges
            bucket_start = int(math.floor((i + 1) * every) + 1)
            bucket_end = int(math.floor((i + 2) * every) + 1)
            if bucket_end > len(data):
                bucket_end = len(data)
                
            bucket_length = bucket_end - bucket_start
            
            # Next bucket average
            next_start = bucket_end
            next_end = int(math.floor((i + 3) * every) + 1)
            if next_end > len(data):
                next_end = len(data)
                
            next_length = next_end - next_start
            if next_length <= 0:
                next_length = 1
                next_start = len(data) - 1
                next_end = len(data)
                
            avg_x = 0.0
            avg_y = 0.0
            for j in range(next_start, next_end):
                x, y = TimeSeriesMath._get_timestamp_value(data[j])
                avg_x += x
                avg_y += y
            avg_x /= next_length
            avg_y /= next_length
            
            # Find the point in current bucket that forms the largest triangle
            point_a_x, point_a_y = TimeSeriesMath._get_timestamp_value(data[a])
            
            max_area = -1.0
            max_area_index = -1
            
            for j in range(bucket_start, bucket_end):
                point_x, point_y = TimeSeriesMath._get_timestamp_value(data[j])
                # Area of triangle formula
                area = abs(
                    (point_a_x - avg_x) * (point_y - point_a_y) -
                    (point_a_x - point_x) * (avg_y - point_a_y)
                ) * 0.5
                
                if area > max_area:
                    max_area = area
                    max_area_index = j
                    
            sampled.append(data[max_area_index])
            a = max_area_index
            
        # Always include the last point
        sampled.append(data[-1])
        return sampled

    @staticmethod
    def apply_window_function(data: List[Dict[str, Any]], function_name: str, window_size: int) -> List[Dict[str, Any]]:

        if not data or window_size <= 1:
            return data
            
        results = []
        window = deque(maxlen=window_size)
        
        for item in data:
            _, y = TimeSeriesMath._get_timestamp_value(item)
            window.append(y)
            
            new_item = item.copy()
            if len(window) == 0:
                continue
                
            if function_name == 'sma':
                new_item['window_value'] = statistics.mean(window)
            elif function_name == 'rolling_median':
                new_item['window_value'] = statistics.median(window)
            elif function_name == 'variance':
                new_item['window_value'] = statistics.variance(window) if len(window) > 1 else 0.0
            elif function_name == 'stddev':
                new_item['window_value'] = statistics.stdev(window) if len(window) > 1 else 0.0
            else:
                new_item['window_value'] = y # Fallback
                
            results.append(new_item)
            
        return results

    @staticmethod
    def calculate_trend_metrics(data: List[Dict[str, Any]]) -> Dict[str, float]:

        if not data:
            return {}
            
        values = [TimeSeriesMath._get_timestamp_value(item)[1] for item in data]
        n = len(values)
        
        current_val = values[-1] if n > 0 else 0.0
        
        if n == 1:
            return {
                "current_value": current_val,
                "previous_value": current_val,
                "growth_rate": 0.0,
                "variance": 0.0,
                "std_dev": 0.0,
                "forecast_value": current_val,
                "anomaly_score": 0.0
            }
            
        # Split into two halves for current vs previous (basic approach)
        mid = n // 2
        prev_half = values[:mid]
        curr_half = values[mid:]
        
        prev_avg = sum(prev_half) / len(prev_half) if prev_half else current_val
        curr_avg = sum(curr_half) / len(curr_half) if curr_half else current_val
        
        # Variance and StdDev
        var = statistics.variance(values) if n > 1 else 0.0
        std = statistics.stdev(values) if n > 1 else 0.0
        
        # Linear Regression (Least Squares) for Slope (Growth Rate)
        # x will be normalized to 0, 1, 2... for numerical stability
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * y for i, y in enumerate(values))
        sum_xx = sum(i * i for i in range(n))
        
        denominator = (n * sum_xx - sum_x ** 2)
        slope = 0.0
        intercept = current_val
        if denominator != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
            
        # Forecast: predict what the value will be in 'n' steps from now (1 full window into future)
        forecast_value = slope * (n * 2) + intercept
        
        # Anomaly Score (0-100) based on Z-score of the most recent point
        mean_val = sum(values) / n
        z_score = 0.0
        if std > 0:
            z_score = abs((current_val - mean_val) / std)
            
        # Cap anomaly score at 100 (z_score of 3+ is considered highly anomalous ~99.7%)
        anomaly_score = min(100.0, (z_score / 3.0) * 100.0)
        
        return {
            "current_value": curr_avg,
            "previous_value": prev_avg,
            "growth_rate": slope,
            "variance": var,
            "std_dev": std,
            "forecast_value": forecast_value,
            "anomaly_score": anomaly_score
        }
