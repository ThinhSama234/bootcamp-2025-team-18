FROM node AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

FROM node

WORKDIR /app

COPY package*.json ./

RUN npm ci --production

COPY --from=builder /app/src ./src
COPY --from=builder /app/tsconfig.json .

RUN npm install tsx

ENV PORT=3000

EXPOSE 3000

CMD ["npm", "start"]