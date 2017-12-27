sp_gent knp_para 
if exists(select 1 from sysobjects where name = 'knp_para' and type = 'U')
begin
	drop table dbo.knp_para
end
go
create table dbo.knp_para (   
--ͨ�ò���
paramp     varchar(8)        not null ,    --��������
paratp     varchar(8)        not null ,    --��������
paracd     varchar(12)       not null ,    --��������
parana     u_fullna              null ,    --��������
paraam     money                 null ,    --�������
paradt     smalldatetime         null ,    --��������
parach     u_charac              null ,    --�����ַ�
parbch     u_charac              null ,    --�����ַ�b
parcch     u_charac              null ,    --�����ַ�c
pardch     u_charac              null ,    --�����ַ�d
parech     u_charac              null ,    --�����ַ�e
constraint pk_knp_para primary key clustered (paramp, paratp, paracd)
) 
lock allpages
on 'default'
go
(return status = 0)
