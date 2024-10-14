FROM debian:11-slim

LABEL org.opencontainers.image.authors="dovecot@dovecot.org"

ENV container=docker \
    LC_ALL=C \
    TZ=America/Guayaquil
ARG DEBIAN_FRONTEND=noninteractive

# Añadir claves y fuentes de APT
ADD dovecot.gpg /etc/apt/keyrings/dovecot.gpg
ADD dovecot.list /etc/apt/sources.list.d/

# Copiar archivos de configuración de Dovecot y Postfix
COPY dovecot.conf /etc/dovecot/conf.d/dovecot.conf
COPY postfix/main.cf /etc/postfix/main.cf

# Copiar certificados SSL
COPY mail.smartquail.io/certs/fullchain.pem /etc/dovecot/private/fullchain.pem
COPY mail.smartquail.io/private/privkey.pem /etc/dovecot/private/privkey.pem



# Archivos de configuración postfix+Dovecot
COPY configPD/dovecot-sql.conf.ext /etc/dovecot/dovecot-sql.conf.ext
COPY configPD/10-auth.conf /etc/dovecot/conf.d/10-auth.conf
COPY configPD/10-mail.conf /etc/dovecot/conf.d/10-mail.conf
COPY configPD/10-ssl.conf /etc/dovecot/conf.d/10-ssl.conf

# Copiar el script de inicio
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Crear usuario y grupo postfix si no existen
RUN if ! id -u postfix > /dev/null 2>&1; then \
        addgroup --system postfix && \
        adduser --system --ingroup postfix --no-create-home --shell /sbin/nologin postfix; \
    fi

# Instalar paquetes necesarios y configurar el entorno
RUN apt-get -y update && \
    apt-get -y install \
      tini \
      dovecot-core \
      dovecot-gssapi \
      dovecot-imapd \
      dovecot-ldap \
      dovecot-lmtpd \
      dovecot-lua \
      dovecot-managesieved \
      dovecot-mysql \
      dovecot-pgsql \
      dovecot-pop3d \
      dovecot-sieve \
      dovecot-solr \
      dovecot-sqlite \
      dovecot-submissiond \
      ca-certificates \
      ssl-cert \
      vim \
      tzdata && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g 1000 vmail && \
    useradd -u 1000 -g 1000 vmail -d /srv/vmail && \
    passwd -l vmail && \
    mkdir -p /srv/mail && \
    chown vmail:vmail /srv/mail && \
    mkdir -p /var/mail && \
    chown vmail:vmail /var/mail && \
    chmod 755 /var/mail && \
    mkdir -p /var/spool/postfix/private && \
    chown vmail:vmail /var/spool/postfix/private && \
    # Configurar la zona horaria
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Configurar permisos y propiedad para directorios
RUN mkdir -p /var/mail/info@mail.smartquail.io/tmp && \
    chown -R vmail:vmail /var/mail && \
    chmod -R 755 /var/mail

EXPOSE 24
EXPOSE 110
EXPOSE 143
#EXPOSE 587
EXPOSE 990
EXPOSE 993
#EXPOSE 4190

VOLUME ["/etc/dovecot", "/var/mail/"]

# Usar el script de inicio para arrancar el servicio
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/start.sh"]
