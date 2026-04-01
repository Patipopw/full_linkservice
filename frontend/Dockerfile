FROM node:20-alpine

WORKDIR /app

RUN apk update && apk upgrade --no-cache
# ก๊อปปี้ไฟล์ package เพื่อลง dependencies ก่อน (ช่วยเรื่อง Cache)
COPY package*.json ./
RUN npm install

# ก๊อปปี้ไฟล์ที่เหลือ
COPY . .

# สั่งรัน (จะถูกทับด้วย command ใน docker-compose อีกทีเพื่อความชัวร์)
CMD ["npm", "run", "dev"]
