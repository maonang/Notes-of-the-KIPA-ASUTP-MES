# Язык ST (Structured Text)

Обновление параметров
- Если параметр «Способ исполнения» программы на языке ST установлен на значение «По вызову», то параметры в области VAR_INPUT не будут получать актуальные значения до вызова этой программы.

Изменение параметров
- Если нужно изменить параметр, учитывая его значение, то его необходимо поместить в обе области VAR (VAR_INPUT и VAR_OUTPUT).
Нахождение только в VAR_OUTPUT будет провоцировать жесткую запись в параметр начального значения или сформированное в ходе работы алгоритма. Использование еще одной программы на языке ST не позволит её изменять на нужное значение.

Количество элементов в массиве:
UPPER_BOUND(ARR:= <Название массива>, DIM:= <Номер оси>)
Пример: i_cnt := UPPER_BOUND(ARR:= arr_obj, DIM:= 0);

Изменить размер массива:
<Название массива> := RESIZE_ARRAY(ARR := <Название массива>, INIT := <Название структуры массива> , SIZE:=<Новый размер массива>);  

Пример: struct_p_route_obj_list := RESIZE_ARRAY(ARR := struct_p_route_obj_list , INIT := x_struct_route_obj_list , SIZE:=struct_p_db_t_route_ALL[1].p7);  

Склеивание строк (конкатенация):
CONCAT('<Строка 1>','<Строка 2>')
Пример: s = CONCAT('a = ',INT_TO_STRING(i));

Длина строки:  
LEN(<Параметр строкового типа данных>)  
Пример: IF LEN(s_text) > 0 THEN ... 

- '$N' - символ переноса строки  
- '$'' - символ одинарной кавычки  
- EXIT - прерывание цикла FOR  
- IF ... THEN ... ELSIF END_IF - шаблон цикла FOR (Если ... то ..., иначе если ... то ... конец цикла)  
- Работа с двумерными статическими массивами:  
Пример структуры данных массива:  
TYPE struct_OPC_UA_Motor_WorkTime:  
STRUCT  
id: LINT := 0;  
kks: STRING := '""';  
hour: LINT := 0;  
folder: STRING := '""';  
END_STRUCT;  
END_TYPE  

Заполнение полей массива в программе на языке ST:
struct_p_Motor_WorkTime[1].id := 1;  
struct_p_Motor_WorkTime[1].kks := 'M1';  
struct_p_Motor_WorkTime[1].hour := 10;  
struct_p_Motor_WorkTime[1].folder := 'NOR';  

Таймер по тактам выполнения программы (раз в 100 мс):  
// Количество минут  
lr_p1 := FLOOR(i_timer / 120);  
// Количество секунд  
lr_p2 := FLOOR((i_timer MOD 120) / 2);  
s_str := CONCAT(IN1:= DINT_TO_STRING(OSCAT.D_TRUNC(lr_p1)), IN2:= ' мин ', IN3:= DINT_TO_STRING(OSCAT.D_TRUNC(lr_p2)), IN4:= ' сек');  
