FROM nginx:alpine

# Копируем index.html
COPY index.html /usr/share/nginx/html/index.html

# Копируем CSS файлы
COPY css/base.css /usr/share/nginx/html/css/base.css
COPY css/layout.css /usr/share/nginx/html/css/layout.css
COPY css/components.css /usr/share/nginx/html/css/components.css
COPY css/hero.css /usr/share/nginx/html/css/hero.css
COPY css/modal.css /usr/share/nginx/html/css/modal.css

# Копируем JS файлы
COPY js/main.js /usr/share/nginx/html/js/main.js
COPY js/auth.js /usr/share/nginx/html/js/auth.js
COPY js/search.js /usr/share/nginx/html/js/search.js
COPY js/modal.js /usr/share/nginx/html/js/modal.js
COPY js/toast.js /usr/share/nginx/html/js/toast.js
COPY js/scroll-lock.js /usr/share/nginx/html/js/scroll-lock.js
COPY js/constants.js /usr/share/nginx/html/js/constants.js

# Открываем порт 80
EXPOSE 80

# Запускаем nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"]