# domain-datainput2gen
URL: .../domain-datainput2gen/index.html

| Тип запроса | URL-адрес конечной точки (Endpoint URL) | Описание |
| --- | --- | --- |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">Audit</div> | <div align="center">Аудит данных</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `GET`  | /api/v1/audit/input-statuses | Получить список статусов ввода за период. |
| `GET`  | /api/v1/audit/on-scheduled/data-states | Получить аудиторскую информацию данных ввода "По расписанию". |
| `GET`  | /api/v1/audit/on-requirement/data-states | Получить аудиторскую информацию данных ввода для листов "По требованию". |
| `GET`  | /api/v1/audit/data | Получить аудиторскую информацию данных ввода |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">Configuration</div> | <div align="center">Операции с конфигурациями листов ручного ввода</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `POST`  | /api/v1/configs/group/root | Создать корневую группу |
| `POST`  | /api/v1/configs/group/sheet | Создать группу-лист |
| `PUT`  | /api/v1/configs/group/edit | Обновить данные группы. |
| `DELETE`  | /api/v1/configs/group/delete | Удалить конфигурацию группы. |
| `POST`  | /api/v1/configs/sheet/parameter-group | Создать группировку параметров на листе ввода. |
| `POST`  | /api/v1/configs/sheet | Создать конфигурацию листа. |
| `GET`  | /api/v1/configs/sheet | Получить конфигурацию листа. |
| `PUT`  | /api/v1/configs/sheet/edit | Редактировать основную конфигурацию листа. |
| `POST`  | /api/v1/configs/sheet/draft | Создать черновик для существующей опубликованной или планируемой к публикации конфигурации. |
| `GET`  | /api/v1/configs/structural-elements | Получить все структурные элементы: группы, листы (только опубликованные). |
| `GET`  | /api/v1/configs/structural-elements/not-published | Получить все черновики и отложенные конфигурации листов. |
| `GET`  | /api/v1/configs/structural-elements/archived | Получить все архивные конфигурации листов. |
| `GET`  | /api/v1/configs/structural-elements/version | Получить версию структурной конфигурации. |
| `GET`  | /api/v1/configs/sheet/actual | Получить последнюю актуальную конфигурацию листа. |
| `GET`  | /api/v1/configs/sheet/not-published | Получить черновик или отложенную конфигурацию листа. |
| `DELETE`  | /api/v1/configs/sheet/not-published | Удаление черновика или запланированной конфигурации листа. |
| `POST`  | /api/v1/configs/sheet/parameter | Создать конфигурацию параметра. Применение: Множественное добавление конфигураций полей в одну форму ручного ввода |
| `PUT`  | /api/v1/configs/sheet/parameter/edit | Редактировать конфигурацию параметра. |
| `DELETE`  | /api/v1/configs/sheet/parameter/delete | Удалить конфигурацию параметра. |
| `PUT`  | /api/v1/configs/sheet/parameter-group/edit | Редактировать конфигурацию группы параметров. |
| `DELETE`  | /api/v1/configs/sheet/parameter-group/delete | Удалить конфигурацию группы параметров. |
| `PUT`  | /api/v1/configs/sheet/publish | Публикация конфигурации листа. |
| `PUT`  | /api/v1/configs/sheet/archive | Архивация конфигурации листа. |
| `DELETE`  | /api/v1/configs/sheet/delete-all-data | Окончательное удаление конфигурации листа и всех связанных данных. |
| `PUT`  | /api/v1/configs/sheet/recover | Восстановление архивной конфигурации через создание черновика. |
| `PUT`  | /api/v1/configs/sheet/copy | Копирование актуальной конфигурации через создание черновика. |
| `GET`  | /api/v1/configs/sheet/parameter/platform-integration | Запрос данных конфигурации интеграции с платформой для параметра. |
| `POST`  | /api/v1/configs/sheet/mark-om-outdated | Отметить конфигурацию параметров ОМ как устаревшую. |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">Display</div> | <div align="center">Настройки отображения параметров, групп параметров, листов и структурных элементов</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `POST`  | /api/v1/display/parameter/hide | Скрыть параметр |
| `POST`  | /api/v1/display/parameter/show | Показать параметр |
| `POST`  | /api/v1/display/parameter-group/hide | Скрыть группу параметров |
| `POST`  | /api/v1/display/parameter-group/show | Показать группы параметров |
| `POST`  | /api/v1/display/structural-elemet/hide | Скрыть структурный элемент |
| `POST`  | /api/v1/display/structural-elemet/show | Показать структурный элемент |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">Platform</div> | <div align="center">Интеграция с платформой</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `GET`  | /api/v1/platform/models | Получить список моделей из платформы. |
| `GET`  | /api/v1/platform/objects | Получить список объектов. |
| `GET`  | /api/v1/platform/properties | Получить список свойств объекта. |
| `POST`  | /api/v1/platform/uom-import | Импорт единиц измерения из Платформы. |
| `POST`  | /api/v1/platform/rtdb-dictionary-import | Импорт дискретного набора из Платформы. |
| `GET`  | /api/v1/platform/rtdb-dictionaries | Получение списка дискретных наборы из Платформы. |
| `GET`  | /api/v1/platform/rtdb-dictionary | Получение дискретного набора из Платформы по внешнему идентификатору (идентификатор дискретного набора в модуле Ручной Ввод) |
| `GET`  | /api/v1/platform/rtdb-search | Поиск тегов БДРВ по имени. |
| `POST`  | /api/v1/platform/evaluate-expression | Вычисление выражения модулем MVEL. Применение: Проверка выполнения MVEL-выражений перед добавлением в расчетные поля формы ручного ввода |
| `GET`  | /api/v1/platform/rtdb-search-by-property | Поиск тега БДРВ, привязанного к свойству объекта. |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">ReferenceData</div> | <div align="center">Операции со справочными данными</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `POST`  | /api/v1/reference-data/fill-csv | Замена записей справочника |
| `GET`  | /api/v1/reference-data/items | Получить пользовательский справочник и его элементы. |
| `GET`  | /api/v1/reference-data/export-csv | Экспорт справочника в CSV |
| `PUT`  | /api/v1/reference-data/archive | Отправить в архив справочник и все его элементы. |
| `POST`  | /api/v1/reference-data/create | Создать новый справочник. |
| `GET`  | /api/v1/reference-data/list | Получить список справочников. |
| `PUT`  | /api/v1/reference-data/udpate | Обновить метаданные справочника. |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">RequirementSheet</div> | <div align="center">Оерации с данными листов "По требованию"</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `POST`  | /api/v1/sheets/on-requirement/state | Создать состояние листа "по требованию". |
| `GET`  | /api/v1/sheets/on-requirement/state | Запрос получения актуального состояния для листа по требованию. |
| `GET`  | /api/v1/sheets/on-requirement/input-data | Получить данные ввода за период в порядке убывания от самых новых данных ввода, до самых старых для листов с типом по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/personal/change | Изменить набор персональных данных ввода пользователя для состояния листа по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/published/change | Изменить набор общих данных ввода для состояния листа по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/approve | Подтвердить данные ввода для состояния листа по требованию. |
| `DELETE`  | /api/v1/sheets/on-requirement/state/input-data/personal/delete | Удалить все персональные данные ввода. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/approved/edit | Отредактировать набор подтвержденных данных ввода для состояния листа по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/start-editing | Перевести лист в режим редактирования для листа по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/end-editing | Отключить режим редактирования листа для листа по требованию. |
| `GET`  | /api/v1/sheets/on-requirement/last-input-data-time | Получить время последних данных ввода для листов с типом по требованию. |
| `PUT`  | /api/v1/sheets/on-requirement/state/input-data/recover | Восстановление данных из родительской формы ввода. |
|🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹🔹|
|<div align="center">☑️</div>| <div align="center">ScheduledSheet</div> | <div align="center">Операции с данными листов "По расписанию"</div> |
|<div align="center">🔽</div>|<div align="center">🔽</div>|<div align="center">🔽</div>|
| `POST`  | /api/v1/sheets/on-scheduled/state | Создать состояние листа "по расписанию". |
| `GET`  | /api/v1/sheets/on-scheduled/state | Получить состояние листа "по расписанию". |
| `GET`  | /api/v1/sheets/on-scheduled/input-statuses | Получить статусы ввода за период в порядке убывания от самого нового состояния листа, до самого старого для листов с типом по расписанию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/personal/change | Изменить набор персональных данных ввода пользователя для состояния листа по расписанию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/published/change | Изменить набор общих данных ввода для состояния листа по расписанию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/approve | Подтвердить данные ввода для состояния листа по расписанию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/approved/edit | Отредактировать набор подтвержденных данных ввода для состояния листа по расписанию. |
| `DELETE`  | /api/v1/sheets/on-scheduled/state/input-data/personal/delete | Удалить все персональные данные ввода. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/start-editing | Перевести лист в режим редактирования для листа по расписанию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/end-editing | Отключить режим редактирования листа для листа по расписанию. |
| `POST`  | /api/v1/sheets/on-scheduled/state/migrate | Мигрировать состояние листа на последнюю акутальную версию. |
| `PUT`  | /api/v1/sheets/on-scheduled/state/input-data/recover | Восстановление данных из родительской формы ввода. |
