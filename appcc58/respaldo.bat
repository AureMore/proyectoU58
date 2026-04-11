set anio=%date:~6,4%
set mes=%date:~3,2%
set dia=%date:~0,2%
set hora=%time:~0,2%
set nombre=dumpcc58_%anio%%mes%%dia%_%hora%.sql
mysqldump -u root -pVm27797908* bdcc58 > d:\bkp\bd\respaldo_u58\%nombre%