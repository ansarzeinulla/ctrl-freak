FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
# This leverages Docker cache
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the application for production
RUN npm run build

# --- Stage 2: Serve the application with Nginx ---
FROM nginx:1.25-alpine

# Copy the build output from the 'build' stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for the Nginx server
EXPOSE 80

# The default Nginx command will start the server automatically