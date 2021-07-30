import os
import smtplib
import urllib.parse

from random import randint
from flask import Flask, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, \
    SubmitField, IntegerField, DateField, SelectField, FileField, TextAreaField
from wtforms.validators import InputRequired, Email, DataRequired
from base64 import b64encode

SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
random_string = os.urandom(9)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electioneeringdatabase.db'
random_string0 = randint(1000000, 1111111)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()
print(random_string0, 1)
election_voter = None
election_phone_number = None
# # TODO Constants ... make sure to replace these constants with the email address and password of the main admin #
#  TODO After replacing the code below with your details... ensure that you look online for how to allow less secure
#   apps gain access to gmail in your gmail settings otherwise, the module that sends the mail would not be able to
#   work
gmail_password = os.environ.get("gmail_password")
gmail_address = os.environ.get("gmail_address")
receiver_email = "lesliedouglas23@gmail.com"


class NewElection(FlaskForm):
    # this is code to arrange and order the form where you add things to the list. it uses the quick forms format
    election_name = StringField('What is the name of your election?', validators=[InputRequired()])
    no_of_participants = IntegerField('How many participants are contesting in this election',
                                      validators=[InputRequired()])
    election_start = DateField('When is the start date for the election "DD/MM/YYYY" ', validators=[InputRequired()])
    election_end = DateField('When is the end date for the election "DD/MM/YYYY" ', validators=[InputRequired()])
    no_of_voters = IntegerField('Provide an estimate of how many voters you are expecting',
                                validators=[InputRequired()])
    election_domain = StringField("What email domain does your average voter use.\n e.g. 'stu.cu.edu.ng' or "
                                  "'yahoo.com', "
                                  "If you would like it to be open to the public, Enter '.everybody' ",
                                  validators=[InputRequired()])
    report_frequency = IntegerField("How often would you like to receive reports.\n Enter your value as a multiple of "
                                    "a "
                                    "day e.g. '1' for every day '1/2' for every 12 hours", validators=[InputRequired()])
    submit = SubmitField('Submit')


