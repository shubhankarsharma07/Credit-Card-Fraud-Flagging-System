# Credit Card Fraud Detection Pipeline

A robust, rule-based fraud detection system for real-time credit card transaction monitoring. This ETL pipeline processes transaction data, identifies suspicious activities using multiple fraud indicators, and generates comprehensive daily reports for risk management teams.

## 🎯 Overview

This fraud detection system implements a multi-layered approach to identify potentially fraudulent credit card transactions. It analyzes transaction patterns, spending behaviors, and geographical indicators to flag high-risk activities requiring manual review.

### Key Capabilities

- **Real-time Processing**: Handles transaction streams with efficient data validation
- **Multi-factor Risk Assessment**: Combines amount, frequency, location, and category-based risk scoring
- **Rule-based Detection**: Implements industry-standard fraud indicators
- **Automated Reporting**: Generates daily monitoring reports with comprehensive statistics
- **Database Integration**: Stores flagged transactions in MySQL for review workflows
- **Comprehensive Logging**: Detailed execution logs for audit and debugging

## 📊 Features

### Fraud Detection Rules

The pipeline implements the following fraud detection mechanisms:

1. **HIGH_AMOUNT** - Flags transactions exceeding ₹50,000
2. **FOREIGN_COUNTRY** - Detects transactions made outside India
3. **UNUSUAL_SPENDING** - Identifies spending patterns that deviate significantly from user history (3σ threshold or 5x average)

### Risk Scoring System

Each flagged transaction receives a risk score (0-100) based on:

- **Amount Risk** (0-30 points): Weighted by transaction value
- **Frequency Risk** (0-25 points): Number of transactions within 1-hour window
- **Location Risk** (0-25 points): Rapid geographical changes
- **Category Risk** (5-15 points): High-risk merchant categories (Jewelry, Electronics, Automobiles)

Risk classification:
- **High Risk**: 70-100 (Requires immediate review)
- **Medium Risk**: 40-69 (Priority review recommended)
- **Low Risk**: 0-39 (Standard review queue)

## 🏗️ System Architecture

```
┌─────────────────┐
│  CSV Input      │
│  (Transaction   │
│   Logs)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EXTRACT        │
│  - Data ingestion│
│  - Validation   │
│  - Cleaning     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TRANSFORM      │
│  - Rule engine  │
│  - Risk scoring │
│  - Pattern      │
│    detection    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LOAD           │
│  - MySQL insert │
│  - Report gen   │
│  - Logging      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Outputs:                       │
│  • Review_Required table        │
│  • daily_fraud_report.txt       │
│  • fraud_detection.log          │
└─────────────────────────────────┘
```

## 🔧 Prerequisites

- Python 3.7+
- MySQL Server 5.7+
- Required Python packages:
  - pandas
  - mysql-connector-python
  - logging (standard library)

## 📥 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fraud-detection-pipeline.git
cd fraud-detection-pipeline
```

2. **Install dependencies**
```bash
pip install pandas mysql-connector-python
```

3. **Configure database connection**

Create a `config.py` file in the project root:

```python
# config.py
DB_HOST = "localhost"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
```

4. **Set up MySQL database**

The pipeline will automatically create the database and table structure on first run. Ensure your MySQL user has CREATE and INSERT privileges.

## 🚀 Usage

### Basic Execution

```bash
python fraud_detection_pipeline.py
```

### Input Data Format

The pipeline expects a CSV file named `transaction_logs.csv` with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | string | Unique transaction identifier |
| user_id | string | User account identifier |
| timestamp | datetime | Transaction timestamp (ISO format) |
| amount | float | Transaction amount in rupees |
| country | string | Country of transaction |
| merchant_category | string | Merchant business category |

**Example CSV:**
```csv
transaction_id,user_id,timestamp,amount,country,merchant_category
TXN001,USR123,2026-04-23 10:30:00,45000,India,Electronics
TXN002,USR456,2026-04-23 11:15:00,85000,USA,Jewelry
```

### Output Files

1. **daily_fraud_report.txt** - Comprehensive daily summary
   - Transaction statistics
   - Risk distribution
   - Most common fraud triggers
   - Score analytics

2. **fraud_detection.log** - Detailed execution log
   - Processing steps
   - Validation warnings
   - Error messages
   - Performance metrics

## 💾 Database Schema

### Review_Required Table

```sql
CREATE TABLE Review_Required (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    country VARCHAR(50) NOT NULL,
    merchant_category VARCHAR(50) NOT NULL,
    triggered_rules TEXT NOT NULL,
    risk_score FLOAT NOT NULL,
    explanation TEXT NOT NULL,
    flagged_timestamp DATETIME NOT NULL
);
```

## 📈 Sample Output

### Daily Report Summary
```
Total Transactions Processed: 100
Invalid Transactions: 0
Flagged Transactions: 43
Flagging Rate: 43.00%

