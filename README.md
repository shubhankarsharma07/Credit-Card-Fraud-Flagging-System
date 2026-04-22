# Credit Card Fraud Detection Pipeline

A production-ready ETL pipeline built in Python that processes credit card transactions, identifies fraudulent activity using rule-based detection, and generates automated risk assessment reports.

## Overview

This project implements an end-to-end fraud detection system that simulates real-world financial security operations. The pipeline processes transaction data, validates records, applies intelligent fraud detection rules, calculates multi-factor risk scores, and stores flagged transactions for manual review while maintaining comprehensive audit logs.

## Features

### Data Processing & Validation
The pipeline ingests transaction data from CSV files and performs rigorous validation checks. Each transaction must contain all required fields including transaction ID, user ID, timestamp, amount, country, and merchant category. The system validates that amounts are positive numerical values and timestamps are properly formatted. Invalid records are logged with specific error messages and excluded from further processing, ensuring data quality throughout the pipeline.

### Rule-Based Fraud Detection
The system implements three core detection rules that identify suspicious patterns. The high-amount rule flags transactions exceeding fifty thousand rupees, which is a common indicator of potential fraud. The foreign-country rule identifies transactions occurring outside India, helping detect unauthorized international purchases. The unusual-spending rule performs statistical analysis on each user's transaction history, flagging amounts that exceed the user's average by more than three standard deviations or by a factor of five, catching sudden spending spikes that may indicate account compromise.

### Multi-Factor Risk Scoring
Each flagged transaction receives a comprehensive risk score from zero to one hundred based on four weighted factors. Amount risk contributes up to thirty points and increases progressively with transaction value. Frequency risk adds up to twenty-five points based on the number of transactions in the previous hour, detecting rapid-fire fraudulent activity. Location risk contributes up to twenty-five points when users make transactions in different countries within a short timeframe, identifying impossible travel patterns. Category risk adds five to fifteen points based on merchant type, with high-value categories like jewelry, electronics, and automobiles receiving higher weights.

### Automated Database Storage
All flagged transactions are stored in a SQLite database in the Review_Required table. Each record includes the complete transaction details, a JSON array of triggered rules, the calculated risk score, a detailed explanation of why the transaction was flagged, and a timestamp of when it was flagged. This creates a permanent audit trail for compliance and investigation purposes.

### Daily Monitoring Reports
The pipeline automatically generates comprehensive text-based reports that provide a complete overview of fraud detection activity. These reports include transaction summaries showing total processed, invalid, and flagged counts along with the flagging rate. Risk level distributions categorize flagged transactions into high risk (seventy to one hundred), medium risk (forty to sixty-nine), and low risk (zero to thirty-nine) categories. Statistical analysis provides minimum, maximum, average, and median risk scores. Trigger frequency analysis ranks the most common fraud rules by occurrence count.

### Structured Logging
Every stage of the pipeline generates detailed logs that enable monitoring and troubleshooting. Logs capture data ingestion progress, validation errors with specific row numbers and reasons, fraud detection results, database operations, and report generation status. All logs are written to both a file and console with timestamps and severity levels.

## Technical Architecture

### Pipeline Flow
The system follows a classic ETL (Extract, Transform, Load) architecture with three distinct phases. The Extract phase reads transaction data from CSV files, validates each record against required fields and data types, filters out invalid records with detailed logging, sorts transactions by timestamp for chronological processing, and returns both valid and invalid counts. The Transform phase applies fraud detection rules to each transaction, builds user transaction history for behavioral analysis, calculates statistical baselines for unusual spending detection, computes multi-factor risk scores with component breakdown, and generates detailed explanations for each flagged transaction. The Load phase initializes the SQLite database and creates necessary tables, stores all flagged transactions with complete metadata, generates comprehensive daily monitoring reports, and maintains execution logs for audit purposes.

### Risk Scoring Algorithm
The risk scoring system uses a sophisticated multi-component approach. Amount risk is calculated on a progressive scale where transactions over one hundred thousand rupees receive thirty points, those over seventy-five thousand receive twenty-five points, those over fifty thousand receive twenty points, those over thirty thousand receive ten points, and smaller amounts receive proportional points up to ten based on a formula dividing amount by three thousand. Frequency risk examines transactions in the previous hour where five or more transactions receive twenty-five points, three to four transactions receive fifteen points, two transactions receive ten points, and single transactions receive zero points. Location risk detects rapid country changes where different countries within six hours receive twenty-five points, within twenty-four hours receive fifteen points, and beyond twenty-four hours receive five points. Category risk assigns fifteen points to high-risk categories like jewelry, electronics, and automobiles, ten points to medium-risk categories like furniture, shopping, and hotels, and five points to all other categories. The final score is capped at one hundred to maintain consistency.

## Tech Stack

**Programming Language:** Python 3.x

**Data Processing:** Pandas for efficient data manipulation and statistical analysis

**Database:** SQLite for lightweight, serverless transaction storage

**Logging:** Python logging module with file and console handlers

**Date/Time:** datetime module for timestamp processing and time-based fraud detection