class NewCandidate(FlaskForm):
    election_of_candidate = SelectField('Choose the election for the candidate',
                                        choices=["🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
                                        validators=[InputRequired()])
    candidate_name = StringField('What is the name of the Candidate?', validators=[InputRequired()])
    candidate_age = IntegerField('What is the age of the Candidate?', validators=[InputRequired()])
    candidate_sex = IntegerField('What is the sex of this Candidate? Male/Female', validators=[InputRequired()])
    candidate_hobbies = StringField('What does the candidate like to do in their spare time',
                                    validators=[InputRequired()])
    candidate_policy = TextAreaField('What does the Candidate plan to do when they enter office',
                                     validators=[InputRequired()])
    candidate_past_positions = StringField("What are the previous positions that have been held by this candidate",
                                           validators=[InputRequired()])
    candidate_about = TextAreaField('Insert a short Bio about the candidate',
                                    validators=[InputRequired()])
    candidate_email = StringField('Insert an email address for the candidate',
                                  validators=[InputRequired()])
    candidate_picture1 = FileField("Upload your 1st picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_picture2 = FileField("Upload your 2nd picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_picture3 = FileField("Upload your 3rd picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_picture4 = FileField("Upload your 4th picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_profile_picture = FileField("Upload the candidate's profile pic", validators=[InputRequired()])
    submit = SubmitField('Create New Candidate')


class CandidateChanges(FlaskForm):
    election_of_candidate = SelectField('Choose the election for the candidate',
                                        choices=["🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
                                        validators=[InputRequired()])
    candidate_name = SelectField('Choose the candidate you want to edit from these candidates',
                                 choices=["a", "b", "c", "d", "e"],
                                 validators=[InputRequired()])
    candidate_age = IntegerField('What is the age of the Candidate?', validators=[InputRequired()])
    candidate_sex = IntegerField('What is the sex of this Candidate', validators=[InputRequired()])
    candidate_hobbies = StringField('What does the candidate like to do in their spare time',
                                    validators=[InputRequired()])
    candidate_policy = TextAreaField('What does the Candidate plan to do when they enter office',
                                     validators=[InputRequired()])
    candidate_past_positions = StringField("What are the previous positions that have been held by this candidate",
                                           validators=[InputRequired()])
    candidate_picture1 = FileField("Upload your 1st picture of the candidate",
                                   validators=[InputRequired()])
    candidate_picture2 = FileField("Upload your 2nd picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_picture3 = FileField("Upload your 3rd picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_picture4 = FileField("Upload your 4th picture of the candidate ",
                                   validators=[InputRequired()])
    candidate_profile_picture = FileField("Upload the candidate's profile picture", validators=[InputRequired()])
    delete_candidate = SelectField('Would you like to Delete this Candidate',
                                   choices=["YES", "NO"],
                                   validators=[InputRequired()])
    submit = SubmitField('Edit Candidate')


class DeleteElection(FlaskForm):
    election_of_candidate = SelectField('Choose which election you would like to delete',
                                        choices=["🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
                                        validators=[InputRequired()])
    submit = SubmitField("Delete")


class VoteForm(FlaskForm):
    email1 = StringField('email', validators=[DataRequired("An email address is required"), Email()])
    phone_number = StringField('Phone Number', validators=[InputRequired()])
    submit1 = SubmitField("Vote")


class Elections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_name = db.Column(db.String(250), unique=False, nullable=False)
    no_of_participants = db.Column(db.Integer, unique=False, nullable=False)
    election_start = db.Column(db.Integer, unique=False, nullable=False)
    election_end = db.Column(db.Integer, unique=False, nullable=False)
    no_of_voters = db.Column(db.Integer, unique=False, nullable=False)
    election_domain = db.Column(db.String(250), unique=False, nullable=False)
    report_frequency = db.Column(db.String(250), unique=False, nullable=False)
    candidate_name = db.Column(db.String(250), unique=True, nullable=True)
    candidate_age = db.Column(db.Integer, unique=False, nullable=True)
    candidate_sex = db.Column(db.Integer, unique=False, nullable=True)
    candidate_hobbies = db.Column(db.String(250), unique=False, nullable=True)
    candidate_policies = db.Column(db.String(250), unique=True, nullable=True)
    candidate_past_positions = db.Column(db.String(250), unique=True, nullable=True)
    candidate_email = db.Column(db.String(250), unique=True, nullable=True)
    candidate_about = db.Column(db.String(250), unique=True, nullable=True)
    candidate_picture1 = db.Column(db.Text, unique=True, nullable=True)
    candidate_picture2 = db.Column(db.Text, unique=True, nullable=True)
    candidate_picture3 = db.Column(db.Text, unique=True, nullable=True)
    candidate_picture4 = db.Column(db.Text, unique=True, nullable=True)
    candidate_profile_picture = db.Column(db.Text, unique=True, nullable=True)
    election_admin = db.Column(db.String(250), unique=False, nullable=False)
    vote_count = db.Column(db.Integer, unique=False, nullable=False)
    db.create_all()


class Voters1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_call = db.Column(db.String(250), unique=False, nullable=False)
    election_voted = db.Column(db.String(250), unique=False, nullable=False)
    election_voter = db.Column(db.String(250), unique=False, nullable=False)
    election_phone_number = db.Column(db.Integer, unique=False, nullable=False)
    db.create_all()


# functions
# function to remove duplicate in a list
def Remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list


def elections_happening(admin_email):
    records_you_can_access = Elections.query.filter(Elections.election_admin.endswith(admin_email)).all()
    election_names = Remove([members.election_name for members in records_you_can_access])
    return election_names


def elections_available_public():
    records_you_can_access = db.session.query(Elections).all()
    election_names = Remove([members.election_name for members in records_you_can_access])
    election_records = []
    for members in election_names:
        election_records.append(Elections.query.filter_by(election_name=members).first())
    return election_records


def have_voted_before(election_name, voter):
    records_you_can_access = db.session.query(Voters1).all()
    specific_election_records = [members for members in records_you_can_access if
                                 members.election_call == election_name]
    specific_voter_history = [members for members in specific_election_records if members.election_voter == voter]
    has_voted = len(specific_voter_history)
    return has_voted


def available_candidates(admin_email):
    records_you_can_access = Elections.query.filter(Elections.election_admin.endswith(admin_email)).all()
    candidate_names = Remove([members.candidate_name for members in records_you_can_access])
    return candidate_names


def vote_totalled(election_title):
    # function to check the total number of votes that have been cast for a specific election
    contestants_in_election = Elections.query.filter_by(election_name=election_title).all()
    current_votes = 0
    for contestants in contestants_in_election:
        current_votes += contestants.vote_count
    return current_votes


def current_winner(election_title):
    # function to check who is currently winning the election by the number of votes that they currently have
    contestants_in_election = Elections.query.filter_by(election_name=election_title).all()
    list_of_participants = [members.candidate_name for members in contestants_in_election]
    list_of_vote_counts = [members.vote_count for members in contestants_in_election]
    winning_candidate = list_of_participants[list_of_vote_counts.index(max(list_of_vote_counts))]
    return winning_candidate


@app.route('/')
def home_page():
    red = randint(1, 6)
    picture_path = f'../static/homeimages/gallery/fulls/0{red}.jpg'
    election_records = db.session.query(Elections).all()
    if len(election_records) == 0:
        return admin_login()
    most_recent_election = election_records[-1]
    picture1 = b64encode(most_recent_election.candidate_picture1).decode("utf-8")
    picture2 = b64encode(most_recent_election.candidate_picture2).decode("utf-8")
    picture3 = b64encode(most_recent_election.candidate_picture3).decode("utf-8")
    picture4 = b64encode(most_recent_election.candidate_picture4).decode("utf-8")
    picture5 = b64encode(most_recent_election.candidate_profile_picture).decode("utf-8")
    picture6 = b64encode(most_recent_election.candidate_profile_picture).decode("utf-8")
    all_election_records = elections_available_public()
    number = len(election_records)

    return render_template("homepage.html", most_recent_election=most_recent_election, number=number,
                           all_election_records=all_election_records, picture_path=picture_path, picture1=picture1,
                           picture2=picture2, picture3=picture3, picture4=picture4, picture5=picture5,
                           picture6=picture6)


@app.route("/candidatelistings")
def candidate_listings():
    election_records = db.session.query(Elections).all()
    most_recent_election = election_records[-1]
    picture1 = b64encode(most_recent_election.candidate_picture1).decode("utf-8")
    picture2 = b64encode(most_recent_election.candidate_picture2).decode("utf-8")
    picture3 = b64encode(most_recent_election.candidate_picture3).decode("utf-8")
    picture4 = b64encode(most_recent_election.candidate_picture4).decode("utf-8")
    profile_picture = b64encode(most_recent_election.candidate_profile_picture).decode("utf-8")
    return render_template('candidatedetails.html', election_record=most_recent_election, picture1=picture1,
                           picture2=picture2, picture3=picture3, picture4=picture4, profile_picture=profile_picture)


@app.route("/candidatelistings/<election_id>")
def candidate_listings1(election_id):
    election_record = Elections.query.get(election_id)
    picture1 = b64encode(election_record.candidate_picture1).decode("utf-8")
    picture2 = b64encode(election_record.candidate_picture2).decode("utf-8")
    picture3 = b64encode(election_record.candidate_picture3).decode("utf-8")
    picture4 = b64encode(election_record.candidate_picture4).decode("utf-8")
    profile_picture = b64encode(election_record.candidate_profile_picture).decode("utf-8")
    return render_template('candidatedetails.html', election_record=election_record, picture1=picture1,
                           picture2=picture2, picture3=picture3, picture4=picture4, profile_picture=profile_picture)


@app.route('/sendmail/<candidate_email>', methods=['POST'])
def sendmail(candidate_email):
    if request.method == 'POST':
        a_name = request.form['name']
        a_email = request.form['email']
        a_message = request.form['message']
        with smtplib.SMTP('smtp.gmail.com') as email_protocol:
            email_protocol.starttls()
            email_protocol.login(user=gmail_address, password=gmail_password)
            email_protocol.sendmail(from_addr=gmail_address, to_addrs=candidate_email,
                                    msg=f"Subject:{a_name} says Hello!\n\nHey, my name is {a_name},my email address is {a_email}\nI have a message for you which reads:\n{a_message}")
        return render_template('homepage.html')


@app.route("/electiondetails")
def election_details():
    election_records = db.session.query(Elections).all()
    most_recent_election = election_records[-1].election_name
    candidates = Elections.query.filter_by(election_name=most_recent_election).all()
    candidates = candidates[1:len(candidates)]
    candidates_except_first = candidates[1:len(candidates)]
    vote_tally = vote_totalled(most_recent_election)
    winning_candidate = current_winner(most_recent_election)
    number = len(candidates)
    picture = b64encode(candidates[0].candidate_profile_picture).decode("utf-8")
    for members in candidates:
        members.candidate_profile_picture = b64encode(members.candidate_profile_picture).decode("utf-8")

    return render_template('electiondetails.html', candidates_except_first=candidates_except_first,
                           candidates=candidates, number=number, vote_tally=vote_tally,
                           winning_candidate=winning_candidate, picture=picture)


@app.route("/electiondetails/<election_id>")
def election_details1(election_id):
    election_in_question = Elections.query.get(election_id)
    election_in_question = election_in_question.election_name
    candidates = Elections.query.filter_by(election_name=election_in_question).all()
    candidates = candidates[1:len(candidates)]
    candidates_except_first = candidates[1:len(candidates)]
    number = len(candidates)
    vote_tally = vote_totalled(election_in_question)
    winning_candidate = current_winner(election_in_question)
    return render_template('electiondetails.html', candidates=candidates,
                           candidates_except_first=candidates_except_first, number=number, vote_tally=vote_tally,
                           winning_candidate=winning_candidate)


@app.route('/contactadmin', methods=["POST", "GET"])
def contact_admin():
    if request.method == 'POST':
        a_name = request.form['name']
        a_email = request.form['email']
        a_phone_number = request.form['phone_number']
        a_message = request.form['message']
        with smtplib.SMTP('smtp.gmail.com') as email_protocol:
            email_protocol.starttls()
            email_protocol.login(user=gmail_address, password=gmail_password)
            email_protocol.sendmail(from_addr=gmail_address, to_addrs=receiver_email,
                                    msg=f"Subject:{a_name} says Hello!\n\nHey, my name is {a_name},my email address is {a_email}, my phone number is {a_phone_number}.\nI have a message for you which reads:\n{a_message}")
        title_content = "Your message has been successfully sent"
        subtitle_content = ""
        return render_template("landing_page.html", title_content=title_content, subtitle_content=subtitle_content)
    else:
        title_content = 'Contact Me'
        subtitle_content = 'Have questions? I have answers'
        return render_template("landing_page.html", title_content=title_content, subtitle_content=subtitle_content)


# when you click on sign, you are sending the random string that would be used for the end of the url already to
# the sign in page
@app.route('/login')
def admin_login():
    global random_string
    random_string = os.urandom(10)
    return render_template('adminlogin.html', random_string=random_string)


@app.route('/signup')
def admin_signup():
    return render_template('signup.html')


@app.route('/vote/<candidate_id>/<election_name>', methods=['POST', 'GET'])
def vote_for_candidate(candidate_id, election_name):
    global election_voter, election_phone_number
    form = VoteForm()
    if form.validate_on_submit():

        if have_voted_before(election_name=election_name, voter=form.email1.data) == 0:
            election_voter = form.email1.data
            election_phone_number = form.phone_number.data
            with smtplib.SMTP('smtp.gmail.com') as email_protocol:
                # # TODO right now, this software can only run and be hosted locally, the very last step would be to
                #  adapt the code below to allow other computers access the IP
                ip_address = request.remote_addr
                email_protocol.starttls()
                email_protocol.login(user=gmail_address, password=gmail_password)
                election_name = urllib.parse.quote(election_name)
                url = f"http://{ip_address}:5000/vote/{candidate_id}/{random_string0}/{election_name}"
                email_protocol.sendmail(from_addr=gmail_address, to_addrs=election_voter,
                                        msg=f"Subject: Vote Verification\n\nClick the link below in order to vote : "
                                            f"{url}")
            title = 'Hurry Up!'
            subtitle = 'Check your email for your vote link before it expires'
            return render_template('landing_page.html', title_content=title, subtitle_content=subtitle)
        else:
            title = "Sorry about this"
            subtitle = 'It looks like your vote has already been recorded for this election!'
            return render_template('landing_page.html', title_content=title, subtitle_content=subtitle)
    return render_template('votepage.html', candidate_id=candidate_id, election_name=election_name, form=form)


@app.route('/vote/<candidate_id>/<random_string5>/<election_name>')
def tally_votes(candidate_id, random_string5, election_name):
    if int(random_string5) == random_string0:
        # code to update the database of people who have voted to register that someone just voted
        candidate = Elections.query.get(candidate_id)
        candidate_name = candidate.candidate_name
        db.create_all()
        admin = Voters1(election_call=election_name, election_voted=candidate_name, election_voter=election_voter,
                        election_phone_number=election_phone_number)
        db.session.add(admin)
        db.session.commit()
        # code to update the database of candidates to reflect that a vote increment has happened
        new_vote_count = int(candidate.vote_count) + 1
        candidate.vote_count = new_vote_count
        db.session.commit()
        title = 'Congrats! your vote was casted successfully'
        subtitle = 'Keep doing your civic duty'
        return render_template('contactadmin.html', title_content=title, subtitle_content=subtitle)
    else:
        title = 'Oops! Sorry There!'
        subtitle = 'There must have been an error in your process or your link timed out.. go back to vote again'
        return render_template('contactadmin.html', title_content=title, subtitle_content=subtitle)


# # TODO CREATE A DATABASE THAT ALLOWS NEW USERS TO REGISTER AND BECOME ADMINS .. IN THE MEANTIME, YOU CAN CHANGE THE
#  VALUES WRITTEN BELOW TO GAIN ACCESS in the post request, that random string from the post request is sent to the
#  url bar via the means below
@app.route("/makeelection/<the_random_string>", methods=['POST', 'GET'])
def make_election(the_random_string):
    if request.method == 'POST':
        form = NewElection()
        adminlogin = request.form["admin-login"]
        adminpassword = request.form["admin-password"]
        # # TODO THESE DETAILS ON THE NEXT LINE ARE THE CURRENT ADMIN USERNAME AND PASSWORD
        if adminlogin == 'admin@email.com' and adminpassword == '12345678':
            random_string1 = os.urandom(10)
            return render_template('electioncreation.html',
                                   randomstring1=random_string1, form=form)
        else:
            return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('footer.html'))


@app.route('/newelection/<randomstring1>', methods=['POST', 'GET'])
def new_election(randomstring1):
    if request.method == 'POST':
        # code to create new table for a new election using the normal request module
        db.create_all()
        admin = Elections(election_name=request.form['election_name'],
                          no_of_participants=request.form['no_of_participants'],
                          election_start=request.form['election_start'],
                          election_end=request.form['election_end'],
                          no_of_voters=request.form['no_of_voters'],
                          election_domain=request.form['election_domain'],
                          report_frequency=request.form['report_frequency'],
                          election_admin='lesliedouglas23@gmail.com',
                          vote_count=0)
        db.session.add(admin)
        db.session.commit()
        NewCandidate.election_of_candidate = SelectField('Choose your election from the drop down menu',
                                                         choices=elections_happening('douglas23@gmail.com'),
                                                         validators=[InputRequired()])

        form = NewCandidate()
        random_string2 = os.urandom(12)
        return render_template('candidatecreation.html', form=form, randomstring2=random_string2)
    # the line of code below is to ensure that they can only get to the editing page via a get request
    # if the string content matches this
    elif request.method == 'GET' and randomstring1 == '\xd3\xc1\x12\xe1\xa8M\xea\xb1\xb1L\xb5\xd8\x80\xad\x083G\xb2a' \
                                                      '\xb3w\xd8\x14\x16\xbdMP\xae\xf6\xdb\xe2':
        form = NewElection()
        randomstring1 = '\xd3\xc1\x12\xe1\xa8M\xea\xb1\xb1L\xb5\xd8\x80\xad\x083G\xb2a' \
                        '\xb3w\xd8\x14\x16\xbdMP\xae\xf6\xdb\xe2'
        return render_template('electioncreation.html', form=form, randomstring1=randomstring1)


@app.route('/newcandidate/<randomstring2>', methods=['POST', 'GET'])
def new_candidate(randomstring2):
    if request.method == 'POST':
        name_of_election = request.form['election_of_candidate']
        election_entry = Elections.query.filter_by(election_name=name_of_election).first()
        admin = Elections(election_name=name_of_election,
                          no_of_participants=election_entry.no_of_participants,
                          election_start=election_entry.election_start,
                          election_end=election_entry.election_end,
                          no_of_voters=election_entry.no_of_voters,
                          election_domain=election_entry.election_domain,
                          report_frequency=election_entry.report_frequency,
                          election_admin='lesliedouglas23@gmail.com',
                          vote_count=0,
                          candidate_name=request.form['candidate_name'],
                          candidate_age=request.form['candidate_age'],
                          candidate_sex=request.form['candidate_sex'],
                          candidate_hobbies=request.form['candidate_hobbies'],
                          candidate_policies=request.form['candidate_policy'],
                          candidate_past_positions=request.form['candidate_past_positions'],
                          candidate_about=request.form['candidate_past_positions'],
                          candidate_email=request.form['candidate_email'],
                          candidate_picture1=request.files['candidate_picture1'].read(),
                          candidate_picture2=request.files['candidate_picture1'].read(),
                          candidate_picture3=request.files['candidate_picture1'].read(),
                          candidate_picture4=request.files['candidate_picture1'].read(),
                          candidate_profile_picture=request.files['candidate_profile_picture'].read())
        db.session.add(admin)
        db.session.commit()
        CandidateChanges.election_of_candidate = SelectField('Choose your election from the drop down menu',
                                                             choices=elections_happening('douglas23@gmail.com'),
                                                             validators=[InputRequired()])
        CandidateChanges.candidate_name = SelectField('Choose which candidate you would like to update from drop down '
                                                      'menu',
                                                      choices=available_candidates('douglas23@gmail.com'),
                                                      validators=[InputRequired()])
        form = CandidateChanges()
        random_string3 = os.urandom(12)
        return render_template('candidateedition.html', form=form, randomstring3=random_string3)
    elif request.method == 'GET' and randomstring2 == '\x0f\xc8\x8a\xbdW\x06\xc1l\x97\xf5\xf5\xefiS\xb5\n\xa3\x9do' \
                                                      '\x19\xfb\x9c\xcd\xdd\x17oC\xb6a\xd9':
        NewCandidate.election_of_candidate = SelectField('Choose your election from the drop down menu',
                                                         choices=elections_happening('douglas23@gmail.com'),
                                                         validators=[InputRequired()])
        form = NewCandidate()
        randomstring2 = '\x0f\xc8\x8a\xbdW\x06\xc1l\x97\xf5\xf5\xefiS\xb5\n\xa3\x9do' \
                        '\x19\xfb\x9c\xcd\xdd\x17oC\xb6a\xd9'
        return render_template('candidatecreation.html', form=form, randomstring2=randomstring2)


@app.route('/editcandidate/<randomstring3>', methods=['POST', 'GET'])
def edit_candidate(randomstring3):
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        user = Elections.query.filter_by(candidate_name=candidate_name).first()
        user.candidate_age = request.form['candidate_age']
        user.candidate_sex = request.form['candidate_sex']
        user.candidate_hobbies = request.form['candidate_hobbies']
        user.candidate_policies = request.form['candidate_policy']
        user.candidate_past_positions = request.form['candidate_past_positions']
        user.candidate_picture1 = request.files['candidate_picture1'].read()
        user.candidate_picture2 = request.files['candidate_picture2'].read()
        user.candidate_picture3 = request.files['candidate_picture3'].read()
        user.candidate_picture4 = request.files['candidate_picture4'].read()
        user.candidate_profile_picture = request.files['candidate_profile_picture'].read()
        db.session.commit()
        DeleteElection.election_of_candidate = SelectField('Choose the Election you wish to delete',
                                                           choices=elections_happening('douglas23@gmail.com'),
                                                           validators=[InputRequired()])
        form = DeleteElection()
        random_string4 = os.urandom(12)
        return render_template('electiondeletion.html', form=form, randomstring4=random_string4)
    elif request.method == 'GET' and randomstring3 == '\x0f\xc8\x8a\xbdW\x06\xc1l\x97\xf5\xf5\xefiS\xb5\n\xa3\x9do' \
                                                      '\x19\xfb\x9c\xcd\xdd\x17oC\xb6a\xd9':
        CandidateChanges.election_of_candidate = SelectField('Choose your election from the drop down menu',
                                                             choices=elections_happening('douglas23@gmail.com'),
                                                             validators=[InputRequired()])
        CandidateChanges.candidate_name = SelectField('Choose which candidate you would like to update from drop down '
                                                      'menu',
                                                      choices=available_candidates('douglas23@gmail.com'),
                                                      validators=[InputRequired()])
        form = CandidateChanges()
        randomstring3 = '\x0f\xc8\x8a\xbdW\x06\xc1l\x97\xf5\xf5\xefiS\xb5\n\xa3\x9do' \
                        '\x19\xfb\x9c\xcd\xdd\x17oC\xb6a\xd9'
        return render_template('candidateedition.html', form=form, randomstring3=randomstring3)


@app.route('/deleteelection/<randomstring4>', methods=['POST', 'GET'])
def delete_election(randomstring4):
    if request.method == 'POST':
        election_name = request.form['election_of_candidate']
        user = Elections.query.filter_by(election_name=election_name).all()
        for members in user:
            db.session.delete(members)
            db.session.commit()
        return render_template('homepage.html')
    elif request.method == 'GET' and randomstring4 == '\xd3\xc1\x12\xe1\xa8M\xea\xb1\xb1L\xb5\xd8\x80\xad\x083G\xb2a' \
                                                      '\xb3w\xd8\x14\x16\xbdMP\xae\xf6\xdb\xe2':
        DeleteElection.election_of_candidate = SelectField('Choose the Election you wish to delete',
                                                           choices=elections_happening('douglas23@gmail.com'),
                                                           validators=[InputRequired()])
        form = DeleteElection()
        randomstring4 = '\xd3\xc1\x12\xe1\xa8M\xea\xb1\xb1L\xb5\xd8\x80\xad\x083G\xb2a' \
                        '\xb3w\xd8\x14\x16\xbdMP\xae\xf6\xdb\xe2'
        return render_template('electiondeletion.html', form=form, randomstring4=randomstring4)


if __name__ == "__main__":
    app.run(debug=True)
