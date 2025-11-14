# stage 1: The Frontend Builder
# Use an official Node.js image to build our React app.
FROM node:18-alpine AS builder

# Set the working directory inside the container for frontend code
WORKDIR /app/frontend

# Copy the package.json and package-lock.json first.
# Docker will cache this step.
# As long as these files don't change, Docker won't re-run 'npm install'.
# for me: docker runs in stages: check first stage - if hasnt changed it uses cache, and than the second...
# until some stage changed, thats when he breaks from here on and copys everything- package json is better to be used cachedly so it doesnt
# run npm install when its not needed
COPY frontend/package.json frontend/package-lock.json ./

# Install all frontend dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Run the build script from the package.json
# This creates the static files in the /app/frontend/dist folder.
RUN npm run build

# stage 2: final stage, starting from python image, and copy just the stuff we need
FROM python:3.10-slim

# work directory
WORKDIR app

# copy the requiremnets
COPY requirements.txt .

# install backend python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the backend code, scripts, etc.
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# Run the database initialization script during the build
# This creates the .db file inside the image itself.
RUN python -m backend.init_db

# Copy *only* the built static files from the dist folder
COPY --from=builder /app/frontend/dist ./frontend/dist

# listening port
EXPOSE 8000

# command to run the servicer
# shell form -use the $PORT variable from render
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
