FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# We will install dependencies at runtime during development using docker-compose command
# or we can install them here. For dev, doing it via entrypoint/compose command is often easier
# if we mount the volume, but installing here creates a base layer.
RUN npm install

# Copy all frontend code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Start Vite server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
