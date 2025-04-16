from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
import bcrypt  # For password hashing
import shutil
import os
from fastapi import Path, File
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
app = FastAPI()
from fastapi import Form
from fastapi import Form, File, UploadFile
from fastapi.responses import FileResponse
import json
import sendgrid
from fastapi import Depends
from dotenv import load_dotenv
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.responses import JSONResponse
import smtplib
import jwt
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException, Path, Request
import uuid
from fastapi import BackgroundTasks
from werkzeug.utils import secure_filename
import asyncio
import logging
import sys
import requests
import urllib.parse

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cafe-beata-backend")

# Create uploads directory and its subdirectories
UPLOAD_DIR = "uploads"
AVATARS_DIR = os.path.join(UPLOAD_DIR, "avatars")
os.makedirs(AVATARS_DIR, exist_ok=True)

# Mount the uploads directory for static file serving
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
SECRET_KEY = os.getenv("SECRET_KEY")

# Debugging: print values to check if they are loaded correctly.
print(f"SMTP_SERVER: {SMTP_SERVER}, SMTP_PORT: {SMTP_PORT}, SMTP_USER: {SMTP_USER}, FROM_EMAIL: {FROM_EMAIL}")
ALGORITHM = "HS256"

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue dev server for Inventory System
        "http://127.0.0.1:5173", 
        "http://localhost:8080",  # Vue dev server for Cafe Beata
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Type"],
)

class ResetPasswordRequest(BaseModel):
    email: str

class ResetPassword(BaseModel):
    newPassword: str


def generate_reset_token(email: str):
    expiration = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"exp": expiration, "sub": email}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_reset_email(to_email, reset_url):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = 'Password Reset Request'

    body = f'Click the following link to reset your password: {reset_url}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        server.connect(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

import mysql.connector

@app.post("/request-password-reset")
async def request_password_reset(request: ResetPasswordRequest, background_tasks: BackgroundTasks):
    email = request.email

    # Connect to the database and check if the email exists
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM userso WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(status_code=400, detail="Email not found")

    # Generate reset token and reset URL
    reset_token = generate_reset_token(email)
    reset_url = f"http://127.0.0.1:8000/reset-password/{reset_token}"

    # Add send_reset_email to background task
    background_tasks.add_task(send_reset_email, email, reset_url)

    # Respond immediately to the client
    return {"message": "Password reset link sent to your email!"}

@app.get("/reset-password/{token}")
async def reset_password_page(token: str):
    """Redirect to frontend reset password page"""
    reset_url = f"http://localhost:8080/reset-password/{token}"  # Make sure this URL matches your frontend route
    return RedirectResponse(url=reset_url)
    

@app.post("/reset-password/{token}")
async def reset_password_with_token(token: str, reset_data: ResetPassword):
    print(f"Received token: {token}")  # Debugging: print received token
    
    try:
        # Decode the token to extract the email
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_token.get("sub")

        # If no email is found in the token, throw an error
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        # Check if the token is expired
        if datetime.utcnow() > datetime.utcfromtimestamp(decoded_token["exp"]):
            raise HTTPException(status_code=400, detail="Token expired")

        # Proceed with updating the password in the database
        hashed_new_password = bcrypt.hashpw(reset_data.newPassword.encode('utf-8'), bcrypt.gensalt())

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE userso SET password = %s WHERE email = %s", (hashed_new_password, email))
        connection.commit()

        return {"message": "Password reset successfully!"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.PyJWTError as e:  # Correct exception name for PyJWT
        print(f"Error decoding JWT: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid token")




# Database connection function
def get_db_connection():
    db_config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),  # Empty password or remove this line if no password is used
        "database": os.getenv("DB_NAME", "cafe_beata"),
        "port": int(os.getenv("DB_PORT", "3306"))
    }

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
        else:
            print("Database connection failed: Not connected")
            return None
    except Error as e:
        print(f"Database connection error: {e}")
        # Try once more with no password as fallback
        try:
            db_config["password"] = ""
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                print("Connected with fallback (empty password)")
                return connection
        except Error as fallback_error:
            print(f"Fallback connection error: {fallback_error}")
        return None

@app.get("/")
async def root():
    return {"message": "FastAPI is running with CORS enabled!"}

# Model for User registration and login (Only email and password for login)
class User(BaseModel):
    email: str
    password: str
    username: str 

# Separate model for login (no secret_answer)
class UserLogin(BaseModel):
    email: str
    password: str  # Only email and password needed for login

# Model for password reset functionality

# Model for User Profile Data
class UserProfile(BaseModel):
    username: str
    email: str
    course: str
    gender: str
    about_me: str

@app.post("/register")
async def register(user: User):
    print(f"Received user data: {user}")  # Debugging: print the received user data
    if not user.email.endswith("@uic.edu.ph"):
        raise HTTPException(status_code=400, detail="Email must be the UIC EMAIL address")

    username = user.username  

    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM userso WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store the username (no secret_answer)
    cursor.execute("INSERT INTO userso (email, password, username) VALUES (%s, %s, %s)", 
                   (user.email, hashed_password, username))  
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "Account created successfully"}



@app.post("/check-username")
async def check_username(request: dict):
    username = request.get("username")
    
    # Connect to the database and check if the username already exists
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userso WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    cursor.close()
    connection.close()

    if existing_user:
        return {"exists": True}  # Username already taken
    else:
        return {"exists": False}  # Username is available


@app.post("/login")
async def login(user: UserLogin):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM userso WHERE email = %s", (user.email,))
    db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email")

    stored_password = db_user[2]
    if not bcrypt.checkpw(user.password.encode('utf-8'), stored_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Incorrect password")

    cursor.close()
    connection.close()

    return {"message": "Login successful", "username": db_user[3]}  # Return the username (assuming it is at index 3)



@app.post("/reset-password")
async def reset_password(reset_data: ResetPassword):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()

    # Check if email exists
    cursor.execute("SELECT * FROM userso WHERE email = %s", (reset_data.email,))
    db_user = cursor.fetchone()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not found")

    # Hash the new password before updating it
    hashed_new_password = bcrypt.hashpw(reset_data.newPassword.encode('utf-8'), bcrypt.gensalt())

    # Update the password
    cursor.execute("UPDATE userso SET password = %s WHERE email = %s", 
                   (hashed_new_password, reset_data.email))  # Store the new password as hashed
    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "Password reset successful"}


