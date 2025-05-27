# Stage 1: Build
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Add nginx security headers
RUN echo "server_tokens off;" >> /etc/nginx/conf.d/default.conf

# Configure permissions and directories
RUN adduser -D -H -u 1000 -s /sbin/nologin -G www-data www-data && \
    chown -R www-data:www-data /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    # Create required nginx directories with proper permissions
    mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 755 /var/cache/nginx /var/run /var/log/nginx

# Expose port
EXPOSE 80

# Start nginx - must run as root to bind to port 80
CMD ["nginx", "-g", "daemon off;"] 