RISK LEVEL DISTRIBUTION
High Risk (70-100): 0 transactions
Medium Risk (40-69): 17 transactions
Low Risk (0-39): 26 transactions

MOST COMMON FRAUD TRIGGERS
HIGH_AMOUNT: 22 occurrences
FOREIGN_COUNTRY: 21 occurrences
UNUSUAL_SPENDING: 12 occurrences
```

## 🗂️ Project Structure

```
fraud-detection-pipeline/
│
├── fraud_detection_pipeline.py    # Main ETL pipeline
├── config.py                       # Database configuration
├── transaction_logs.csv            # Input data (not in repo)
├── daily_fraud_report.txt          # Generated report
├── fraud_detection.log             # Execution log
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

## 🔄 Pipeline Workflow

1. **Data Extraction**
   - Reads CSV transaction data
   - Validates required fields
   - Filters invalid records
   - Sorts by timestamp

2. **Transformation**
   - Applies fraud detection rules
   - Calculates user spending patterns
   - Computes multi-factor risk scores
   - Generates detailed explanations

3. **Loading**
   - Initializes MySQL database
   - Stores flagged transactions
   - Generates daily report
   - Updates execution logs

## 🛡️ Data Validation

The pipeline performs comprehensive validation:

- ✅ Required field presence check
- ✅ Positive amount validation
- ✅ Timestamp format verification
- ✅ Empty/null value detection
- ✅ Data type consistency

Invalid records are logged with detailed error messages and excluded from processing.

## 🎯 Use Cases

- **Financial Institutions**: Monitor credit card transactions for fraud
- **E-commerce Platforms**: Detect suspicious purchase patterns
- **Payment Processors**: Flag high-risk transactions in real-time
- **Risk Management**: Generate compliance reports for audit
- **Data Analytics**: Historical fraud pattern analysis

## 🚧 Future Enhancements

- [ ] Machine learning model integration
- [ ] Real-time streaming processing (Apache Kafka)
- [ ] Advanced behavioral analytics
- [ ] Geographic velocity checks
- [ ] Email/SMS alerting system
- [ ] Web dashboard for monitoring
- [ ] API endpoints for integration
- [ ] Docker containerization
- [ ] Unit test coverage
- [ ] CI/CD pipeline setup

## 📝 Configuration Options

### Modifying Detection Rules

Edit the `transform()` function in `fraud_detection_pipeline.py`:

```python
# Adjust high amount threshold
if txn['amount'] > 50000:  # Change threshold value

# Modify country restrictions
if txn['country'].upper() != 'INDIA':  # Add multiple countries

# Tune unusual spending sensitivity
if txn['amount'] > (avg_amount + 3 * std_amount):  # Adjust multiplier
```

### Risk Score Weights

Adjust weights in the risk calculation section:

```python
# Maximum risk scores per factor
amount_risk = 30      # 0-30 points
frequency_risk = 25   # 0-25 points
location_risk = 25    # 0-25 points
category_risk = 15    # 0-15 points
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

**Shubhankar Sharma**

## 🙏 Acknowledgments

- Inspired by industry-standard fraud detection practices
- Built with Python data processing best practices
- Designed for scalability and maintainability

**Note**: This is a rule-based detection system intended for educational and development purposes. Production deployments should include additional security measures, machine learning models, and compliance with financial regulations (PCI DSS, GDPR, etc.).
