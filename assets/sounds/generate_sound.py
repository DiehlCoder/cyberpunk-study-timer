import math
import struct
import wave
from pathlib import Path

def generate_soft_bell(filename="assets/sounds/bell.wav"):
    sample_rate = 44100
    duration = 2.5  # seconds
    num_samples = int(sample_rate * duration)
    
    # Harmonics of a pleasant warm chime (E major pentatonic / meditation bell)
    frequencies = [659.25, 1318.5, 1975.5, 2637.0]  # E5, E6, B6, E7
    weights = [1.0, 0.45, 0.2, 0.1]
    decay_rates = [1.8, 2.5, 3.2, 4.0]
    
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = 0.0
        for freq, weight, decay in zip(frequencies, weights, decay_rates):
            # Exponential decay envelope
            envelope = math.exp(-decay * t)
            value += weight * envelope * math.sin(2.0 * math.pi * freq * t)
        
        # Soft attack ramp to avoid clicks
        attack = min(1.0, t / 0.005)
        value *= attack
        
        # Clamp & scale to 16-bit PCM integer
        sample_val = int(max(-1.0, min(1.0, value * 0.7)) * 32767)
        samples.append(sample_val)
        
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        raw_data = struct.pack(f'<{len(samples)}h', *samples)
        wav_file.writeframes(raw_data)

if __name__ == "__main__":
    generate_soft_bell()
