import streamlit as st
import mysql.connector
import hashlib

# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",  # Your MySQL host
        user="sql12738793",                # Your MySQL user
        password="nYPr75TmMH",             # Your MySQL password
        database="sql12738793",            # Your MySQL database name
        port=3306                          # Your MySQL port
    )

# Hashing function using sha256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User registration
def register_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()
    
    # Hash the password
    hashed_password = hash_password(password)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()
        st.success("User registered successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# User login
def login_user(username, password):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if user and user['password_hash'] == hash_password(password):
        return user['id']
    else:
        return None

# Save password
def save_password(user_id, site_name, site_username, site_password):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        # Store the actual password (not hashed)
        cursor.execute("INSERT INTO passwords (user_id, site_name, username, password) VALUES (%s, %s, %s, %s)",
                       (user_id, site_name, site_username, site_password))  # Save actual password
        connection.commit()
        st.success(f"Password for {site_name} saved successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# View stored passwords
def view_passwords(user_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM passwords WHERE user_id = %s", (user_id,))
    passwords = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return passwords

# Delete password
def delete_password(password_id):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM passwords WHERE id = %s", (password_id,))
        connection.commit()
        st.success("Password deleted successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Main app
def main():
    st.title("Password Manager")

    menu = ["Register", "Login", "Password Manager"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Register"):
            if new_user and new_password:
                register_user(new_user, new_password)
            else:
                st.error("Please provide both username and password")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state['user_id'] = user_id
                st.session_state['logged_in'] = True
                st.success(f"Logged in as {username}")
            else:
                st.error("Invalid credentials")

    elif choice == "Password Manager":
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            st.subheader("Manage Your Passwords")
            action = st.selectbox("Action", ["Add Password", "View Passwords", "Delete Password"])

            if action == "Add Password":
                site_name = st.text_input("Site Name")
                site_username = st.text_input("Site Username")
                site_password = st.text_input("Password", type='password')

                if st.button("Save Password"):
                    if site_name and site_username and site_password:
                        save_password(st.session_state['user_id'], site_name, site_username, site_password)
                    else:
                        st.error("Please fill all fields")

            elif action == "View Passwords":
                passwords = view_passwords(st.session_state['user_id'])
                for pw in passwords:
                    if st.checkbox(f"Show password for {pw['site_name']}"):
                        st.write(f"Site: {pw['site_name']}, Username: {pw['username']}, Password: {pw['password']}")
                    else:
                        st.write(f"Site: {pw['site_name']}, Username: {pw['username']}, Password: [hidden]")

            elif action == "Delete Password":
                passwords = view_passwords(st.session_state['user_id'])
                password_id = st.selectbox("Select Password to Delete", [pw['id'] for pw in passwords])
                if st.button("Delete"):
                    delete_password(password_id)
        else:
            st.error("You need to log in first")

if __name__ == '__main__':
    main()
