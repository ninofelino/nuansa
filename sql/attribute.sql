INSERT INTO public.product_attribute_value(id, name,attribute_id)
SELECT ROW_NUMBER () OVER (ORDER BY 1) as id ,ukuran as name,1 as attribute_id from
(
select ukuran from "INV" 
where ukuran!=''
group by 1 order by 1 
) t  
ON CONFLICT DO NOTHING;
