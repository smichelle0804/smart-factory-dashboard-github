# Smart Factory Energy Efficiency & Anomaly Detection

## Overview

This project develops a **smart factory energy-efficiency monitoring and anomaly-detection system** using large-scale RTU power data. The analysis covers **33,696,013 observations from 13 continuously operating pieces of factory equipment**, with measurements collected at approximately **5-second intervals**.

The main objective was to identify equipment showing abnormal or inefficient electrical behavior, particularly through **power-factor anomalies**, and to build an interactive monitoring dashboard that allows users to inspect equipment conditions, anomaly events, and model results.

The project combines statistical anomaly detection, machine learning, time-series monitoring, and interactive visualization into an end-to-end **Smart Factory Energy Efficiency Cockpit**.

---

## Project Objectives

The project focused on three main tasks:

1. Screen all 13 pieces of equipment to identify machines with relatively abnormal energy behavior.
2. Apply multiple anomaly-detection methods to the selected equipment and compare their detection patterns.
3. Build an interactive dashboard for operational monitoring and anomaly investigation.

---

## Dataset

| Item | Description |
|---|---|
| Total observations | **33,696,013 rows** |
| Equipment | **13 machines** |
| Sampling interval | Approximately **5 seconds** |
| Main focus | Power-factor inefficiency and abnormal electrical behavior |
| Key variables | Power factor, active power, reactive power, voltage/current imbalance, and related electrical indicators |

Because the original dataset was extremely large, the analysis also used resampling and aggregation at different time intervals for efficient monitoring and visualization.

