import pandas as pd
import sqlite3
import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fraud_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract(file_path):
    logger.info(f"Starting data ingestion from {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Read {len(df)} records from input file")
    except FileNotFoundError:
        logger.error(f"Input file not found: {file_path}")
        return None, 0, 0
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        return None, 0, 0
    required_fields = ['transaction_id', 'user_id', 'timestamp', 'amount', 'country', 'merchant_category']
    valid_rows = []
    invalid_count = 0
    for idx, row in df.iterrows():
        if any(pd.isna(row[field]) or str(row[field]).strip() == '' for field in required_fields):
            invalid_count += 1
            logger.warning(f"Invalid record at index {idx}: Missing or empty field")
            continue
        try:
            if float(row['amount']) <= 0:
                invalid_count += 1
                logger.warning(f"Invalid record at index {idx}: Amount must be positive")
                continue
        except:
            invalid_count += 1
            logger.warning(f"Invalid record at index {idx}: Invalid amount format")
            continue
        try:
            pd.to_datetime(row['timestamp'])
            valid_rows.append(row)
        except:
            invalid_count += 1
            logger.warning(f"Invalid record at index {idx}: Invalid timestamp format")
    valid_df = pd.DataFrame(valid_rows)
    valid_df['timestamp'] = pd.to_datetime(valid_df['timestamp'])
    valid_df = valid_df.sort_values('timestamp').reset_index(drop=True)
    logger.info(f"Data ingestion completed. Valid: {len(valid_rows)}, Invalid: {invalid_count}")
    return valid_df, len(valid_rows), invalid_count

def transform(df):
    logger.info("Starting rule-based fraud detection...")
    flagged = []
    for idx, txn in df.iterrows():
        triggered_rules = []
        if txn['amount'] > 50000:
            triggered_rules.append({
                'rule': 'HIGH_AMOUNT',
                'description': f"Transaction amount {txn['amount']:.2f} exceeds 50,000 rupees threshold"
            })
        if txn['country'].upper() != 'INDIA':
            triggered_rules.append({
                'rule': 'FOREIGN_COUNTRY',
                'description': f"Transaction made in foreign country: {txn['country']}"
            })
        user_history = df[(df['user_id'] == txn['user_id']) & (df.index < idx)]
        if len(user_history) > 0:
            avg_amount = user_history['amount'].mean()
            std_amount = user_history['amount'].std()
            
            if (std_amount > 0 and txn['amount'] > (avg_amount + 3 * std_amount)) or (txn['amount'] > avg_amount * 5):
                triggered_rules.append({
                    'rule': 'UNUSUAL_SPENDING',
                    'description': f"Amount {txn['amount']:.2f} significantly exceeds user average {avg_amount:.2f}"
                })
        if triggered_rules:
            if txn['amount'] > 100000:
                amount_risk = 30
            elif txn['amount'] > 75000:
                amount_risk = 25
            elif txn['amount'] > 50000:
                amount_risk = 20
            elif txn['amount'] > 30000:
                amount_risk = 10
            else:
                amount_risk = min(txn['amount'] / 3000, 10)
            one_hour_ago = txn['timestamp'] - timedelta(hours=1)
            recent_txns = df[(df['user_id'] == txn['user_id']) & 
                            (df['timestamp'] > one_hour_ago) & 
                            (df['timestamp'] <= txn['timestamp'])]
            count = len(recent_txns)
            if count >= 5:
                frequency_risk = 25
            elif count >= 3:
                frequency_risk = 15
            elif count >= 2:
                frequency_risk = 10
            else:
                frequency_risk = 0
            user_prev = df[(df['user_id'] == txn['user_id']) & 
                          (df['timestamp'] < txn['timestamp'])].sort_values('timestamp')
            if len(user_prev) > 0 and user_prev.iloc[-1]['country'] != txn['country']:
                time_diff_hours = (txn['timestamp'] - user_prev.iloc[-1]['timestamp']).total_seconds() / 3600
                if time_diff_hours < 6:
                    location_risk = 25
                elif time_diff_hours < 24:
                    location_risk = 15
                else:
                    location_risk = 5
            else:
                location_risk = 0
            if txn['merchant_category'] in ['Jewelry', 'Electronics', 'Automobile']:
                category_risk = 15
            elif txn['merchant_category'] in ['Furniture', 'Shopping', 'Hotel']:
                category_risk = 10
            else:
                category_risk = 5
            risk_score = min(amount_risk + frequency_risk + location_risk + category_risk, 100.0)
            explanation = f"Transaction flagged with risk score of {risk_score:.2f}/100.\n"
            explanation += f"\nTriggered Rules ({len(triggered_rules)}):\n"
            for i, rule in enumerate(triggered_rules, 1):
                explanation += f"{i}. {rule['rule']}: {rule['description']}\n"
            explanation += f"\nRisk Factors:\n"
            explanation += f"- Amount: ₹{txn['amount']:,.2f}\n"
            explanation += f"- Country: {txn['country']}\n"
            explanation += f"- Merchant Category: {txn['merchant_category']}\n"
            explanation += f"- Time: {txn['timestamp']}"
            flagged.append({
                'transaction': txn,
                'triggered_rules': triggered_rules,
                'risk_score': risk_score,
                'explanation': explanation
            })
    logger.info(f"Flagged {len(flagged)} transactions based on rules")
    logger.info("Processing risk scores...")
    logger.info("Risk scoring completed")
    return flagged

