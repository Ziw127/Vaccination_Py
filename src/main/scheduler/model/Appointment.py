import pymssql
import random
from db.ConnectionManager import ConnectionManager
from util.Util import Util
import sys
from random import choice
sys.path.append("../util/*")
sys.path.append("../db/*")


class Appointment:
    def __init__(self, ID, date, pname, cname, vname):
        self.ID = ID
        self.date = date
        self.pname = pname
        self.cname = cname
        self.vname = vname

    # get the appointment of patient
    def get_patient(patient_name):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT id, vname, time, cname FROM Appointments WHERE pname = %s"
        try:
            cursor.execute(get_patient_details, patient_name)
            for row in cursor:
                print("Appointment ID: " + str(row['id']))
                print("Vaccine: "+str(row['vname']))
                print("Time: "+str(row['time']))
                print("Caregiver: "+str(row['cname']))
        except pymssql.Error:
            print("Error occurred when getting Patient")
            cm.close_connection()

        cm.close_connection()
        return None

    # get the appointment of caregiver
    def get_caregiver(caregiver_name):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT id, vname, time, pname FROM Appointments WHERE cname = %s"
        try:
            cursor.execute(get_caregiver_details, caregiver_name)
            for row in cursor:
                print("Appointment ID: " + str(row['id']))
                print("Vaccine: "+str(row['vname']))
                print("Time: "+str(row['time']))
                print("Patient: "+str(row['pname']))
        except pymssql.Error:
            print("Error occurred when getting Caregivers")
            cm.close_connection()

        cm.close_connection()
        return None

    def get_date(id):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_date_details = "SELECT * FROM Appointments WHERE id = %d"
        try:
            cursor.execute(get_date_details, id)
            for row in cursor:
                return row['time']
        except pymssql.Error:
            print("Error occurred when getting date")
            cm.close_connection()
        cm.close_connection()
        return None

    def get_caregivername(id):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_date_details = "SELECT * FROM Appointments WHERE id = %d"
        try:
            cursor.execute(get_date_details, id)
            for row in cursor:
                return row['cname']
        except pymssql.Error:
            print("Error occurred when getting date")
            cm.close_connection()
        cm.close_connection()
        return None

    def create_id():
        a = random.randint(1, 300)  # create ID radomly
        return a

    def get_id(self):
        return self.ID

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointment = "INSERT INTO Appointments VALUES (%d, %s, %s,%s,%s)"
        try:
            cursor.execute(
                add_appointment, (self.ID, self.date, self.vname, self.cname, self.pname))
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Appointment")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    def cancel_appointment(n):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointment = "DELETE FROM Appointments WHERE id= %d"
        try:
            cursor.execute(
                add_appointment, (n))
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when deleting")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()
