Вывод команды ls -ld top\_secret (показать права на папку).



──(orion㉿kali)-\[\~/top\_secret]

└─$ ls -la       

total 12

drwx------  2 orion orion 4096 May 11 12:07 .

drwx------ 17 orion orion 4096 May 11 12:18 ..

\-rw-------  1 orion orion   26 May 11 12:07 codes.txt



Картинка 1-2



Вывод команды ls -l top\_secret/codes.txt (показать права на файл).



──(orion㉿kali)-\[\~/top\_secret]

└─$ ls -l codes.txt  

\-rw------- 1 orion orion 26 May 11 12:07 codes.txt



Картинка 1-2



Скриншот попытки чтения файла от имени пользователя intern (с ошибкой Permission denied).

Картинка 2



Вывод команды ls -la \~/.ssh (показать права на ключи).



┌──(orion㉿kali)-\[\~/top\_secret]

└─$ ls -la \~/.ssh

total 20

drwx------  2 orion orion 4096 May 11 12:22 .

drwx------ 17 orion orion 4096 May 11 12:18 ..

\-rw-------  1 orion orion   92 May 11 12:25 authorized\_keys

\-rw-------  1 orion orion  399 May 11 12:22 id\_ed25519

\-rw-r--r--  1 orion orion   92 May 11 12:22 id\_ed25519.pub



Картинка 3-4





