import csv
from flask import Flask, jsonify, request, send_file
from models import *
from flask_cors import CORS
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.security import generate_password_hash
import jwt

app = Flask(__name__)

CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SECRET_KEY'] = "anuragiitmadras"

db.init_app(app)


def insert_dummy_data():
    colleagues_data = [
        {"name": "Alice Johnson", "email": "22dp1000105@ds.study.iitm.ac.in",
            "department": "IT", "designation": "Analyst"},
        {"name": "Anurag Kumar", "email": "akanuragkumar75@gmail.com",
            "department": "Developer", "designation": "Developer"},
        # {"name": "Ritika", "email": "training@kvqaindia.com",
        #     "department": "Leadership", "designation": "CTO"},
        # {"name": "Lav Kaushik", "email": "lav@kvqaindia.com",
        #     "department": "Leadership", "designation": "CEO"},
        # {"name": "Eva Adams", "email": "eva.adams@bing.com", "designation": "HR"},
    ]

    # colleagues = [Colleagues(name=data['name'], email=data['email'],
    #                          designation=data['designation']) for data in colleagues_data]

    for data in colleagues_data:
        existing_colleague = Colleagues.query.filter_by(
            email=data['email']).first()
        if not existing_colleague:  # Only insert if email doesn't exist
            colleague = Colleagues(
                name=data['name'], email=data['email'], department=data['department'], designation=data['designation'])
            db.session.add(colleague)

    questions_data = [
        {"question_text": "What is your favorite security practice?", "options": [
            "Password Management", "Two-Factor Authentication", "Phishing Awareness"], "answer": "Phishing Awareness"},
        {"question_text": "How often do you update your passwords?", "options": [
            "Monthly", "Quarterly", "Annually"], "answer": "Quarterly"},
        {"question_text": "Have you ever encountered a phishing attempt?", "options": [
            "Yes", "No"], "answer": "Yes"},
        {"question_text": "What do you do when you receive a suspicious email?", "options": [
            "Ignore", "Report", "Click"], "answer": "Report"},
        {"question_text": "Do you use different passwords for different accounts?", "options": [
            "Yes", "No"], "answer": "Yes"},
    ]

    for data in questions_data:
        existing_question = Questions.query.filter_by(
            question_text=data['question_text']).first()
        if not existing_question:
            question = Questions(question_text=data['question_text'],
                                 options=data['options'], answer=data['answer'])
            db.session.add(question)

    users_data = [
        {"email": "anurag@gmail.com",
            "username": "tech@kvqaindia", "password": "asdfgh"}
    ]

    for data in users_data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if not existing_user:  # Only insert if email doesn't exist
            user = User(email=data['email'], username=data['username'])
            user.set_password(data['password'])  # Hash the password
            db.session.add(user)

    db.session.commit()


with app.app_context():
    db.create_all()
    insert_dummy_data()


class EmailTemplate:
    def __init__(self, template_file):

        with open(template_file, 'r') as file:
            self.template = file.read()

    def generate_email(self, sender_name, sender_email, recipient_name, subject):

        email_content = self.template
        email_content = email_content.replace('{{sender_name}}', sender_name)
        email_content = email_content.replace('{{sender_email}}', sender_email)
        email_content = email_content.replace(
            '{{recipient_name}}', recipient_name)
        email_content = email_content.replace('{{subject}}', subject)

        email_content = email_content.replace('\n', '<br>')
        email_content = email_content.replace('\n\n', '</p><p>')
        email_content = f"<p>{email_content}</p>"

        return email_content


