# model person
id,username,password,name,gender,birth_date,school,degree,telephone,email

# model HR
id,username,password,name,company

# model job
id,name,desc,city,salary_low,salary_high,is_done,degree,experience

# model star
id,person_id,job_id

# model bio
id,person_id,url


gender { 女, 男 }

degree {
0不限
1初中及以下
2中专
3高中
4大专
5本科
6硕士研究生
7博士研究生
}

expr {
0    不限
1    在校生
2    应届生
3    1年以内
4    1-3年
5    3-5年
6    5-10年
}