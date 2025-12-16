# Temperature-Dependent Performance of Prompting Strategies in Extended Reasoning Language Models

## Overview
This repository contains the code and resources related to the paper "Temperature-Dependent Performance of Prompting Strategies in Extended Reasoning Language Models" by Mousa Salah. The study systematically investigates the interplay between temperature sampling and prompting strategies (Zero-Shot vs. Chain-of-Thought) in large language models with extended reasoning capabilities.

## Abstract
Extended reasoning capabilities in large language models enable test-time computation for complex problem-solving, yet optimal configuration of temperature and prompting strategy remains underexplored. We systematically evaluate chain-of-thought versus zero-shot prompting across four temperature settings (0.0, 0.4, 0.7, 1.0) using Grok-4.1 with extended reasoning on 39 mathematical problems from AMO-Bench, a challenging International Mathematical Olympiad-level benchmark. We find that zero-shot prompting achieves peak performance at moderate temperatures (59% accuracy at T=0.4-0.7), while chain-of-thought performs best at temperature extremes. Most notably, the benefit of extended reasoning increases from 6× at T=0.0 to 14.3× at T=1.0. These results suggest temperature should be optimized jointly with prompting strategy, challenging the common practice of using T=0 for reasoning tasks.

## Key Findings
1.  **Strategy-dependent temperature effects:** Zero-shot prompting achieves peak performance at moderate temperatures (59.0% accuracy at T=0.4 and T=0.7), while chain-of-thought performs best at temperature extremes (53.8% at T=0.0, 59.0% at T=1.0). This temperature-dependent reversal challenges the notion that one prompting strategy uniformly outperforms another.
2.  **Reasoning amplification at high temperature:** The benefit of extended reasoning increases dramatically from 6.0× at T=0.0 to 14.3× at T=1.0. This suggests extended reasoning mechanisms can productively harness temperature-induced exploration rather than being degraded by it.
3.  **Practical configuration guidelines:** For extended reasoning systems on mathematical tasks, zero-shot prompting with moderate temperature (0.4-0.7) achieves optimal performance, challenging the common practice of using T=0 for reasoning tasks.

## Methodology
### Dataset
We evaluate on AMO-Bench, a challenging benchmark containing 50 International Mathematical Olympiad-level problems. For this study, 39 problems compatible with parser-based automated evaluation were selected, spanning diverse mathematical domains.

### Model and Configuration
We use Grok-4.1, accessed through the OpenRouter API, which provides explicit control over extended reasoning. Evaluations were conducted across four temperature values: T=0.0 (deterministic), T=0.4, T=0.7 (moderate exploration), and T=1.0 (high diversity).

### Prompting Strategies
Two fundamental prompting approaches were evaluated:
*   **Zero-Shot Prompt:** Only the problem statement and answer format specification.
*   **Chain-of-Thought Prompt:** Adds the minimal instruction "Solve this step by step." before the problem statement and answer format.

### Experimental Design
A complete factorial evaluation was implemented with 2 Prompt Types (Zero-shot vs. CoT) × 2 Reasoning Modes (Disabled vs. Enabled) × 4 Temperatures (0.0, 0.4, 0.7, 1.0) across the 39 AMO-Bench problems, totaling 624 evaluations.

### Answer Extraction and Grading
An automated parsing pipeline followed by a rigorous manual verification process was used to grade all 624 model predictions. Manual review was crucial for ensuring accuracy due to the complexity of IMO-level mathematics.

## Results

### Overall Accuracy by Temperature
| Temperature | Correct/Total | Accuracy |
|-------------|---------------|----------|
| 0.0         | 49/156        | 31.4%    |
| 0.4         | 50/156        | 32.1%    |
| 0.7         | 50/156        | 32.1%    |
| 1.0         | 46/156        | 29.5%    |

### Reasoning Mode Impact by Temperature
| Temp | No Reasoning | With Reasoning | Multiplier |
|------|--------------|----------------|------------|
| 0.0  | 9.0% (7/78)  | 53.8% (42/78)  | 6.0×       |
| 0.4  | 7.7% (6/78)  | 56.4% (44/78)  | 7.3×       |
| 0.7  | 9.0% (7/78)  | 55.1% (43/78)  | 6.1×       |
| 1.0  | 3.8% (3/78)  | 55.1% (43/78)  | 14.3×      |

### Performance with Extended Reasoning Enabled
| Temperature | Zero-Shot | Chain-of-Thought |
|-------------|-----------|------------------|
| 0.0         | 53.8%     | 53.8%            |
| 0.4         | 59.0%     | 53.8%            |
| 0.7         | 59.0%     | 51.3%            |
| 1.0         | 51.3%     | 59.0%            |

## Plots
Visualizations of the key results are available in the `plots/` directory:
*   `plots/figure1.png`: Line plot showing accuracy vs temperature for the 4 conditions.
*   `plots/figure2.png`: Bar chart of reasoning multipliers by temperature, with T=1.0 highlighted.

## Repository Structure
```
.
├── LICENSE               # Project license (MIT License)
├── README.md             # This README file
├── requirements.txt      # Python dependencies
├── utils.py              # Utility scripts (e.g., for data processing)
├── experiment/
│   ├── 0.0 exp/          # Experiment results and scripts for T=0.0
│   ├── 0.4 exp/          # Experiment results and scripts for T=0.4
│   ├── 0.7 exp/          # Experiment results and scripts for T=0.7
│   └── 1.0 exp/          # Experiment results and scripts for T=1.0
├── plots/
│   ├── figure1.pdf       # Plot: Accuracy vs temperature (PDF)
│   ├── figure1.png       # Plot: Accuracy vs temperature (PNG)
│   ├── figure2.pdf       # Plot: Reasoning multipliers (PDF)
│   └── figure2.png       # Plot: Reasoning multipliers (PNG)
└── results/
    └── merged.json       # Merged manually checked results
```

## Installation
To replicate the environment or run related scripts, install the required packages:
```bash
pip install -r requirements.txt
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries, please contact Mousa Salah at hello@mousasalah.com.

---
**Short Title:** Temperature-Dependent Performance in Extended Reasoning LLMs
**Keywords:** LLMs, Temperature Sampling, Chain-of-Thought Prompting, Zero Shot Prompting, Extended Reasoning, Prompt Engineering, Mathematical Reasoning.