@app.route('/')
def home():
    return 'Hello World'


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'message': 'User with this email or username already exists!'}), 409

    new_user = User(email=email, username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    credentials = request.json  # Get JSON data from the request
    username = credentials.get('username')
    password = credentials.get('password')

    user = User.query.filter_by(
        username=username).first()  # Query user by username

    # Verify if user exists and check password
    if user and user.check_password(password):
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)  # Correct usage here
        }
        token = jwt.encode(
            payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"message": "Login Successful", "access_token": token}), 200

    return jsonify({"message": "Invalid username or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    # JWT is stateless, just inform the client to delete the token
    return jsonify({"message": "Logged out successfully"}), 200


emailed_candidates = []


@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    global emailed_candidates
    emailed_candidates = []

    request_data = request.json
    selected_department = request_data.get('department')

    if not selected_department:
        return jsonify({'error': 'No department selected'}), 400

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

    if selected_department == 'HR':
        with open(os.path.join(templates_dir, 'hr_email_template.html')) as f:
            email_template = f.read()
        action_name = "Update Payroll Information"
        email_subject = "Important: Update Your Payroll Information for Q4"
    elif selected_department == 'Accounts':
        with open(os.path.join(templates_dir, 'accounts_email_template.html')) as f:
            email_template = f.read()
        action_name = "Update Credentials"
        email_subject = "Reminder: Update Your Credentials for Compliance"
    # else:
    #     with open(os.path.join(templates_dir, 'email_template.html')) as f:
    #         email_template = f.read()
    #     action_name = "Complete Action"
    #     email_subject = "Action Required: Complete Task"  # Default subject

    colleagues = Colleagues.query.all()

    from_email = "akanuragkumar4@gmail.com"
    password = "ibairoljmhkjmqah"

    for colleague in colleagues:
        # tracking_link = f"https://phishing-mail-application.onrender.com/phishing_test/{colleague.id}"
        # tracking_link = f"https://phishing-mail-frontend.vercel.app/phishing_test/{colleague.id}"
        tracking_link = f"http://localhost:8080/phishing_test/{colleague.id}"

        print(f"Generated tracking link for {colleague.name}: {tracking_link}")

        to_email = colleague.email
        msg = MIMEMultipart('related')
        msg['Subject'] = email_subject
        msg['From'] = from_email
        msg['To'] = to_email

        body = email_template.replace("{{recipient_name}}", colleague.name)
        body = body.replace("{{action_link}}", tracking_link)
        body = body.replace("{{action_name}}", action_name)
        body = body.replace("{{email_subject}}", email_subject)

        html_content = f"""
        <html>
            <body>
                {body}
                <p>Best regards,</p>
                <img src="cid:signature_image" alt="Company Signature" />
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))

        signature_image_path = os.path.join('templates', 'Capture.JPG')
        with open(signature_image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<signature_image>')
            msg.attach(img)

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(from_email, password)
                server.send_message(msg)
            print(f"Email sent to {colleague.email}")

            emailed_candidates.append({
                'name': colleague.name,
                'email': colleague.email,
                'designation': colleague.designation
            })
            print("Emailed candidates list after sending:", emailed_candidates)

        except Exception as e:
            print(f"Failed to send email to {colleague.email}: {str(e)}")

    return jsonify({'message': 'Phishing emails sent to colleagues.'})


@app.route('/phishing_test/<int:colleague_id>', methods=['GET'])
def phishing_test(colleague_id):
    print(f'Phishing test accessed for colleague ID: {colleague_id}')

    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    return jsonify({'message': 'Tracking link accessed successfully', 'colleague_id': colleague_id})
    # return redirect(f'https://kvphishing.netlify.app/phishing_test/{colleague_id}')


@app.route('/generate_emailed_candidates_report', methods=['GET', 'POST'])
def generate_emailed_candidates_report():
    global emailed_candidates

    if not emailed_candidates:
        print("No candidates in emailed_candidates:",
              emailed_candidates)
        return jsonify({'error': 'No successfully emailed candidates.'}), 400

    print("Generating CSV for:", emailed_candidates)

    try:
        csv_file_path = "emailed_candidates_report.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'email', 'department', 'designation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(emailed_candidates)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/users')
def users():
    user = Colleagues.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'department': u.department, 'designation': u.designation} for u in user])


@app.route('/phising_click/<int:colleague_id>', methods=['POST'])
def phising_click(colleague_id):
    print(f'Received request for colleague ID: {colleague_id}')
    colleague = Colleagues.query.get(colleague_id)
    if not colleague:
        return jsonify({'error': 'Colleague not found.'}), 404

    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    if report:
        report.clicked = True
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
    db.session.commit()

    candidate_data = {
        'id': colleague.id,
        'name': colleague.name,
        'email': colleague.email,
        'department': colleague.department,
        'designation': colleague.designation
    }

    return jsonify({'message': 'Click recorded', 'candidate': candidate_data})


@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Reports.query.all()
    report_data = [{'id': r.id, 'colleague_id': r.colleague_id, 'clicked': r.clicked,
                    'answered': r.answered, 'answers': r.answers} for r in reports]
    return jsonify(report_data)


@app.route('/phishing_opened/<int:colleague_id>', methods=['GET'])
def phishing_opened(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    print(
        f'Processing click for colleague ID: {colleague_id} | Existing report: {report}')

    if report:
        report.clicked = True
        print(f'Updated existing report for ID {colleague_id} to clicked=True')
    else:
        report = Reports(colleague_id=colleague_id,
                         clicked=True, answered=False, answers={})
        db.session.add(report)
        print(f'Created new report for ID {colleague_id} with clicked=True')

    db.session.commit()
    return jsonify({'message': 'Thank you for participating in our phishing awareness program.', 'showPopup': True})


def evaluate_answers(submitted_answers):
    questions = Questions.query.all()
    correct_answers = [str(q.answer).strip().lower()
                       for q in questions]
    score = 0
    total_questions = len(correct_answers)

    for i, submitted_answer in enumerate(submitted_answers):
        if i < total_questions:
            submitted_answer = str(submitted_answer).strip().lower()
            correct_answer = correct_answers[i]

            print(
                f"Comparing submitted: '{submitted_answer}' with correct: '{correct_answer}'")

            if submitted_answer == correct_answer:
                score += 1

    return (score / total_questions) * 100 if total_questions > 0 else 0


@app.route('/submit_answers/<int:colleague_id>', methods=['POST'])
def submit_answers(colleague_id):
    data = request.get_json()
    report = Reports.query.filter_by(colleague_id=colleague_id).first()

    if report and report.clicked:
        report.answered = True
        report.answers = data['answers']
        report.score = evaluate_answers(data['answers'])
        db.session.commit()

        return jsonify({'message': 'Answers submitted successfully.', 'score': report.score})

    return jsonify({'error': 'User did not click the phishing link.'}), 400


@app.route('/generate_reports', methods=['GET', 'POST'])
def generate_reports():
    try:
        reports = Reports.query.all()
        report_data = []

        for report in reports:
            colleague = Colleagues.query.get(report.colleague_id)
            report_entry = {
                'Colleague Name': colleague.name,
                'Colleague Email': colleague.email,
                'Department': colleague.department,
                'Designation': colleague.designation,
                'Clicked': report.clicked,
                'Answered': report.answered,
                'Score': report.score,
            }
            report_data.append(report_entry)

        csv_file_path = "candidate_reports.csv"
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Colleague Name', 'Colleague Email', 'Department',
                          'Designation', 'Clicked', 'Answered', 'Score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in report_data:
                writer.writerow(data)

        return send_file(csv_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download_report/<int:colleague_id>', methods=['GET'])
def download_report(colleague_id):
    report = Reports.query.filter_by(colleague_id=colleague_id).first()
    colleague = Colleagues.query.get(colleague_id)

    if not report or not colleague:
        return jsonify({'error': 'Report or colleague not found.'}), 404

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 770, "Phishing Awareness Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 740, f"Report for: {colleague.name}")
    pdf.drawString(100, 720, f"Email: {colleague.email}")
    pdf.drawString(100, 700, f"Department: {colleague.department}")

    pdf.setLineWidth(1)
    pdf.line(100, 690, 500, 690)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 670, "Phishing Email Status:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, 650, f"Clicked: {'Yes' if report.clicked else 'No'}")
    pdf.drawString(120, 630, f"Answered: {'Yes' if report.answered else 'No'}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 600, "Answers Provided:")

    pdf.setFont("Helvetica", 12)
    y_position = 580
    if report.answers:
        for i, answer in enumerate(report.answers, start=1):
            pdf.drawString(120, y_position, f"Q{i}: {answer}")
            y_position -= 20
    else:
        pdf.drawString(120, y_position, "No answers submitted")
        y_position -= 20

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, y_position - 20, "Overall Performance:")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, y_position - 40,
                   f"Score: {report.score if report.score else 0}")

    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(100, 50, "Generated on: " +
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name=f'report_{colleague_id}.pdf', mimetype='application/pdf')


@app.route('/upload_colleagues_data', methods=['POST'])
def upload_colleagues_data():
    try:
        db.session.query(Colleagues).delete()

        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                colleague = Colleagues(
                    name=row['Full Name'],
                    email=row['Work Email'],
                    department=row['Department'],
                    designation=row['Job Title']
                )
                db.session.add(colleague)

            db.session.commit()
            return jsonify({'message': 'Data uploaded successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format. Please upload an .xlsx file.'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error processing file: {str(e)}'}), 500


@app.route('/questions', methods=['GET'])
def get_questions():
    questions = Questions.query.all()
    return jsonify([{
        'id': question.id,
        'question_text': question.question_text,
        'options': question.options,
        'answer': question.answer
    } for question in questions])


@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Questions.query.get(question_id)
    if question:
        return jsonify({
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'answer': question.answer
        })
    return jsonify({'error': 'Question not found!'}), 404


@app.route('/questions', methods=['POST'])
def add_question():
    data = request.json
    new_question = Questions(
        question_text=data['question_text'],
        options=data['options'],
        answer=data['answer']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Question added!', 'id': new_question.id}), 201


@app.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    print(f"Updating question ID: {question_id}")
    data = request.json
    print(f"Received data: {data}")

    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    question.question_text = data['question_text']
    question.options = data['options']
    question.answer = data['answer']
    db.session.commit()
    return jsonify({'message': 'Question updated!'})


@app.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = Questions.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found!'}), 404

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted!'})


if __name__ == "__main__":
    app.run(debug=True)
