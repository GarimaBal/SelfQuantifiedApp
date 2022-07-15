# SelfQuantifiedApp

LOGIN and SIGNUP:
A QuantifiedSelfApp was created for the final project of my modern application development course. When the application starts running, the user sees a welcome message and the options to sign up and login. If the user does not have a username, they can click on sign up with a unique username or they can log in with an existing 
username.

Username has to be unique. When signing up with an existing user name, user is given an appropriate message along with the options to go back to the sign up page or to the login page. If the user tries to log in with a username that does not exist in the database, they are given an appropriate message along with the option to sign up.

After signing up successfully, the user is taken to the login page where they must login. Once successfully logged in, they given a message confirming that they are logged in and are given the option to enter their userpage. The login and sign up page have a slot for password as well but this slot is non-functional, only username is required.


DASHBOARD:

Once a user clicks on ‘Proceed to userpage’ after logging in, they are taken to their Dashboard. On this page all the trackers associated with the username are displayed. Along side the tracker name is the Last Tracker time which displays the last time the tracker was logged and a set of actions that can be 
taken. The actions present for a tracker are New entry, edit and delete. The user also has the option to create a new tracker and logout below the tracker table. The trackers on the tracker table are separated by a line for minimal aesthetics and clear organisation. The tracker names are hyperlinked to redirect users to the logpage.

The edit option take user to the edit tracker page where they can edit the name, description and settings associated with a tracker, in case of Multiple choice trackers, comma-separated values in the setting will be displayed as the option while logging so that user can only edit the existing settings or add comma-separate values but not reduce them. The tracker type is also displayed on the edit page but is a disabled field which means that it cannot be changed. The user can make changes and submit which will bring them back to the dashboard or they have the option to click on ‘Back to Dashboard’ to return without making any changes. The existing value of the field are displayed on this page.

The delete option can be used to delete a tracker and all the associated logs in the backend. After deletion is complete the user is directed to the dashboard.
The new entry option is used to redirect users to a page where they can make a new log for a particular tracker. ‘log tracker:’ along with the tracker name is displayed as the heading of this page. The timestamp is displayed along with the appropriate fields to record the value. The input type of the numerical type log and the time duration type log have to be a numbers, for time duration the value has to be in minutes. For Boolean type log and Multiple choice type log, radio type buttons are displayed for with the available options, for Boolean log True and False are the only options. Once all the details are filled by the user, they can either click on ‘Log it’ to go back to the dashboard with the log stored or they can click on ‘Back to Dashboard’ to abandon the entry and go back to the dashboard.

If a user does not have any tracker associated with their username, an appropriate message is displayed along with the options to create a new tracker or logout.


CREATE TRACKER:

The create tracker page has an appropriate heading with fields to enter the tracker name, description and settings. There is a dropdown to select the tracker type next to which is a submit button to finalise the changes and redirect the user to dashboard. The user also has the option to abort creating a tracker by clicking in the ‘Back to Dashboard’ option. The settings option on this page is required if the tracker type is multiple choice. They need to be comma separated values and this message is presented on this page.


LOGPAGE:

The log page for a tracker that can be accessed by clicking on the hyperlinked name of a tracker on the dashboard displays all the logs associated with a particular tracker. This includes the date and time of the log, the value of the log, the notes entered and action buttons that can be used to edit or delete a log. This page has the option to go back to the dashboard and create a new entry into the log. Below these options is a heading called ‘Data Tables’ which have the option to view data tables and graphs for specific time periods.

The Edit button along side a log will take the user to the log edit page where they will be able to edit the value associated with that log and the notes associated with a log.

The Delete button can be used to delete a particular log


DATA TABLES:

Data pages for various time durations are displayed at the bottom of the log page. The options include 1 week, 1 month, 6 month, 1 year and All time. Upon clicking them, the user is taken to a page similar to the log page where the logs in that time frame are displayed along with the graph for the values in 
that time frame.
