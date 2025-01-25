Бот для записи на какие-либо услуги.
(черновая версия README, актуальная будет после написания бота)

Для запуска:
1 - git clone проект
2 - установить зависимости из requierements.txt
3 - создать .env по шаблону из .env-example
4 - заполнить docker-compose.yml, запустить compose
5 - применить миграции базы данных через alembic

У бота есть четкое разделение на группы пользователей (у каждой группы свой функционал).
В боте реализован функционал рассылок, отложенных сообщений, системы подписки.
Все управление ботом происходит от роли Старшего Администратора прямо в телеграмм.

Старший администратор - технические функции для работы с ботом.
Имеет минимально необходимый функционал для управления ботом.
![image](https://github.com/user-attachments/assets/59f50762-9220-4992-a124-6c906827de9f)

Администратор - является "мастером" к которому могут записываться люди.
Позволяет гибко настраивать расписание работы, делать ручные записи/заметки, поддерживает массовую рассылку.
![image](https://github.com/user-attachments/assets/a6d96c42-c9e4-4fff-a3fc-167b9f036970)

Пользователь - является "клиентом" который регистрируется по ссылке от своего мастера, и может записываться к нему без личного общения.
(тут скрин меню пользователя)


