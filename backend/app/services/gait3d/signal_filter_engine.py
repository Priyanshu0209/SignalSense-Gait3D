import math
import statistics
from typing import List, Dict, Any, Tuple

class SignalFilterEngine:

    @staticmethod
    def apply_savitzky_golay(values: List[float], window_size: int = 7) -> List[float]:

        n = len(values)
        if n < window_size or window_size < 3:
            return values.copy()

        # Ensure odd window size
        if window_size % 2 == 0:
            window_size -= 1
            
        # Standard coefficients for quadratic 7-point window: [-2, 3, 6, 7, 6, 3, -2] / 21
        # Coefficients for 5-point window: [-3, 12, 17, 12, -3] / 35
        if window_size == 5:
            coeffs = [-3/35.0, 12/35.0, 17/35.0, 12/35.0, -3/35.0]
            half = 2
        else: # Default 7-point
            coeffs = [-2/21.0, 3/21.0, 6/21.0, 7/21.0, 6/21.0, 3/21.0, -2/21.0]
            half = 3
            
        smoothed = []
        for i in range(n):
            if i < half or i >= n - half:
                smoothed.append(values[i])
            else:
                val = 0.0
                for j in range(-half, half + 1):
                    val += values[i + j] * coeffs[j + half]
                smoothed.append(round(val, 3))
        return smoothed

    @staticmethod
    def apply_butterworth_lowpass(values: List[float], cutoff_hz: float = 3.5, sample_rate_hz: float = 20.0) -> List[float]:

        n = len(values)
        if n < 3 or sample_rate_hz <= 0 or cutoff_hz >= sample_rate_hz / 2.0:
            return values.copy()

        # Calculate bilinear transform filter coefficients for 2nd order Butterworth
        w0 = 2.0 * math.pi * (cutoff_hz / sample_rate_hz)
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha = sin_w0 / (2.0 * math.sqrt(2.0))
        
        b0 = (1.0 - cos_w0) / 2.0
        b1 = 1.0 - cos_w0
        b2 = (1.0 - cos_w0) / 2.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
        
        # Normalize by a0
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0
        
        filtered = [values[0], values[0]]
        for i in range(2, n):
            y = (b0 * values[i] +
                 b1 * values[i-1] +
                 b2 * values[i-2] -
                 a1 * filtered[i-1] -
                 a2 * filtered[i-2])
            filtered.append(round(y, 3))
            
        return filtered

    @staticmethod
    def compute_fft(values: List[float], sample_rate_hz: float = 20.0, max_bins: int = 30) -> Dict[str, Any]:

        n = len(values)
        if n < 10 or sample_rate_hz <= 0:
            return {"frequencies": [], "magnitudes": [], "dominant_frequency_hz": 0.0, "spectral_entropy": 0.0}

        # Mean subtraction (remove zero-frequency DC component)
        avg = statistics.mean(values)
        centered = [v - avg for v in values]
        
        # Apply Hanning window to prevent spectral leakage
        windowed = [centered[i] * (0.5 - 0.5 * math.cos(2.0 * math.pi * i / (n - 1))) for i in range(n)]
        
        frequencies = []
        magnitudes = []
        
        # Only evaluate frequencies up to Nyquist limit (sample_rate / 2)
        half_n = min(n // 2, max_bins * 2)
        freq_resolution = sample_rate_hz / float(n)
        
        dominant_freq = 0.0
        max_mag = 0.0
        total_mag = 0.0
        
        for k in range(1, half_n): # skip k=0 DC component
            freq_hz = k * freq_resolution
            if freq_hz > 5.0: # Human locomotion is rarely above 5 Hz
                break
                
            real_part = 0.0
            imag_part = 0.0
            for t in range(n):
                angle = 2.0 * math.pi * k * t / n
                real_part += windowed[t] * math.cos(angle)
                imag_part -= windowed[t] * math.sin(angle)
                
            magnitude = math.sqrt(real_part**2 + imag_part**2) / (n / 2.0)
            magnitude = round(magnitude, 4)
            
            frequencies.append(round(freq_hz, 2))
            magnitudes.append(magnitude)
            total_mag += magnitude
            
            if freq_hz >= 0.6 and magnitude > max_mag:
                max_mag = magnitude
                dominant_freq = freq_hz

        # Calculate Spectral Entropy as measure of movement chaos / predictability
        entropy = 0.0
        if total_mag > 0.0:
            for mag in magnitudes:
                p = mag / total_mag
                if p > 0:
                    entropy -= p * math.log(p, 2)
        
        return {
            "frequencies": frequencies,
            "magnitudes": magnitudes,
            "dominant_frequency_hz": round(dominant_freq, 2),
            "max_magnitude": round(max_mag, 3),
            "spectral_entropy": round(entropy, 3)
        }

signal_filter_singleton = SignalFilterEngine()

def get_signal_filter_engine() -> SignalFilterEngine:
    return signal_filter_singleton
