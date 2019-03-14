from dbfread import DBF
import sqlite3
from sqlite3 import Error
import dataset
from odoo import http,exceptions
import json
import os
class Stock:
      info='Stock Module'

      def poserverupload(self)
          pass
          
      def importStock(self):
          sqlsyntax="""
          select a.id,a.podate,'WH/IN/'||a.ponum as PONUM,cast(a.suplier as integer) as PARTNER_ID,
          '['||group_concat(json_object(
          'name','asal',
          'product_id',b.invcode,
          'date',a.podate,
          'date_expected',a.podate,
          'picking_id',1,
          'product_uom',1,
          'location_id',8,
          'location_dest_id',12,
          'quantity_done',b.qrcv
           ))||']' as json
           from receiving a
           left outer join receivingdetail b on a.ponum=b.ponum
           group by 1,2,3 
          """
          sqlsales="""
          select * from
          (
           select NORCP as name,CUSCODE as partner_id
           ,DDATE as dateorder
           ,NORCP,FLAG,CODE from sales where FLAG in('PLU','RTN','D%1')
           ) 
          """
          sumber='/mnt/poserver/ics/DAT/'
          db = dataset.connect('sqlite:///:memory:')
          db = dataset.connect('sqlite:///poserverdb.db')
          terima = db['receiving']
          terimadetail = db['receivingdetail'] 
          sales=db['sales']
          inv=db['inv']
          suplier = db['suplier'] 
          fileupload=['RCV2','INV','RCV1','SUP']

          for fupload in fileupload:
              X=0 
              namafile=sumber+fupload+'.DBF'
              if os.path.isfile(namafile):
                 for record in DBF(sumber+fupload+'.DBF',encoding='iso-8859-1'):
                     print('insert record'+fupload) 
                     X=X+1 
                     record['nomor']=X
                     db[fupload].insert(record)
              else:
                  print('File Not Found'); 
          for record in DBF(sumber+'RCV2.DBF',encoding='iso-8859-1'):
              print('stock----------------------->>>>>>>>>>>>>>>')
              print("RCV2")
              terimadetail.insert(record)
          for record in DBF(sumber+'INV.DBF',encoding='iso-8859-1'):
              print('stock----------------------->>>>>>>>>>>>>>>')
              print("INV")
              inv.insert(record)    
          for record in DBF(sumber+'RCV1.DBF',encoding='iso-8859-1'):
              print("RCV1")
              terima.insert(record)
          for record in DBF(sumber+'SUP.DBF',encoding='iso-8859-1'):
              print("SUP")
              suplier.insert(record)
          for record in DBF('/mnt/poserver/SALES/C0010109.DBF',encoding='iso-8859-1'):
              print("sales")
              sales.insert(record)        

          print("Starting upload")    
          #browse_record('stock_move',21)
          #cur = db.cursor()
          results=db.query(sqlsyntax) 
          #http.request.cr.execute('delete from stock_picking;delete from stock_move')
          XX=0;
          for row in results:
              #print(row)
              XX=XX+1
              print(XX)

              sup=http.request.env['res.partner'].browse(row['PARTNER_ID'])
              if not sup.exists():
                 kd=1 
              else:
                 kd=row['PARTNER_ID'] 
              print('********************************************')   
              print(row['json'])
              print('*******XXXXXXXXXXXXXXXXXXXXXXXXXX************')

              js=json.loads(row['json'])
              #mlines=http.request.env['stock.move'].create([(0,0,js)])
              
              move_lines=[(0,0,{'name':'ngasal','date':row['PODATE'],'date_expected':row['PODATE'],'product_id':10270241,'product_uom_qty':1,'product_uom':1,'location_id':8,'location_dest_id':12,'procure_method':'make to stock'})]
              data={'state':'assigned','id':row['id'],'name':row['PONUM'],'location_id':8,'location_dest_id':12,'picking_type_id':1,'partner_id':kd}
              udata={'location_id':8,'location_dest_id':12,'picking_type_id':1,'partner_id':kd,'state':'assigned','scheduled_date':row['PODATE'],'move_lines':move_lines}
              
              #cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              print(cari.id) 
              if not cari.exists():
                 id=http.request.env['stock.picking'].create(data)
                 for j in js: 
                  print(type(js))
                  print(type(j))
                  j['picking_id']=id['id']
                  try:
                     mlines=http.request.env['stock.move'].create(j)
                  except :
                     pass 
                     #http.request._cr.rollback()
              
              else:
                  print('------------------------ update')
                  try:
                      cari.write(udata)

                  except:
                      print("error")     
          return "Import Stock"

