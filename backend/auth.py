import streamlit as st
import os
import sys
import pymysql
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from backend.database import SqlConnection

class ValidateUser:
    @staticmethod
    def validate_name(name):
        if(len(name) == 0):
            return False
        if(len(name) <= 2):
            st.error("Please Enter a Vaild Name")
            return False
        special_chars = [
        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', 
        '{', '}', '[', ']', '|', '\\', ':', ';', "'", '"', '<', '>', ',', '.', '?', '/'
        ]
        for char in name:
            if(char in special_chars or char.isdigit()):
                st.error("Please Enter a Vaild Name")
                return False
        return True
    
    @staticmethod
    def validate_email(email):
        if(len(email) == 0):
            return False
        
        if(('@' not in email)):
            st.error("Invalid Email")
            return False
        
        if(email.count("@") != 1):
            st.error("Invalid Email")
            return False
        
        if(" " in email):
            st.error("Invalid Email")
            return False
        
        local,domain = email.split("@")

        if(not local or not domain):
            st.error("Invalid Email")
            return False
        
        if("." not in domain):
            st.error("Invalid Email")
            return False

        if(domain.startswith(".") or domain.endswith(".")):
            st.error("Invalid Email")
            return False
        
        return True
    
    @staticmethod
    def validate_password(password):
        
        if(len(password) == 0):
            return False
        
        special_chars = [
        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', 
        '{', '}', '[', ']', '|', '\\', ':', ';', "'", '"', '<', '>', ',', '.', '?', '/'
        ]
        capital_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        small_letters = "abcdefghijklmnopqrstuvwxyz"

        special_chars_flag = False
        capital_case_flag = False
        small_case_flag = False
        number_flag = False

        for char in password:
            if(char in special_chars and special_chars_flag == False):
                special_chars_flag = True
            if(char in capital_letters and capital_case_flag == False):
                capital_case_flag = True
            if(char in small_letters and small_case_flag == False):
                small_case_flag = True
            if(char.isdigit() and number_flag == False):
                number_flag = True
        
        if(not(special_chars_flag and small_case_flag and capital_case_flag and number_flag)):
            st.error("Choose a Strong Password")
            return False

        return True
    

