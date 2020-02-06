![grail.png](/Icon/grail-processing.png)


# Grail Processing #

Этот простой скетч принимает сообщения от Grail и отображает текст на экране,
скетч можно использовать вместе с программами для виджеинга таких как Resolume,
MadMapper, VDMX и других которые поддерживают технологию Syphon (Spout для Windows).

Также в данном скетче возможно набирать текст вручную, а что бы его убрать нужно нажать **TAB**.

По умолчанию скетч не выводит изображение кроме как на экран, для того чтобы
сделать вывод через Syphon или Spout нужно файл **Server.pde-syphon** или **Server.pde-spout**
переименовать в **Server.pde**, а оригинальный файл переименовать в **Server.bypass-pde** или удалить.

Для того чтобы запустить скетч потребуются следующие библиотеки:

* netP5
* oscP5
* JSpout

Их можно скачать по следующей ссылке:  
http://www.sojamo.de/libraries/oscP5/
https://github.com/leadedge/SpoutProcessing/releases

Также для Windows нужен spout:

* spout (http://spout.zeal.co/)

## Управление ##

** Tab **		Убирает текст с экрана  
** ESC **		Выход из приложения

Have fun!
