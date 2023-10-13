# Report Generation

This Python project is designed to generate reports for multiple stores and calculate the uptime and downtime of these stores. The script uses Flask as the web framework, SQLite as the database for storing data, and Pandas for data manipulation.

> This algorithm takes ~ 1 min per 100 stores on an i7 12th Gen CPU

> So, for the given data size of 13559 stores
> the report will be generated in around 3 hours.

## Database Setup
We begin by establishing a connection to an SQLite database (`loop.db`) and creating three tables:
1. `store_data`: To store observational data for stores, including `store_id`, `timestamp_utc`, and `status`.
2. `business_hours`: To store business hours for stores, including `store_id`, `day_of_week`, `start_time_local`, and `end_time_local`.
3. `store_timezones`: To store store timezones, mapping `store_id` to a `timezone_str`.

## Data Import
After creating the tables, the we read data from three CSV files (`store_data.csv`, `business_hours.csv`, and `store_timezones.csv`) and populate the corresponding tables in the SQLite database. This data import enables subsequent analysis.

## Flask Application
A Flask web application is created for triggering report generation and providing access to the generated reports. A breakdown of the Flask-related components:

### Endpoints
1. `/trigger_report` (GET): This endpoint triggers the report generation process. It generates a unique report ID, initiates a new thread to run the `generate_report` function, and returns the report ID in the response.
2. `/get_report` (GET): This endpoint retrieves a generated report by report ID. It checks the status of the report generation. If the report is complete, it sends the report as a CSV file for download.

### Report Status
A dictionary named `report_status` is used to track the status of report generation. When a report is triggered, its status is set to "Running." When the report is complete, its status is updated to "Complete."

### Reports Directory
A directory named "reports" is created to store the generated reports. The `generate_report` function saves each store's uptime and downtime data in a CSV file within this directory.

## Report Generation and Uptime-Downtime Calculation Logic
The heart of the script lies in the `generate_report` function and the `calculate_uptime_downtime` function.

### `calculate_uptime_downtime` Function
This function calculates uptime and downtime for a given store within three time periods: the last hour, the last day, and the last week. It uses the following logic:

1. Determine the timestamps for the last hour, day, and week.
2. Filter observational data for the store within these time periods.
3. If business hours are defined for the store, calculate uptime and downtime based on business hours.
4. Track uptime and downtime within the specified time periods.
5. Handle the remaining time in the last observation if any.
6. Return the calculated values in minutes or hours, depending on the time period.

### `generate_report` Function
This function generates a report for all stores. It does the following:

1. Connect to the database and retrieve the required data.
2. Convert timestamps from UTC to local time for each store.
3. Determine the current timestamp, and sort the data by timestamp.
4. Loop through each store, calculate uptime and downtime using the `calculate_uptime_downtime` function, and write the results to a CSV file.
5. Update the report's status to "Complete" when the report is generated.

## Project Setup
1. **Create a Virtual Environment (Optional)**:

   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment (Windows)
   venv\Scripts\activate

   # Activate the virtual environment (Linux/macOS)
   source venv/bin/activate
   ```

2. **Install Project Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
   
## Running the Project

1. **Run the Flask Application**: To start the Flask application, execute the following command in the project directory:

   ```bash
   python app.py
   ```

   This will start the server, and you should see a message indicating that the server is running, usually on port 3000.

   ```bash
   Server started at port 3000
   ```

2. **Interact with the Project**:
   - You can interact with the project via HTTP endpoints using a web browser or API client like [Postman](https://www.postman.com/) or `curl`.

## Using the Project

The project provides two main endpoints for interaction:

1. **Trigger Report Generation**: To initiate report generation for the stores, visit the following URL in your web browser or make a GET request using an API client:

   ```
   http://localhost:3000/trigger_report
   ```

   This will trigger the report generation process, and you will receive a unique `report_id` in the response.

2. **Get Generated Report**: To retrieve a generated report, use the `report_id` obtained from the previous step. Visit the following URL or make a GET request:

   ```
   http://localhost:3000/get_report?report_id=<report_id>
   ```

   If the report is complete, it will be available for download as a CSV file.