FROM node:22

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY src/ ./src
COPY tsconfig.json ./

RUN npm install tsx

EXPOSE ${PORT}

CMD ["npm", "start"]