"""
Train and update phishing detection ML model with legitimate college & placement email samples.
"""

import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "spam.csv"
MODEL_PATH = PROJECT_ROOT / "phishing_model.pkl"

# Diverse samples of legitimate college, placement, academic, and university communications
COLLEGE_PLACEMENT_SAMPLES = [
    # Placement cell notices
    "Subject: Campus Placement Drive 2026 - Sri Sairam College of Engineering | Dear Students, Infosys recruitment drive registration is now open. Eligible students must submit their resumes and register on the training portal before 5 PM tomorrow.",
    "Subject: Placement Registration - Mandatory for all Final Year Students | Placement Cell Sairam: Please find the Google Form link to register for the upcoming Zoho campus drive. Ensure your CGPA and marks are accurately updated.",
    "Subject: TCS National Qualifier Test (NQT) - Registration Instructions | Sairam CE Placement Department: All registered 7th-semester candidates are requested to verify their hall tickets and reporting time for the upcoming campus recruitment drive.",
    "Subject: Cognizant Campus Recruitment Drive - Interview Schedule | Dear Final Year Candidates, The shortlist for round 2 technical interviews has been announced by the placement cell. Check the attached list for your interview slot.",
    "Subject: Pre-Placement Talk by Wipro Technologies | Sairam Institutions: Join the online pre-placement presentation tomorrow at 10:00 AM on Microsoft Teams. Attendance is compulsory for all eligible branches.",
    "Subject: Accenture Placement Drive Shortlisted Candidates List | Dear Students, Congratulations to the candidates shortlisted for the virtual assessment round. Please review the company instructions and prepare your resume.",
    "Subject: Internship Opportunity at Zoho Corp - Placement Cell Announcement | Sairam CE: Third-year students are invited to apply for the summer development internship. Fill in your details via the placement portal.",
    "Subject: Resume Review & Aptitude Training Session | Department of Training and Placement, Sri Sairam College of Engineering: Mock interview sessions and soft-skills workshop will commence from Monday in Seminar Hall 2.",
    "Subject: Placement Drive: Amazon Campus Hiring for Software Development Engineer | Placement Office: Eligible CSE and ECE students can submit their applications for the preliminary coding assessment.",
    "Subject: Important Update: Capgemini Campus Drive Assessment Link | Dear Students, The online assessment link from Capgemini has been sent to your registered college email. Complete the test before the deadline.",

    # College administration & academic notices
    "Subject: Semester End Examination Timetable Announced - Anna University | Sri Sairam College of Engineering Examination Cell: The official semester examination schedule has been published on the college notice board and website.",
    "Subject: Internal Assessment Test (IAT-1) Schedule | Academic Dean Sairam CE: All department students are informed that the first internal assessment will be held starting next week. Syllabus and schedule are attached.",
    "Subject: Project Review Schedule for Final Year Engineering Students | Department HOD: Phase-1 project demonstration and presentation will take place on Friday in the department conference hall.",
    "Subject: College Symposium & Technical Paper Presentation - Sairam CE | National level technical symposium invitations. Register your teams for paper presentation, coding hackathon, and robotics events.",
    "Subject: Sairam Institutions Annual Sports Day & Cultural Fest | All students and faculty are invited to participate in the upcoming sports meet and inter-college cultural competitions.",
    "Subject: NPTEL / SWAYAM Online Certification Course Registration | Academic Coordinator: Students enrolled in NPTEL credit courses are requested to submit their assignment progress to department mentors.",
    "Subject: Library Book Return and Digital Repository Access | Sri Sairam Central Library: Access IEEE Xplore, ScienceDirect, and digital thesis repository through college intranet portal.",
    "Subject: Fee Payment Reminder for Academic Year 2026 | Sairam College of Engineering Accounts Department: Students can make online tuition and bus fee payments via the secure net banking portal.",
    "Subject: Guest Lecture on Artificial Intelligence and Cloud Computing | IEEE Student Branch Sairam CE: Expert session by industry veterans on emerging tech and cyber security trends.",
    "Subject: Placement Cell Circular: Sri Sairam College of Engineering [placement@sairamce.edu.in] | Campus interview dress code, etiquette, and resume checklist for incoming recruitment partners.",
    "Subject: Hall Ticket Distribution for University Practical Exams | Exam Section Sairam: Collect your signed hall tickets from respective department mentors between 9 AM and 4 PM.",
    "Subject: Industrial Visit Permission & Consent Form | Mechanical and Civil Engineering Departments: Industrial field visit to manufacturing facility approved for next Thursday.",
    "Subject: Hackathon 2026 - Innovation Cell Sairam | Register for the 24-hour hackathon on Smart City and AI Solutions with cash prizes and incubation support.",
    "Subject: Sairam Alumni Meet 2026 - Registration Open | Join fellow alumni and mentors for the annual alumni gathering and networking dinner on campus.",
    "Subject: Placement Drive Results - Hexaware Technologies | Sairam CE Placement: We are proud to announce 45 students selected in the on-campus recruitment drive. Offer letters will be dispatched shortly."
]

