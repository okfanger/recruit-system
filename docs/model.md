# model person
id,username,password,name,gender,birth_date,school,degree,telephone,email

# model HR
id,username,password,name,company

# model job
id,name,desc,city,salary_low,salary_high,is_done,degree,experience

# model star
id,person_id,job_id

# model bio
id,job_id,person_id,url


gender { 女, 男 }

degree {
不限, 初中及以下, 中专, 高中, 大专, 本科, 硕士研究生, 博士研究生
}

expr {'不限','在校生','应届生','1年以内','1-3年','3-5年','5-10年'}

salary {

}