from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
import uuid
from datetime import datetime
import logging
import bcrypt
from .db import get_db_connection, get_db
from fastapi.responses import JSONResponse
from urllib.parse import urljoin

# Create a secure_filename function since werkzeug might not be available
def secure_filename(filename):
    """Generate a secure version of the filename"""
    return filename.replace(" ", "_").lower()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("users")

UsersRouter = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "cafe_staff"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    profile_pic: Optional[str] = None
    created_at: datetime

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class UserProfile(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    profile_pic: Optional[str] = None
    date_added: Optional[datetime] = None
    created_at: Optional[datetime] = None
    joined: Optional[str] = None

@UsersRouter.get("/")
async def get_all_users():
    """Get all users"""
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        # First check if the users table has email and created_at columns
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
        created_at_column_exists = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'date_added'")
        date_added_column_exists = cursor.fetchone()
        
        # Build the query based on available columns
        if email_column_exists and created_at_column_exists:
            # New schema
            query = """
            SELECT id, username, email, role, profile_pic, created_at
            FROM users
            ORDER BY created_at DESC
            """
        elif date_added_column_exists:
            # Legacy schema
            query = """
            SELECT id, username, '' as email, role, profile_pic, date_added as created_at
            FROM users
            ORDER BY date_added DESC
            """
        else:
            # Fallback
            query = """
            SELECT id, username, '' as email, role, profile_pic, NOW() as created_at
            FROM users
            """
            
        cursor.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"success": True, "users": users}
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@UsersRouter.get("/{user_id}")
async def get_user_by_id(user_id: int):
    """Get user by ID"""
    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        # First check if the users table has email and created_at columns
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
        created_at_column_exists = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'date_added'")
        date_added_column_exists = cursor.fetchone()
        
        # Build the query based on available columns
        if email_column_exists and created_at_column_exists:
            # New schema
            query = """
            SELECT id, username, email, role, profile_pic, created_at
            FROM users
            WHERE id = %s
            """
        elif date_added_column_exists:
            # Legacy schema
            query = """
            SELECT id, username, '' as email, role, profile_pic, date_added as created_at
            FROM users
            WHERE id = %s
            """
        else:
            # Fallback
            query = """
            SELECT id, username, '' as email, role, profile_pic, NOW() as created_at
            FROM users
            WHERE id = %s
            """
            
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
            
        return {"success": True, "user": user}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@UsersRouter.options("/")
async def options_create_user():
    """Handle preflight requests for create user endpoint"""
    return {}

