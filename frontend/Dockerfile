# Stage 1: Build the React app
FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install --save-dev @babel/plugin-proposal-private-property-in-object

COPY . .

RUN npm run build

# Stage 2: Serve the React app using Nginx
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]