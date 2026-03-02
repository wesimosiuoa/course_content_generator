

def insert (connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
def select (connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        raise e 
    
    finally:
        cursor.close()
def update (connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()

def delete (connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()

def select_one (connection, query, params=None):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    except Exception as e:
        raise e 
    finally:
        cursor.close()

def select_all(conn, query, params=None):
    cursor = conn.cursor(dictionary=True)   # 👈 THIS IS CRITICAL
    cursor.execute(query, params or ())
    results = cursor.fetchall()
    cursor.close()
    return results