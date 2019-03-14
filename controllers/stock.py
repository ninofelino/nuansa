from dbfread import DBF
import sqlite3
from sqlite3 import Error
import dataset
from odoo import http,exceptions
import json
import os 
import logging
import re
from psycopg2 import IntegrityError
class Stock:
      info='Stock Module'
     
      def __init__(self):
          self.data = []
          self.db = dataset.connect('postgresql://felino:felino@localhost/nbi')
          #cr.dbname
      def inv2odoo(self):
          self.data = []
          product_attribute_value="""
          insert into product_attribute_value(id,name,attribute_id)
          select index as id ,ukuran as name,1 as attribute_id from "INV" 
          where index>0 
          GROUP BY 1,2 ORDER BY 1  
          ON CONFLICT DO NOTHING
          """
          mclass="""
          insert into product_category(id,name)
          select code::float,mclass
          from
          (
          select "MCLSCODE" as mclass,
          replace(replace(replace(replace(replace(replace(replace(replace(replace("MCLSCODE",'A','1'),'B','2'),'C','3'),'D','4'),'E','5'),'F','6'),'G','7'),'H','8'),'M','') as code
          from"INV" 
          WHERE LEFT("MCLSCODE",1)='M' 
          GROUP BY 1,2 ORDER BY 1 
          ) t where code!=''
          ON CONFLICT DO NOTHING
          """
          sql="""
          select replace(article,'''','') as article,(select "DESC" from "SUP" WHERE "CODE"=LEFT("INV"."CODE",3)) as vendor,LEFT("INV"."CODE",3)::int as vendorid,
          (select id from product_category where name="MCLSCODE")::int as mclscode,
          "SELLPRC" as list_price,"COSTPRC" as standard_price,
          cast(min("CODE") as integer) as id,count(*) as jm,json_agg(ukuran order by ukuran) as sizerange,
          json_agg(json_build_object('barcode',"CODE",'attribut',ukuran,'desc1',"DESC1",'onhand',"LQOH",'attribute',index)) as product
          from "INV" group by 1,2,3,4,5,6
          """
          sqlinsert="""
          insert into product_template(id,name,type,categ_id,uom_id,uom_po_id,responsible_id,tracking,active,purchase_line_warn)
          values
          (%s,'%s','product',1,1,1,1,'none',True,'no-message') ON CONFLICT DO NOTHING
          """
          product_cat="""
          SELECT "MCLSCODE" FROM "INV"GROUP BY 1
          """
          attribut_line="""
          insert into product_attribute_line(id,product_tmpl_id,attribute_id) values(\
                  %s,%s,1) ON CONFLICT  DO  NOTHING RETURNING id
          """
          product_insert="""
          insert into product_product(id,product_tmpl_id,default_code,active,create_uid,write_uid)\
            values(%s,%s,'%s',TRUE,1,1) ON CONFLICT ON CONSTRAINT product_product_pkey DO UPDATE SET product_tmpl_id=%s
          """
          product_attribute="""
            insert into product_attribute_value_product_product_rel(product_product_id, product_attribute_value_id)\
            values(%s,%s) ON CONFLICT DO NOTHING
            """
          produck_line_attr="""
          INSERT INTO public.product_attribute_line_product_attribute_value_rel(
          product_attribute_line_id, product_attribute_value_id)
          VALUES (%s,%s)  ON CONFLICT DO NOTHING;
          """ 
          product_attr="""
          INSERT INTO public.product_attribute(
            id, name, sequence, create_variant, create_uid, create_date, 
            write_uid, write_date)
            VALUES (?, ?, ?, ?, ?, ?, 
            ?, ?);
          """
          attribut="""
          INSERT INTO public.product_attribute(
            id, name) VALUES(1,'SIZE') ON CONFLICT DO NOTHING;
          """
          attribut_line_product_attribute_value="""
          INSERT INTO public.product_attribute_line_product_attribute_value_rel(
            product_attribute_line_id, product_attribute_value_id)
          VALUES (%s, %s) ON CONFLICT DO NOTHING;
          """
          product_attribute_value_product_product_rel="""
          INSERT INTO public.product_attribute_value_product_product_rel(
          product_product_id, product_attribute_value_id)
          VALUES (%s,%s) ON CONFLICT DO NOTHING;
          """
          #http.request.cr.execute("delete from product_template where description='upload';") 
          http.request.cr.commit()
          
          qry=http.request.cr
          #attr=self.db.query(attribut)
          #for rec in attr:     
              #http.request.env['product.attribute'].create({'name':rec[1]})
          http.request.cr.execute(attribut)
          http.request.cr.execute(product_attribute_value)
          
          http.request.cr.commit() 
          results = self.db.query(sql)
          for rec in results:
              print(sqlinsert %(rec['id'],rec['article']))
              http.request.cr.execute(sqlinsert %(rec['id'],rec['article'])) 
              http.request.cr.commit()
              id=http.request.env['product.template'].browse(rec['id'])
              http.request.cr.execute(mclass)
              http.request.cr.commit()
              category=1 
              vendor=rec['vendorid']
              if not rec['mclscode'] is None:
                 category=rec['mclscode']
              id.write({'name':rec['article'],'active':True,'type':'product','list_price':rec['list_price'],'categ_id':category,'purchase_method':'receive','company_id':1,'purchase_ok':True,'rental':False,'standard_price':rec['standard_price'],'default_code':rec['id'],'vendor':vendor})
              print('write--------------------------------------',attribut_line)
              print(attribut_line %(rec['id'],rec['id']))
              http.request.cr.execute(attribut_line %(rec['id'],rec['id']))
              product=rec['product']
              http.request.cr.commit() 
              try:
                 pass 
                 #with http.request.env.cr.savepoint(): 
                 #     http.request.cr.execute("delete from product_product where product_tmpl_id="+str(rec['id']))
                 #     http.request.cr.commit()
              except:
                  pass    
              attr=''
            
              for pro in product:
                  sq=(product_insert %(pro['barcode'],rec['id'],pro['barcode'],rec['id']))
                  print('---------------------------',pro)
                  
                  http.request.cr.execute(sq)
                  if pro['attribute'] != None:
                     if pro['attribute'] != 0:
                        print(pro) 
                        attr=(produck_line_attr %(rec['id'],pro['attribute']))
                        print('>>>>>>>>>>>>>>>>>',pro['attribute'])
                        http.request.cr.execute(attr)
                        http.request.cr.commit()
                        print('++++++++++++++')
                        rel=product_attribute_value_product_product_rel %(pro['barcode'],pro['attribute'])  
                        print('++++++++++++++',rel)
                        try:
                           http.request.cr.execute(rel)
                           http.request.cr.commit()
                        except:
                            pass    
                  #print(atr_line)   
                 
                  

          return 'ok'

      def poserver(self):
          server='/mnt/poserver/ics/DAT/'
          X=0
          #db = dataset.connect('sqlite:///poserverdb.db')
          fileupload=['RETST1','RETST2','RTSU1','RTSU2','RETSU1','RETSU2','RDIS1','RDIS2','TRANS1','TRANS2','STORE','SUP','RCV1','RCV2','INV','TRANS2S1','TRANS2S2','CUS','SUP'] 
         
          #fileupload=['INV'] 
          for fupload in fileupload:
              uk=['ALL','01','2','3','4','5','O','S','M','L','XL','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45']
              namafile=server+fupload+'.DBF'
              if os.path.isfile(namafile):
                 self.db.query('DROP TABLE IF EXISTS '+fupload+';')
                 self.db[fupload].drop()
                 for record in DBF(server+fupload+'.DBF',encoding='iso-8859-1'):
                     print('insert record'+fupload) 
                     X=X+1 
                     record['nomor']=X
                     if fupload=='INV':
                        ukuran=''   
                        print('--------->>>>>>>>>>>>>>>>',X)
                        #rex=r'\sS|\sM$|\sL$|\sXL$|\sXXL$|\s1$|\s2$|\s3$|\s4$|\s5$|\s6$|\s7$|\s8$|\s9$|\s18|\s19|\s20|\s21|\s22|\s23|\s24|\s25|\s26|\s27|\s28|\s29|\s30|\s31|\s32|\s33|\s34|\s35|\s36|\s36\s|\s37|\s37\s|\s38|\s38\s|\s39|\s40|\s41|\s42|\s43|\s44|\s45'
                        rex=r'\s\d{2}$|\s\d{2}\s|\s\D$|\sS$|\sS\s|\sXL$|\sXL\s|\sXXL$|\sXXL\s|\sXXXL$|\sXXXL\s|\sd$'
                        if re.search(rex,record['DESC1']):
                           record['ukuran']=re.search(rex,record['DESC1']).group(0)
                           record['ukuran']=record['ukuran'].strip()
                           record['article']=re.sub(record['ukuran'],'',record['DESC1'])
                           
                           if not record['ukuran'] in uk:
                                record['index']=0
                           else:
                                record['index']=uk.index(record['ukuran'])
                                print(uk.index(record['ukuran']))
                        else:
                           record['ukuran']=''   
                           record['article']=record['DESC1']
                           
                           #record['atribute_value']=
                        print("mclass->>>>>>>>>>>>>>>>>>>>>>>>>..") 
                        record['categ_id']=0
                        #record['MCLSCODE'].replace('A','1').replace('B','2').replace('C','3').replace('D','4').replace('E','5'),replace('F','6').replace('G','7').replace('H','8').replace('M','')
                              
                        print(record['article'],'!',record['ukuran'],'!',record['DESC1'])      
                     if fupload=="SUP":
                        #record['BALANCE']=0
                        record['VALDORD']=0 

                     self.db[fupload].insert(record)
              else:
                  print("Not Found")       

          return "posserver"
      def testinv(self):
          db = dataset.connect('sqlite:///poserverdb.db')
          results=db.query('select desc1 from inv limit 100')
          for rec in results:
              print('-------------------------------------')
              
              isi=rec['DESC1']
              if re.search(r'37|38',isi):
                 ukuran=re.search(r'37|38',isi).group(0)
                 article=re.sub(ukuran,'',isi)
              else:
                 ukuran=''   
                 article=isi
              
              print(rec['DESC1'],'!',article,'!',ukuran)  
          return "EEE"  
      def importVendor(self):
          # res_partner_id_seq
          # ALTER SEQUENCE res_partner_id_seq RESTART WITH 22000;
          vendorsql="""
          insert into res_partner(id,name,picking_warn,invoice_warn,purchase_warn,supplier,active,company_id,display_name)
          SELECT "CODE"::INT as id,"DESC" as name,
          'no-message' as picking_warn,
          'no-message' as invoice_warn,
          'no-message' as purchase_warn,
          True as supplier,
          True as active,
          1 as company_id,
          "DESC" as display_name
          FROM "SUP" 
          ON CONFLICT  ON CONSTRAINT res_partner_pkey DO update SET active=true,
          company_id=1,write_uid=1;
          """
          return 'vendor'    
      def importStock(self):
          #delete from stock_picking;
          #delete from stock_move;
          #DELETE FROM stock_move_line
          #DELETE FROM STOCK_QUANT
          vendor="""
          insert into res_partner(
              invoice_warn,invoice_warn_msg, picking_warn, picking_warn_msg, purchase_warn,supplier,active,company_id,id,name)
             
select 
'no-message' as invoice_warn,
'no-message' as invoice_warn_msg,
'no-message' as picking_warn,
'no-message' as picking_warn_msg,
'no-message' as purchase_warn,

true as supplier,
true as active,
1 as company_id,
"CODE"::int as id,"DESC" as name from "SUP"
 ON CONFLICT DO NOTHING;
          """
          sqlsyntax="""
          select a.ID,1 as location_id,11 as location_dest_id,a."SUPLIER"::int as "PARTNER_ID",a."PODATE",'WH/IN/'||a."PONUM" as "PONUM",json_agg(
          json_build_object(
          'name',a."PONUM",   
          'product_id',b."INVCODE",
          'date',a."PODATE",
          'date_expected',a."PODATE",
          'picking_id',1,
          'product_uom',1, 
          'location_id',1,
          'location_dest_id',1, 
          'quantity_done',b."QRCV" 
           
          )) as json
          from "RCV1" a 
          left outer join "RCV2" b on a."PONUM"=b."PONUM"
          group by 1,2,3 order by "PONUM"
          
           
          """
          sqlsales="""
          select * from
          (
           select NORCP as name,CUSCODE as partner_id
           ,DDATE as dateorder
           ,NORCP,FLAG,CODE from sales where FLAG in('PLU','RTN','D%1')
           ) 
          """
          results=self.db.query(sqlsyntax)
          for row in results: 
              bpartner="""
              insert into res_partner(
              invoice_warn,invoice_warn_msg, picking_warn, picking_warn_msg, purchase_warn,supplier,active,company_id,id,name)
              values
              ('no-message','no-message','no-message','no-message','no-message',TRUE,True,1,%s,'%s')   
                ON CONFLICT ON CONSTRAINT  res_partner_pkey DO UPDATE SET supplier=True,active=true,company_id=1;
              """
              self.db.query(bpartner %(row['PARTNER_ID'],'nama'+str(row['PARTNER_ID'])))
              self.db.commit()

              sup=http.request.env['res.partner'].browse(row['PARTNER_ID'])
              move_lines=[(0,0,{})]
              data={'state':'assigned','name':row['PONUM'],'location_id':1,'location_dest_id':1,'picking_type_id':1,'partner_id':row['PARTNER_ID'],'scheduled_date':row['PODATE']}
              udata={'location_id':1,'location_dest_id':1,'picking_type_id':1,'partner_id':row['PARTNER_ID'],'state':'assigned','scheduled_date':row['PODATE']}
              cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              if not cari.exists():
                 id=http.request.env['stock.picking'].create(data)
              cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              #cari.write({'partner_id':row['PARTNER_ID']})
              #self.db.query('delete from stock_move where picking_id='+str(cari.id))
              #self.db.commit()
              for j in row['json']:
                  print("--------------------->>>",cari.id,j['product_id'],j)
                  smove={'picking_id':cari.id,
                  'name':'test','date':row['PODATE'],'date_expected':row['PODATE']
                  ,'product_id':j['product_id'],'location_id':row['location_id'],
                  'location_dest_id':row['location_dest_id'],
                  'product_uom':1,'quantity_done':j['quantity_done']
                  }
                  try: 
                      with http.request.env.cr.savepoint():
                           http.request.env['stock.move'].create(smove)
                           
                  except IntegrityError:
                         return "error"

                  http.request.cr.commit()
                  #print("Error",cari.id,j)
                  #,'product_qty':j['quantity_done']
                  #http.request.cr.commit()
                  #http.request.env['stock.quant'].create({'product_id':j['product_id'],'location_id':j['location_id'],'quantity':j['quantity_done'],'reserved_qty':0})
                  #mlines=http.request.env['stock.move'].create(j)
              #cari.state='assigned'
               #stock_quant    
                     
                       
          return "Import Stock"

      def importWh(self):
          namastore="""
          select "CODE"::int+1 as id,"DESC" as name,"NICKNAME" as code from "STORE"
          """
          http.request.cr.execute(namastore)
          data = http.request.cr.fetchall()
          #gudang.write({'name':rec[1],'active':True,'loc_stock_id':rec[0]})
          for rec in data:
              id=rec[0]
              print(id,type(id))
              gudang=http.request.env['stock.warehouse'].sudo().browse(id) 
              if not gudang.exists():
                  print('create new') 
                  try:
                      http.request.cr.execute("insert into stock_warehouse(delivery_steps,reception_steps,lot_stock_id,company_id,view_location_id,id,name,code) values('ship_only','one_step',1,1,11,%s,'%s','%s')" %(rec[0],rec[1],rec[2][1:5]))
                      http.request.cr.commit()
                  except:
                      print("error")  
                      http.request.cr.rollback()

              else:    
                  print("update")
                  try:
                     pass 
                     #gudang.write({'name':rec[1],'active':True,'loc_stock_id':rec[0]})
                  except:
                      print("error")   
              #print(gudang)
