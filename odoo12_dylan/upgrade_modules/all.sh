docker-compose restart
docker exec -it odoo12_dylan_web_1 bash -c "/usr/bin/odoo -p 8070 -d hwseta_09_19 --db_user odoo --db_host db --db_pass seekz -u all"

