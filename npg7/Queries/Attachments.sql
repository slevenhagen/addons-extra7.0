﻿SELECT 
  ir_attachment.write_date, 
  ir_attachment.description, 
  ir_attachment.url, 
  ir_attachment.file_type, 
  ir_attachment.name, 
  ir_attachment.file_size, 
  ir_attachment.res_name, 
  ir_attachment.res_model, 
  ir_attachment.company_id, 
  ir_attachment.type, 
  ir_attachment.datas_fname, 
  ir_attachment.res_id, 
  ir_attachment.store_fname
FROM 
  public.ir_attachment;
