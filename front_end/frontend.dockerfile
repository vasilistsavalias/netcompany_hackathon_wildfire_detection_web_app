
    FROM node:18-alpine AS frontend-builder
    WORKDIR /app
    
    COPY front_end/package*.json ./
    RUN npm install
    
    COPY front_end/ ./
    RUN npm run build

    FROM nginx:alpine
    WORKDIR /usr/share/nginx/html
    
    COPY --from=frontend-builder /app/dist /usr/share/nginx/html
    
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    
    RUN chown -R nginx:nginx /usr/share/nginx/html
    
    EXPOSE 80
    
    CMD ["nginx", "-g", "daemon off;"]