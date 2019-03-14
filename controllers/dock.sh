docker run -d --name unkkuri-odoo --link unkkuri-db:db -p 8869:8869 \
 --network unkkuri-odoo-nw \
 --mount source=unkkuri-odoo-data,target=/var/lib/odoo \
 --mount source=unkkuri-odoo-extra-addons,target=/mnt/extra-addons \
 --env POSTGRES_PASSWORD=unkkuri-secret-pw \
 veivaa/odoo:12.0