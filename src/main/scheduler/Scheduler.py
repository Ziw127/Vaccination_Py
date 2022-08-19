import sys
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):  # create_patient <username> <password>
    if len(tokens) != 3:
        print("Please try again! Enter Name and Password")
        return

    username = tokens[1]
    password = tokens[2]

    if not username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        patient.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            if row['Username'] is None:
                return False
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Enter Name and Password")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if not username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        caregiver.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:

            if row['Username'] is None:
                return False

    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def login_patient(tokens):
    # if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_caregiver is not None:
        print("A caregiver currently logged-in, Please wait until it log-out")
        return
    if current_patient is not None:
        print("A patient already logged-in!")
        return

    if len(tokens) != 3:
        print("Please try again! Enter Name and Password")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if patient is None:
        print("Please try again!")
        print("Your username of Password is wrong!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>

    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global current_caregiver
    if current_patient is not None:
        print("A patient currently logged-in, Please wait until it log-out")
        return
    if current_caregiver is not None:
        print("A caregiver already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Enter Name and Password")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
        print("Your username of Password is wrong!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver

# Check if a caregiver is available at a given time


def caregiver_available(d):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    select_date = "SELECT * FROM Availabilities WHERE Time = %s"
    caregivers = []

    try:
        cursor.execute(select_date, (d))
        for row in cursor:
            # print(row['Username'])
            caregivers.append(row['Username'])
        if caregivers is None or len(caregivers) == 0:
            return False
        else:
            return True

    except pymssql.Error:
        print("Error occurred when updating caregiver availability")
        cm.close_connection()
    cm.close_connection()


def search_caregiver_schedule(tokens):
    #  check 1: check if the user logs in
    global current_caregiver
    global current_patient
    if current_caregiver:
        print("login as caregiver")
    elif current_patient:
        print("login as patient")
    else:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    if not caregiver_available(d):
        print("No caregiver is available at this time")

    try:

        print("The caregivers that are available at "+date+" are:")
        Caregiver.search_caregiver(d)
    except ValueError:
        print("Please enter a valid date!")

    print("--------------Vaccine name and Available dose:--------------")
    Vaccine.getall()


def reserve(tokens):
    #  check 1: check if is the patient logs in
    global current_caregiver
    global current_patient
    if current_caregiver:
        print("This service only for Patient!")
        return
    elif current_patient:
        print("You logged in as a patient")
    else:
        print("Please login as a patient first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again! Enter the required information fully")
        return

    date, vaccine = tokens[1], tokens[2]
    vaccine.capitalize()
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    caregiver = None  # Choose a  caregiver randomly
    ID = None

    d = datetime.datetime(year, month, day)

    if not caregiver_available(d):
        print("No caregiver is available at this time")
        print("Please select other date!")
        return

    try:
        # Check if the current vaccine has enough doses
        available_dose = Vaccine.get_doses(vaccine)

        caregiver = Caregiver.random_caregiver(d)
        patient = current_patient.get_username()
        print("The caregiver at "+date+" is:"+caregiver)
        # print("Your name is: "+patient)
        ID = Appointment.create_id()

        print()
        print("******Here is your information of appointment:******")
        # print(ID, date, patient, caregiver, vaccine)
        print("Appointment ID: %d" % ID)
        print("Appointment date: %s" % date)
        print("Patient name: %s" % patient)
        print("Caregiver name: %s" % caregiver)
        print("Vaccine: %s" % vaccine)
        appointment = Appointment(ID, date, patient, caregiver, vaccine)
        appointment.save_to_db()
        print()
        print("*** Appointment made successfully!**")
        # upload available doses
        Vaccine.update_available_doses(vaccine, available_dose)
        # upload availability pf caregiver
        Caregiver.delete_availability(caregiver, d)

    except ValueError:
        print("Please enter a valid date!")


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def show_appointments():
    #  check 1: check if the current user is patient or caregiver
    global current_caregiver
    global current_patient

    Name = None
    if current_caregiver:
        Name = current_caregiver.get_username()
        print("You logged in as a caregiver"+Name)
        print("******Here is your information of appointment:******")
        Appointment.get_caregiver(Name)

    elif current_patient:
        Name = current_patient.get_username()
        print("You logged in as a patient:"+Name)
        print("******Here is your information of appointment:******")
        Appointment.get_patient(Name)
    else:
        print("Please login first!")
        return


def cancel(tokens):
    if len(tokens) != 2:
        print("Please try again!")
        return

    global current_caregiver
    global current_patient

    ID = int(tokens[1])
    time = Appointment.get_date(ID)
    name = Appointment.get_caregivername(ID)

    if current_caregiver:
        Name = current_caregiver.get_username()
        print("You logged in as a caregiver"+Name)
        Appointment.cancel_appointment(ID)
        current_caregiver.upload_availability(time)
        print("You cancel the appointment "+str(ID)+" Successfully")

    elif current_patient:
        Name = current_patient.get_username()
        print("You logged in as a patient:"+Name)
        Appointment.cancel_appointment(ID)
        Caregiver.add_availability(name, time)
        print("You cancel the appointment "+str(ID)+" Successfully")

    else:
        print("Please login first!")
        return


# 3 different Vaccines used in the db: Pfizer, Moderna, Janssen
def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            vaccine.save_to_db()
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error:
            print("Error occurred when adding doses")

    print("Doses updated!")


def logout():
    global current_patient
    global current_caregiver

    if current_caregiver is not None:
        print("Caregiver logged out successfully")
        current_caregiver = None

    if current_patient is not None:
        print("Patient logged out successfully ")
        current_patient = None


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")

        print("> create_patient <username> <password>")
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")
        print("> login_caregiver <username> <password>")

        print("> search_caregiver_schedule <date>")
        print("> reserve <date> <vaccine>")
        print("> upload_availability <date>")

        print("> cancel <appointment_id>")
        print("> add_doses <vaccine> <number>")

        print("> show_appointments")
        print("> logout")
        print("> quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments()
        elif operation == "logout":
            logout()
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