## Installation

Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/credit-card-fraud-detection.git
cd credit-card-fraud-detection
```

Install the required dependencies:
```bash
pip install pandas
```

The project uses SQLite which comes built-in with Python, so no additional database installation is required.

## Usage

### Running the Pipeline

Execute the fraud detection pipeline using the following command:
```bash
python fraud_detection_pipeline.py
```

### Input Requirements

The pipeline expects a CSV file named `transaction_logs.csv` in the same directory with the following columns:

- **transaction_id**: Unique identifier for each transaction
- **user_id**: Unique identifier for the cardholder
- **timestamp**: Transaction date and time in ISO format (YYYY-MM-DD HH:MM:SS)
- **amount**: Transaction amount in rupees (must be positive)
- **country**: Country where transaction occurred
- **merchant_category**: Category of the merchant (e.g., Grocery, Electronics, Hotel)

### Output Files

The pipeline generates three output files after each execution:

**fraud_detection.db**: SQLite database containing the Review_Required table with all flagged transactions, their risk scores, triggered rules, and detailed explanations.

**daily_fraud_report.txt**: Human-readable text report with transaction summary statistics, risk level distribution across high/medium/low categories, risk score statistics including min/max/average/median, and most common fraud triggers ranked by occurrence.

**fraud_detection.log**: Detailed execution logs capturing data ingestion progress, validation errors with row numbers, fraud detection results, database operations, and report generation status.

## Project Structure

```
credit-card-fraud-detection/
│
├── fraud_detection_pipeline.py    # Main pipeline script with ETL logic
├── transaction_logs.csv            # Input transaction data (sample or real)
├── fraud_detection.db              # Output database (generated)
├── daily_fraud_report.txt          # Output monitoring report (generated)
├── fraud_detection.log             # Execution logs (generated)
├── Credit_Card_Fraud_Detection_Report.docx  # Project documentation
└── README.md                       # This file
```

## Sample Results

In a typical execution processing one hundred transactions, the pipeline demonstrates its effectiveness with the following results:

**Transaction Processing:** Out of one hundred transactions processed, zero were invalid due to data quality issues, and forty-three were flagged as potentially fraudulent, resulting in a flagging rate of forty-three percent.

**Risk Distribution:** The flagged transactions were distributed across risk levels with zero high-risk cases (seventy to one hundred score), seventeen medium-risk cases (forty to sixty-nine score), and twenty-six low-risk cases (zero to thirty-nine score).

**Statistical Analysis:** Risk scores ranged from a minimum of 7.97 to a maximum of 65.00, with an average score of 32.24 and a median score of 35.00.

**Fraud Triggers:** The most common fraud triggers were HIGH_AMOUNT with twenty-two occurrences, FOREIGN_COUNTRY with twenty-one occurrences, and UNUSUAL_SPENDING with twelve occurrences.

These results demonstrate the pipeline's ability to identify various fraud patterns and prioritize them based on risk severity, enabling efficient manual review processes.

## Key Learning Outcomes

This project demonstrates several critical data engineering and fraud analytics concepts:

**ETL Pipeline Design:** Implementing a complete Extract-Transform-Load workflow with proper error handling, data validation, and logging at each stage.

**Data Quality Management:** Validating input data, handling missing values, enforcing data type constraints, and maintaining audit trails of invalid records.

**Statistical Analysis:** Computing user behavioral baselines, detecting anomalies using standard deviation, and building adaptive fraud detection rules.

**Risk Modeling:** Designing multi-factor risk scoring systems that combine different risk signals into a unified score with proper weighting and normalization.

**Database Operations:** Creating relational schemas, inserting transaction records, maintaining referential integrity, and building queryable fraud detection systems.

**Logging Best Practices:** Implementing structured logging with appropriate severity levels, multiple output handlers, and detailed context for debugging.

## Future Enhancements

Several improvements could extend this project's capabilities:

**Machine Learning Integration:** Replace or augment rule-based detection with supervised learning models trained on historical fraud data, enabling the system to learn complex patterns automatically.

**Real-Time Processing:** Implement streaming data processing using frameworks like Apache Kafka or Apache Flink to analyze transactions as they occur rather than in batch mode.

**Advanced Analytics Dashboard:** Build interactive visualizations using tools like Plotly, Dash, or Streamlit to display real-time fraud statistics, trend analysis, and risk score distributions.

**Alert System:** Implement automated notifications via email or SMS when high-risk transactions are detected, enabling immediate investigation.

**Geographic Analysis:** Add geolocation validation to detect impossible travel patterns based on actual geographic distances and time differences.

**Merchant Risk Profiles:** Build dynamic merchant risk scores based on historical fraud rates, enabling more accurate category-based risk assessment.

**API Integration:** Expose the fraud detection engine as a REST API for integration with transaction processing systems and third-party applications.

## Contributing

Contributions are welcome! If you would like to improve this project, please follow these steps:

Fork the repository to your own GitHub account. Create a new branch for your feature or bug fix using a descriptive name. Make your changes with clear, commented code. Test your changes thoroughly to ensure they work as expected. Submit a pull request with a detailed description of your modifications.

## License

This project is open source and available under the MIT License. You are free to use, modify, and distribute this code for personal or commercial purposes.

## Contact

For questions, suggestions, or collaboration opportunities, please reach out:

**GitHub:** https://github.com/shubhankarsharma07

**LinkedIn:** https://www.linkedin.com/in/shubhankarsharma07/

**Email:** shubhankarsharma0099@gmail.com

---

**Note:** This project is designed for educational and demonstration purposes. In production environments, fraud detection systems require additional security measures, regulatory compliance, and integration with external fraud databases and verification services.
