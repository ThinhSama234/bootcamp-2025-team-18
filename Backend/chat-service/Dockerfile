FROM node:22

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY src/ ./src
COPY tsconfig.json ./

RUN npm install tsx

ENV PORT=3000
ENV CHATDB_URL=
ENV LOCATION_SERVICE_GRPC_URL=

EXPOSE 3000

CMD ["npm", "start"]