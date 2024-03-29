from datetime import datetime, timedelta
from settings import NID1, Password1, SID1, Name1, NID2, Password2, SID2, Name2
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import datetime as dt
import calendar
import time
import pytz


reservation_date = dt.datetime.now()+timedelta(days=7)

reservation_rooms = ["370B", "370A", "381", "386", "176", "172",
                     "377", "378", "379", "387", "388", "389", "371", "372", "373"]

url = "https://ucf.libcal.com/spaces?lid=2824&gid=4780&c=0"


def main():
    print("Date Reserveing: " +
          reservation_date.strftime("%B %d, %Y").replace(' 0', ' '), flush=True)

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    driver1 = webdriver.Remote(
        "http://172.17.0.2:4444", options=webdriver.ChromeOptions())
    driver1.get(url)
    gotoday(driver1)
    ReserveEngine(driver1, datetime.strptime("10:00am", "%I:%M%p"), datetime.strptime(
        "2:00pm", "%I:%M%p"), NID1, Password1, SID1, Name1)
    ReserveEngine(driver1, datetime.strptime("2:00pm", "%I:%M%p"), datetime.strptime(
        "6:00pm", "%I:%M%p"), NID2, Password2, SID2, Name2)
    Exit(driver1)
    # driver3 = webdriver.Chrome()
    # driver3.get(url)
    # gotoday(driver3)
    # ReserveEngine(driver3, datetime.strptime("6:00pm", "%I:%M%p"), datetime.strptime("10:00pm", "%I:%M%p"), "NID" , "PASSWORD", "PID", "RESERVATION NAME")

# confirms availability and calls reserve fuction to reserve it.


def ReserveEngine(driver, start, finish, nid, passwrd, pid, name):
    i = 0
    while True:
        if checkavailable(driver, i, start, finish):
            print("Reserving Room: " + reservation_rooms[i], flush=True)
            reserve(driver, i, start, finish, nid, passwrd, pid, name)
            break
        else:
            print("Could not reserve: " + reservation_rooms[i], flush=True)
            i += 1

# Log In function


def login(driver, username, password, name):
    print("Logging In As "+name, flush=True)
    username_field = driver.find_element(
        "xpath", "//input[@id='userNameInput']")
    username_field.send_keys(username)
    password_field = driver.find_element(
        "xpath", "//input[@id='passwordInput']")
    password_field.send_keys(password)
    sign_on_button = driver.find_element("xpath", "//span[@id='submitButton']")
    sign_on_button.click()
    time.sleep(5)
    print("Logged In Sucessfully As "+name, flush=True)

# Log out function


def logout(driver, name):
    print("Logging out As "+name, flush=True)
    driver.find_element(By.LINK_TEXT, "Logout").click()
    print("Logged out Sucessfully As "+name, flush=True)
    driver.get(url)
    gotoday(driver)


# Room reservation function

def reserve(driver, roomInt, start, finish, nid, passwrd, pid, name):
    times = getTimesInList(start, finish)
    print(times[0]+" to "+times[len(times)-1]+" on " +
          reservation_date.strftime("%A, %B %d, %Y").replace(' 0', ' '), flush=True)
    myTimes = ListAvailablesStrings(start, finish, reservation_rooms[roomInt])
    temp = driver.find_element(
        "xpath", "//a[@class='fc-timeline-event fc-h-event fc-event fc-event-start fc-event-end fc-event-future s-lc-eq-avail' and @aria-label='"+myTimes[0]+"']")
    driver.execute_script("arguments[0].click();", temp)
    time.sleep(4)
    dropdown = driver.find_element(
        "xpath", "//select[@class='form-control input-sm b-end-date']")
    dropselect = Select(dropdown)
    dropselect.select_by_visible_text(times[len(
        times)-1]+" "+reservation_date.strftime("%A, %B %d, %Y").replace(' 0', ' '))
    time.sleep(3)
    driver.find_element("xpath", "//button[@id='submit_times']").click()
    time.sleep(2)
    login(driver, nid, passwrd, name)
    time.sleep(2)
    driver.find_element(
        "xpath", "//button[@class='btn btn-primary' and @name='continue']").click()
    driver.find_element("xpath", "//input[@name='nick']").send_keys(name)
    dropdown = driver.find_element("xpath", "//select[@name='q2613']")
    dropselect = Select(dropdown)
    dropselect.select_by_visible_text("Undergraduate Student")
    driver.find_element("xpath", "//input[@id='q2614']").send_keys(pid)
    driver.find_element(
        "xpath", "//button[@type='submit' and @id='btn-form-submit']").click()
    time.sleep(3)
    print("Booked Room: " + reservation_rooms[roomInt], flush=True)
    logout(driver, name)
    # Exit(driver)


# Helper Functions: #

def date_to_unix_timestamp(date):
    date_object = dt.datetime.strptime(
        date, '%Y-%m-%d').replace(tzinfo=pytz.timezone('GMT'))
    return (int(date_object.timestamp())) * 1000


# changes current date to reservation date to list availability

def gotoday(driver):
    driver.find_element(
        "xpath", "//button[@class='fc-goToDate-button btn btn-default btn-sm' and @aria-label='Go To Date']").click()
    if (driver.find_element("xpath", "//th[@class='datepicker-switch'and @colspan='5']").text != reservation_date.strftime("%B %Y")):
        driver.find_element("xpath", "//th[@class='next']").click()
        print("Going to: "+driver.find_element("xpath",
              "//th[@class='datepicker-switch'and @colspan='5']").text, flush=True)
    driver.find_element("xpath", "//td[@data-date='" + str(
        date_to_unix_timestamp(reservation_date.strftime("%Y-%m-%d"))) + "']").click()
    time.sleep(1)


# creates list of all reservation time (every 30 mins)

def getTimesInList(start, end):
    times = []
    while start <= end:
        times.append(start.strftime("%I:%M%p").lstrip('0').lower())
        start += timedelta(minutes=30)
    return times


# Creates list of availablity strings

def ListAvailablesStrings(start, end, roomToReseve):
    i = 0
    finals = []
    times = getTimesInList(start, end)
    while start <= end:
        finals.append(times[i]+" "+reservation_date.strftime("%A, %B %d, %Y").replace(
            ' 0', ' ')+" - Room "+roomToReseve+" - Available")
        start += timedelta(minutes=30)
        i = i + 1
    return finals

# Checks for availability


def checkavailable(driver, roomNum, start, finish):
    myTimes = ListAvailablesStrings(start, finish, reservation_rooms[roomNum])
    try:
        for i in range(len(myTimes)):
            driver.find_element(
                "xpath", "//a[@class='fc-timeline-event fc-h-event fc-event fc-event-start fc-event-end fc-event-future s-lc-eq-avail' and @aria-label='"+myTimes[i]+"']")
        return True
    except Exception:
        return False


def Exit(driver):
    print("Good Bye", flush=True)
    driver.close()

# Calling Main: #


main()
