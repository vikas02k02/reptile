from flask import Flask, render_template, request, jsonify, session
import pandas as pd
from imports.rto_contacts_dl import rto_contacts_dl
from imports.rto_contacts_rc import rto_contacts_rc
from sp import call_chatbot_stored_procedure
from format_datetime import format_datetime_columns

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def process_data(result, dl_rc_type):

    if result:

        if dl_rc_type == 'DL':

            df = pd.DataFrame(result, columns=['ApplicationNo', 'RTOcode', 'RecievedDateTime', 'PrintStatus', 'PrintDateTime'])

        elif dl_rc_type == 'RC':

            df = pd.DataFrame(result, columns=['ApplicationNo', 'RTOcode', 'RecievedDateTime', 'PrintStatus', 'PrintDateTime'])
        
        df = format_datetime_columns(df)

        response = generate_print_message(df, dl_rc_type)

        fixed = f"Dear User,<br>Your application {df['ApplicationNo'][0]} recieved on {df['RecievedDateTime_Date'][0]} at {df['RecievedDateTime_Time'][0]} "

        return fixed, response
    
    else:
        fixed = f"Dear User,"
        response =f"<br>Please enter a valid application number:"
        return fixed, response


def generate_print_message(df, dl_rc_type):

    if dl_rc_type == 'DL':

        if df['PrintStatus'][0] == 'COM':
            rto_code = df['RTOcode'][0] 

            if rto_code in rto_contacts_dl:
                rto_info = rto_contacts_dl[rto_code]
                response = f"<br>DL has been printed on {df['PrintDateTime_Date'][0]} at {df['PrintDateTime_Time'][0]}<br>Card handed over to department SPOC.<br>Mr {rto_info['name']} {rto_code}<br>Contact: {rto_info['contact']}<br>Thank you for reaching out"

            else:
                response = f"<br>DL has been printed on {df['PrintDateTime_Date'][0]} at {df['PrintDateTime_Time'][0]}<br>Pending for card handover to department<br>Thank you for reaching out"

        elif df['PrintStatus'][0] in ['P', 'WIP', 'PWIP']:

            response = f"<br>Your Driving Licence application is pending for print<br>Thank you for reaching out"
        
        else:
            response = f"<br>Your Driving Licence application is pending for print<br>Thank you for reaching out"


    elif dl_rc_type == 'RC':

        if df['PrintStatus'][0] == 'COM':
            rto_code = df['RTOcode'][0] 

            if rto_code in rto_contacts_rc:
                rto_info = rto_contacts_rc[rto_code]
                response = f"<br>DL has been printed on {df['PrintDateTime_Date'][0]} at {df['PrintDateTime_Time'][0]}<br>Card handed over to department SPOC.<br>Mr {rto_info['name']} {rto_code}<br>Contact: {rto_info['contact']}<br>Thank you for reaching out"

            else:
                response = f"<br>DL has been printed on {df['PrintDateTime_Date'][0]} at {df['PrintDateTime_Time'][0]}<br>Pending for card handover to department<br>Thank you for reaching out"

        elif df['PrintStatus'][0] in ['P', 'WIP', 'PWIP']:

            response = f"<br>Your Driving Licence application is pending for print<br>Thank you for reaching out"

    return response


@app.route('/', methods=['GET', 'POST'])
def main_chat(): 
    if request.method == 'GET':
        initial_message = "Hello! I'm your URJA assistant to help you with print status of your Driving license and Registration certificate. Please select DL & RC Type​"
        return render_template('chatbot.html', initial_message=initial_message)
    
    elif request.method == 'POST':
        user_input = request.json.get('user_input')
        
        if user_input == 'DL':
            response = "Please enter your DL Application Number:"
            session['conversation_stage'] = 'DL_stage'
            session['query_type'] = "APPLICATION_DETAILS"
            session['dl_rc_type'] = "DL"

        elif user_input == 'RC':
            response = "Please enter your RC Application Number:"
            session['conversation_stage'] = 'RC_stage'
            session['query_type'] = "APPLICATION_DETAILS"
            session['dl_rc_type'] = "RC"
                
        elif 'conversation_stage' in session:
            if session['conversation_stage'] in ['DL_stage', 'RC_stage']:

                if user_input:
                    result = call_chatbot_stored_procedure(session['query_type'], user_input, session['dl_rc_type'])
                    fixed, output = process_data(result, session['dl_rc_type'])
                    response = f"{fixed} {output}"
                else:
                    response = "Please enter a valid application number."
            else:
                response = "Invalid conversation stage"
        else:
            response = "Please select DL or RC to start."
        
        return jsonify({'response': response})

@app.route('/clear-session', methods=['POST'])
def clear_session():
    try:
        data = request.json
        if data and 'conversation_stage' in data and data['conversation_stage'] == True:
            session.pop('conversation_stage', None)
            session.pop('query_type', None)
            session.pop('dl_rc_type', None)
            return jsonify({'message': 'Session cleared successfully'}), 200
        else:
            return jsonify({'error': 'Invalid request data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)