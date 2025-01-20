FROM httpd:alpine
EXPOSE 80
COPY products_versions.json /usr/share/nginx/html/products_versions.json
COPY products_versions.html /usr/share/nginx/html/products_versions.html
COPY products_versions.html /usr/share/nginx/html/index.html