# 스마트팩토리 전력 이상 탐지 대시보드

**green그린그림 · 제5회 BDAI 채용 연계 데이터 분석 공모전**  
한국어 (English Below)

[대시보드 열기](https://appapppy-npeaynqsm3spwhkgjxzpxq.streamlit.app/)

13종 설비의 전력 데이터에서 **어느 설비와 시점을 먼저 확인할지** 보여주는 Streamlit 관제 프로토타입입니다. 설비별 이상률과 IQR·EWMA·Isolation Forest의 탐지 결과를 한 화면에서 비교하고, 역률 추이와 반복 이벤트를 확인할 수 있습니다.

## 사용 방법

1. **통합 관제**에서 분석 기간과 표시할 설비를 선택합니다.
2. **설비별 비효율 탐지 순위**에서 우선 확인할 설비를 찾습니다. 이 데이터에서는 예비건조기(15번)가 집중 관리 후보입니다.
3. 그래프나 시점 선택 메뉴에서 역률 변화를 살펴보고, 같은 시점에 **IQR·EWMA·Isolation Forest 중 어떤 방법이 이상으로 판정했는지** 확인합니다.
4. 시간당 EWMA 이벤트와 최근 이벤트 로그를 보고 반복 발생 구간을 우선 점검 대상으로 정합니다.

대시보드는 이상을 **현장 점검 후보**로 제시합니다. 이상 판정만으로 고장 원인이나 에너지 손실을 확정하지 않습니다.

## 표시 지표의 기준

대시보드에 사용한 자료는 2024-12-01부터 2025-04-30까지 수집된 RTU 전력 데이터입니다. 원자료는 13종 설비, 33,696,013건, 19개 변수이며, 집중 분석 설비는 예비건조기(15번)입니다.

| 대시보드 지표 | 분석 결과 | 집계 기준 |
| --- | ---: | --- |
| 전체 설비 IF 이상률 1위 | **1.62%** | 예비건조기의 5분 집계 자료 |
| IQR 탐지 | **20,317건** | 예비건조기의 5초 관측치 |
| EWMA 탐지 | **26,244건** | 예비건조기의 5초 관측치 |
| EWMA 이벤트 | **25,991개** | 연속된 탐지 관측치를 이벤트로 묶은 결과 |
| 정밀 IF 탐지 | **20,736건** | 예비건조기의 5초 관측치 |
| 고빈도 구간 | **369개** | 시간당 EWMA 이벤트 **10.93건 초과** |

**IF**는 Isolation Forest를 뜻합니다. 1.62%는 전체 설비를 비교하는 **5분 집계 자료**의 이상률이고, 나머지 탐지 건수는 예비건조기의 **5초 원자료**를 기준으로 합니다. EWMA의 **26,244건**은 이상으로 판정한 관측치 수이며, **25,991개**는 이를 이벤트 단위로 묶은 수입니다. 시간당 10.93건은 점검 순위를 위한 초기 운영 기준입니다.

## 적용 범위

이 저장소의 대시보드는 **제공된 과거 RTU 데이터와 분석 결과를 조회하는 프로토타입**입니다. 현장 RTU 스트림과 자동 연결된 상용 실시간 관제 시스템은 아닙니다. 정답 라벨과 현장 점검 기록이 없어 화면의 이상 판정을 실제 고장이나 확인된 절감 효과로 해석할 수 없습니다.

Streamlit Community Cloud에서 앱이 휴면 상태라면 접속자가 화면의 **“Yes, get this app back up!”** 버튼으로 다시 열 수 있습니다.

# Smart Factory Power Anomaly Monitoring Dashboard




**Team green그린그림 · 5th BDAI Data Analytics Competition**  
English 

[Open dashboard](https://appapppy-npeaynqsm3spwhkgjxzpxq.streamlit.app/)

This Streamlit prototype helps users identify **which equipment and time periods to inspect first** in power data from 13 equipment types. It brings equipment-level anomaly rates, IQR/EWMA/Isolation Forest decisions, power-factor trends, and recurring events into one monitoring view.

## How to use it

1. Select a date range and equipment in **Integrated monitoring**.
2. Review the **equipment anomaly ranking** to find a candidate for inspection. In this dataset, the preliminary dryer (equipment 15) is the priority candidate.
3. Inspect the power-factor trend and select a timestamp to see **which of IQR, EWMA, and Isolation Forest flagged it**.
4. Use hourly EWMA counts and the recent event log to prioritize recurring periods for field inspection.

The dashboard presents anomalies as **candidates for field inspection**. A detection alone does not establish the physical cause of a fault or confirm an energy loss.

## Metric definitions

The dashboard uses RTU power data collected from December 1, 2024 to April 30, 2025. The source data contains 33,696,013 records, 19 variables, and 13 equipment types. Detailed monitoring focuses on the preliminary dryer (equipment 15).

| Dashboard metric | Result | Unit and scope |
| --- | ---: | --- |
| Highest equipment IF anomaly rate | **1.62%** | Preliminary dryer; five-minute aggregates |
| IQR detections | **20,317** | Five-second observations of the preliminary dryer |
| EWMA detections | **26,244** | Five-second observations of the preliminary dryer |
| EWMA events | **25,991** | Consecutive flagged observations grouped into events |
| Detailed IF detections | **20,736** | Five-second observations of the preliminary dryer |
| High-frequency periods | **369** | Above **10.93 EWMA events per hour** |

**IF** means Isolation Forest. The **1.62%** screening rate uses **five-minute aggregates across equipment**; the detailed detection counts use **five-second observations** from the selected equipment. **26,244** counts EWMA-flagged observations, while **25,991** counts grouped events. The 10.93-events-per-hour threshold is an initial rule for inspection priority.

## Scope

This dashboard is a **prototype for reviewing supplied historical RTU data and analysis results**. It is not a production system connected to a live RTU stream. Without ground-truth fault labels and field inspection records, its alerts cannot establish an actual failure or measured savings.

If the app is asleep on Streamlit Community Cloud, a visitor can click **“Yes, get this app back up!”** to reopen it.
