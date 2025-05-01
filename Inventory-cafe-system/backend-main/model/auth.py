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
        query = "SELECT id, username, password, role, status FROM users WHERE username = %s"
        cursor.execute(query, (login_data.username,))
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"User not found: {login_data.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Check if the user is inactive
        if user['status'] == 'Inactive':
            logger.warning(f"Inactive user attempted login: {login_data.username}")
            raise HTTPException(status_code=403, detail="Your account is inactive. Please contact support.")
        
        # Regular password checking
        stored_password = user.get("password", "")
        
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