@UsersRouter.post("/")
async def create_user(
    request: Request,
    username: str = Form(None),
    password: str = Form(None), 
    email: str = Form(None), 
    role: str = Form(None), 
    profile_pic: Optional[UploadFile] = File(None),
    user_data: UserCreate = None
):
    """
    Create a new user with support for both form data and JSON
    """
    connection = None
    cursor = None
    
    try:
        # Get connection from pool
        connection = get_db()
        cursor = connection.cursor()
        
        # Determine if this is a form submission or JSON
        is_form_data = username is not None
        
        if is_form_data:
            # Process form data
            if not all([username, password, role]):
                logger.error(f"Missing form fields: username={username}, role={role}")
                raise HTTPException(status_code=400, detail="Missing required form fields")
            
            # Default email if not provided
            if not email:
                email = f"{username}@cafebeata.com"
        else:
            # Process JSON data
            if not user_data:
                logger.error("No JSON data provided")
                raise HTTPException(status_code=400, detail="No user data provided")
            username = user_data.username
            password = user_data.password
            email = user_data.email
            role = user_data.role
        
        logger.info(f"Attempting to create user with username={username}, email={email}")
        
        # Check if user already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            logger.warning(f"User creation failed: username already exists for {username}")
            raise HTTPException(status_code=400, detail=f"User with this username already exists")
            
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Handle profile picture upload if provided
        profile_pic_path = None
        if profile_pic:
            try:
                # Create directory if it doesn't exist
                os.makedirs("uploads/profile_pics", exist_ok=True)
                
                # Generate a safe filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{username}_{timestamp}_{secure_filename(profile_pic.filename)}"
                
                # Create full file path for saving
                full_file_path = os.path.join("uploads/profile_pics", filename)
                
                # Create database path - just the filename
                profile_pic_path = f"uploads/profile_pics/{filename}"
                
                # Save the file
                with open(full_file_path, "wb") as buffer:
                    shutil.copyfileobj(profile_pic.file, buffer)
                    
                logger.info(f"Profile picture saved at: {full_file_path}")
                logger.info(f"Profile picture path stored in DB: {profile_pic_path}")
            except Exception as e:
                logger.error(f"Error saving profile picture: {str(e)}")
                # Continue without profile picture if error occurs
        
        # Check if the 'email' column exists in the users table
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone()
        
        # Check if the 'created_at' column exists in the users table
        cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
        created_at_column_exists = cursor.fetchone()
        
        # Insert the new user with appropriate columns
        if email_column_exists and created_at_column_exists:
            # New schema with email and created_at fields
            query = """
            INSERT INTO users (username, password, email, role, profile_pic, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (username, hashed_password, email, role, profile_pic_path))
        else:
            # Legacy schema without email and possibly with date_added instead of created_at
            query = """
            INSERT INTO users (username, password, role, profile_pic, date_added)
            VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (username, hashed_password, role, profile_pic_path))
            
        # Get the last inserted ID
        user_id = cursor.lastrowid
        
        # Commit the transaction
        connection.commit()
        
        logger.info(f"User created successfully with ID {user_id}")
        
        # Return success response with user ID
        return {"success": True, "user_id": user_id, "message": "User created successfully"}
        
    except HTTPException:
        # Rethrow HTTP exceptions
        raise
    except Exception as e:
        # Log detailed error
        logger.error(f"Error creating user: {str(e)}")
        
        if connection:
            connection.rollback()
            
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
        
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@UsersRouter.put("/{user_id}")
async def update_user(
    user_id: int, 
    username: str = Form(None),
    email: str = Form(None),
    role: str = Form(None),
    status: str = Form(None),
    profile_pic: Optional[UploadFile] = File(None)
):
    """Update an existing user with support for both form data and JSON"""
    try:
        connection = get_db()
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Determine if this is a form submission or JSON
        is_form_data = username is not None
        
        # Initialize update fields and values
        update_fields = []
        update_values = []
        
        if is_form_data:
            # Process form data
            if username:
                update_fields.append("username = %s")
                update_values.append(username)
                
            if email:
                update_fields.append("email = %s")
                update_values.append(email)
                
            if role:
                update_fields.append("role = %s")
                update_values.append(role)
            
            # Handle profile picture upload if provided
            profile_pic_path = None
            if profile_pic:
                try:
                    # Create directory if it doesn't exist
                    os.makedirs("uploads/profile_pics", exist_ok=True)
                    
                    # Generate a safe filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    filename = f"{username or 'user'}_{timestamp}_{secure_filename(profile_pic.filename)}"
                    
                    # Create full file path for saving
                    full_file_path = os.path.join("uploads/profile_pics", filename)
                    
                    # Create database path
                    profile_pic_path = f"uploads/profile_pics/{filename}"
                    
                    # Save the file
                    with open(full_file_path, "wb") as buffer:
                        shutil.copyfileobj(profile_pic.file, buffer)
                        
                    logger.info(f"Profile picture saved at: {full_file_path}")
                    
                    # Add profile_pic to update fields
                    update_fields.append("profile_pic = %s")
                    update_values.append(profile_pic_path)
                except Exception as e:
                    logger.error(f"Error saving profile picture: {str(e)}")
        
        # If no fields to update, return early
        if not update_fields:
            return {"success": True, "message": "No fields to update"}
            
        # Construct the update query
        update_query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        # Add user_id to values
        update_values.append(user_id)
        
        # Execute the update
        cursor.execute(update_query, update_values)
        connection.commit()
        
        # Get the updated user data to return
        cursor.execute("SELECT id, username, email, role, profile_pic FROM users WHERE id = %s", (user_id,))
        updated_user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user": updated_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@UsersRouter.options("/{user_id}")
async def options_update_user(user_id: int):
    """Handle preflight requests for update user endpoint"""
    return {}

@UsersRouter.delete("/{user_id}")
async def delete_user(user_id: int):
    """Delete a user"""
    try:
        connection = get_db()
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
            
        # Delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Profile picture upload endpoint
