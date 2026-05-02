# Zerobot Hardware Embodiment (BODY)

This document describes the physical hardware that you (the agent) are currently embodying.

## Core System
- **Processor**: Raspberry Pi Zero 2 W
- **Servo Driver**: Waveshare Servo Driver HAT (PCA9685)
- **Power**: 12V External Supply

## Physical Structure: Quadruped Crab-Bot
The robot has a crab-like structure with **4 legs**, each using **2 servos** (Total 8 servos).

### Kinematics Chain
Each leg has two segments:
1. **Primary Joint (Shoulder)**: Connected directly to the main body frame.
2. **Secondary Joint (Knee)**: Connected to the primary leg segment.

### Servo Mapping
- **Front Left Leg**: 
  - **L1** (Shoulder - Body to Leg)
  - **L3** (Joint - Connected to L1)
- **Front Right Leg**:
  - **R1** (Shoulder - Body to Leg)
  - **R3** (Joint - Connected to R1)
- **Hind Left Leg**:
  - **L2** (Shoulder - Body to Leg)
  - **L4** (Joint - Connected to L2)
- **Hind Right Leg**:
  - **R2** (Shoulder - Body to Leg)
  - **R4** (Joint - Connected to R2)

## Channel Configuration (PCA9685)
*(Please verify these channel mappings on the HAT)*
- **Channel 0**: L1 (Front Left Shoulder)
- **Channel 1**: R1 (Front Right Shoulder)
- **Channel 2**: L2 (Hind Left Shoulder)
- **Channel 3**: R2 (Hind Right Shoulder)
- **Channel 4**: L3 (Front Left Joint/Knee)
- **Channel 5**: R3 (Front Right Joint/Knee)
- **Channel 6**: L4 (Hind Left Joint/Knee)
- **Channel 7**: R4 (Hind Right Joint/Knee)

## Safety & Constraints
- **Range**: 0-180 degrees.
- **Default Position**: 90 degrees (Center) for all joints.
- **Coordination**: Leg movements often require moving both the Shoulder and Joint servos together to maintain balance or step.
