sp_gent knp_para 
if exists(select 1 from sysobjects where name = 'knp_para' and type = 'U')
begin
	drop table dbo.knp_para
end
go
create table dbo.knp_para (   
--通用参数
paramp     varchar(8)        not null ,    --参数主类
paratp     varchar(8)        not null ,    --参数次类
paracd     varchar(12)       not null ,    --参数代码
parana     u_fullna              null ,    --参数名称
paraam     money                 null ,    --参数金额
paradt     smalldatetime         null ,    --参数日期
parach     u_charac              null ,    --参数字符
parbch     u_charac              null ,    --参数字符b
parcch     u_charac              null ,    --参数字符c
pardch     u_charac              null ,    --参数字符d
parech     u_charac              null ,    --参数字符e
constraint pk_knp_para primary key clustered (paramp, paratp, paracd)
) 
lock allpages
on 'default'
go
(return status = 0)
