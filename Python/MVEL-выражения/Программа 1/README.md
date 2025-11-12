Конвертер простого MVEL-выражения для расчета дебаланса с добавлением проверки на значения Bad.  
  
Пример (часть исходного и конечного выражения укорочены в местах многоточия).  
Было:  
Double Debalance = F219 + ... + FA01 + (F15 + ... + LOSKON) * (-1); Debalance  
  
Стало:  
Double DF219; if (Fn.badVal($F219, '*')) {DF219 = 0} else {DF219 = F219};  
...  
Double DFA01; if (Fn.badVal($FA01, '*')) {DFA01 = 0} else {DFA01 = FA01};  
Double DF15; if (Fn.badVal($F15, '*')) {DF15 = 0} else {DF15 = F15};  
...  
Double DLOSKON; if (Fn.badVal($LOSKON, '*')) {DLOSKON = 0} else {DLOSKON = LOSKON};  
Double Debalance = DF219 + ... + DFA01 + (DF15 + ... + DLOSKON) * (-1); Debalance  
В конце требуется через notepad удалить только переносы строк регуляркой \r\n  
