# Cafe Pre-ordering System

A full-stack application for cafe pre-ordering with Vue.js frontend and FastAPI backend.

## Project setup

### Frontend
```
npm install
```

### Backend
```
pip install -r requirements.txt
```

## Development

### Compiles and hot-reloads for development
```
npm run serve
```

### Run backend server
```
cd backend
uvicorn main:app --reload
```

### Compiles and minifies for production
```
npm run build
```

## Deployment on Railway

### Prerequisites
1. Create a Railway account at https://railway.app/
2. Install Railway CLI: `npm i -g @railway/cli`
3. Login to Railway: `railway login`

### Steps to Deploy
1. Initialize Railway project: `railway init`
2. Add MySQL database service: `railway add`
3. Set environment variables:
   ```
   railway vars set DB_HOST=<your-railway-mysql-host>
   railway vars set DB_USER=<your-railway-mysql-user>
   railway vars set DB_PASSWORD=<your-railway-mysql-password>
   railway vars set DB_NAME=<your-railway-mysql-database>
   railway vars set DB_PORT=<your-railway-mysql-port>
   railway vars set SMTP_SERVER=smtp.gmail.com
   railway vars set SMTP_PORT=587
   railway vars set SMTP_USER=<your-email>
   railway vars set SMTP_PASSWORD=<your-email-app-password>
   railway vars set FROM_EMAIL=<your-email>
   railway vars set SECRET_KEY=<your-secret-key>
   ```
4. Deploy the application: `railway up`

### Accessing Your Deployed Application
Once deployed, you can access your application at the URL provided by Railway.

## Environment Variables
The application requires the following environment variables:
- `DB_HOST`: MySQL database host
- `DB_USER`: MySQL database user
- `DB_PASSWORD`: MySQL database password
- `DB_NAME`: MySQL database name
- `DB_PORT`: MySQL database port
- `SMTP_SERVER`: SMTP server for sending emails
- `SMTP_PORT`: SMTP port
- `SMTP_USER`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `FROM_EMAIL`: Email address to send from
- `SECRET_KEY`: Secret key for JWT token generation
