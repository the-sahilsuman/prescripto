FROM node:22

WORKDIR /admin

COPY package*.json ./
RUN npm install 
COPY . .

RUN npm install pm2 -g
EXPOSE 5174

# Run Vite dev server with --host for external access
CMD ["pm2-runtime", "npm", "--name", "admin", "--", "run", "dev", "--", "--host", "--port", "5174"]