# Additional clear phishing samples to maintain high sensitivity against actual threats
EXTRA_PHISHING_SAMPLES = [
    "Subject: URGENT: Your Google Workspace account will be terminated in 24 hours | Click here to verify password and confirm credentials immediately or lose all email data.",
    "Subject: Security Alert: Unauthorized login attempt from Russia | Your Microsoft 365 account has been locked. Verify identity now at http://fake-login-security.ru/verify",
    "Subject: Payroll Department: Direct deposit payment failed | Update your bank account details and social security number immediately to avoid withholding salary: http://phish-payroll.com",
    "Subject: Official Notice: IRS Tax Refund of $3,450.00 Approved | Submit your debit card number, CVV, and PIN to claim your refund within 48 hours.",
    "Subject: PayPal: Suspicious transaction of $849.99 detected | If you did not make this purchase, click immediately to cancel payment and reset password.",
    "Subject: IT Helpdesk: Immediate password reset required | All student and faculty accounts must verify credentials on http://sairamce-portal-login.xyz/login.php",
    "Subject: Lottery Winner: You have won 1,000,000 GBP in Microsoft annual sweepstakes | Send your passport copy and wire transfer fee to claims agent.",
    "Subject: DHL Express: Delivery failure for your parcel | Download and run tracking_receipt.exe to reschedule parcel shipment.",
    "Subject: Bitcoin Investment: Double your crypto in 24 hours guaranteed | Send 0.1 BTC to receive 0.5 BTC instantly from Binance smart contract."
]


def train():
    print("[1/5] Loading training data from", DATASET_PATH)
    try:
        df = pd.read_csv(DATASET_PATH, encoding="latin-1")
        # Identify text and label columns
        label_col = "v1" if "v1" in df.columns else ("label" if "label" in df.columns else df.columns[0])
        text_col = "v2" if "v2" in df.columns else ("text" if "text" in df.columns else ("message" if "message" in df.columns else df.columns[1]))
        
        texts = df[text_col].dropna().astype(str).tolist()
        labels = df[label_col].dropna().astype(str).str.lower().tolist()
        
        # Convert labels to binary (0 = ham/legitimate, 1 = spam/phishing)
        binary_labels = [1 if l in {"spam", "phishing", "1", "true"} else 0 for l in labels]
    except Exception as e:
        print(f"Error loading spam.csv: {e}. Creating baseline dataset...")
        texts = []
        binary_labels = []

    print(f"Loaded {len(texts)} existing samples.")

    # Add college placement legitimate samples (label = 0)
    print(f"[2/5] Augmenting dataset with {len(COLLEGE_PLACEMENT_SAMPLES)} legitimate college/placement emails...")
    for sample in COLLEGE_PLACEMENT_SAMPLES:
        texts.append(sample)
        binary_labels.append(0)

    # Add extra phishing samples (label = 1)
    print(f"Adding {len(EXTRA_PHISHING_SAMPLES)} targeted phishing threat samples...")
    for sample in EXTRA_PHISHING_SAMPLES:
        texts.append(sample)
        binary_labels.append(1)

    # Train TF-IDF Vectorizer
    print("[3/5] Vectorizing text with TfidfVectorizer (unigram + bigram)...")
    vectorizer = TfidfVectorizer(
        max_features=6000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    X = vectorizer.fit_transform(texts)
    y = np.array(binary_labels)

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

    print(f"[4/5] Training Random Forest Classifier on {X_train.shape[0]} samples...")
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=35,
        min_samples_split=3,
        random_state=42,
        class_weight="balanced"
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy on Test Set: {acc * 100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=["Legitimate (Ham)", "Phishing (Spam)"]))

    # Test specifically on college placement emails
    print("Testing college placement email predictions:")
    test_placement_emails = [
        "Placement Cell Sairam: Please register for the Zoho campus drive immediately.",
        "Dear Students, please register on the portal immediately for the upcoming campus drive. Infosys recruitment test schedule.",
        "Anna University exam hall ticket notification from placement@sairamce.edu.in",
        "Mandatory registration for campus placement drive - Sri Sairam College of Engineering"
    ]
    test_features = vectorizer.transform(test_placement_emails)
    test_probs = clf.predict_proba(test_features)
    for email_text, prob in zip(test_placement_emails, test_probs):
        phish_prob = prob[1] * 100
        print(f"  [{phish_prob:.1f}% risk] {email_text[:70]}...")

    # Save trained model bundle
    bundle = {
        "model": clf,
        "vectorizer": vectorizer,
        "metadata": {
            "version": "2.0.0",
            "classes": [0, 1],
            "trained_on": "spam.csv + college_placement_dataset",
            "accuracy": float(acc)
        }
    }
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(bundle, f)
    print(f"[5/5] Successfully saved updated model to {MODEL_PATH}!")


if __name__ == "__main__":
    train()
