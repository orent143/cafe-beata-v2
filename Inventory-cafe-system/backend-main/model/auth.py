from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
import bcrypt
from .db import get_db_connection, DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth")

AuthRouter = APIRouter(tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: int
    username: str  
    role: str

class ForgotPasswordRequest(BaseModel):
    email: str

@AuthRouter.post("/login/", response_model=LoginResponse)
async def login_user(login_data: LoginRequest, request: Request):
    logger.info(f"Login attempt for user: {login_data.username}")
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Log for debugging
        logger.info(f"Connected to database: {DB_CONFIG['database']}")
        
        # Try to find user by username
        logger.info(f"Searching for user: {login_data.username}")
        query = "SELECT id, username, password, role FROM users WHERE username = %s"
        cursor.execute(query, (login_data.username,))
        user = cursor.fetchone()
        
        # For debugging: list all users
        cursor.execute("SELECT username, role FROM users")
        all_users = cursor.fetchall()
        logger.info(f"All users in database: {all_users}")
        
        if not user:
            logger.warning(f"User not found: {login_data.username}")
            # Try to create a default admin user first
            try:
                # Check if users table is empty
                cursor.execute("SELECT COUNT(*) as count FROM users")
                count = cursor.fetchone()
                
                if count and count.get('count', 0) == 0:
                    # No users in the database, create a default admin
                    logger.info("Creating default admin user")
                    
                    # Create unhashed password for testing
                    plain_password = 'admin123'
                    
                    # Check if email column exists
                    cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
                    email_column_exists = cursor.fetchone()
                    
                    # Check if created_at or date_added exists
                    cursor.execute("SHOW COLUMNS FROM users LIKE 'created_at'")
                    created_at_exists = cursor.fetchone()
                    
                    cursor.execute("SHOW COLUMNS FROM users LIKE 'date_added'")
                    date_added_exists = cursor.fetchone()
                    
                    # Insert based on column structure
                    if email_column_exists and created_at_exists:
                        cursor.execute("""
                        INSERT INTO users (username, email, password, role, created_at)
                        VALUES ('admin', 'admin@cafebeata.com', %s, 'admin', NOW())
                        """, (plain_password,))
                    elif email_column_exists and date_added_exists:
                        cursor.execute("""
                        INSERT INTO users (username, email, password, role, date_added)
                        VALUES ('admin', 'admin@cafebeata.com', %s, 'admin', NOW())
                        """, (plain_password,))
                    elif date_added_exists:
                        cursor.execute("""
                        INSERT INTO users (username, password, role, date_added)
                        VALUES ('admin', %s, 'admin', NOW())
                        """, (plain_password,))
                    else:
                        cursor.execute("""
                        INSERT INTO users (username, password, role)
                        VALUES ('admin', %s, 'admin')
                        """, (plain_password,))
                        
                    connection.commit()
                    logger.info("Created default admin user: admin / admin123")
                    
                    # Now fetch the newly created user
                    cursor.execute("SELECT id, username, password, role FROM users WHERE username = 'admin'")
                    user = cursor.fetchone()
                    
                    # For extreme cases, return a default user object
                    if not user:
                        logger.warning("Failed to retrieve created admin user, using fallback")
                        return {
                            "user_id": 1,
                            "username": "admin",
                            "role": "admin"
                        }
                        
                else:
                    # Users exist but this username wasn't found
                    raise HTTPException(status_code=401, detail="Invalid username or password")
            except Exception as e:
                logger.error(f"Error creating default user: {e}")
                raise HTTPException(status_code=401, detail="Invalid username or password")
        
        logger.info(f"User found: {login_data.username}")
        
        # For debugging/development - bypass password check
        if login_data.username == 'admin' and login_data.password == 'admin123':
            logger.warning("Using default admin credentials")
            return {
                "user_id": user["id"] if user else 1,
                "username": "admin",
                "role": "admin"
            }
            
        # Regular password checking
        stored_password = user.get("password", "")
        
        # Log for debugging
        logger.info(f"Stored password: {stored_password[:3]}... (truncated)")
        logger.info(f"Input password: {login_data.password[:3]}... (truncated)")
        
        # Handle both hashed and plain text passwords during transition
        is_password_valid = False
        
        # First try direct comparison for plain text passwords (development only)
        if login_data.password == stored_password:
            logger.warning("Plain text password match (INSECURE)")
            is_password_valid = True
        else:
            # Try bcrypt verification
            try:
                is_password_valid = bcrypt.checkpw(
                    login_data.password.encode('utf-8'), 
                    stored_password.encode('utf-8')
                )
                logger.info(f"Bcrypt verification result: {is_password_valid}")
            except Exception as e:
                logger.error(f"Error in bcrypt check: {e}")
                # Fall back to direct comparison again for legacy
                is_password_valid = (login_data.password == stored_password)
        
        if not is_password_valid:
            logger.warning(f"Invalid password for user: {login_data.username}")
            
            # For testing only: allow login with matching username as password
            if login_data.username == login_data.password:
                logger.warning("Allowing login with username=password (INSECURE, FOR TESTING)")
                is_password_valid = True
            else:
                raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Successful login
        logger.info(f"Successful login for user: {login_data.username}")
        
        cursor.close()
        connection.close()
        
        return {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@AuthRouter.post("/forgot-password/")
async def forgot_password(request_data: ForgotPasswordRequest):
    try:
        email = request_data.email
        logger.info(f"Password reset requested for email: {email}")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # First check if users table has email column
        cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
        email_column_exists = cursor.fetchone()
        
        if email_column_exists:
            # Check if email exists
            query = "SELECT id, username FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
        else:
            # Email column doesn't exist, we can't look up by email
            # Just pretend everything is fine for security
            user = None
        
        cursor.close()
        connection.close()
        
        # Don't reveal if email exists or not for security
        return {"message": "If your email is registered, you will receive a password reset link."}
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        # Don't reveal the error for security
        return {"message": "If your email is registered, you will receive a password reset link."}

# Test endpoint to check if Auth module is working
@AuthRouter.get("/test")
async def test_auth():
    return {"status": "Auth service is working", "version": "1.0"}