@UsersRouter.post("/{user_id}/profile-pic")
async def upload_profile_pic(user_id: int, profile_pic: UploadFile = File(...), request: Request = None):
    """Upload a profile picture for a user"""
    connection = None
    cursor = None
    try:
        # Use connection pool instead of direct connection
        connection = get_db()
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
            
        # Check if uploads directory exists, if not create it
        os.makedirs("uploads/profile_pics", exist_ok=True)
        
        # Generate file name with timestamp to prevent caching
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{user_id}_{timestamp}_{secure_filename(profile_pic.filename)}"
        full_file_path = os.path.join("uploads/profile_pics", file_name)
        
        # Create relative path for database storage
        db_file_path = f"uploads/profile_pics/{file_name}"
        
        # Save the file
        try:
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(profile_pic.file, buffer)
        except Exception as file_error:
            logger.error(f"Error saving profile picture file: {str(file_error)}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(file_error)}")

        # Update user profile picture in the database - store the proper path
        logger.info(f"Saving profile picture path to database: {db_file_path}")
        
        cursor.execute("""
        UPDATE users
        SET profile_pic = %s
        WHERE id = %s
        """, (db_file_path, user_id))
        
        connection.commit()
        
        # Format the full URL if request object is available
        full_url = None
        if request:
            base_url = str(request.base_url)
            full_url = urljoin(base_url, db_file_path)
            
        logger.info(f"Profile picture uploaded successfully. Path: {db_file_path}, Full URL: {full_url}")
            
        return {
            "success": True,
            "message": "Profile picture uploaded successfully",
            "file_path": db_file_path,
            "full_url": full_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Rollback on error
        if connection:
            try:
                connection.rollback()
            except:
                pass
                
        logger.error(f"Error uploading profile picture for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading profile picture: {str(e)}")
    finally:
        # Ensure connection resources are properly closed
        if cursor:
            try:
                cursor.close()
            except:
                pass
                
        if connection:
            try:
                connection.close()
            except:
                pass

# Ensure users table exists
def ensure_users_table_exists():
    """Ensure the users table exists and has the correct structure"""
    try:
        connection = get_db()
        cursor = connection.cursor()
        
        # First check if the users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Create users table if it doesn't exist
            logger.info("Creating users table from scratch")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'cafe_staff',
                profile_pic VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        else:
            # Table exists, check if it has the email column
            cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
            email_column_exists = cursor.fetchone()
            
            if not email_column_exists:
                logger.info("Adding email column to users table")
                try:
                    # Add email column
                    cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN email VARCHAR(100) NULL
                    """)
                    
                    # Update existing rows with default email
                    cursor.execute("""
                    UPDATE users 
                    SET email = CONCAT(username, '@cafebeata.com') 
                    WHERE email IS NULL
                    """)
                    
                    # Now make it NOT NULL
                    cursor.execute("""
                    ALTER TABLE users 
                    MODIFY email VARCHAR(100) NOT NULL UNIQUE
                    """)
                except Exception as e:
                    logger.warning(f"Could not add email column: {e}")
                    # If we can't add the column, we'll need to adapt our code
                    # to work without it
            
            # Check if it has created_at column
            cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
            created_at_exists = cursor.fetchone()
            
            if not created_at_exists:
                logger.info("Adding created_at column to users table")
                try:
                    cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                except Exception as e:
                    logger.warning(f"Could not add created_at column: {e}")
                    # If we can't add the column, we'll adapt
        
        # Check if admin user exists
        # If email column doesn't exist, we'll just check by username
        admin_exists = False
        try:
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()
        except Exception as e:
            logger.warning(f"Error checking for admin user: {e}")
        
        if not admin_exists:
            logger.info("Creating admin user")
            # Create admin user with default password 'admin123'
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            
            try:
                # Try to insert with email field
                cursor.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES ('admin', 'admin@cafebeata.com', %s, 'admin')
                """, (hashed_password.decode('utf-8'),))
            except Exception as e:
                logger.warning(f"Error inserting admin with email: {e}")
                try:
                    # Try without email field if it doesn't exist
                    cursor.execute("""
                    INSERT INTO users (username, password, role)
                    VALUES ('admin', %s, 'admin')
                    """, (hashed_password.decode('utf-8'),))
                except Exception as e2:
                    logger.error(f"Failed to create admin user: {e2}")
            
            # Create a test cafe staff user
            staff_password = bcrypt.hashpw('staff123'.encode('utf-8'), bcrypt.gensalt())
            
            try:
                # Try to insert with email field
                cursor.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES ('staff', 'staff@cafebeata.com', %s, 'cafe_staff')
                """, (staff_password.decode('utf-8'),))
            except Exception as e:
                logger.warning(f"Error inserting staff with email: {e}")
                try:
                    # Try without email field if it doesn't exist
                    cursor.execute("""
                    INSERT INTO users (username, password, role)
                    VALUES ('staff', %s, 'cafe_staff')
                    """, (staff_password.decode('utf-8'),))
                except Exception as e2:
                    logger.error(f"Failed to create staff user: {e2}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        logger.info("Users table verified")
        
    except Exception as e:
        logger.error(f"Error ensuring users table exists: {str(e)}")
        # Don't re-raise, just log the error
        # This allows the application to continue even if user setup fails

# Add these compatibility routes at the end of the file
@UsersRouter.get("/users/{user_id}")
async def get_user_by_id_compat(user_id: int):
    """Compatibility route for old URL structure"""
    logger.info(f"Compatibility route called: /users/{user_id}")
    return await get_user_by_id(user_id)

@UsersRouter.post("/users/")
async def create_user_compat(user_data: UserCreate):
    """Compatibility route for old URL structure"""
    logger.info("Compatibility route called: /users/")
    return await create_user(user_data.username, user_data.password, user_data.email, user_data.role)

@UsersRouter.put("/users/{user_id}")
async def update_user_compat(user_id: int, user_data: UserUpdate):
    """Compatibility route for old URL structure"""
    logger.info(f"Compatibility route called: /users/{user_id}")
    return await update_user(user_id, user_data.username, user_data.email, user_data.role)

@UsersRouter.delete("/users/{user_id}")
async def delete_user_compat(user_id: int):
    """Compatibility route for old URL structure"""
    logger.info(f"Compatibility route called: /users/{user_id}")
    return await delete_user(user_id)

@UsersRouter.post("/users/{user_id}/profile-pic")
async def upload_profile_pic_compat(user_id: int, profile_pic: UploadFile = File(...)):
    """Compatibility route for old URL structure"""
    logger.info(f"Compatibility route called: /users/{user_id}/profile-pic")
    return await upload_profile_pic(user_id, profile_pic)

@UsersRouter.get("/users/profile")
async def get_current_user_profile_compat(request: Request):
    """Compatibility route for old URL structure"""
    logger.info("Compatibility route called: /users/profile")
    return await get_current_user_profile(request)

@UsersRouter.get("/profile")
async def get_current_user_profile(request: Request):
    """Get the current user's profile"""
    connection = None
    cursor = None
    try:
        # Get the user ID from the Authorization header or session
        # For simplicity, we'll get it from the query parameters
        user_id = request.query_params.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized. User ID is required.")
        
        # Use the connection pool instead of direct connection
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        
        # First check if the users table has email and created_at columns
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone() is not None
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
        created_at_column_exists = cursor.fetchone() is not None
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'date_added'")
        date_added_column_exists = cursor.fetchone() is not None
        
        # Build the query based on available columns
        if email_column_exists and created_at_column_exists:
            # New schema
            query = """
            SELECT id, username, email, role, profile_pic, NULL as date_added, created_at
            FROM users
            WHERE id = %s
            """
        elif date_added_column_exists:
            # Legacy schema
            query = """
            SELECT id, username, '' as email, role, profile_pic, date_added, NULL as created_at
            FROM users
            WHERE id = %s
            """
        else:
            # Fallback
            query = """
            SELECT id, username, '' as email, role, profile_pic, NULL as date_added, NOW() as created_at
            FROM users
            WHERE id = %s
            """
            
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Format the joined date
        joined = None
        if user.get('created_at'):
            joined = user['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        elif user.get('date_added'):
            joined = user['date_added'].strftime("%Y-%m-%d %H:%M:%S")
            
        # Format the profile picture URL
        profile_pic = user.get('profile_pic')
        base_url = str(request.base_url)
        
        if profile_pic:
            # Check if the profile_pic is a relative path or already a full URL
            if not (profile_pic.startswith('http://') or profile_pic.startswith('https://')):
                profile_pic = urljoin(base_url, profile_pic)
        
        # Create a response object with properly formatted fields
        user_profile = {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'] if user.get('email') else f"{user['username']}@cafebeata.com",
            "role": user['role'],
            "profile_pic": profile_pic,
            "date_added": user.get('date_added'),
            "created_at": user.get('created_at'),
            "joined": joined
        }
        
        return {"success": True, "user": user_profile}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # Ensure connection resources are properly closed
        if cursor:
            try:
                cursor.close()
            except:
                pass
                
        if connection:
            try:
                connection.close()
            except:
                pass