@app.get("/profile/{email}")
async def get_profile(email: str):
    # URL decode the email parameter if it contains encoded characters
    email = urllib.parse.unquote(email)
    
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    cursor.execute("SELECT id, email, username, course, gender, avatar FROM userso WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        # Return the avatar path stored in the database
        return {
            "id": user[0],
            "email": user[1],
            "username": user[2],
            "course": user[3],
            "gender": user[4],
            "avatar": user[5] if user[5] else "/assets/default.png"  # Fallback to default if no avatar
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")



@app.put("/profile/{email}")
async def update_profile(
    email: str,
    username: str = Form(...),
    course: str = Form(None),  # Changed from required to optional
    gender: str = Form(None),  # Changed from required to optional
    avatar: Optional[str] = Form(None)  # Avatar can be a file path or URL
):
    # URL decode the email parameter if it contains encoded characters
    email = urllib.parse.unquote(email)
    
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = connection.cursor()

        # Update user profile in the database with the selected avatar (URL or file path)
        cursor.execute(
            """
            UPDATE userso
            SET username = %s, course = %s, gender = %s, avatar = %s
            WHERE email = %s
            """,
            (username, course, gender, avatar, email)
        )
        connection.commit()

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.post("/profile/upload-avatar/{email}")
async def upload_avatar(email: str, avatar: UploadFile = File(...)):
    # URL decode the email parameter if it contains encoded characters
    email = urllib.parse.unquote(email)
    
    # Sanitize email for filename by replacing @ and other special characters with underscores
    safe_email = email.replace("@", "_").replace(".", "_")
    
    # Define the file path
    avatar_filename = f"{safe_email}_{avatar.filename}"
    avatar_path = os.path.join(AVATARS_DIR, avatar_filename)
    
    try:
        with open(avatar_path, "wb") as file:
            shutil.copyfileobj(avatar.file, file)  # Save the uploaded file to the server
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error uploading avatar")

    # Return the URL to access the uploaded avatar
    avatar_url = f"/uploads/avatars/{avatar_filename}"
    
    return {"message": "Avatar uploaded successfully", "avatar_url": avatar_url}


@app.get("/uploads/avatars/{filename}")
async def get_avatar(filename: str):
    file_path = os.path.join(AVATARS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Avatar not found")


class OrderStatusUpdate(BaseModel):
    status: str  # Expecting a JSON body with "status"


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: float
    image: Optional[str] = None  # Add image field with default None


class Order(BaseModel):
    customer_name: str
    items: List[OrderItem]  # List of OrderItem objects
    status: str


@app.get("/orders")
async def get_orders(status: Optional[str] = "pending", customer_name: Optional[str] = None):
    connection = get_db_connection()
    if connection is None:
        # Return empty results instead of throwing an error
        return {"orders": [], "error": "Database connection failed"}
    
    try:
        cursor = connection.cursor(dictionary=True)

        if customer_name:
            cursor.execute("SELECT * FROM orderso WHERE customer_name = %s AND status = %s", (customer_name, status))
        else:
            cursor.execute("SELECT * FROM orderso WHERE status = %s", (status,))  # Fetch orders by status

        orders = cursor.fetchall()

        for order in orders:
            try:
                if isinstance(order["items"], str):  
                    order["items"] = json.loads(order["items"])  
            except json.JSONDecodeError:
                order["items"] = []  

        cursor.close()
        connection.close()

        return {"orders": orders}
    except Exception as e:
        # Log the error and return an empty result
        print(f"Error fetching orders: {str(e)}")
        try:
            if connection and connection.is_connected():
                connection.close()
        except:
            pass
        return {"orders": [], "error": f"Error fetching orders: {str(e)}"}

@app.put("/orders/{order_id}")
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True, buffered=True)

    try:
        # Check if the order exists
        cursor.execute("SELECT * FROM orderso WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Debug logging
        print(f"Updating order {order_id} to status: {status_update.status}")
        print(f"Order data: {order}")
        
        # Update the status
        cursor.execute("UPDATE orderso SET status = %s WHERE id = %s", (status_update.status, order_id))

        # If marking as completed, handle stock reduction
        if status_update.status == "completed":
            try:
                items = json.loads(order["items"]) if isinstance(order["items"], str) else order["items"]
                print(f"Processing items for stock update: {items}")
                
                for item in items:
                    try:
                        print(f"Processing item: {item}")
                        cursor.execute("SELECT id, external_source, external_id FROM itemso WHERE name = %s", (item["name"],))
                        item_result = cursor.fetchone()
                        
                        if item_result:
                            item_id = item_result["id"]
                            quantity_to_reduce = item["quantity"]
                            
                            # Check if item stock exists
                            cursor.execute("SELECT quantity FROM item_stocks WHERE item_id = %s", (item_id,))
                            stock_result = cursor.fetchone()
                            
                            if stock_result:
                                # Update existing stock - no result set to consume with UPDATE
                                cursor.execute(
                                    "UPDATE item_stocks SET quantity = GREATEST(0, quantity - %s) WHERE item_id = %s",
                                    (quantity_to_reduce, item_id)
                                )
                                print(f"Updated stock for item {item_id}, reduced by {quantity_to_reduce}")

                                # If this item is from the inventory system, notify it about the stock change
                                if item_result["external_source"] == "inventory" and item_result["external_id"]:
                                    try:
                                        # First broadcast the local update to ensure UI refreshes quickly
                                        await manager.broadcast({
                                            "type": "stock_update",
                                            "item_id": item_id,
                                            "new_quantity": max(0, stock_result.get('quantity', 0) - quantity_to_reduce),
                                            "min_stock_level": stock_result.get('min_stock_level', 5),
                                            "timestamp": datetime.now().isoformat()
                                        })
                                        
                                        # Make request to inventory system using JSON data with proper error handling
                                        inventory_url = f"http://127.0.0.1:8001/api/stock/adjust/{item_result['external_id']}"
                                        inventory_data = {
                                            "action": "subtract",
                                            "quantity": quantity_to_reduce,
                                            "reason": f"Order {order_id} completed"
                                        }
                                        print(f"Sending inventory update to: {inventory_url}")
                                        print(f"Inventory update data: {inventory_data}")
                                        
                                        # Set a timeout to avoid hanging if the inventory system is down
                                        inventory_response = requests.post(
                                            inventory_url,
                                            json=inventory_data,
                                            headers={"Content-Type": "application/json"},
                                            timeout=5  # 5 second timeout
                                        )
                                        
                                        print(f"Inventory system response: {inventory_response.status_code} - {inventory_response.text}")
                                        
                                        if inventory_response.status_code == 200:
                                            print(f"Successfully updated inventory for item {item_result['external_id']}")
                                            
                                            # Also send a webhook notification to trigger UI refresh
                                            try:
                                                webhook_response = requests.post(
                                                    "http://127.0.0.1:8001/api/inventory-webhook/stock-update",
                                                    json={"product_id": item_result['external_id']},
                                                    headers={"Content-Type": "application/json"},
                                                    timeout=5
                                                )
                                                print(f"Webhook notification response: {webhook_response.status_code} - {webhook_response.text}")
                                            except Exception as webhook_error:
                                                print(f"Error sending webhook notification: {str(webhook_error)}")
                                        else:
                                            print(f"Failed to update inventory system: {inventory_response.text}")
                                            # Log the error but don't fail the order
                                            logger.error(f"Failed to update inventory system for order {order_id}: {inventory_response.text}")
                                    except requests.exceptions.Timeout:
                                        print(f"Timeout connecting to inventory system")
                                        logger.error(f"Timeout connecting to inventory system for order {order_id}")
                                    except requests.exceptions.ConnectionError:
                                        print(f"Connection error to inventory system")
                                        logger.error(f"Connection error to inventory system for order {order_id}")
                                    except Exception as inv_error:
                                        print(f"Error updating inventory system: {str(inv_error)}")
                                        # Log the error but don't fail the order
                                        logger.error(f"Error updating inventory system for order {order_id}: {str(inv_error)}")
                            else:
                                # Item exists but no stock record found - create one with 0 quantity
                                print(f"No stock record found for item {item_id}, creating with 0 quantity")
                                cursor.execute(
                                    "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, 0, 1)",
                                    (item_id,)
                                )
                        else:
                            print(f"Item not found in database: {item['name']}")
                    except Exception as item_error:
                        print(f"Error processing item {item.get('name', 'unknown')}: {str(item_error)}")
                        # Continue processing other items
                
                # ADDED: Update the sales table for each item in the order
                try:
                    print("Updating sales records in inventory system...")
                    for item in items:
                        try:
                            # Get item information
                            cursor.execute("SELECT id, external_source, external_id, name FROM itemso WHERE name = %s", (item["name"],))
                            item_result = cursor.fetchone()
                            
                            if item_result and item_result["external_source"] == "inventory" and item_result["external_id"]:
                                # Calculate remitted amount (price * quantity)
                                quantity_sold = item["quantity"]
                                unit_price = item.get("price", 0)
                                remitted = quantity_sold * unit_price
                                product_id = item_result["external_id"]
                                
                                print(f"Adding sales record for product ID {product_id}: {quantity_sold} units at {unit_price} each")
                                
                                # Option 1: Direct database update (since both systems share the same database)
                                try:
                                    # Get product details from inventory system
                                    cursor.execute("""
                                        SELECT ProductName, Image, UnitPrice FROM inventoryproduct 
                                        WHERE id = %s
                                    """, (product_id,))
                                    product_data = cursor.fetchone()
                                    
                                    if product_data:
                                        product_name = product_data.get("ProductName", item_result["name"])
                                        image = product_data.get("Image", None)
                                        db_unit_price = product_data.get("UnitPrice", unit_price)
                                        
                                        # Insert or update sales record
                                        cursor.execute("""
                                            INSERT INTO sales (
                                                product_id, 
                                                product_name, 
                                                Image, 
                                                quantity_sold, 
                                                unit_price,
                                                remitted, 
                                                created_at
                                            )
                                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                                            ON DUPLICATE KEY UPDATE 
                                                quantity_sold = quantity_sold + VALUES(quantity_sold), 
                                                remitted = remitted + VALUES(remitted)
                                        """, (
                                            product_id, 
                                            product_name, 
                                            image, 
                                            quantity_sold, 
                                            db_unit_price,
                                            remitted
                                        ))
                                        print(f"Sales record updated for {product_name} (ID: {product_id})")
                                except Exception as sales_db_error:
                                    print(f"Error directly updating sales table: {str(sales_db_error)}")
                                
                                # Option 2: API call to inventory system (as fallback)
                                try:
                                    # Call the inventory API to update sales
                                    sales_url = "http://127.0.0.1:8001/api/sales/update"
                                    sales_data = {
                                        "product_id": int(product_id),
                                        "quantity_sold": quantity_sold,
                                        "remitted": remitted
                                    }
                                    
                                    sales_response = requests.post(
                                        sales_url,
                                        json=sales_data,
                                        headers={"Content-Type": "application/json"},
                                        timeout=5
                                    )
                                    
                                    if sales_response.status_code == 200:
                                        print(f"Successfully updated sales via API for item {product_id}")
                                    else:
                                        print(f"Failed to update sales via API: {sales_response.text}")
                                except Exception as sales_api_error:
                                    print(f"Error updating sales via API: {str(sales_api_error)}")
                        except Exception as item_sales_error:
                            print(f"Error processing sales for item {item.get('name', 'unknown')}: {str(item_sales_error)}")
                except Exception as sales_error:
                    print(f"Error updating sales records: {str(sales_error)}")
                    # Don't fail the order status update if sales update fails
            except Exception as items_error:
                print(f"Error processing order items: {str(items_error)}")
                # Don't fail the order status update if stock update fails
        
        connection.commit()

        # Broadcast the status update to all connected clients
        await manager.broadcast({
            "type": "order_status_update",
            "order_id": order_id,
            "status": status_update.status,
            "timestamp": datetime.now().isoformat()
        })

        return {"message": f"Order {order_id} marked as {status_update.status}"}

    except Exception as e:
        connection.rollback()
        print(f"Error updating order status: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()


# WebSocket Manager for handling multiple connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                print(f"Error broadcasting message: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and wait for any messages
            data = await websocket.receive_text()
            
            # Process received messages
            try:
                message = json.loads(data)
                
                # Handle user notifications from admin
                if message.get('type') == 'user_notification':
                    # Forward the message to all connected clients
                    await manager.broadcast({
                        "type": "user_notification",
                        "action": message.get('action'),
                        "notification": message.get('notification'),
                        "target_user": message.get('target_user')
                    })
            except json.JSONDecodeError:
                print(f"Received invalid JSON message: {data}")
            except Exception as e:
                print(f"Error processing WebSocket message: {str(e)}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

@app.post("/orders")
async def create_order(order: Order):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor()

    try:
        # Start a transaction
        connection.start_transaction()

        # Find the highest existing order_id
        cursor.execute("SELECT MAX(id) FROM orderso")
        result = cursor.fetchone()

        last_order_id = result[0] if result[0] else 0
        new_order_id = last_order_id + 1 if last_order_id < 999 else 1

        # Ensure the order ID is always 3 digits
        formatted_order_id = f"{new_order_id:03d}"

        # Prepare the order items as JSON
        try:
            items_json = json.dumps([{
                "name": item.name,
                "quantity": item.quantity,
                "price": item.price,
                "image": item.image if hasattr(item, 'image') else None
            } for item in order.items])
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error processing items: " + str(e))

        # Insert the new order
        cursor.execute(
            "INSERT INTO orderso (id, customer_name, items, status) VALUES (%s, %s, %s, %s)",
            (formatted_order_id, order.customer_name, items_json, order.status)
        )

        # Commit the transaction
        connection.commit()

        # Create the order object for broadcasting
        order_data = {
            "id": formatted_order_id,
            "customer_name": order.customer_name,
            "items": [item.dict() for item in order.items],
            "status": order.status,
            "created_at": datetime.now().isoformat()
        }

        # Broadcast the new order to all connected clients
        await manager.broadcast({
            "type": "new_order",
            "order": order_data
        })

        return {"message": "Order created successfully", "order_id": formatted_order_id}

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Error creating order: " + str(e))

    finally:
        cursor.close()
        connection.close()

@app.get("/orders/{order_id}")
async def get_order_details(order_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orderso WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    connection.close()

    if order:
        try:
            order["items"] = json.loads(order["items"]) if order["items"] else []
        except json.JSONDecodeError:
            order["items"] = []

        return order
    else:
        raise HTTPException(status_code=404, detail="Order not found")

# Item Management Endpoints
@app.get('/api/items')
async def get_items():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Include external_source field to identify inventory items
        cursor.execute("""
            SELECT 
                id, name, price, category, image, external_source, external_id 
            FROM 
                itemso
        """)
        
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Add a debug log for items from the inventory system
        inventory_items = [item for item in items if item.get('external_source') == 'inventory']
        print(f"Found {len(inventory_items)} items from inventory in the database")
        
        return {"items": items}
    except Exception as e:
        print(f"Error getting items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/items')
async def add_item(name: str = Form(...), price: float = Form(...), category: str = Form(None), image: UploadFile = File(...)):
    try:
        # Save image file
        filename = secure_filename(image.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        image_path = f"/uploads/avatars/{filename}"
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO itemso (name, price, image, category) VALUES (%s, %s, %s, %s)",
            (name, price, image_path, category)
        )
        
        # Get the ID of the newly inserted item
        item_id = cursor.lastrowid
        
        # Create initial stock record for the item
        cursor.execute(
            "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, %s, %s)",
            (item_id, 0, 0)  # Default values: 0 quantity and 0 min_stock_level
        )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Broadcast menu update
        await manager.broadcast({
            "type": "menu_update",
            "action": "add",
            "item": {
                "id": item_id,
                "name": name,
                "price": price,
                "category": category,
                "image": image_path
            }
        })
        
        return {"message": "Item added successfully", "image_path": image_path, "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put('/api/items/{item_id}')
async def update_item(
    item_id: int,
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(None),
    image: UploadFile = File(None)
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if image:
            # Save new image
            filename = secure_filename(image.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            image_path = f"/uploads/avatars/{filename}"
            
            # Delete old image if exists
            cursor.execute("SELECT image FROM itemso WHERE id = %s", (item_id,))
            old_image = cursor.fetchone()
            if old_image and old_image[0]:
                old_path = os.path.join(UPLOAD_DIR, os.path.basename(old_image[0]))
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            cursor.execute(
                "UPDATE itemso SET name = %s, price = %s, category = %s, image = %s WHERE id = %s",
                (name, price, category, image_path, item_id)
            )
        else:
            cursor.execute(
                "UPDATE itemso SET name = %s, price = %s, category = %s WHERE id = %s",
                (name, price, category, item_id)
            )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Broadcast menu update
        await manager.broadcast({
            "type": "menu_update",
            "action": "update",
            "item": {
                "id": item_id,
                "name": name,
                "price": price,
                "category": category,
                "image": image_path if image else None
            }
        })
        
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete('/api/items/{item_id}')
async def delete_item(item_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get the image path before deleting
        cursor.execute("SELECT image FROM itemso WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        
        if item and item[0]:
            # Remove the image file
            image_path = os.path.join(UPLOAD_DIR, os.path.basename(item[0]))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the item's stock record first
        cursor.execute("DELETE FROM item_stocks WHERE item_id = %s", (item_id,))
        
        # Then delete the item
        cursor.execute("DELETE FROM itemso WHERE id = %s", (item_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        # Broadcast menu update
        await manager.broadcast({
            "type": "menu_update",
            "action": "delete",
            "item_id": item_id
        })
        
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Category Management Endpoints
@app.get('/api/categories')
async def get_categories():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, type, icon, created_at FROM categorieso ORDER BY name")
        categories = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"categories": categories}
    except Exception as e:
        print(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")

@app.post('/api/categories')
async def add_category(
    name: str = Form(...),
    type: str = Form(...),
    icon: str = Form(...)
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if category already exists
        cursor.execute("SELECT id FROM categorieso WHERE name = %s", (name,))
        if cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=400, detail="Category already exists")
        
        # Validate type
        if type not in ['drinks', 'food', 'ready_made']:
            cursor.close()
            raise HTTPException(status_code=400, detail="Invalid category type")
        
        # Insert new category
        cursor.execute(
            "INSERT INTO categorieso (name, type, icon) VALUES (%s, %s, %s)",
            (name, type, icon)
        )
        connection.commit()
        
        new_category_id = cursor.lastrowid
        cursor.close()
        
        # Broadcast category update via WebSocket
        await manager.broadcast({
            "type": "category_update",
            "action": "add",
            "category": {
                "id": new_category_id,
                "name": name,
                "type": type,
                "icon": icon
            }
        })
        
        return {
            "id": new_category_id,
            "name": name,
            "type": type,
            "icon": icon,
            "message": "Category added successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error adding category: {e}")
        raise HTTPException(status_code=500, detail="Failed to add category")

@app.delete('/api/categories/{category_id}')
async def delete_category(category_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if category exists
        cursor.execute("SELECT name FROM categorieso WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        if not category:
            cursor.close()
            raise HTTPException(status_code=404, detail="Category not found")
        
        category_name = category[0]
        
        # Check if category is in use
        cursor.execute("SELECT id FROM itemso WHERE category = %s", (category_name,))
        if cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=400, detail="Cannot delete category that has items")
        
        # Delete category
        cursor.execute("DELETE FROM categorieso WHERE id = %s", (category_id,))
        connection.commit()
        cursor.close()
        
        # Broadcast category update via WebSocket
        await manager.broadcast({
            "type": "category_update",
            "action": "delete",
            "category_id": category_id,
            "category_name": category_name
        })
        
        return {"message": "Category deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error deleting category: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete category")

@app.put('/api/categories/{category_id}')
async def update_category(
    category_id: int,
    name: str = Form(...),
    type: str = Form(...),
    icon: str = Form(...)
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if category exists
        cursor.execute("SELECT name FROM categorieso WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        if not category:
            cursor.close()
            raise HTTPException(status_code=404, detail="Category not found")
            
        old_name = category[0]
        
        # Check if new name already exists (excluding current category)
        cursor.execute("SELECT id FROM categorieso WHERE name = %s AND id != %s", (name, category_id))
        if cursor.fetchone():
            cursor.close()
            raise HTTPException(status_code=400, detail="Category name already exists")
        
        # Validate type
        if type not in ['drinks', 'food', 'ready_made']:
            cursor.close()
            raise HTTPException(status_code=400, detail="Invalid category type")
        
        # Update category
        cursor.execute(
            "UPDATE categorieso SET name = %s, type = %s, icon = %s WHERE id = %s",
            (name, type, icon, category_id)
        )
        
        # Update items with old category name
        cursor.execute(
            "UPDATE itemso SET category = %s WHERE category = %s",
            (name, old_name)
        )
        
        connection.commit()
        cursor.close()
        
        # Broadcast category update via WebSocket
        await manager.broadcast({
            "type": "category_update",
            "action": "update",
            "category": {
                "id": category_id,
                "name": name,
                "type": type,
                "icon": icon,
                "old_name": old_name
            }
        })
        
        return {
            "id": category_id,
            "name": name,
            "type": type,
            "icon": icon,
            "message": "Category updated successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")

# Stock Management Models
class StockUpdate(BaseModel):
    action: str  # 'add', 'subtract', or 'set'
    quantity: int
    reason: str

class MinStockLevel(BaseModel):
    min_stock_level: int

# Stock Management Endpoints
@app.get('/api/stocks')
async def get_stocks():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, i.name as item_name, i.category 
            FROM item_stocks s 
            JOIN itemso i ON s.item_id = i.id
        """)
        stocks = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"success": True, "items": stocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/stocks')
async def create_stock_record(request: dict):
    try:
        item_id = request.get("item_id")
        quantity = request.get("quantity", 0)
        min_stock_level = request.get("min_stock_level", 0)
        
        if not item_id:
            raise HTTPException(status_code=400, detail="Item ID is required")
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if stock record already exists
        cursor.execute("SELECT item_id FROM item_stocks WHERE item_id = %s", (item_id,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return {"success": False, "message": "Stock record already exists for this item"}
        
        # Create new stock record
        cursor.execute(
            "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, %s, %s)",
            (item_id, quantity, min_stock_level)
        )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Broadcast stock update
        await manager.broadcast({
            "type": "stock_update",
            "item_id": item_id,
            "new_quantity": quantity,
            "min_stock_level": min_stock_level
        })
        
        return {"success": True, "message": "Stock record created successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put('/api/stocks/{item_id}/update')
async def update_stock(item_id: int, stock_update: StockUpdate):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # First check if the tables exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'cafe_beata' 
            AND table_name IN ('item_stocks', 'stock_transactions', 'stock_alerts')
        """)
        tables_count = cursor.fetchone()[0]
        if tables_count < 3:
            raise HTTPException(status_code=500, detail="Required database tables are missing")

        # First get current stock and item details
        cursor.execute("""
            SELECT s.quantity, s.min_stock_level, i.name as item_name, i.category 
            FROM item_stocks s 
            JOIN itemso i ON s.item_id = i.id 
            WHERE s.item_id = %s
        """, (item_id,))
        stock_result = cursor.fetchone()
        
        if not stock_result:
            raise HTTPException(status_code=404, detail=f"Stock record not found for item_id: {item_id}")
        
        current_quantity = stock_result[0]
        min_stock_level = stock_result[1]
        item_name = stock_result[2]
        category = stock_result[3]
        new_quantity = current_quantity

        print(f"Processing stock update - Action: {stock_update.action}, Current: {current_quantity}, Update: {stock_update.quantity}")

        # Calculate new quantity based on action
        if stock_update.action == "add":
            new_quantity = current_quantity + stock_update.quantity
        elif stock_update.action == "subtract":
            if current_quantity < stock_update.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock")
            new_quantity = current_quantity - stock_update.quantity
        elif stock_update.action == "set":
            new_quantity = stock_update.quantity
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {stock_update.action}")

        print(f"New quantity calculated: {new_quantity}")

        # Update stock
        try:
            cursor.execute(
                "UPDATE item_stocks SET quantity = %s WHERE item_id = %s",
                (new_quantity, item_id)
            )
            print(f"Stock updated successfully for item_id: {item_id}")
        except Exception as e:
            print(f"Error updating stock: {str(e)}")
            raise

        # Log transaction
        try:
            cursor.execute(
                """INSERT INTO stock_transactions 
                   (item_id, action, quantity, previous_quantity, new_quantity, reason) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (item_id, stock_update.action, stock_update.quantity, current_quantity, new_quantity, stock_update.reason)
            )
            print("Transaction logged successfully")
        except Exception as e:
            print(f"Error logging transaction: {str(e)}")
            # Continue even if logging fails
            pass

        # Check if we need to create an alert
        alert_type = None
        try:
            if new_quantity <= min_stock_level:
                alert_type = "out_of_stock" if new_quantity == 0 else "low_stock"
                cursor.execute(
                    """INSERT INTO stock_alerts (item_id, alert_type, quantity) 
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE 
                       alert_type = VALUES(alert_type),
                       quantity = VALUES(quantity),
                       created_at = CURRENT_TIMESTAMP""",
                    (item_id, alert_type, new_quantity)
                )
                print(f"Stock alert created: {alert_type}")
        except Exception as e:
            print(f"Error handling stock alert: {str(e)}")
            # Continue even if alert creation fails
            pass

        connection.commit()
        print("Transaction committed successfully")

        # Broadcast stock update via WebSocket
        await manager.broadcast({
            "type": "stock_update",
            "item_id": item_id,
            "item_name": item_name,
            "category": category,
            "new_quantity": new_quantity,
            "min_stock_level": min_stock_level,
            "alert_type": alert_type
        })

        return {"success": True, "new_quantity": new_quantity}
    except HTTPException as he:
        if connection:
            connection.rollback()
        raise he
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Unexpected error in stock update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed")

@app.put('/api/stocks/{item_id}/min-level')
async def update_min_stock_level(item_id: int, min_stock: MinStockLevel):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            "UPDATE item_stocks SET min_stock_level = %s WHERE item_id = %s",
            (min_stock.min_stock_level, item_id)
        )
        
        connection.commit()
        cursor.close()
        connection.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/stocks/alerts')
async def get_stock_alerts():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, i.name as item_name, i.category 
            FROM stock_alerts a 
            JOIN itemso i ON a.item_id = i.id 
            ORDER BY a.created_at DESC
        """)
        alerts = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"success": True, "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_stock_tables():
    """Create necessary tables for stock management if they don't exist"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First check if the itemso table has the external_source and external_id columns
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = 'cafe_beata' 
            AND table_name = 'itemso' 
            AND column_name = 'external_source'
        """)
        if cursor.fetchone()[0] == 0:
            # Add external_source and external_id columns to the itemso table
            cursor.execute("""
                ALTER TABLE itemso 
                ADD COLUMN external_source VARCHAR(50) NULL, 
                ADD COLUMN external_id VARCHAR(50) NULL,
                ADD COLUMN last_updated DATETIME NULL
            """)
            print("Added external_source and external_id columns to itemso table")
        
        # Check if item_stocks table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'cafe_beata' 
            AND table_name = 'item_stocks'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Create item_stocks table
            cursor.execute("""
                CREATE TABLE item_stocks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 0,
                    min_stock_level INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES itemso(id) ON DELETE CASCADE
                )
            """)
            print("Created item_stocks table")
        
        # Check if stock_transactions table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'cafe_beata' 
            AND table_name = 'stock_transactions'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Create stock_transactions table
            cursor.execute("""
                CREATE TABLE stock_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    quantity INT NOT NULL,
                    previous_quantity INT NOT NULL,
                    new_quantity INT NOT NULL,
                    transaction_type ENUM('Add', 'Subtract', 'Set') NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INT,
                    FOREIGN KEY (item_id) REFERENCES itemso(id) ON DELETE CASCADE
                )
            """)
            print("Created stock_transactions table")
        
        # Check if stock_alerts table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'cafe_beata' 
            AND table_name = 'stock_alerts'
        """)
        
        if cursor.fetchone()[0] == 0:
            # Create stock_alerts table
            cursor.execute("""
                CREATE TABLE stock_alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    item_id INT NOT NULL,
                    alert_type ENUM('low_stock', 'out_of_stock') NOT NULL,
                    status ENUM('new', 'acknowledged', 'resolved') NOT NULL DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged_at TIMESTAMP NULL,
                    resolved_at TIMESTAMP NULL,
                    FOREIGN KEY (item_id) REFERENCES itemso(id) ON DELETE CASCADE
                )
            """)
            print("Created stock_alerts table")
            
        connection.commit()
    except Exception as e:
        print(f"Error creating stock tables: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Background tasks
background_tasks = set()

async def sync_inventory_products_background():
    """Background task to periodically sync inventory products"""
    try:
        while True:
            # Sync every 1 minute instead of 5 minutes
            await asyncio.sleep(60)
            try:
                await sync_inventory_products()
                print(f"[{datetime.now()}] Auto-synced inventory products")
            except Exception as e:
                print(f"[{datetime.now()}] Error in auto-sync: {e}")
    except asyncio.CancelledError:
        print("Inventory sync background task was cancelled")

@app.on_event("startup")
async def startup_event():
    # Start background task for periodic stock synchronization
    logger.info("Starting background stock sync task...")
    try:
        # Use asyncio.create_task instead of adding to the background_tasks set
        asyncio.create_task(background_stock_sync())
        logger.info("Background stock sync task started")
        
        # Connect to the inventory system WebSocket for real-time updates
        logger.info("Connecting to inventory system WebSocket...")
        try:
            from utils.inventory_client import connect_to_inventory_websocket
            asyncio.create_task(connect_to_inventory_websocket())
            logger.info("Inventory WebSocket connection initialized")
        except Exception as e:
            logger.error(f"Error initializing inventory WebSocket connection: {e}")
            # This shouldn't block the app from starting
    except Exception as e:
        logger.error(f"Error starting background tasks: {e}")
        # This shouldn't block the app from starting

@app.on_event("shutdown")
async def shutdown_event():
    for task in background_tasks:
        task.cancel()

@app.get('/api/sync-inventory-products')
async def sync_inventory_products():
    """
    Synchronize Ready-Made products from the inventory system to the cafe-beata menu
    """
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Log all available products and their process types for debugging
        cursor.execute("SELECT id, ProductName, ProcessType, Status FROM inventoryproduct")
        all_products = cursor.fetchall()
        print(f"Available products in inventory: {len(all_products)}")
        print(f"Process types found: {set([p.get('ProcessType') for p in all_products])}")
        
        # Get ONLY Ready-Made products from the inventory system - CASE SENSITIVE check
        cursor.execute("""
            SELECT id, ProductName, UnitPrice, Image, Quantity, Threshold, ProcessType, Status 
            FROM inventoryproduct 
            WHERE ProcessType = 'Ready-Made'
        """)
        inventory_products = cursor.fetchall()
        
        print(f"Query for strictly 'Ready-Made' products found: {len(inventory_products)} products")
        
        if not inventory_products:
            # If no products found with Ready-Made, try other common variants as fallback
            cursor.execute("""
                SELECT id, ProductName, UnitPrice, Image, Quantity, Threshold, ProcessType, Status 
                FROM inventoryproduct 
                WHERE ProcessType IN ('Ready Made', 'Ready_Made', 'ReadyMade', 'READY-MADE', 'ready-made')
            """)
            fallback_products = cursor.fetchall()
            print(f"Fallback query found: {len(fallback_products)} products")
            
            if fallback_products:
                inventory_products = fallback_products
            else:
                # Delete any inventory products that no longer match the ProcessType
                cursor.execute("DELETE FROM itemso WHERE external_source = 'inventory'")
                connection.commit()
                return {"success": False, "message": "No Ready-Made products found in inventory system. Cleared existing inventory items."}
        
        print(f"Found {len(inventory_products)} Ready-Made products to import")
        if inventory_products:
            # Log the first few products for debugging
            sample = inventory_products[:3] if len(inventory_products) > 3 else inventory_products
            print(f"Sample products: {[(p['id'], p['ProductName'], p['ProcessType']) for p in sample]}")
        
        # Get existing Ready-Made items from cafe-beata
        cursor.execute("""
            SELECT id, name, external_id FROM itemso 
            WHERE external_source = 'inventory'
        """)
        existing_items = cursor.fetchall()
        existing_ids = {item['external_id']: item['id'] for item in existing_items}
        
        # Make sure the Ready Made category exists
        cursor.execute("SELECT id, name FROM categorieso WHERE name = 'Ready Made' OR type = 'ready_made'")
        ready_made_category = cursor.fetchone()
        
        if not ready_made_category:
            # Create the Ready Made category if it doesn't exist
            cursor.execute(
                "INSERT INTO categorieso (name, type, icon) VALUES (%s, %s, %s)",
                ('Ready Made', 'ready_made', 'fas fa-shopping-basket')
            )
            connection.commit()
            ready_made_category_id = cursor.lastrowid
            category_name = 'Ready Made'
        else:
            ready_made_category_id = ready_made_category['id']
            category_name = ready_made_category['name']
            
        added_count = 0
        updated_count = 0
        imported_ids = set()
        
        # Process each inventory product
        for product in inventory_products:
            # Format the image path if needed - properly handle inventory system images
            image_path = product['Image']
            if image_path:
                # If image path is just a filename without path (common in inventory system)
                if '/' not in image_path and '\\' not in image_path:
                    # Direct URL to the inventory system products folder
                    image_path = f"http://localhost:8001/uploads/products/{image_path}"
                # If it starts with /uploads/ or uploads/
                elif image_path.startswith('/uploads/') or image_path.startswith('uploads/'):
                    # Clean up the path and use the inventory system URL with products folder
                    clean_path = image_path.replace('/uploads/', '').replace('uploads/', '')
                    image_path = f"http://localhost:8001/uploads/products/{clean_path}"
                # If it's already a full URL, keep it as is
                elif image_path.startswith('http://') or image_path.startswith('https://'):
                    pass
                else:
                    # For any other format, assume it's a relative path to the inventory system
                    image_path = f"http://localhost:8001/uploads/products/{image_path}"
            else:
                # Default image if none provided
                image_path = "/assets/default.png"
                
            if str(product['id']) in existing_ids:
                # Update existing item
                item_id = existing_ids[str(product['id'])]
                cursor.execute("""
                    UPDATE itemso 
                    SET name = %s, price = %s, image = %s, last_updated = NOW(), category = %s 
                    WHERE id = %s
                """, (
                    product['ProductName'],
                    product['UnitPrice'],
                    image_path,
                    category_name,  # Always set the category to Ready Made
                    item_id
                ))
                
                # Also update stock levels
                cursor.execute("""
                    UPDATE item_stocks 
                    SET quantity = %s, min_stock_level = %s, last_updated = NOW()
                    WHERE item_id = %s
                """, (
                    product.get('Quantity', 0) or 0,
                    product.get('Threshold', 0) or 0,
                    item_id
                ))
                
                updated_count += 1
                imported_ids.add(str(product['id']))
            else:
                # Insert new item
                cursor.execute("""
                    INSERT INTO itemso 
                    (name, price, category, image, external_source, external_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    product['ProductName'],
                    product['UnitPrice'],
                    category_name,
                    image_path,
                    'inventory',
                    str(product['id'])
                ))
                new_item_id = cursor.lastrowid
                added_count += 1
                imported_ids.add(str(product['id']))
                
                # Create stock record for the item
                cursor.execute("""
                    INSERT INTO item_stocks (item_id, quantity, min_stock_level)
                    VALUES (%s, %s, %s)
                """, (
                    new_item_id, 
                    product.get('Quantity', 0) or 0,
                    product.get('Threshold', 0) or 0
                ))
        
        # Delete any inventory products that are no longer in the inventory system
        # or that don't match the ProcessType criteria
        ids_to_keep = ", ".join([f"'{id}'" for id in imported_ids]) if imported_ids else "''"
        cursor.execute(f"""
            DELETE FROM itemso 
            WHERE external_source = 'inventory' 
            AND external_id NOT IN ({ids_to_keep})
        """)
        removed_count = cursor.rowcount
        
        connection.commit()
        
        # If items were added or updated, send a WebSocket notification to refresh menus
        if added_count > 0 or updated_count > 0 or removed_count > 0:
            await manager.broadcast({
                "type": "menu_update",
                "message": f"Menu updated with items from inventory system"
            })
            
        return {
            "success": True,
            "message": f"Synchronized inventory products: {added_count} added, {updated_count} updated, {removed_count} removed"
        }
    except Exception as e:
        print(f"Error syncing inventory products: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.get("/api/sync-inventory-stocks")
async def sync_inventory_stocks():
    """
    Syncs stock levels from the inventory system to the cafe system for all Ready-Made products.
    This is used by the webhook handler and background task.
    """
    connection = None
    
    try:
        # Get a database connection
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        logger.info("Starting inventory stock sync...")
        
        # 1. Get all external products that we need to sync from the cafe-beata database
        cursor.execute("""
            SELECT id, name, external_id, external_source
            FROM itemso 
            WHERE external_source = 'inventory' AND external_id IS NOT NULL
        """)
        local_items = cursor.fetchall()
        
        if not local_items:
            logger.info("No inventory items found to sync")
            return {"success": True, "message": "No inventory items found to sync"}
        
        logger.info(f"Found {len(local_items)} inventory items to sync")
        
        # 2. Make a request to the inventory system to get current stock levels for ready-made products
        try:
            inventory_response = requests.get(
                "http://127.0.0.1:8001/api/inventory/inventoryproducts/filter?process_type=Ready-Made",
                timeout=5
            )
            
            if inventory_response.status_code != 200:
                logger.error(f"Failed to fetch inventory products: {inventory_response.status_code} - {inventory_response.text}")
                return {"success": False, "message": f"Failed to fetch inventory products: {inventory_response.status_code}"}
                
            inventory_products = inventory_response.json()
            logger.info(f"Fetched {len(inventory_products)} Ready-Made products from inventory system")
            
            # Create a lookup dictionary for faster access
            inventory_lookup = {str(product['id']): product for product in inventory_products}
            
            # 3. Update the stock levels in cafe-beata
            updated_count = 0
            out_of_sync_count = 0
            
            for item in local_items:
                external_id = item['external_id']
                inventory_product = inventory_lookup.get(str(external_id))
                
                if inventory_product:
                    inventory_quantity = inventory_product.get('Quantity', 0)
                    threshold = inventory_product.get('Threshold', 5) or 5
                    
                    # Check existing stock quantity in cafe-beata
                    cursor.execute("SELECT quantity FROM item_stocks WHERE item_id = %s", (item['id'],))
                    stock_result = cursor.fetchone()
                    
                    if stock_result:
                        current_quantity = stock_result['quantity']
                        
                        # Only update if quantities don't match
                        if current_quantity != inventory_quantity:
                            cursor.execute(
                                "UPDATE item_stocks SET quantity = %s, min_stock_level = %s WHERE item_id = %s",
                                (inventory_quantity, threshold, item['id'])
                            )
                            logger.info(f"Updated stock for {item['name']} (ID: {item['id']}) from {current_quantity} to {inventory_quantity}")
                            updated_count += 1
                    else:
                        # Create a new stock record
                        cursor.execute(
                            "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, %s, %s)",
                            (item['id'], inventory_quantity, threshold)
                        )
                        logger.info(f"Created new stock record for {item['name']} (ID: {item['id']}) with quantity {inventory_quantity}")
                        updated_count += 1
                else:
                    logger.warning(f"Product with external_id {external_id} not found in inventory system")
                    out_of_sync_count += 1
            
            connection.commit()
            
            if updated_count > 0:
                logger.info(f"Synchronized {updated_count} inventory products.")
                
                # Send WebSocket notification about stock update to refresh clients
                await manager.broadcast({
                    "type": "inventory_sync_complete",
                    "updated_count": updated_count,
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "message": f"Synchronized inventory stock levels: {updated_count} updated. {out_of_sync_count} products need full sync."
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to inventory system: {str(e)}")
            return {"success": False, "message": f"Error connecting to inventory system: {str(e)}"}
        
    except Exception as e:
        logger.error(f"Error syncing inventory stock levels: {str(e)}")
        if connection:
            connection.rollback()
        return {"success": False, "message": f"Error syncing inventory stock levels: {str(e)}"}
    finally:
        if connection:
            cursor.close()
            connection.close()

# Add a webhook endpoint for the inventory system to call when stock changes
@app.post("/api/inventory-webhook/stock-update")
async def inventory_webhook_stock_update(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for inventory system to call when stock changes
    """
    try:
        # Get the data from the request
        data = await request.json()
        
        # Log what we received
        print(f"Received inventory webhook data: {data}")
        
        # Verify webhook (basic validation)
        if "product_id" not in data:
            print("Invalid webhook data, missing product_id")
            return {"success": False, "message": "Invalid webhook data, missing product_id"}
            
        # Extract the data
        product_id = data.get("product_id")
        product_name = data.get("product_name")
        quantity = data.get("quantity")
        status = data.get("status")
        
        # Log detailed information
        print(f"Processing stock update for product: {product_id}, name: {product_name}, quantity: {quantity}, status: {status}")
        
        # If detailed data is provided, update the item directly
        if product_name and quantity is not None:
            connection = get_db_connection()
            if connection is None:
                print("Database connection failed in webhook handler")
                return {"success": False, "message": "Database connection failed"}

            cursor = connection.cursor(dictionary=True)
            
            try:
                # Check if the external item exists in our system
                cursor.execute(
                    "SELECT id FROM itemso WHERE external_id = %s AND external_source = 'inventory'", 
                    (product_id,)
                )
                item_result = cursor.fetchone()
                
                if item_result:
                    local_item_id = item_result["id"]
                    print(f"Found local item ID {local_item_id} for inventory product {product_id}")
                    
                    # Get minimum stock level if it exists
                    cursor.execute("SELECT min_stock_level FROM item_stocks WHERE item_id = %s", (local_item_id,))
                    stock_level_result = cursor.fetchone()
                    min_stock_level = 5  # Default
                    if stock_level_result:
                        min_stock_level = stock_level_result.get('min_stock_level', 5)
                    
                    # Update the stock quantity
                    cursor.execute(
                        "UPDATE item_stocks SET quantity = %s WHERE item_id = %s",
                        (quantity, local_item_id)
                    )
                    
                    rows_affected = cursor.rowcount
                    if rows_affected > 0:
                        print(f"Updated {rows_affected} rows for item {local_item_id}")
                        
                        # Immediate broadcast to all connected clients for fast UI refresh
                        asyncio.create_task(manager.broadcast({
                            "type": "stock_update",
                            "item_id": local_item_id,
                            "new_quantity": quantity,
                            "min_stock_level": min_stock_level,
                            "timestamp": datetime.now().isoformat()
                        }))
                    else:
                        print(f"No stock record existed for item {local_item_id}, creating one")
                        # If no stock record exists, create one
                        cursor.execute(
                            "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = VALUES(quantity)",
                            (local_item_id, quantity, min_stock_level)
                        )
                        
                        # Broadcast this new stock record too
                        asyncio.create_task(manager.broadcast({
                            "type": "stock_update",
                            "item_id": local_item_id,
                            "new_quantity": quantity,
                            "min_stock_level": min_stock_level,
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    connection.commit()
                    print(f"Successfully updated stock for item {local_item_id} to {quantity}")
                else:
                    print(f"External product {product_id} not found in local system")
            except Exception as e:
                print(f"Error updating item stock in webhook: {str(e)}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        
        # Schedule a full stock sync in the background for consistency
        asyncio.create_task(sync_inventory_stocks())
        
        return {"success": True, "message": "Stock update processed"}
    except Exception as e:
        print(f"Error in inventory webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create a background task to sync stock levels periodically
async def background_stock_sync():
    """
    Background task that runs every 5 minutes to sync stock levels 
    from inventory system to cafe-beata
    """
    while True:
        try:
            # Run stock sync
            logger.info("Running scheduled inventory stock sync")
            await sync_inventory_stocks()
            
            # Wait for 5 minutes
            await asyncio.sleep(300)  # 300 seconds = 5 minutes
        except Exception as e:
            logger.error(f"Error in background stock sync: {e}")
            # Wait a minute before trying again
            await asyncio.sleep(60)

# Add this function to sync a specific inventory product
async def sync_specific_inventory_product(product_id: int):
    """
    Sync a specific inventory product in real-time
    """
    logger.info(f"Syncing specific inventory product: {product_id}")
    try:
        connection = get_db_connection()
        if connection is None:
            logger.error("Database connection failed")
            return False
            
        cursor = connection.cursor(dictionary=True)
        
        # Check if this product exists in our system
        cursor.execute(
            "SELECT id, name FROM itemso WHERE external_id = %s AND external_source = 'inventory'", 
            (product_id,)
        )
        
        item_result = cursor.fetchone()
        
        if not item_result:
            logger.info(f"Product {product_id} not found in cafe-beata, attempting to fetch and create it")
            # This product isn't in our system yet, we need to fetch it and create it
            from utils.inventory_client import get_inventory_product
            
            # Fetch the product details from inventory
            inventory_product = await get_inventory_product(product_id)
            
            if not inventory_product or not inventory_product.get("success"):
                logger.error(f"Failed to fetch product {product_id} from inventory")
                cursor.close()
                connection.close()
                return False
                
            # Create the product in our system
            await sync_inventory_products()  # This will create the product if it doesn't exist
            
            # Check again if the product exists now
            cursor.execute(
                "SELECT id, name FROM itemso WHERE external_id = %s AND external_source = 'inventory'", 
                (product_id,)
            )
            
            item_result = cursor.fetchone()
            
            if not item_result:
                logger.error(f"Product {product_id} still not found after sync attempt")
                cursor.close()
                connection.close()
                return False
        
        # At this point, we have the item in our database
        local_item_id = item_result["id"]
        logger.info(f"Found local item ID {local_item_id} for inventory product {product_id}")
        
        # Fetch the latest stock information from inventory
        from utils.inventory_client import get_inventory_product
        product_data = await get_inventory_product(product_id)
        
        if not product_data or not product_data.get("success"):
            logger.error(f"Failed to fetch updated product data for {product_id}")
            cursor.close()
            connection.close()
            return False
            
        # Extract product details
        product = product_data.get("product", {})
        quantity = product.get("Quantity", 0)
        threshold = product.get("Threshold", 5)
        
        # Update the stock in our database
        cursor.execute("SELECT quantity FROM item_stocks WHERE item_id = %s", (local_item_id,))
        stock_result = cursor.fetchone()
        
        if stock_result:
            # Update existing stock
            cursor.execute(
                "UPDATE item_stocks SET quantity = %s, min_stock_level = %s WHERE item_id = %s",
                (quantity, threshold, local_item_id)
            )
            logger.info(f"Updated stock for {item_result['name']} (ID: {local_item_id}) to {quantity}")
        else:
            # Create new stock record
            cursor.execute(
                "INSERT INTO item_stocks (item_id, quantity, min_stock_level) VALUES (%s, %s, %s)",
                (local_item_id, quantity, threshold)
            )
            logger.info(f"Created new stock record for {item_result['name']} (ID: {local_item_id}) with quantity {quantity}")
        
        connection.commit()
        
        # Broadcast the stock update to all connected clients
        await manager.broadcast({
            "type": "stock_update",
            "item_id": local_item_id,
            "new_quantity": quantity,
            "min_stock_level": threshold,
            "timestamp": datetime.now().isoformat()
        })
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Error syncing specific inventory product {product_id}: {e}")
        return False