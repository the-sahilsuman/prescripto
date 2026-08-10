FROM node:22

WORKDIR /frontend

COPY package*.json ./
RUN npm install 
COPY . .

RUN npm install pm2 -g
EXPOSE 5173

# Run Vite dev server with --host to allow external access
# pm2-runtime runs npm script "dev" in foreground
CMD ["pm2-runtime", "npm", "--name", "frontend", "--", "run", "dev", "--", "--host", "--port", "5173"]
