import odoolib

#from odoorpc import ODOO
"""
1.Buat Attribut di Product_Attribut_line
2.Buat Product di  product_attribut_value
3.Isi Product_template
4.Isi Product Product 
3.Buat Mclas di Product_catagory
"""




# server proxy object

server = jsonrpclib.Server('localhost:8069')
print(dir(server))
