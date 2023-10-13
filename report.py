import os
from datetime import datetime, timedelta
import database
import pandas as pd


# Dictionary to track the status of report generation
report_status = {}

# Define the directory to store generated reports
reports_directory = "reports"
if not os.path.exists(reports_directory):
    os.makedirs(reports_directory)


# Function to calculate uptime and downtime for a store
def calculate_uptime_downtime(store_id, current_timestamp, df_store, business_hours):
    # Calculate timestamps for the last hour, day, and week
    start_time_hour = current_timestamp - \
        timedelta(minutes=60)
    start_time_day = current_timestamp - \
        timedelta(minutes=1440)
    start_time_week = current_timestamp - \
        timedelta(minutes=10080)

    # Filter data for the store and the time period of last week
    observations = df_store[(df_store['store_id'] == store_id) &
                            (df_store['timestamp_local'] >= start_time_week) &
                            (df_store['timestamp_local'] <= current_timestamp)]

    # If there are no business hours defined, assume 24/7 availability
    if business_hours.empty:
        business_hours = pd.DataFrame([{'day': i, 'start_time_local': '00:00:00',
                                        'end_time_local': '23:59:59'} for i in range(7)])

    total_uptime_hour = 0
    total_downtime_hour = 0

    total_uptime_day = 0
    total_downtime_day = 0

    total_uptime_week = 0
    total_downtime_week = 0

    last_observation_time = None

    # Iterate through observations and calculate uptime and downtime for last hour, day and week
    for index, observation in observations.iterrows():
        timestamp = observation['timestamp_local']
        status = observation['status']

        day_of_week = timestamp.weekday()
        business_hour_row = business_hours[business_hours['day']
                                           == day_of_week]
        if not business_hour_row.empty:
            start_time_local = datetime.strptime(
                business_hour_row['start_time_local'].values[0], "%H:%M:%S")
            end_time_local = datetime.strptime(
                business_hour_row['end_time_local'].values[0], "%H:%M:%S")

            if start_time_local.time() <= timestamp.time() <= end_time_local.time():
                if last_observation_time is not None:
                    time_difference = (
                        timestamp - last_observation_time).total_seconds() / 60
                    if status == 'active':
                        if timestamp >= start_time_hour:
                            total_uptime_hour += time_difference
                        if timestamp >= start_time_day:
                            total_uptime_day += time_difference
                        if timestamp > start_time_week:
                            total_uptime_week += time_difference
                    else:
                        if timestamp >= start_time_hour:
                            total_downtime_hour += time_difference
                        if timestamp >= start_time_day:
                            total_downtime_day += time_difference
                        if timestamp > start_time_week:
                            total_downtime_week += time_difference

        last_observation_time = timestamp

    # Handle the remaining time in the last observation
    if last_observation_time is not None:
        remaining_time = (current_timestamp -
                          last_observation_time).total_seconds() / 60
        if status == 'active':
            if last_observation_time >= start_time_hour:
                total_uptime_hour += remaining_time
            if last_observation_time >= start_time_day:
                total_uptime_day += remaining_time
            if timestamp > start_time_week:
                total_uptime_week += remaining_time
        else:
            if last_observation_time >= start_time_hour:
                total_downtime_hour += remaining_time
            if last_observation_time >= start_time_day:
                total_downtime_day += remaining_time
            if timestamp > start_time_week:
                total_downtime_week += remaining_time

    return int(total_uptime_hour), int(total_downtime_hour), int(total_uptime_day/60), int(total_downtime_day/60), int(total_uptime_week/60), int(total_downtime_week/60)


# Function to generate a report
def generate_report(report_id, db):
    (store_data_df, business_hours_df, store_timezones_df) = database.retrieve_data()

    store_data_df['timestamp_utc'] = pd.to_datetime(store_data_df['timestamp_utc'], format="%Y-%m-%d %H:%M:%S.%f %Z",
                                                    errors="coerce").fillna(pd.to_datetime(store_data_df['timestamp_utc'], format="%Y-%m-%d %H:%M:%S %Z", errors="coerce"))

    # Convert timestamps to local time
    store_timezone_map = dict(
        zip(store_timezones_df['store_id'], store_timezones_df['timezone_str']))
    default_timezone = "America/Chicago"

    store_data_df['timezone'] = store_data_df['store_id'].map(
        store_timezone_map)
    store_data_df['timezone'].fillna(default_timezone, inplace=True)
    store_data_df['timestamp_local'] = store_data_df.apply(
        lambda row: row['timestamp_utc'].tz_convert(row['timezone']), axis=1)

    current_timestamp = store_data_df['timestamp_utc'].max()

    store_data_df = store_data_df.sort_values(by='timestamp_local')

    store_ids = store_timezones_df['store_id'].unique()
    n = len(store_ids)

    report_filepath = os.path.join("reports", f"report_{report_id}.csv")

    # For each store id generate report and store it into a csv file
    with open(report_filepath, "a") as file:
        file.write("store_id,uptime_last_hour(in minutes),uptime_last_day(in hours),update_last_week(in hours),downtime_last_hour(in minutes),downtime_last_day(in hours),downtime_last_week(in hours)\n")

        for i in range(n):
            id = store_ids[i]
            business_hours = business_hours_df[business_hours_df['store_id'] == id]
            result = calculate_uptime_downtime(
                id, current_timestamp, store_data_df, business_hours)
            file.write(
                f"{id},{result[0]},{result[2]},{result[4]},{result[1]},{result[3]},{result[5]}\n")
            if i % 100 == 0:
                print(f"Debug: {report_id} progress --> {i}/{n}\n")

    report_status[report_id] = "Complete"
