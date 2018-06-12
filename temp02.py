



('SELECT "t1"."id", "t1"."created_date", "t1"."update_time", "t1"."created_by", "t1"."update_by", "t1"."name", "t1"."description", "t1"."requirement", "t1"."status", "t1"."fps", "t1"."head_in", "t1"."tail_out", "t1"."duration", "t1"."cut_in", "t1"."cut_out", "t1"."cut_duration", "t1"."handles", "t1"."final_delivery", "t1"."thumbnail_file_path", "t1"."project_id", "t1"."sequence_id" FROM "shots" AS "t1" ORDER BY "t1"."name", "t1"."created_date"', [])

('SELECT "t1"."id", "t1"."created_date", "t1"."update_time", "t1"."created_by", "t1"."update_by", "t1"."name", "t1"."description", "t1"."requirement", "t1"."status", "t1"."fps", "t1"."head_in", "t1"."tail_out", "t1"."duration", "t1"."cut_in", "t1"."cut_out", "t1"."cut_duration", "t1"."handles", "t1"."final_delivery", "t1"."thumbnail_file_path", "t1"."project_id", "t1"."sequence_id" FROM "shots" AS "t1" INNER JOIN "sequences" AS "t2" ON ("t1"."sequence_id" = "t2"."id") ORDER BY "t2"."name", "t1"."created_date"', [])



