import mysql.connector

from mysql.connector import errorcode

from typing import Optional, Tuple



# --- Database Configuration ---

# IMPORTANT: These are the credentials you provided.

DB_CONFIG = {

    'user': 'root',

    'password': 'Anikul@2143',

    'host': '127.0.0.1',  # or 'localhost'

    'database': 'Project'

}



# --- SQL Statements ---

# Note: The 'age' column has been removed as per your request.

TABLES = {}

TABLES['employee'] = (

    "CREATE TABLE IF NOT EXISTS `employee` ("

    "  `id` INT AUTO_INCREMENT PRIMARY KEY,"

    "  `first_name` VARCHAR(50) NOT NULL,"

    "  `last_name` VARCHAR(50) NOT NULL,"

    "  `email` VARCHAR(100) UNIQUE NOT NULL,"

    "  `hire_date` DATE NOT NULL,"

    "  `salary` DECIMAL(10,2) NOT NULL,"

    "  `department` VARCHAR(50)"

    ") ENGINE=InnoDB")



INSERT_EMPLOYEES_SQL = (

    "INSERT INTO employee "

    "(first_name, last_name, email, hire_date, salary, department) "

    "VALUES (%s, %s, %s, %s, %s, %s)"

)



# Sample data to be inserted (without 'age')

employees_data = [

    ('John', 'Doe', 'john.doe@example.com', '2022-01-15', 60000.00, 'Engineering'),

    ('Jane', 'Smith', 'jane.smith@example.com', '2021-07-01', 75000.00, 'Marketing'),

    ('Alice', 'Johnson', 'alice.johnson@example.com', '2023-03-10', 50000.00, 'Sales'),

    ('Bob', 'Brown', 'bob.brown@example.com', '2020-11-20', 80000.00, 'HR'),

    ('Tom', 'Brown', 'tom.brown@example.com', '2020-11-20', 80000.00, 'HR') # Corrected email

]





def main():

    """

    Main function to connect to the database, create the table,

    insert the data, and display the results.

    """

    cnx = None

    try:

        # Establish the database connection

        print("Connecting to the database...")

        cnx = mysql.connector.connect(**DB_CONFIG)

        cursor = cnx.cursor()

        print("Connection successful.")



        # --- Create the table ---

        table_name = 'employee'

        print(f"Creating table `{table_name}`... ", end='')

        # Using "CREATE TABLE IF NOT EXISTS" is safer

        cursor.execute(TABLES[table_name])

        print("OK")





        # --- Insert the data ---

        # To avoid re-inserting data every time, we can check if the table is empty

        cursor.execute("SELECT COUNT(*) FROM employee")

        result = cursor.fetchone()  # type: ignore

        if result and result[0] == 0:

            print(f"Inserting data into `{table_name}`...")

            # The executemany() method is efficient for inserting multiple rows.

            cursor.executemany(INSERT_EMPLOYEES_SQL, employees_data)

            # Commit the transaction to make the changes permanent

            cnx.commit()

            print(f"{cursor.rowcount} records inserted successfully.")

        else:

            print("Data already exists in the employee table. Skipping insertion.")





        # --- Fetch and display the data in a tabular format ---

        print("\n--- Employee Data ---")

        cursor.execute("SELECT id, first_name, last_name, email, hire_date, salary, department FROM employee")



        # Get column names from the cursor description

        columns = [desc[0] for desc in cursor.description]

        # Fetch all rows

        rows = cursor.fetchall()



        if not rows:

            print("No data found in the employee table.")

            return



        # Create a format string for the header and rows

        # We'll give each column a fixed width for alignment

        header_format = "{:<5} {:<15} {:<15} {:<30} {:<15} {:<15} {:<15}"

        row_format = "{:<5} {:<15} {:<15} {:<30} {:<15} {:<15.2f} {:<15}"



        # Print header

        print(header_format.format(*columns))

        print("-" * 110) # Separator line



        # Print each row

        for row in rows:

            # Convert date object to string for formatting

            formatted_row = list(row)

            formatted_row[4] = str(row[4])

            print(row_format.format(*formatted_row))



    except mysql.connector.Error as err:

        # Handle potential connection or SQL errors

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:

            print("Something is wrong with your user name or password")

        elif err.errno == errorcode.ER_BAD_DB_ERROR:

            print("Database does not exist")

        else:

            print(err)

        # If an error occurs, roll back any changes

        if cnx and cnx.is_connected():

            print("Rolling back changes.")

            cnx.rollback()



    finally:

        # --- Clean up ---

        # Ensure the connection is always closed

        if cnx and cnx.is_connected():

            cursor.close()

            cnx.close()

            print("\nMySQL connection is closed.")



if __name__ == '__main__':

    main()