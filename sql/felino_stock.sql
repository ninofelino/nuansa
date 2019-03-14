-- View: public.felino_stock

-- DROP VIEW public.felino_stock;

CREATE OR REPLACE VIEW public.felino_stock AS 
 SELECT ( SELECT res_partner.name
           FROM res_partner
          WHERE res_partner.id = t.vendor) AS vendor,
    ( SELECT product_template.name
           FROM product_template
          WHERE product_template.id = t.ti) AS name,
    sum(t.beli) AS beli,
    sum(t.jual) AS jual
   FROM ( SELECT ( SELECT product_product.product_tmpl_id
                   FROM product_product
                  WHERE product_product.default_code::text = a.barcode::text) AS ti,
            "left"(a.barcode::text, 3)::integer AS vendor,
            b.flag,
            a.barcode,
            a.qty AS beli,
            b.qty AS jual
           FROM felino_receivedetail a
             LEFT JOIN felino_eoddetail b ON a.barcode::text = b.barcode::text
          WHERE b.flag::text = 'PLU'::text) t
  GROUP BY (( SELECT res_partner.name
           FROM res_partner
          WHERE res_partner.id = t.vendor)), (( SELECT product_template.name
           FROM product_template
          WHERE product_template.id = t.ti));

ALTER TABLE public.felino_stock
  OWNER TO postgres;
