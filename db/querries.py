
import mysql.connector
import logging

logging.basicConfig(filename='xe_scrapper.log', level=logging.DEBUG) # encoding='utf-8'


def insert_variables_into_table(property_id, property_url, bedroom, bathroom, floor, house_reconstruction,
                                building_space, compass, title, price, door, canopy, heating, description, has_oil):
    connection = None
    try:
        # In MySQL 8.0, caching_sha2_password is the default authentication plugin rather than mysql_native_password.
        connection = mysql.connector.connect(host='localhost',
                                             database='xedb',
                                             user='root',
                                             password='ctfVGBUIJ67gyBUINXERCTr6vt7bHNJ',
                                             auth_plugin='mysql_native_password')

        # Check if property_id exists in our database
        cursor = connection.cursor()
        query = f'SELECT property_id FROM `homes` WHERE property_id = {property_id}'
        res = cursor.execute(query)

        id_found = False
        id_fetched = cursor.fetchone()
        if type(id_fetched) == tuple:
            id_fetched = id_fetched[0]
        if id_fetched == int(property_id):
            logging.debug(f'{property_id} property_id found in db, skipping insert...')
            id_found = True

        # if the house hasn't been already stored in our database, execute insert command
        if not id_found:
            mySql_insert_query = """INSERT INTO homes (property_id, property_url, bedroom, bathroom, floor, 
                                        house_reconstruction, building_space, compass, title, price, door, canopy, heating,
                                        description, has_oil) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            record = (property_id, property_url, bedroom, bathroom, floor, house_reconstruction, building_space, compass,
                      title, price, door, canopy, heating, description, has_oil)
            cursor.execute(mySql_insert_query, record)
            connection.commit()
            logging.debug("Record inserted successfully into homes table")

    except mysql.connector.Error as error:
        logging.error("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logging.debug("MySQL connection is closed")

    return not id_found
