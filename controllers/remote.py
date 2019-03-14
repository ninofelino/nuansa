
import odoorpc

# Prepare the connection to the server
odoo = odoorpc.ODOO('nbi.falinwa.com')

# Check available databases
print(odoo.db.list())

# Login
odoo.login('PT_Nuansa_Baru_Indonesia', 'eko', '********')

# Current user
user = odoo.env.user
print(user.name)            # name of the user connected
print(user.company_id.name) # the name of its company



