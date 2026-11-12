FROM node:22-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install -g npm@12.2.2
RUN npm ci --omit=dev

COPY . .
EXPOSE 3000

CMD ["node", "src/server.js"]
