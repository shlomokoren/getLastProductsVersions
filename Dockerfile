FROM httpd:alpine
EXPOSE 80
COPY products_versions.json /usr/local/apache2/htdocs/products_versions.json
COPY products_versions.html /usr/local/apache2/htdocs/products_versions.html
COPY products_versions.html /usr/local/apache2/htdocs/index.html