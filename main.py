import mysql.connector
from mysql.connector import Error
import PySimpleGUI as sg
from datetime import datetime


timesls = ['11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'] #time slots list
roomn = ['R1', 'R2', 'R3', 'R4', 'R5']  #room numbers list

#GUI Layout
sg.theme('Dark Blue 14')
layout = [[sg.Text('Organiser:'), sg.Input(key='-org-')],
          [sg.Text('Attendees:'), sg.Input(key='-atten-')],
          [sg.Text('Date:'), sg.Input(key='-date-'), sg.CalendarButton('Choose Date', format='%Y-%m-%d', target='-date-')],
          [sg.Text('Time Slot:'), sg.Combo(timesls, key='-timeslot-')],
          [sg.Text('Room Number:'), sg.Combo(roomn, key='-roomno-')],
          [sg.Text('Status: '), sg.Text('', size=(50, 1), key='-alert-')],
          [sg.Button('Schedule'), sg.Button('Exit')]]

try:
    #connecting to the MySQL database
    connection = mysql.connector.connect(host='sql6.freesqldatabase.com',
                                         database='sql6428528',
                                         user='sql6428528',
                                         password='57aq4RsVqN')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("SELECT database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        cursor.execute("SELECT * FROM meetings;")
        records = cursor.fetchall()
        print("Total number of rows in table: ", cursor.rowcount)

except Error as e:
    print("Error while connecting to MySQL", e)
i = 1
window = sg.Window('Meeting Scheduler', layout)
def checkSchedule():

    #getting values from GUI
    orgInput = values['-org-']
    atten = values['-atten-']
    date = values['-date-']
    time = values['-timeslot-']
    rno = values['-roomno-']
    today = datetime.today().strftime('%Y-%m-%d')
    test = []
    #print(orgInput, atten, date, time, rno)

#Checks Organiser Conflict
    cursor.execute("SELECT * FROM `meetings` WHERE Organiser = %s AND "
                   "MeetingDate = %s AND "
                   "MeetingTimeSlot = %s ", (orgInput, date, time))
    ocon = cursor.fetchall()    #ocon = organiser conflict
    #print(ocon)

# Checks Organiser Conflict in Attendees
    cursor.execute("SELECT * FROM `meetings` WHERE FIND_IN_SET(%s, Attendees) AND "
                   "MeetingDate = %s AND "
                   "MeetingTimeSlot = %s ", (orgInput, date, time))
    ocona = cursor.fetchall()   #ocona = organiser conflict in attendees
    #print(ocona)

#Checks Attendee Conflict
    indivisualatten = atten.replace(' ','').split(',') #seperates the attendees list
    ne = ne1 = 0  #ne = not empty
    em = em1 = 0  #em = empty
    for i in indivisualatten: #loops through each attendee
        temp = i
        cursor.execute("SELECT * FROM meetings WHERE FIND_IN_SET(%s, Attendees) AND "
                       "MeetingDate = %s AND "
                       "MeetingTimeSlot = %s  ", (temp, date, time))

        acon = cursor.fetchall()    #acon = attendees conflict
        if (acon != test):
            ne = ne + 1
        else:
            em = em + 1

# Checks Attendees Conflict in Organiser
    for j in indivisualatten:
        temp1 = j
        cursor.execute("SELECT * FROM meetings WHERE Organiser = %s AND "
                       "MeetingDate = %s AND "
                       "MeetingTimeSlot = %s", (temp1, date, time))
        acono = cursor.fetchall()   #acono = attendees conflict in organiser
        if(acono != test):
            ne1 = ne1 + 1
        else:
            em1 = em1 + 1

#Checks Room Conflict
    cursor.execute("SELECT * FROM meetings WHERE Room = %s AND "
                   "MeetingDate = %s AND "
                   "MeetingTimeSlot = %s", (rno, date, time))
    rcon = cursor.fetchall()    #rcon = room conflict


    if test != ocon:
        print('Schedule Conflict Detected! \nPlease choose another DATE/TIME.\n')
        window['-alert-'].update("Schedule Conflict Detected! Please choose another DATE/TIME.", text_color='orange red')

    elif test != ocona:
        print('Schedule Conflict Detected! \nPlease choose another DATE/TIME.\n')
        window['-alert-'].update("Schedule Conflict Detected! Please choose another DATE/TIME.", text_color='orange red')

    elif ne != 0:
        print('Schedule Conflict Detected! \nPlease choose another DATE/TIME.\n')
        window['-alert-'].update("Schedule Conflict Detected! Please choose another DATE/TIME.", text_color='orange red')

    elif ne1 != 0:
        print('Schedule Conflict Detected! \nPlease choose another DATE/TIME.\n')
        window['-alert-'].update("Schedule Conflict Detected! Please choose another DATE/TIME.", text_color='orange red')

    elif test != rcon:
        print('Schedule Conflict Detected! \nPlease choose another Room.\n')
        window['-alert-'].update("Schedule Conflict Detected! Please choose another Room.", text_color='orange red')

    #checks if the textfileds are empty
    elif orgInput == '' or atten == '' or date == '' or time == '' or rno == '':
        window['-alert-'].update("Please fill all text fields.", text_color='orange red')

    #checks if the date is a past date
    elif date < today:
        print("Please select future dates")
        window['-alert-'].update("Please select future dates!", text_color='orange red')

    #no conflict case -> schedules meeting
    else:
        nospaceatten = atten.replace(' ', '') #removes whitespaces from attendees
        print('No Schedule Conflicts Detected \nScheduling Meeting...')
        cursor.execute("INSERT into meetings (Organiser, Attendees, MeetingDate, MeetingTimeSlot, Room)"
                       "VALUES(%s, %s, %s, %s, %s)", (orgInput, nospaceatten, date, time, rno))
        connection.commit()
        print('Meeting Scheduled.')
        window['-alert-'].update("Your Meeting is Scheduled!", text_color='green')


while True:
        event, values = window.Read()

        if event == 'Schedule':
            checkSchedule()


        elif event is None or event == 'Exit':
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
            break
            window.close()



