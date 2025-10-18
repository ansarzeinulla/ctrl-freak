# Use the official lightweight Nginx image
FROM nginx:alpine

# Set the working directory to the default Nginx web root
WORKDIR /usr/share/nginx/html

# Copy the index.html file from the build context (the project root)
# into the container's web root.
COPY index.html .

# Expose port 80 (the default Nginx port)
EXPOSE 80