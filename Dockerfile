FROM httpd:alpine
EXPOSE 80
COPY products_versions.json /usr/local/apache2/htdocs/products_versions.json
COPY products_versions.html /usr/local/apache2/htdocs/products_versions.html
COPY products_versions.html /usr/local/apache2/htdocs/index.html
COPY atlassian_products_versions.json /usr/local/apache2/htdocs/atlassian_products_versions.json
COPY atlassian_security_vulnerability_products.json  /usr/local/apache2/htdocs/atlassian_security_vulnerability_products.json