# generate_sounds.py - Robotic 8-bit sound effects for Zerobot
import wave
import struct
import math
import random
from pathlib import Path

def generate_complex_wav(filename, duration, volume=0.3, 
                         freq_start=440, freq_end=440, 
                         wave_type='square', noise=0.0,
                         vibrato_freq=0, vibrato_amt=0,
                         robotic=False):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    path = Path("zerobot/assets/sounds") / filename
    
    with wave.open(str(path), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        phase = 0
        for i in range(num_samples):
            t = float(i) / sample_rate
            progress = i / num_samples
            
            # 1. Calculate frequency
            freq = freq_start * (freq_end / freq_start) ** progress
            if vibrato_freq > 0:
                freq += math.sin(2 * math.pi * vibrato_freq * t) * vibrato_amt
            
            # 2. Oscillator
            sample = 0
            if wave_type == 'square':
                sample = 1.0 if math.sin(phase) > 0 else -1.0
            elif wave_type == 'triangle':
                sample = 2.0 * abs(2.0 * (phase / (2 * math.pi) - math.floor(phase / (2 * math.pi) + 0.5))) - 1.0
            
            phase += 2 * math.pi * freq / sample_rate
            
            # 3. Robotic Speech Effect (PWM/Vocal vibration)
            if robotic:
                # Add a 50Hz "buzz" to simulate vocal cords
                buzz = 1.0 if math.sin(2 * math.pi * 50 * t) > 0 else 0.5
                sample *= buzz
            
            # 4. Add Noise
            if noise > 0:
                sample = sample * (1 - noise) + (random.random() * 2 - 1) * noise
            
            # 5. Envelope
            if progress < 0.1: env = progress / 0.1
            elif progress > 0.7: env = 1.0 - (progress - 0.7) / 0.3
            else: env = 1.0
                
            sample *= env * volume
            packed_sample = struct.pack('<h', int(sample * 32767))
            wav_file.writeframesraw(packed_sample)
    print(f"Generated {filename}")

def generate_hello_robotic():
    # Two-part "Hel-lo" sound
    sample_rate = 44100
    path = Path("zerobot/assets/sounds/hello.wav")
    
    with wave.open(str(path), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Syllable 1: "Hel" (Short, low)
        dur1 = 0.15
        for i in range(int(sample_rate * dur1)):
            t = float(i) / sample_rate
            freq = 220 # A3
            sample = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)
            sample *= (1.0 if math.sin(2 * math.pi * 60 * t) > 0 else 0.4) # Robotic buzz
            packed_sample = struct.pack('<h', int(sample * 0.3 * 32767))
            wav_file.writeframesraw(packed_sample)
            
        # Short gap
        for i in range(int(sample_rate * 0.05)):
            wav_file.writeframesraw(struct.pack('<h', 0))
            
        # Syllable 2: "lo" (Longer, rising)
        dur2 = 0.25
        for i in range(int(sample_rate * dur2)):
            t = float(i) / sample_rate
            progress = i / (sample_rate * dur2)
            freq = 330 + progress * 110 # E4 to A4
            sample = (1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0)
            sample *= (1.0 if math.sin(2 * math.pi * 60 * t) > 0 else 0.4) # Robotic buzz
            env = 1.0 - progress
            packed_sample = struct.pack('<h', int(sample * 0.3 * env * 32767))
            wav_file.writeframesraw(packed_sample)
    print("Generated robotic hello.wav")

def generate_all():
    generate_hello_robotic()
    generate_complex_wav("starting.wav", 0.6, freq_start=110, freq_end=1760, wave_type='triangle')
    generate_complex_wav("thinking.wav", 0.15, freq_start=880, freq_end=1320, volume=0.1, wave_type='sine')
    generate_complex_wav("success.wav", 0.3, freq_start=523, freq_end=1046, wave_type='square', volume=0.2)
    generate_complex_wav("error.wav", 0.4, freq_start=150, freq_end=100, noise=0.6, wave_type='square')
    generate_complex_wav("goodbye.wav", 0.5, freq_start=880, freq_end=220, wave_type='square', volume=0.2)

if __name__ == "__main__":
    generate_all()
