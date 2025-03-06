# Лабораторная работа №2 по дисциплине "Базы данных"

### ER-диаграмма
![ER-диаграмма](/db_lab_2/image.png)

### Схема отношений
![Схема отношений](/db_lab_2/relationship.png)

### Реляционные схемы

| Админ     |                          |           |           |            |             |            |
|-----------|--------------------------|-----------|-----------|------------|-------------|------------|
| id_админа | email                    | Фамилия   | Имя       | Отчество   | логин       | пароль     |
| 1         | mvladislav6745@gmail.com | Мельников | Владислав | Дмитриевич | mvlad_12317 | j7TG8)spRw |

| Сотрудник     |                       |          |            |            |                |            |            |
|---------------|-----------------------|----------|------------|------------|----------------|------------|------------|
| ID_сотрудника | email                 | Фамилия  | Имя        | Отчество   | Должность      | логин      | пароль     |
| 1             | kosukhinah8@gmail.com | Косухина | Анастасия  | Сергеевна  | менеджер       | n8nastya13 | 8IL;ie.g[! |
| 2             | efanOFF228@gmail.com  | Ефанов   | Александр  | Дмитриевич | СММ-специалист | shullya_15 | Q*QN%hw7t3 |

| Задача    |                                                                 |                       |                   |
|-----------|-----------------------------------------------------------------|-----------------------|-------------------|
| ID_задачи | описание задачи                                                 | статус задачи         | дата формирования |
| 1         | Обновить список тарифов                                         | на согласовании       | 06.03.2025        |
| 2         | Настроить почтовый сервер для клиента ООО "Скрепки почти даром" | в процессе выполнения | 03.03.2025        |

| Подзадача    |                                                                |                  |
|--------------|----------------------------------------------------------------|------------------|
| id_подзадачи | описание подзадачи                                             | статус подзадачи |
| 1            | Сформулировать гипотезу необходимости добавления нового тарифа | 0                |
| 2            | Обновить ER-диаграмму базы                                     | 1                |

| Клиент     |                         |              |
|------------|-------------------------|--------------|
| id_клиента | email                   | моб. телефон |
| 1          | yiy-ojofolu85@yandex.ru | 89375228427  |
| 2          | tesemi-vuca5@bk.ru      | 89610831388  |

| Социальная сеть           |                                     |
|---------------------------|-------------------------------------|
| Telegram                  | VK                                  |
| https://t.me/vladysasdham | https://vk.com/mikhailvsdse_ya_rusi |

| Правовой статус |         |
|-----------------|---------|
| юрлицо          | физлицо |
| 0               | 1       |

| Правовой статус |         |
|-----------------|---------|
| юрлицо          | физлицо |
| 0               | 1       |


| Сделка    |                 |
|-----------|-----------------|
| id_сделки | статус сделки   |
| 1         | ожидание оплаты |
| 2         | на согласовании |

| Тариф     |              |               |           |
|-----------|--------------|---------------|-----------|
| id_тарифа | название     | кол-во памяти | стоимость |
| 1         | минимальный  | 50            | 500       |
| 2         | оптимальный  | 75            | 650       |
| 3         | максимальный | 100           | 1000      |

| Дополнительная услуга |               |                 |
|-----------------------|---------------|-----------------|
| Регистрация домена    | Профилировщик | Почтовый сервер |
| 1                     | 1             | 0               |
