FROM nginx:alpine

# Копируем статические файлы frontend
COPY index.html /usr/share/nginx/html/index.html
COPY styles.css /usr/share/nginx/html/styles.css

# Открываем порт 80
EXPOSE 80

# Запускаем nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"]
