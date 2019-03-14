select article,ukuran,description,description,
substring(description from '26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42'),
REGEXP_REPLACE(description,'26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42','X'),
REGEXP_REPLACE(description,'/([0-9,]+(\.[0-9]{3})?)/','X')

 from felino_felino LIMIT 100