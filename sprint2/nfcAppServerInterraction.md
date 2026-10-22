# Проектирование взаимодействия считывателя с сервером

Данный документ описывает логику обмена данными между мобильным приложением-считывателем (Android App) и сервером при отметке посещаемости.

## 1. Как определяется занятие

Занятие (конкретная пара/урок) **не вычисляется сервером автоматически** по расписанию. Занятие определяет сам преподаватель. 

Перед тем как начать сканировать пропуска, преподаватель в интерфейсе Android-приложения вручную выбирает:
*   Дисциплину (`subject_id`)
*   Группу (`group_id`)
*   Режим работы (`check_in` — приход или `check_out` — уход)

![alt text](https://github.com/Glaurung2000/images/blob/master/%D0%9E%D1%82%D0%BC%D0%B5%D1%82%D0%BA%D0%B0_%D0%BF%D0%BE%D1%81%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F.png)

Таким образом, при поднесении карты студента к телефону, приложение уже "знает", к какому именно занятию относится эта отметка.

## 2. Какие данные передаются

При сканировании пропуска приложение формирует HTTP-запрос `POST /v1/attendance`.

**Заголовки запроса:**
*   `X-Device-Id` — уникальный идентификатор устройства.
*   `X-Timestamp` — текущее время в формате ISO 8601.
*   `X-Signature` — криптографическая подпись запроса, сгенерированная в Android Keystore.

**Тело запроса (JSON):**
*   `uid` — уникальный идентификатор (UID) считанного студенческого пропуска.
*   `subject_id` — ID дисциплины, выбранной преподавателем.
*   `group_id` — ID группы, выбранной преподавателем.
*   `event_type` — тип события: `"check_in"` (пришел) или `"check_out"` (ушел).
*   `timestamp` — время совершения отметки.

## 3. Диаграмма последовательности

Диаграмма отображает процесс от чтения физического пропуска до получения ответа от сервера. Блок `alt` описывает обработку различных сценариев (успех и ошибки согласно тест-кейсам).

```mermaid
sequenceDiagram
    autonumber
    participant App as Android App (Считыватель)
    participant NFC as NFC-модуль
    participant Card as Студенческий пропуск
    participant KS as Android Keystore
    participant API as Сервер (REST API)

    Note over App: Преподаватель выбрал дисциплину,<br/>группу и режим (приход/уход)
    
    App->>NFC: Запрос на чтение UID
    NFC->>Card: Радиосигнал 13.56 МГц
    Card-->>NFC: Передача UID
    NFC-->>App: UID пропуска

    App->>KS: Передать данные запроса для подписи
    Note over KS: Подпись: method + path + body + timestamp
    KS-->>App: Подпись (X-Signature)

    App->>API: POST /v1/attendance (UID, subject_id, group_id, event_type, timestamp)
    
    Note over API: Проверка подписи, устройства,<br/>поиск связей и проверка данных

    alt Подпись невалидна
        API-->>App: 401 Unauthorized (invalid_signature)
    else Студент не найден / Неизвестный UID
        API-->>App: 404 Not Found (unknown_uid)
    else Согласие отозвано
        API-->>App: 403 Forbidden (consent_revoked)
    else Студент из другой группы
        API-->>App: 403 Forbidden (student_wrong_group)
    else Повторный check_in
        API-->>App: 409 Conflict (duplicate_check_in)
    else check_out без check_in
        API-->>App: 409 Conflict (check_out_without_in)
    else Успешная отметка
        API-->>App: 200 OK
        Note over App: Отображение успешного результата (зеленая галочка)
    end
