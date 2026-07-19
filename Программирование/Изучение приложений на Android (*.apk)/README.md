# Инструментарий для реверс-инжиниринга Android/Unity приложений

Подборка основных инструментов для анализа, декомпиляции и модификации приложений на платформе Android с движком Unity.

---

## Основные инструменты

### Apktool
Инструмент для декодирования ресурсов APK-файлов и их последующей пересборки.

**Ссылка:** [apktool.org](https://apktool.org/)

**Назначение:** Распаковка APK, извлечение ресурсов, манифеста, smali-кода.

---

### Il2CppDumper

#### Основная версия v6.7.46
Поддержка Unity v5.3 (2022.2)

**Ссылка:** [Perfare/Il2CppDumper](https://github.com/Perfare/Il2CppDumper)

#### Модифицированная версия v6.7.46-lxraa.1
Поддержка Unity 6 / metadata v39

**Ссылка:** [lxraa/Il2CppDumper](https://github.com/lxraa/Il2CppDumper)

**Назначение:** Восстановление структур и сигнатур из IL2CPP-бинарников.

---

### Frida
Платформа для динамической инструментации приложений.

**Ссылка:** [frida/frida](https://github.com/frida/frida)

#### Установка frida-server (Android x86_64):

Скачать релиз v17.12.0
wget https://github.com/frida/frida/releases/download/17.12.0/frida-server-17.12.0-android-x86_64.xz

Распаковать
unxz frida-server-17.12.0-android-x86_64.xz

Переименовать
mv frida-server-17.12.0-android-x86_64 frida-server


---

### frida-il2cpp-bridge v0.13.1
Мост для дампа IL2CPP-данных напрямую из памяти процесса.

**Ссылка:** [vfsfitvnm/frida-il2cpp-bridge](https://github.com/vfsfitvnm/frida-il2cpp-bridge)

#### Необходимые файлы для работы:

| Путь | Описание |
|------|----------|
| `C:\...\<папка_apk>\lib\arm64-v8a\libil2cpp.so` | Библиотека IL2CPP |
| `C:\...\<папка_apk>\assets\bin\Data\Managed\Metadata\global-metadata.dat` | Глобальные метаданные |

---

### AssetStudio
Инструмент для извлечения ресурсов из Unity-сборок.

**Ссылка:** [Perfare/AssetStudio](https://github.com/Perfare/AssetStudio)

**Назначение:** Просмотр и экспорт текстур, моделей, аудио и других ассетов.

---

### UABE (Unity Asset Bundle Extractor)
Редактор Asset Bundle-файлов Unity.

**Ссылка:** [SeriousCache/UABE](https://github.com/SeriousCache/UABE)

**Назначение:** Модификация отдельных ассетов внутри бандлов.

---

### JADX
Декомпилятор DEX-файлов в читаемый Java-код.

**Ссылка:** [skylot/jadx](https://github.com/skylot/jadx)

**Назначение:** Преобразование байт-кода Android в Java-исходники.

---

### IDA Pro
Мощный дизассемблер и отладчик.

**Ссылка:** [hex-rays.com/ida-free/](https://hex-rays.com/ida-free/)

**Назначение:** Дизассемблирование и анализ нативного кода (архитектуры ARM/x86).

---

### pidcat
Утилита для фильтрации логов Android по PID-приложения.

**Ссылка:** [raw.githubusercontent.com/JakeWharton/pidcat](https://raw.githubusercontent.com/JakeWharton/pidcat/)

**Назначение:** Упрощение просмотра логов конкретного приложения.

---

## Типовой рабочий процесс

1. **Apktool** — распаковка APK
2. Извлечение `libil2cpp.so` и `global-metadata.dat`
3. **Il2CppDumper** — восстановление сигнатур
4. **JADX** — декомпиляция DEX
5. **AssetStudio** — извлечение ресурсов
6. **frida-il2cpp-bridge** — дамп памяти
7. **IDA Pro** — анализ нативного кода

---

> **Примечание:** Данные инструменты предназначены исключительно для образовательных целей и легального анализа собственных приложений или приложений с явного разрешения правообладателя.