class VerifyUser:
    @staticmethod
    def if_user_exists(user_email):
        """
        Check if a user exists in the database by email using COUNT(*)
        
        Args:
            user_email (str): Email address to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        connect = SqlConnection()
        
        try:
            if connect.connect():
                sql = "SELECT COUNT(*) as count FROM users WHERE email = %s"
                
                with connect.connection.cursor() as cursor:
                    cursor.execute(sql, (user_email,))
                    result = cursor.fetchone()
                    
                    if result:
                        count = result['count']
                        return count > 0
                    else:
                        return False
                    
        except Exception as e:
            print(f"Error checking if user exists: {e}")
            return False
            
        finally:
            connect.disconnect()
        
        return False

    @staticmethod
    def verify_user(email, password):
        """
        Verify user credentials with specific exception handling
        """
        connect = SqlConnection()
        
        try:
            # Input validation - check if email and password are provided
            if not email or not password:
                raise ValueError("Email and password are required")
            
            email = str(email).strip()
            password = str(password).strip()

            if not email or not password:
                raise ValueError("Email and password cannot be empty")
            
            # Validate email length against database schema constraint (VARCHAR(100))
            if len(email) > 100:
                raise ValueError("Email exceeds maximum allowed length")
            
            
            if not connect.connect():
                raise ConnectionError("Failed to connect to database")
            
            # Verify that the users table exists in the database
            table_check_sql = "SHOW TABLES LIKE 'users'"
            with connect.connection.cursor() as cursor:
                cursor.execute(table_check_sql)
                if not cursor.fetchone():
                    raise RuntimeError("Users table not found in database")
            
            
            fetch_sql = "SELECT password FROM users WHERE email = %s"
            with connect.connection.cursor() as cursor:
                cursor.execute(fetch_sql, (email,))
                result = cursor.fetchone()
                
                if not result:
                    raise LookupError("No user found with the provided email")
                
                stored_password = result['password']
                encrypted_password = UserServies.encrypt_password(email, password)
                
                if stored_password == encrypted_password:
                    return True
                else:
                    raise PermissionError("Invalid password - authentication failed")
                    
        except ValueError as e:
            return False
            
        except ConnectionError as e:
            return False
            
        except RuntimeError as e:
            return False
            
        except LookupError as e:
            return False
            
        except PermissionError as e:
            return False
            
        except pymysql.Error as e:
            return False
            
        except Exception as e:
            return False
            
        finally:
            try:
                connect.disconnect()
            except:
                # Ignore disconnection errors during cleanup
                pass


class UserServies:

    @staticmethod
    def create_ids(uid):
        if(isinstance(uid,str)):
            raise ValueError
        id_len = 4
        if(len(str(uid)) <= 4):
            prefix_len = id_len - len(str(uid))
            return "u"+"0"*prefix_len+str(uid)
        else:
            return "u"+str(uid)
    
    @staticmethod
    def generate_user_id():
        """
        Generate a new user ID by checking the database for existing users
        
        Returns:
            int: Next available user ID
            
        Raises:
            Exception: If database connection fails or other database errors occur
        """
        connect = SqlConnection()
        
        try:
            if not connect.connect():
                raise Exception("Failed to connect to database")
            
            # Check if users table exists
            table_check_sql = "SHOW TABLES LIKE 'users'"
            with connect.connection.cursor() as cursor:
                cursor.execute(table_check_sql)
                table_exists = cursor.fetchone()
                
                if not table_exists:
                    raise Exception("Users table does not exist in database")
            
            # Get the count of existing users
            count_sql = "SELECT COUNT(*) as count FROM users"
            with connect.connection.cursor() as cursor:
                cursor.execute(count_sql)
                result = cursor.fetchone()
                
                if result:
                    user_count = result['count']
                    user_count += 1
                    uid = user_count
                else:
                    uid = 1
                    
            return UserServies.create_ids(uid)
            
        except Exception as e:
            print(f"Error generating user ID: {e}")
            raise e
            
        finally:
            connect.disconnect()

    @staticmethod
    def encrypt_password(email,password):
        local,domain = email.split("@")
        del domain
        half_local_len = len(local)//2 - 1
        new_password = local[:half_local_len] + password + local[half_local_len:]
        encrypted_password = ""
        for i in new_password:
            encrypted_password += str((ord(i)**2)+(ord(i)*5)+10) #x^2 + 5x + 10
        return encrypted_password

    @staticmethod
    def user_serialization(user_obj):
        """
        Serialize user data from User class object and insert into database
        
        Args:
            user_obj (User): User class instance with populated data:
                            - user_id: generated user ID
                            - name: user's name
                            - email: user's email
                            - password: user's hashed password
                            - user_exist: boolean flag
        
        Returns:
            str: User ID if successful
            
        Raises:
            Exception: If database operations fail or validation errors occur
        """
        connect = SqlConnection()
        
        try:
            # Validate input is User class instance
            if not hasattr(user_obj, 'user_id') or not hasattr(user_obj, 'name') or \
            not hasattr(user_obj, 'email') or not hasattr(user_obj, 'password'):
                raise ValueError("user_obj must be a User class instance with required attributes")
            
            # Validate required fields are not None or empty
            if not user_obj.user_id or not str(user_obj.user_id).strip():
                raise ValueError("User ID cannot be empty")
            
            if not user_obj.name or not str(user_obj.name).strip():
                raise ValueError("Username cannot be empty")
                
            if not user_obj.email or not str(user_obj.email).strip():
                raise ValueError("Email cannot be empty")
                
            if not user_obj.password or not str(user_obj.password).strip():
                raise ValueError("Password cannot be empty")
            
            # Connect to database
            if not connect.connect():
                raise Exception("Failed to connect to database")
            
                        
            # Validate field lengths according to database schema
            if len(str(user_obj.user_id)) > 10:
                raise ValueError("User ID cannot exceed 10 characters")
            
            if len(user_obj.name) > 50:
                raise ValueError("Username cannot exceed 50 characters")
            
            if len(user_obj.email) > 100:
                raise ValueError("Email cannot exceed 100 characters")
            
            # Prepare SQL and data tuple outside cursor block
            insert_sql = """
            INSERT INTO users (user_id, username, email, password) 
            VALUES (%s, %s, %s, %s)
            """
            
            user_tuple = (
                user_obj.user_id,
                user_obj.name,
                user_obj.email,
                user_obj.password
            )
            
            # Insert user into database
            with connect.connection.cursor() as cursor:
                affected_rows = cursor.execute(insert_sql, user_tuple)
                
                if affected_rows == 0:
                    raise Exception("Failed to insert user into database")
                
                # Commit the transaction
                connect.connection.commit()
                
                # Update user_exist flag to True after successful insertion
                user_obj.user_exist = True
                
                
            return user_obj.user_id
            
        except ValueError as ve:
            print(f"Validation error: {ve}")
            raise ve
            
        except Exception as e:
            print(f"Error in user serialization: {e}")
            # Rollback transaction if connection exists
            if connect.connection:
                try:
                    connect.connection.rollback()
                    print("Transaction rolled back due to error")
                except:
                    pass
            raise e
            
        finally:
            connect.disconnect()

    @staticmethod
    def user_deserialization(email):
        """
        Fetch user data from database and return as dictionary
        
        Args:
            email (str): User's email address to lookup
            
        Returns:
            dict: User data dictionary {user_id, name, email, password} if found, 
                  or dictionary with None values if error occurs
        """
        connect = SqlConnection()
        
        try:
            # Input validation - check if email is provided
            if not email:
                raise ValueError("Email is required")
            
            # Sanitize input by converting to string and stripping whitespace
            email = str(email).strip()
            
            # Validate that email is not empty after sanitization
            if not email:
                raise ValueError("Email cannot be empty")
            
            # Validate email length against database schema constraint (VARCHAR(100))
            if len(email) > 100:
                raise ValueError("Email exceeds maximum allowed length")
            
            # Attempt to establish database connection
            if not connect.connect():
                raise ConnectionError("Failed to connect to database")
            
            # Verify that the users table exists in the database
            table_check_sql = "SHOW TABLES LIKE 'users'"
            with connect.connection.cursor() as cursor:
                cursor.execute(table_check_sql)
                if not cursor.fetchone():
                    raise RuntimeError("Users table not found in database")
            
            # Fetch user data from database based on email
            fetch_sql = "SELECT user_id, username, email, password FROM users WHERE email = %s"
            with connect.connection.cursor() as cursor:
                cursor.execute(fetch_sql, (email,))
                result = cursor.fetchone()
                
                if not result:
                    raise LookupError("No user found with the provided email")
                
                # Create user data dictionary
                user_data = {
                    'user_id': result['user_id'],
                    'name': result['username'],
                    'email': result['email'],
                    'password': result['password']
                }
                
                return user_data
                    
        except Exception as e:
            # Handle all types of errors
            # Return dictionary with all fields set to None
            return {
                'user_id': None,
                'name': None,
                'email': None,
                'password': None
            }
            
        finally:
            try:
                connect.disconnect()
            except:
                # Ignore disconnection errors during cleanup
                pass
    