def load(flagged_transactions, valid_count, invalid_count, db_name):
    logger.info("Initializing database...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Review_Required (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            amount REAL NOT NULL,
            country TEXT NOT NULL,
            merchant_category TEXT NOT NULL,
            triggered_rules TEXT NOT NULL,
            risk_score REAL NOT NULL,
            explanation TEXT NOT NULL,
            flagged_timestamp TEXT NOT NULL
        )
    ''')
    logger.info("Database initialized successfully")
    logger.info("Storing flagged transactions in database...")
    for item in flagged_transactions:
        txn = item['transaction']
        rules_json = json.dumps([r['rule'] for r in item['triggered_rules']])
        cursor.execute('''
            INSERT INTO Review_Required (
                transaction_id, user_id, timestamp, amount, country, 
                merchant_category, triggered_rules, risk_score, explanation, flagged_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            txn['transaction_id'], txn['user_id'], str(txn['timestamp']),
            txn['amount'], txn['country'], txn['merchant_category'],
            rules_json, item['risk_score'], item['explanation'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    conn.commit()
    conn.close()
    logger.info(f"Stored {len(flagged_transactions)} flagged transactions")
    logger.info("Generating daily fraud monitoring report...")
    risk_scores = [item['risk_score'] for item in flagged_transactions]
    high_risk = sum(1 for s in risk_scores if s >= 70)
    medium_risk = sum(1 for s in risk_scores if 40 <= s < 70)
    low_risk = sum(1 for s in risk_scores if s < 40)
    trigger_counts = {}
    for item in flagged_transactions:
        for rule in item['triggered_rules']:
            trigger_counts[rule['rule']] = trigger_counts.get(rule['rule'], 0) + 1
    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'total_transactions_processed': valid_count,
        'invalid_transactions': invalid_count,
        'flagged_transactions': len(flagged_transactions),
        'flagging_rate': (len(flagged_transactions) / valid_count * 100) if valid_count > 0 else 0,
        'high_risk_transactions': high_risk,
        'medium_risk_transactions': medium_risk,
        'low_risk_transactions': low_risk,
        'risk_score_distribution': {
            'min': min(risk_scores) if risk_scores else 0,
            'max': max(risk_scores) if risk_scores else 0,
            'average': sum(risk_scores) / len(risk_scores) if risk_scores else 0,
            'median': sorted(risk_scores)[len(risk_scores) // 2] if risk_scores else 0
        },
        'fraud_triggers_summary': trigger_counts
    }
    with open('daily_fraud_report.txt', 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DAILY FRAUD MONITORING REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Report Date: {report['report_date']}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("-" * 80 + "\n")
        f.write("TRANSACTION SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Transactions Processed: {report['total_transactions_processed']}\n")
        f.write(f"Invalid Transactions: {report['invalid_transactions']}\n")
        f.write(f"Flagged Transactions: {report['flagged_transactions']}\n")
        f.write(f"Flagging Rate: {report['flagging_rate']:.2f}%\n\n")
        f.write("-" * 80 + "\n")
        f.write("RISK LEVEL DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        f.write(f"High Risk (70-100): {report['high_risk_transactions']} transactions\n")
        f.write(f"Medium Risk (40-69): {report['medium_risk_transactions']} transactions\n")
        f.write(f"Low Risk (0-39): {report['low_risk_transactions']} transactions\n\n")
        if risk_scores:
            f.write("-" * 80 + "\n")
            f.write("RISK SCORE STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Minimum Score: {report['risk_score_distribution']['min']:.2f}\n")
            f.write(f"Maximum Score: {report['risk_score_distribution']['max']:.2f}\n")
            f.write(f"Average Score: {report['risk_score_distribution']['average']:.2f}\n")
            f.write(f"Median Score: {report['risk_score_distribution']['median']:.2f}\n\n")
        f.write("-" * 80 + "\n")
        f.write("MOST COMMON FRAUD TRIGGERS\n")
        f.write("-" * 80 + "\n")
        for trigger, count in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{trigger}: {count} occurrences\n")
        f.write("\n" + "=" * 80 + "\n")
    logger.info("Report saved to daily_fraud_report.txt")
    return report

def run_pipeline():
    """Execute the fraud detection pipeline"""
    logger.info("=" * 80)
    logger.info("STARTING CREDIT CARD FRAUD DETECTION PIPELINE")
    logger.info("=" * 80)
    df, valid_count, invalid_count = extract('transaction_logs.csv')
    if df is None:
        logger.error("Pipeline failed at data ingestion stage")
        return False
    total_count = valid_count + invalid_count
    if valid_count == 0:
        logger.error("No valid records to process")
        return False
    flagged_transactions = transform(df)
    report = load(flagged_transactions, valid_count, invalid_count, 'fraud_detection.db')
    logger.info("=" * 80)
    logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Transactions: {total_count}")
    print(f"Valid Transactions: {valid_count}")
    print(f"Invalid Transactions: {invalid_count}")
    print(f"Flagged Transactions: {len(flagged_transactions)}")
    print(f"Flagging Rate: {report['flagging_rate']:.2f}%")
    print(f"\nHigh Risk: {report['high_risk_transactions']}")
    print(f"Medium Risk: {report['medium_risk_transactions']}")
    print(f"Low Risk: {report['low_risk_transactions']}")
    print(f"\nReport saved to: daily_fraud_report.txt")
    print(f"Database: fraud_detection.db")
    print(f"Log file: fraud_detection.log")
    print("=" * 80 + "\n")
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if success:
        print("✓ Fraud detection pipeline completed successfully!")
    else:
        print("✗ Fraud detection pipeline failed. Check logs for details.")